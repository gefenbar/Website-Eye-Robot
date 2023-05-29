import time
import os
import threading
import pandas as pd
import bson.json_util as json_util
import shutil

from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, url_for, make_response, send_file
from flask_cors import CORS

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from scanners.color_contrast import detect_color_contrast
from scanners.small_text import detect_small_text
from scanners.text_overlap import detect_text_overlap
from scanners.edge_overflow import detect_edge_overflow
from scanners.content_overflow import detect_content_overflow

from upload_to_s3 import S3Uploader
from send_to_db import MongoDBClient

app = Flask(__name__)
CORS(app)
load_dotenv()

mongoDbClient = MongoDBClient(
    os.getenv('MONGO_URL'), 'eye-robot')
s3Uploader = S3Uploader(os.getenv('AWS_ACCESS_KEY_ID'),
                        os.getenv('AWS_SECRET_ACCESS_KEY'))


@app.route("/", methods=["GET"])
def heartbeat():
    return "Website Eye Robot is up and running!"


@app.route("/reports", methods=["GET"])
def getReports():

    return json_util.dumps(mongoDbClient.find('reports'))


@app.route("/report", methods=["POST"])
def index():
    if request.method == "POST":
        delete_existing_folders_and_files()
        create_directories_for_screenshots()

        input_url = request.json.get("url")

        # Define the data variable as an empty dictionary
        mongoDbClient.insert_document('reports', {
            'webpageUrl': input_url,
            'issuesFound': []
        })

        paths_to_images = []

        def main_task(url, page_urls):
            resolutions = [(1920, 1080), (1366, 768), (375, 667)]

            driver = webdriver.Chrome(executable_path='chromedriver')
            try:
                # Open URL in web driver and add it to the page_urls list
                driver.get(url)
                page_urls.append(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                visited_pages = set()

                for i, resolution in enumerate(resolutions):
                    visited_pages_resolution = set()  # keep track of visited pages for this resolution

                    # Create folder name based on resolution
                    folder_name = f"{resolution[0]}x{resolution[1]}"

                    # Set window size to current resolution
                    driver.set_window_size(*resolution)

                    while True:
                        # Get current page URL
                        current_url = driver.current_url

                        # Check if current page has already been visited at this resolution
                        if current_url in visited_pages_resolution:
                            print(
                                f"Skipping already visited page at {resolution}: {current_url}")
                            break

                        # Add current page to visited pages at this resolution
                        visited_pages_resolution.add(current_url)
                        driver.execute_script(
                            "document.body.style.overflow = 'hidden';")
                        try:

                            # Wait for the page to finish loading completely
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.TAG_NAME, "body"))
                            )

                            # Get page height
                            page_height = driver.execute_script(
                                "return document.body.scrollHeight"
                            )

                            # Set initial scroll position and section height
                            scroll_position = 0
                            section_height = int(resolution[1] * 0.8)

                            driver.execute_script("window.scrollTo(0, 0)")

                            # Capture screenshots of each section of the page
                            while scroll_position < page_height:
                                img_path_to_save = os.path.join(
                                    folder_name,
                                    f"{i}{len(visited_pages_resolution)}{scroll_position}.png",
                                )
                                driver.save_screenshot(
                                    img_path_to_save
                                )
                                paths_to_images.append(img_path_to_save)
                                scroll_position += section_height
                                driver.execute_script(
                                    f"window.scrollTo(0, {scroll_position})"
                                )
                                time.sleep(0.2)

                            links = driver.find_elements(By.TAG_NAME, "a")

                            for link in links:
                                try:
                                    href = link.get_attribute("href")
                                    if (
                                        href is not None
                                        and href.startswith(url)
                                        and href not in visited_pages_resolution
                                        and "#" not in href
                                        and not href.lower().endswith(".pdf")
                                    ):
                                        driver.get(href)
                                except StaleElementReferenceException:
                                    continue

                        except StaleElementReferenceException:
                            continue

            finally:
                driver.quit()

            scanner_names = ['color_contrast', 'small_text',
                             'text_overlap', 'edge_overflow', 'content_overflow']

            issue_found = False

            lock = threading.Lock()
            threads_list = []
            processed = []

            def process_image(img_path, resolution):
                if img_path in processed:
                    print(f'already processed - {img_path}')
                    return
                processed.append(img_path)
                nonlocal issue_found
                print(f'process - {img_path}, {resolution}')

                for scanner_name in scanner_names:
                    fileName = img_path.split('/')[1]
                    save_path = f'{resolution}/{scanner_name}{fileName}'
                    if scanner_name == 'color_contrast':
                        issue = detect_color_contrast(
                            img_path, save_path)
                    elif scanner_name == 'small_text':
                        issue = detect_small_text(img_path, save_path)
                    elif scanner_name == 'text_overlap':
                        issue = detect_text_overlap(
                            img_path, save_path)
                    elif scanner_name == 'edge_overflow':
                        issue = detect_edge_overflow(
                            img_path, save_path)
                    elif scanner_name == 'content_overflow':
                        issue = detect_content_overflow(
                            img_path, save_path)

                    if issue:
                        with lock:
                            issue_found = True
                            url_ = url.replace('/', '_')
                            saved_path = s3Uploader.upload_to_s3(
                                issue, 'eye-robot', f'{url_}/{save_path}')
                            mongoDbClient.update_array(
                                'reports', input_url, resolution, scanner_name.replace('_', ' '), saved_path, url)

                delete_file(img_path)

            for path_to_image in paths_to_images:
                resolution = path_to_image.split(
                    '/')[0]
                t = threading.Thread(
                    target=process_image, args=(path_to_image, resolution))
                threads_list.append(t)
                t.start()

            for t in threads_list:
                t.join()

            print("Scan Completed")

        # Create a list to store the URLs of the pages visited
        page_urls = []

        # Create a thread for the main task
        main_thread = threading.Thread(
            target=main_task, args=(input_url, page_urls))
        main_thread.start()

        return jsonify({"message": "Task started successfully."}), 200


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File deleted successfully: {file_path}")
    except OSError as e:
        print(f"Error deleting file: {e}")


def delete_existing_folders_and_files():
    folders = [
        '1920x1080',
        '1366x768',
        '375x667'

    ]

    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)


def create_directories_for_screenshots():
    resolutions = ['1920x1080', '1366x768', '375x667']

    for resolution in resolutions:
        folder_name = f"{resolution}"
        os.makedirs(folder_name, exist_ok=True)


if __name__ == '__main__':
    print('listening on port 3002')
    app.run(port=3002)

import time
import os
import threading
import json
import shutil
import requests
import pandas as pd
import io
import cv2

from flask import Flask, render_template, request, jsonify, url_for, make_response, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from NEW_SCANNER_COLOR_CONTRAST import detect_color_contrast
from NEW_SCANNER_SMALL_TEXT import detect_small_text
from NEW_SCANNER_TEXT_OVERLAP import detect_text_overlap

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def heartbeat():
    return "Website Eye Robot is up and running!"


@app.route("/report", methods=["GET"])
def get_report():
    try:
        with open('data.json') as f:
            data = json.load(f)
        return json.dumps(data)
    except FileNotFoundError:
        return jsonify({"message": 'Not found'}), 404


@app.route("/report", methods=["POST"])
def index():
    if request.method == "POST":
        input_url = request.json.get("url")

        # Delete existing folders and files if they exist
        delete_existing_folders_and_files()

        # Define the data variable as an empty dictionary
        data = {}

        def main_task(url, page_urls):
            resolutions = [(1920, 1080), (1366, 768), (375, 667)]

            driver = webdriver.Chrome()
            try:
                # Open URL in web driver and add it to the page_urls list
                driver.get(url)
                page_urls.append(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                visited_pages = set()
                create_directories_for_screenshots()

                for i, resolution in enumerate(resolutions):
                    visited_pages_resolution = set()  # keep track of visited pages for this resolution

                    # Create folder name based on resolution
                    folder_name = f"screenshots_{resolution[0]}x{resolution[1]}"

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

                        try:
                            driver.execute_script(
                                "document.body.style.overflow = 'hidden';")
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
                                driver.save_screenshot(
                                    os.path.join(
                                        folder_name,
                                        f"{i}_{len(visited_pages_resolution)}_{scroll_position}.png",
                                    )
                                )
                                scroll_position += section_height
                                driver.execute_script(
                                    f"window.scrollTo(0, {scroll_position})"
                                )
                                time.sleep(1.2)

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

            base_path = '/home/gefen/Website-Eye-Robot'
            scanner_folder_names = {
                'color_contrast': 'color_contrast_results',
                'small_text': 'small_text_results',
                'text_overlap': 'text_overlap_results'
            }

            create_parent_folders_for_scanners(base_path, scanner_folder_names)

            folder_paths = [
                os.path.join(base_path, 'screenshots_1920x1080'),
                os.path.join(base_path, 'screenshots_1366x768'),
                os.path.join(base_path, 'screenshots_375x667')
            ]

            report_cards = []
            issue_found = False

            lock = threading.Lock()
            threads_list = []

            def process_image(img_path, resolution):
                nonlocal issue_found
                i = 0
                for scanner_name, result_folder_name in scanner_folder_names.items():
                    result_folder_path = os.path.join(
                        base_path, result_folder_name)
                    filename_prefix = f"{scanner_name}_"
                    save_path = os.path.join(
                        result_folder_path, filename_prefix + str(i) + "_" + filename)
                    i += 1

                    if scanner_name == 'color_contrast':
                        issue = detect_color_contrast(
                            img_path, save_path)
                    elif scanner_name == 'small_text':
                        issue = detect_small_text(img_path, save_path)
                    elif scanner_name == 'text_overlap':
                        issue = detect_text_overlap(
                            img_path, save_path)

                    if issue:
                        with lock:
                            issue_found = True
                            page_index = page_urls.index(url)
                            report_cards.append({
                                'name': scanner_name.replace('_', ' ').title(),
                                'image': issue.replace('home/gefen/Website-Eye-Robot/', ''),
                                'resolution': resolution,
                                'page_url': page_urls[page_index]
                            })

            for folder_path in folder_paths:
                resolution = folder_path.replace(
                    '/home/gefen/Website-Eye-Robot/screenshots_', '')
                for filename in os.listdir(folder_path):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        img_path = os.path.join(folder_path, filename)
                        print(f"Processing {img_path}")

                        t = threading.Thread(
                            target=process_image, args=(img_path, resolution))
                        t.start()
                        threads_list.append(t)

            for t in threads_list:
                t.join()

            if issue_found:
                html_list = []
                for report_card in report_cards:
                    html = f"""
                    <div class="report-card">
                        <div class="card-header">
                        <h3>{report_card['name']}</h3>
                        <p> page url -> 
                        <a href="{report_card['page_url']}"> {report_card['page_url']}</a>
                        </p>
                        <p>resolution -> <span>{report_card['resolution']}</span></p>
                        </div>
                        <div class="card-screenshot">
                        <a>
                        <img class="screenshot-img" src='{report_card['image']}'></img>
                        </a>
                        </div>
                    </div>
                    """
                    html_list.append(html)

                html_output = "\n".join(html_list)
                button_html = """
                    <button id="download-btn" onclick="downloadExcel()">Download Excel</button>
                    """
                data[url] = button_html+html_output
            else:
                data[url] = "<p>No issues found.</p>"

            # Save data to a JSON file
            with open('data.json', 'w') as f:
                json.dump(data, f)

        # Create a list to store the URLs of the pages visited
        page_urls = []

        # Create a thread for the main task
        main_thread = threading.Thread(
            target=main_task, args=(input_url, page_urls))
        main_thread.start()

        return jsonify({"message": "Task started successfully."}), 200


def delete_existing_folders_and_files():
    folders = [
        'screenshots_1920x1080',
        'screenshots_1366x768',
        'screenshots_375x667',
        'color_contrast_results',
        'small_text_results',
        'text_overlap_results',
    ]

    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    if os.path.exists('data.json'):
        os.remove('data.json')


def create_directories_for_screenshots():
    resolutions = ['1920x1080', '1366x768', '375x667']

    for resolution in resolutions:
        folder_name = f"screenshots_{resolution}"
        os.makedirs(folder_name, exist_ok=True)


def create_parent_folders_for_scanners(base_path, scanner_folder_names):
    for folder_name in scanner_folder_names.values():
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)


if __name__ == '__main__':
    # delete_existing_folders_and_files()
    app.run(port=3002)

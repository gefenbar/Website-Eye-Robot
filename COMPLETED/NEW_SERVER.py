from flask import Flask, render_template, request, jsonify, url_for, make_response
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
import os
import torch
import matplotlib.pyplot as plt
import shutil
from flask_cors import CORS
import requests
import threading
import json
import pandas as pd
from COMPLETED.SCANNER_COLOR_CONTRAST import color_contrast
from SMALL_TEXT import detect_small_text
# from PREVIOUS_COLOR_CONTRAST import color_contrast
import cv2
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def heartbeat():
    return "Website Eye Robot is up and running!"


@app.route("/report", methods=["GET"])
def get_report():
    try:
        f = open('data.json')
        data = json.load(f)
        f.close()
        return json.dumps(data)
    except:
        return jsonify({"message": 'Not found'}), 404


@app.route("/report", methods=["POST"])
def index():

    if request.method == "POST":
        input_url = request.json.get("url")

        if os.path.exists('/home/gefen/Website-Eye-Robot/screenshots_375x667'):
            shutil.rmtree(
                '/home/gefen/Website-Eye-Robot/screenshots_375x667')
        if os.path.exists('/home/gefen/Website-Eye-Robot/screenshots_1366x768'):
            shutil.rmtree(
                '/home/gefen/Website-Eye-Robot/screenshots_1366x768')
        if os.path.exists('/home/gefen/Website-Eye-Robot/screenshots_1920x1080'):
            shutil.rmtree(
                '/home/gefen/Website-Eye-Robot/screenshots_1920x1080')
        if os.path.exists('/home/gefen/Website-Eye-Robot/results_375x667'):
            shutil.rmtree(
                '/home/gefen/Website-Eye-Robot/results_375x667')
        if os.path.exists('/home/gefen/Website-Eye-Robot/results_1366x768'):
            shutil.rmtree(
                '/home/gefen/Website-Eye-Robot/results_1366x768')
        if os.path.exists('/home/gefen/Website-Eye-Robot/results_1920x1080'):
            shutil.rmtree(
                '/home/gefen/Website-Eye-Robot/results_1920x1080')
        # Delete data.json if it exists
        if os.path.exists("data.json"):
            os.remove("data.json")

        def main_task(**kwargs):
            page_urls = []
            url = kwargs.get('url', '')
            # Define web driver
            driver = webdriver.Chrome()

            # Define list of media query resolutions to capture screenshots at
            resolutions = [(1920, 1080), (1366, 768), (375, 667)]

            try:
                # Open URL in web driver
                driver.get(url)
                # Add the URL to the page_urls list
                page_urls.append(url)
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                visited_pages = set()  # keep track of visited pages

                # Create directories for screenshots
                os.makedirs("screenshots_1920x1080", exist_ok=True)
                os.makedirs("screenshots_1366x768", exist_ok=True)
                os.makedirs("screenshots_375x667", exist_ok=True)
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
                            section_height = 800

                            # Capture screenshots of each section of the page
                            while scroll_position < page_height:
                                driver.execute_script(
                                    f"window.scrollTo(0, {scroll_position})")
                                time.sleep(1)
                                driver.save_screenshot(
                                    os.path.join(
                                        folder_name, f"{i}_{len(visited_pages_resolution)}.png")
                                )
                                scroll_position += section_height
                                driver.execute_script(
                                    f"window.scrollTo(0, {scroll_position})"
                                )
                                time.sleep(1)

                            # Find all links on page
                            links = driver.find_elements(By.TAG_NAME, "a")

                            # Visit all links on page
                            for link in links:
                                try:
                                    href = link.get_attribute("href")
                                    if (
                                        href is not None
                                        and href.startswith(url)
                                        and href not in visited_pages_resolution
                                        and "#" not in href  # added to skip navigating within the same page using href
                                        and not href.lower().endswith(".pdf")
                                    ):
                                        driver.get(href)
                                except StaleElementReferenceException:
                                    continue

                        except StaleElementReferenceException:
                            continue

                # Close web driver
            finally:
                driver.quit()

            # Define the base folder path
            base_path = '/home/gefen/Website-Eye-Robot'

            # Define the folder names for each scanner
            scanner_folder_names = {
                'color_contrast': 'color_contrast_results',
                'small_text': 'small_text_results',
                # Add more scanners and folder names as needed
            }

            # Create the parent folders for each scanner
            for folder_name in scanner_folder_names.values():
                scanner_folder_path = os.path.join(base_path, folder_name)
                if not os.path.exists(scanner_folder_path):
                    os.makedirs(scanner_folder_path)
                    print(f"Created folder: {scanner_folder_path}")

            # Define the folder paths for each resolution
            folder_paths = [
                os.path.join(base_path, 'screenshots_1920x1080'),
                os.path.join(base_path, 'screenshots_1366x768'),
                os.path.join(base_path, 'screenshots_375x667')
            ]

            report_cards = []

            # Loop through the folder paths for each resolution
            for folder_path in folder_paths:
                for filename in os.listdir(folder_path):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        img_path = os.path.join(folder_path, filename)
                        print(f"Processing {img_path}")

                        # Loop through each scanner and run its function
                        for scanner_name, result_folder_name in scanner_folder_names.items():
                            result_folder_path = os.path.join(
                                base_path, result_folder_name)
                            filename_prefix = f"{scanner_name}_"
                            save_path = os.path.join(
                                result_folder_path, filename_prefix + str(i) + "_" + filename)
                            i += 1

                            if scanner_name == 'color_contrast':
                                issue = color_contrast(img_path, save_path)
                            elif scanner_name == 'small_text':
                                issue = detect_small_text(img_path, save_path)

                            # Check if there are any issues found
                            if issue:
                                issue_found = True
                                page_index = page_urls.index(url)
                                report_cards.append({
                                    'name': scanner_name.replace('_', ' ').title(),
                                    'image': issue.replace('home/gefen/Website-Eye-Robot/', ''),
                                    'resolution': folder_path.replace('/home/gefen/Website-Eye-Robot/screenshots_', ''),
                                    'page_url': page_urls[page_index]
                                })

            if issue_found:
                html_list = []
                for report_card in report_cards:
                    html = f"""
                        <div class="report-card">
                            <div class="card-header">
                                <h3>{report_card['name']}</h3>
                                <p> page url-> {report_card['page_url']}</p>
                                <p>resolution-> {report_card['resolution']}</p>
                            </div>
                            <div class="card-screenshot">
                                <img src='{report_card['image']}' alt="Screenshot of Issue #{report_card['name']}">
                            </div>
                        </div>
                    """
                    html_list.append(html)
                all_html = '\n'.join(html_list)
            else:
                all_html = f"""
                    <div class="report-card">
                        <div class="card-header">
                            <h3> No issues found</h3>
                        </div>
                    </div>
                """
            print("FINISHED")

            data = {}
            data[url] = all_html
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        thread = threading.Thread(target=main_task, kwargs={'url': input_url})
        thread.start()
        return 'ok'


if __name__ == '__main__':
    app.run(port=3085)

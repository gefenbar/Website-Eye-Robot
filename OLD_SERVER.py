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
from SCANNER_COLOR_CONTRAST import color_contrast
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
            url = kwargs.get('url', '')
            # Define web driver
            driver = webdriver.Chrome()

            # Define list of media query resolutions to capture screenshots at
            resolutions = [(1920, 1080), (1366, 768), (375, 667)]

            try:
                # Open URL in web driver
                driver.get(url)
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

                           # Set window size to 1920x1080 pixels
                            driver.set_window_size(1920, 1080)

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

            # Define the folder paths for each resolution
            base_path = '/home/gefen/Website-Eye-Robot'
            folder_paths = [
                os.path.join(base_path, 'screenshots_1920x1080'),
                os.path.join(base_path, 'screenshots_1366x768'),
                os.path.join(base_path, 'screenshots_375x667')
            ]
            result_folder_names = [
                os.path.join(base_path, 'results_1920x1080'),
                os.path.join(base_path, 'results_1366x768'),
                os.path.join(base_path, 'results_375x667')
            ]

            i = 1
            html_list = []
            num_of_screenshots = 0
            for folder_name in result_folder_names:
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)
                    print(f"Created folder: {folder_name}")

            for folder_path, result_folder_name in zip(folder_paths, result_folder_names):
                for filename in os.listdir(folder_path):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        img_path = os.path.join(folder_path, filename)
                        print(f"Processing {img_path}")

                        save_path = os.path.join(
                            result_folder_name, filename)
                        result = color_contrast(img_path, save_path)
                        # check if there are any detections
                        if result != "":
                            issue_name = "Color Contrast"  # move this var to the color contrast code
                            issue_resolution = result_folder_name.replace(
                                "results_", '')
                            issue_image = result
                            # issue_image = f"{result_folder_name}/{filename}"
                            page_url = "https://placeholder.com"
                            print(f"resolution:{issue_resolution}")
                            # print(f"imagepath:{issue_image}")
                            html = f"""
                                    <div class="report-card">
                                        <div class="card-header">
                                            <h3>{issue_name}</h3>
                                            <p> page url: {page_url}</p>
                                            <p>resolution: {issue_resolution.replace('/home/gefen/Website-Eye-Robot/', '')}</p>
                                        </div>
                                        <div class="card-screenshot">
                                            <img src='{issue_image.replace('home/gefen/Website-Eye-Robot/', '')}' alt="Screenshot of Issue #{issue_name}">
                                        </div>
                                    </div>
                                """
                            html_list.append(html)
                            num_of_screenshots += 1
                if num_of_screenshots > 0:
                    all_html = '\n'.join(html_list)
                else:
                    # i--> to make the "no issues" message appear only if there are no more images generated
                    all_html = f"""
                                        <div class="report-card">
                                            <div class="card-header">
                                                <h3> No issues found</h3>
                                        </div>
                                    """
                data = {}
                data[url] = all_html
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

        thread = threading.Thread(target=main_task, kwargs={'url': input_url})
        thread.start()
        return 'ok'


if __name__ == '__main__':
    app.run(port=3006)

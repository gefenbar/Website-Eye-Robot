import pytesseract
import cv2
import numpy as np
import re


# testing
import time
from timing import scanners_timing, time_convert
import os

# Constants
MIN_CONTOUR_SIZE = 5
MIN_ASPECT_RATIO = 1
MAX_ASPECT_RATIO = 300
MIN_SOLIDITY = 0.5
OVERFLOW_THRESHOLD = 1.4


def detect_content_overflow(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_content_overflow.jpg", img)

    gray = preprocess_image(img)
    # cv2.imwrite("grayscale_image_content_overflow.jpg", gray)

    thresh = threshold_image(gray)
    cv2.imwrite("thresholded_image_content_overflow.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    cv2.imwrite("morphological_operations_content_overflow.jpg", thresh)

    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False

    # Visualize contours
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("contours_content_overflow.jpg", img_copy)
    i = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        crop_img = img[y:y+h, x:x+w]

        # contour_img_path = f"/home/gefen/Website-Eye-Robot/contours/contour1_{i}.png"
        # cv2.imwrite(contour_img_path, crop_img)
        i += 1

        if contains_text(crop_img) and is_content_overflow(crop_img, contour):
            found_issue = True
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 2)

    if found_issue:
        # print("Found CONTENT_OVERFLOW issue")
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        # print("Not found CONTENT_OVERFLOW issue")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # clahe = cv2.createCLAHE(clipLimit=20.0, tileGridSize=(1, 1))
    # gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 11)


def apply_morphological_operations(thresh):
    kernel_size = 9
    kernel_shape = cv2.MORPH_RECT
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return thresh


def find_contours(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def is_region_of_interest(contour):
    x, y, w, h = cv2.boundingRect(contour)

    if w * h < MIN_CONTOUR_SIZE or not MIN_ASPECT_RATIO <= w / h <= MAX_ASPECT_RATIO:
        return False

    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / (hull_area+1)

    return solidity >= MIN_SOLIDITY


def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(
        crop_img_gray,  config='--psm 6 --oem 1')
    return re.search(r'\w', text)


def is_content_overflow(crop_img, contour):
    # Convert the image to grayscale
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Calculate the percentage of white pixels in the contour
    contour_area = cv2.contourArea(contour)
    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    white_pixel_count = cv2.countNonZero(thresholded)
    white_pixel_percentage = white_pixel_count / contour_area

    # Check if the white pixel percentage exceeds the overflow threshold
    if white_pixel_percentage > OVERFLOW_THRESHOLD:
        return True
    else:
        return False




def test_directory(directory_path, save_directory):
    # Create the save directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    times = 0
    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            start_time = time.time()

            # Construct the full paths for the input image and save path
            img_path = os.path.join(directory_path, filename)
            save_path = os.path.join(save_directory, filename)

            # Call the detect_content_overflow function
            result = detect_content_overflow(img_path, save_path)
            if result:
                print(
                    f"CONTENT_OVERFLOW issue detected in {img_path}. Annotated image saved as {result}.")
            else:
                print(f"No CONTENT_OVERFLOW issue found in {img_path}.")
            times += scanners_timing(start_time)
    print("average time: " + time_convert(times/10))


# Test the directory
directory_path = "/home/gefen/Website-Eye-Robot/tests/REAL TESTS/CONTENT_OVERFLOW/"
save_directory = "/home/gefen/Website-Eye-Robot/tests/REAL TESTS/CONTENT_OVERFLOW_ANNOTATED"
test_directory(directory_path, save_directory)

# detect_content_overflow(
#     "9.jpg", "CONTENT_OVERFLOW.png")

import pytesseract
import cv2
import numpy as np
import re


# for testing
import os

# Constants
MIN_CONTOUR_SIZE = 5
MIN_ASPECT_RATIO = 1
MAX_ASPECT_RATIO = 300
MIN_SOLIDITY = 0.1
OVERFLOW_THRESHOLD = 0.001


def detect_content_overflow(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_content_overflow.jpg", img)

    gray = preprocess_image(img)
    # cv2.imwrite("grayscale_image_content_overflow.jpg", gray)

    thresh = threshold_image(gray)
    # cv2.imwrite("thresholded_image_content_overflow.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    # cv2.imwrite("morphological_operations_content_overflow.jpg", thresh)

    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False

    # Visualize contours
    # cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    # cv2.imwrite("contours_content_overflow.jpg", img_copy)
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
    text = pytesseract.image_to_string(crop_img)
    return bool(re.search(r'\w', text))


def is_content_overflow(crop_img, contour):
    text = pytesseract.image_to_string(crop_img)
    bounding_rect = cv2.boundingRect(contour)
    rect_area = bounding_rect[2] * bounding_rect[3]

    if rect_area == 0:
        return False

    # Convert the image to grayscale
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Threshold the grayscale image
    _, threshold_img = cv2.threshold(
        crop_img_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Find contours of the text in the thresholded image
    text_contours, _ = cv2.findContours(
        threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any text contour overlaps with the region boundary
    for text_contour in text_contours:
        text_rect = cv2.boundingRect(text_contour)
        if rectangles_overlap(text_rect, bounding_rect):
            return True

    return False


def rectangles_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    if (x1 + w1) < x2 or (x2 + w2) < x1 or (y1 + h1) < y2 or (y2 + h2) < y1:
        return False

    return True


# def test_directory(directory_path, save_directory):
#     # Create the save directory if it doesn't exist
#     if not os.path.exists(save_directory):
#         os.makedirs(save_directory)

#     # Iterate over all files in the directory
#     for filename in os.listdir(directory_path):
#         if filename.endswith(".png") or filename.endswith(".jpg"):
#             # Construct the full paths for the input image and save path
#             img_path = os.path.join(directory_path, filename)
#             save_path = os.path.join(save_directory, filename)

#             # Call the detect_content_overflow function
#             result = detect_content_overflow(img_path, save_path)
#             if result:
#                 print(
#                     f"CONTENT_OVERFLOW issue detected in {img_path}. Annotated image saved as {result}.")
#             else:
#                 print(f"No CONTENT_OVERFLOW issue found in {img_path}.")


# Test the directory
# directory_path = "/home/gefen/Website-Eye-Robot/tests/x/"
# save_directory = "/home/gefen/Website-Eye-Robot/tests/REAL TESTS/CONTENT_OVERFLOW_ANNOTATED"
# test_directory(directory_path, save_directory)

# detect_content_overflow(
#     "9.jpg", "CONTENT_OVERFLOW.png")

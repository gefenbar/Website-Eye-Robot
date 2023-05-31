import pytesseract
import cv2
import numpy as np
import re
import itertools

import os

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 1
MAX_ASPECT_RATIO = 300
MIN_SOLIDITY = 0.9
OVERLAP_THRESHOLD = 0.1
THRESHOLD_CONFIDENCE=0.5

def detect_text_overlap(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_text_overlap.jpg", img)

    gray = preprocess_image(img)
    cv2.imwrite("grayscale_image_text_overlap.jpg", gray)

    thresh = threshold_image(gray)
    cv2.imwrite("thresholded_image_text_overlap.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    cv2.imwrite("morphological_operations_text_overlap.jpg", thresh)

    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False

   # Visualize contours
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("contours_text_overlap.jpg", img_copy)
    # Generate pairwise combinations of contours
    contour_pairs = itertools.combinations(contours, 2)

    for contour1, contour2 in contour_pairs:
        if is_region_of_interest(contour1) and is_region_of_interest(contour2):
            x1, y1, w1, h1 = cv2.boundingRect(contour1)
            crop_img1 = img[y1:y1+h1, x1:x1+w1]

            if contains_text(crop_img1):
                x2, y2, w2, h2 = cv2.boundingRect(contour2)
                crop_img2 = img[y2:y2+h2, x2:x2+w2]

                if contains_text(crop_img2):
                    overlap_ratio = compute_overlap_ratio(
                        x1, y1, w1, h1, x2, y2, w2, h2)

                    if overlap_ratio > OVERLAP_THRESHOLD:
                        found_issue = True
                        cv2.rectangle(img_copy, (x1, y1),
                                      (x1+w1, y1+h1), (0, 0, 255), 2)
                        cv2.rectangle(img_copy, (x2, y2),
                                      (x2+w2, y2+h2), (0, 0, 255), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        return ""

    if found_issue:
        # print("Found TEXT_OVERLAP issue")
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        # print("Not found TEXT_OVERLAP issue")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6, 6))
    # gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)


def apply_morphological_operations(thresh):
    kernel_size = 11
    kernel_shape = cv2.MORPH_ELLIPSE
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
    return True


def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(crop_img_gray, config='--psm 6 --oem 1')
    text = text.strip()

    if len(text) == 0:
        return False

    # Calculate the average confidence level of individual characters
    confidences = pytesseract.image_to_boxes(crop_img_gray, config='--psm 6 --oem 1')
    confidences = [float(line.split(' ')[-1]) for line in confidences.splitlines()]
    average_confidence = sum(confidences) / len(confidences)

    # Filter out areas with crystal-clear text
    if average_confidence > THRESHOLD_CONFIDENCE:
        return False

    return True


def compute_overlap_ratio(x1, y1, w1, h1, x2, y2, w2, h2):
    area1 = w1 * h1
    area2 = w2 * h2

    inter_x = max(x1, x2)
    inter_y = max(y1, y2)
    inter_w = min(x1+w1, x2+w2) - inter_x
    inter_h = min(y1+h1, y2+h2) - inter_y

    if inter_w > 0 and inter_h > 0:
        inter_area = inter_w * inter_h
        union_area = area1 + area2 - inter_area
        overlap_ratio = inter_area / union_area
    else:
        overlap_ratio = 0

    return overlap_ratio


def test_directory(directory_path, save_directory):
    # Create the save directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            # Construct the full paths for the input image and save path
            img_path = os.path.join(directory_path, filename)
            save_path = os.path.join(save_directory, filename)

            # Call the detect_text_overlap function
            result = detect_text_overlap(img_path, save_path)
            if result:
                print(
                    f"TEXT_OVERLAP issue detected in {img_path}. Annotated image saved as {result}.")
            else:
                print(f"No TEXT_OVERLAP issue found in {img_path}.")


# Test the directory
directory_path = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/x/"
save_directory = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/TEXT_OVERLAP_ANNOTATED"
test_directory(directory_path, save_directory)

# detect_text_overlap(
#     "/home/gefen/Website-Eye-Robot/screenshots_1920x1080/0_3_0.png", "TEXT_OVERLAP.png")

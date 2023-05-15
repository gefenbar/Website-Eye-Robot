import pytesseract
import cv2
import numpy as np
import re

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 0
MAX_ASPECT_RATIO = 100
MIN_SOLIDITY = 0
COLOR_DIFF_THRESHOLD = 80


def detect_color_contrast(img_path, save_path):
    # Load and preprocess the image
    img = load_image(img_path)
    gray = preprocess_image(img)

    # Apply thresholding and morphological operations
    thresh = threshold_image(gray)
    thresh = apply_morphological_operations(thresh)

    # Find contours in the thresholded image
    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False

    for contour in contours:
        # Check if the contour is a region of interest
        if not is_region_of_interest(contour):
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # Crop the region of interest from the image
        crop_img = img[y:y+h, x:x+w]

        # Check if the region contains text using pytesseract
        if not contains_text(crop_img):
            continue

        # Compute the color difference between the mean and peak color of the region
        color_diff = compute_color_difference(crop_img)

        if color_diff < COLOR_DIFF_THRESHOLD:
            found_issue = True

            # Draw a purple rectangle around the region of interest
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 102, 0), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues found")
        return ""



def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    gray = clahe.apply(gray)
    # gray = cv2.GaussianBlur(gray, (1, 1), 0)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2)


def apply_morphological_operations(thresh):
    kernel_size = 7
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
    if w * h < MIN_CONTOUR_SIZE:
        return False
    aspect_ratio = w / h
    if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
        return False
    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area
    if solidity < MIN_SOLIDITY:
        return False
    return True


def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(
        crop_img_gray, lang='en+heb', config='--psm 6')
    return re.search(r'\w', text)


def compute_color_difference(crop_img):
    mean_color = np.mean(crop_img, axis=(0, 1))
    peak_color = np.max(crop_img, axis=(0, 1))
    color_diff = np.linalg.norm(mean_color - peak_color)
    return color_diff


# detect_color_contrast(
#     '/home/gefen/Website-Eye-Robot/TESTS/test3.png', 'COLOR_CONTRAST.png')

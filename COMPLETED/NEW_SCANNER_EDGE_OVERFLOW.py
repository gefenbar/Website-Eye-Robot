import pytesseract
import cv2
import numpy as np
import re

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 0
MAX_ASPECT_RATIO = 300
MIN_SOLIDITY = 0.3


def detect_text_near_edges(img_path, save_path):
    img = load_image(img_path)
    cv2.imwrite("original_image.jpg", img)
    gray = preprocess_image(img)
    cv2.imwrite("grayscale_image.jpg", gray)
    thresh = threshold_image(gray)
    cv2.imwrite("thresholded_image.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    cv2.imwrite("morphological_operations.jpg", thresh)

    contours = find_contours(thresh)

    img_copy = img.copy()
    found_issue = False

    # Visualize contours
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("contours.jpg", img_copy)
    for contour in contours:
        if is_region_of_interest(contour, img):
            x, y, w, h = cv2.boundingRect(contour)
            crop_img = img[y:y+h, x:x+w]

            if contains_text(crop_img):
                found_issue = True
                cv2.rectangle(img_copy, (x, y),
                              (x+w, y+h), (255, 102, 0), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("No issues found")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)


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


def is_region_of_interest(contour, img):
    x, y, w, h = cv2.boundingRect(contour)
    if w * h < MIN_CONTOUR_SIZE or not MIN_ASPECT_RATIO <= w / h <= MAX_ASPECT_RATIO:
        return False
    edge_threshold = min(img.shape[1], img.shape[0]) * 0.00000001
    if x <= edge_threshold or y <= edge_threshold or x + w >= img.shape[1] - edge_threshold or y + h >= img.shape[0] - edge_threshold:
        return True

    return False


def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(
        crop_img_gray, lang='en+heb', config='--psm 6 --oem 1')
    return re.search(r'\w', text)


detect_text_near_edges(
    "screenshots_1920x1080/0_1_1728.png", "TEXT_NEAR_EDGES.png")

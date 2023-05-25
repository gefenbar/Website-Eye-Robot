import pytesseract
import cv2
import numpy as np
import re

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 0
MAX_ASPECT_RATIO = 3000
MIN_SOLIDITY = 0
OVERFLOW_THRESHOLD = 0.1


def detect_content_overflow(img_path, save_path):
    img = load_image(img_path)
    cv2.imwrite("original_image.jpg", img)

    denoised = denoise_image(img)
    cv2.imwrite("denoised_image.jpg", denoised)

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
        if is_region_of_interest(contour):
            x, y, w, h = cv2.boundingRect(contour)
            crop_img = img[y:y+h, x:x+w]

            if contains_text(crop_img) and is_content_overflow(crop_img, contour):
                found_issue = True
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("No content overflow detected.")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)

def denoise_image(img):
    return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=20.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 121)


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

    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area

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

    text_area = len(text) * rect_area / len(text)
    overflow_ratio = text_area / rect_area

    return overflow_ratio > OVERFLOW_THRESHOLD


detect_content_overflow(
    "1.jpg", "CONTENT_OVERFLOW.png")

import pytesseract
import cv2
import numpy as np
import re

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 0
MAX_ASPECT_RATIO = 300
MIN_SOLIDITY = 0
OVERFLOW_THRESHOLD = 0.5


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

    for contour in contours:
        if is_region_of_interest(contour):
            x, y, w, h = cv2.boundingRect(contour)
            crop_img = img[y:y+h, x:x+w]

            if contains_text(crop_img) and is_content_overflow(crop_img, contour):
                found_issue = True
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 2)

    if found_issue:
        print("Found CONTENT_OVERFLOW issue")
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("Not found CONTENT_OVERFLOW issue")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=20.0, tileGridSize=(1, 1))
    gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)


def apply_morphological_operations(thresh):
    kernel_size =7
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

    # Convert the image to grayscale
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Threshold the grayscale image
    _, threshold_img = cv2.threshold(crop_img_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Find contours of the text in the thresholded image
    text_contours, _ = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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


# detect_content_overflow(
#     "9.jpg", "CONTENT_OVERFLOW.png")

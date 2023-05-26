import pytesseract
import cv2
import numpy as np
import re


def detect_small_text(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_small_text.jpg", img)
    height, width = img.shape[:2]
    min_height, max_height = calculate_min_max_height(height)
    gray = preprocess_image(img)
    # cv2.imwrite("grayscale_image_small_text.jpg", gray)

    thresh = threshold_image(gray)
    # cv2.imwrite("thresholded_image_small_text.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    # cv2.imwrite("morphological_operations_small_text.jpg", thresh)
    contours = find_contours(thresh)

    img_copy = img.copy()
    found_issue = False
    # cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    # cv2.imwrite("contours_small_text.jpg", img_copy)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if (min_height <= h <= max_height):
            crop_img = img[y:y+h, x:x+w]

            if contains_text(crop_img):
                found_issue = True
                cv2.rectangle(img_copy, (x, y),
                              (x+w, y+h), (15, 15, 245), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("No issues found")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def calculate_min_max_height(height):
    reference_height = height
    min_height = 2
    max_height = 7
    ratio = height / reference_height
    min_height = int(ratio * min_height)
    max_height = int(ratio * max_height)
    return min_height, max_height


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def threshold_image(gray):
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 1)
    return thresh


def apply_morphological_operations(thresh):
    kernel_size = 1
    kernel_shape = cv2.MORPH_ELLIPSE
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return thresh


def find_contours(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def contains_text(crop_img):
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(
        gray, lang='eng+heb', config='--psm 6 --oem 1')
    return re.search(r'\w', text)


# detect_small_text("zzz.jpg", "SMALL_TEXT.png")

import pytesseract
import cv2
import numpy as np
import re

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 0.1
MAX_ASPECT_RATIO = 3000
MIN_SOLIDITY = 0
OVERLAP_THRESHOLD = 0.1


def detect_text_overlap(img_path, save_path):
    img = load_image(img_path)
    gray = preprocess_image(img)
    thresh = threshold_image(gray)
    thresh = apply_morphological_operations(thresh)
    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False

    for i, contour1 in enumerate(contours):
        if is_region_of_interest(contour1):
            x1, y1, w1, h1 = cv2.boundingRect(contour1)
            crop_img1 = img[y1:y1+h1, x1:x1+w1]

            if contains_text(crop_img1):
                for j in range(i+1, len(contours)):
                    contour2 = contours[j]
                    if is_region_of_interest(contour2):
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
        print("No issues found")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6, 6))
    gray = clahe.apply(gray)
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
    if w * h < MIN_CONTOUR_SIZE or not (MIN_ASPECT_RATIO <= w / h <= MAX_ASPECT_RATIO):
        return False
    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area
    return solidity >= MIN_SOLIDITY


def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(crop_img_gray, config='--psm 6')
    return re.search(r'\w', text)


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

# detect_text_overlap("/home/gefen/Website-Eye-Robot/screenshots_375x667/2_1_0.png", "TEXT_OVERLAP.png")

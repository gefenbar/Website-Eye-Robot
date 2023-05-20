import pytesseract
import cv2
import numpy as np
import re


def detect_small_text(img_path, save_path):
    img = cv2.imread(img_path)
    height, width = img.shape[:2]
    min_height, max_height = calculate_min_max_height(height)
    gray = preprocess_image(img)
    thresh = apply_thresholding(gray)
    contours = find_contours(thresh)

    img_copy = img.copy()
    found_issue = False

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if (min_height <= h <= max_height):
            crop_img = img[y:y+h, x:x+w]
            # text = pytesseract.image_to_string(cropped_img, lang='eng+heb')
            # if text.strip():
            if contains_text(crop_img):
                found_issue = True
                cv2.rectangle(img_copy, (x, y),
                              (x+w, y+h), (0, 255, 127), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("No issues found")
        return ""


def calculate_min_max_height(height):
    reference_height = 1080
    min_height = 1
    max_height = 14
    ratio = height / reference_height
    min_height = int(ratio * min_height)
    max_height = int(ratio * max_height)
    return min_height, max_height


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
    gray = clahe.apply(gray)
    gray = cv2.GaussianBlur(gray, (1, 3), 0)
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    gray = cv2.filter2D(gray, -1, kernel)
    return gray


def apply_thresholding(gray):
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    thresh = apply_morphological_operations(thresh)
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
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours



def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(
        crop_img_gray, lang='en+heb', config='--psm 6')
    return re.search(r'\w', text)

# detect_text_overlap("/home/gefen/Website-Eye-Robot/screenshots_375x667/2_1_0.png", "TEXT_OVERLAP.png")

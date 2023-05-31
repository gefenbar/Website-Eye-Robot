import pytesseract
import cv2
import numpy as np
import re

# Constants
MIN_CONTOUR_SIZE = 0
MIN_ASPECT_RATIO = 1.2
MAX_ASPECT_RATIO = 400
MIN_SOLIDITY = 0.5
COLOR_DIFF_THRESHOLD =60


def detect_color_contrast(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_color_constrast.jpg", img)

    gray = preprocess_image(img)
    # cv2.imwrite("grayscale_image_color_constrast.jpg", gray)

    thresh = threshold_image(gray)
    # cv2.imwrite("thresholded_image_color_constrast.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    # cv2.imwrite("morphological_image_color_constrast.jpg", thresh)

    contours = find_contours(thresh)

    img_copy = img.copy()
    found_issue = False
    # cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    # cv2.imwrite("contours.jpg_text_overlap", img_copy)
    for contour in contours:
        if is_region_of_interest(contour):
            x, y, w, h = cv2.boundingRect(contour)
            crop_img = img[y:y+h, x:x+w]

            if contains_text(crop_img):
                color_diff = compute_color_difference(crop_img)

                if color_diff < COLOR_DIFF_THRESHOLD:
                    found_issue = True
                    cv2.rectangle(img_copy, (x, y),
                                  (x+w, y+h), (255, 102, 0), 2)
    if found_issue:
        print("Found COLOR_CONTRAST issue")
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("Not found COLOR_CONTRAST issue")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(2, 2))
    gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13,5)

def find_contours(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def apply_morphological_operations(thresh):
    kernel_size =7
    kernel_shape = cv2.MORPH_ELLIPSE
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return thresh



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
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(
        crop_img_gray, lang='en', config='--psm 6 --oem 1')
    return re.search(r'\w', text)


def compute_color_difference(crop_img):
    mean_color = np.mean(crop_img, axis=(0, 1))
    peak_color = np.max(crop_img, axis=(0, 1))
    color_diff = np.linalg.norm(mean_color - peak_color)
    return color_diff


# detect_color_contrast(
#     "1.jpg", "COLOR_CONTRAST.png")

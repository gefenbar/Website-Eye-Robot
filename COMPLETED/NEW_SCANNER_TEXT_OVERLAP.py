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
    for i in range(len(contours)):
        # Check if the contour is a region of interest
        if is_region_of_interest(contours[i]):
            x1, y1, w1, h1 = cv2.boundingRect(contours[i])

            # Crop the region of interest from the image
            crop_img1 = img[y1:y1+h1, x1:x1+w1]

            # Check if the region contains text using pytesseract
            if contains_text(crop_img1):
                # cv2.imshow('Region of Interest', crop_img1)
                # cv2.waitKey(0)
                for j in range(i+1, len(contours)):
                    # Check if the other contour is a region of interest
                    if is_region_of_interest(contours[j]):
                        x2, y2, w2, h2 = cv2.boundingRect(contours[j])

                        # Crop the other region of interest from the image
                        crop_img2 = img[y2:y2+h2, x2:x2+w2]

                        # Check if the other region contains text using pytesseract
                        if contains_text(crop_img2):
                            # Compute the overlap ratio between the two regions
                            overlap_ratio = compute_overlap_ratio(
                                x1, y1, w1, h1, x2, y2, w2, h2)

                            if overlap_ratio > OVERLAP_THRESHOLD:
                                found_issue = True
                                # Draw a red rectangle around the overlapping regions of interest
                                cv2.rectangle(img_copy, (x1, y1),
                                              (x1+w1, y1+h1), (0, 0, 255), 2)
                                cv2.rectangle(img_copy, (x2, y2),
                                              (x2+w2, y2+h2), (0, 0, 255), 2)

    # cv2.destroyAllWindows()
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
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(6, 6))
    gray = clahe.apply(gray)
    # gray = cv2.GaussianBlur(gray, (1, 1), 0)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2)


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
    text = pytesseract.image_to_string(crop_img_gray,
                                       config='--psm 6')
    return re.search(r'\w', text)


def compute_overlap_ratio(x1, y1, w1, h1, x2, y2, w2, h2):
    area1 = w1*h1  # area of the first region
    area2 = w2*h2  # area of the second region

    inter_x = max(x1, x2)  # leftmost x-coordinate of the intersection
    inter_y = max(y1, y2)  # topmost y-coordinate of the intersection
    inter_w = min(x1+w1, x2+w2)-inter_x  # width of the intersection
    inter_h = min(y1+h1, y2+h2)-inter_y  # height of the intersection

    if inter_w > 0 and inter_h > 0:  # if there is an intersection
        inter_area = inter_w*inter_h  # area of the intersection
        union_area = area1+area2-inter_area  # area of the union
        overlap_ratio = inter_area/union_area  # ratio of the intersection to the union
    else:  # if there is no intersection
        overlap_ratio = 0  # no overlap

    return overlap_ratio

# detect_text_overlap("/home/gefen/Website-Eye-Robot/screenshots_375x667/2_1_0.png", "TEXT_OVERLAP.png")

import pytesseract
import cv2
import numpy as np
import re
import os

# Constants
MIN_CONTOUR_SIZE = 10
MIN_ASPECT_RATIO = 3
MAX_ASPECT_RATIO = 800
MIN_SOLIDITY = 0
OVERLAP_THRESHOLD = 0.0000001


def detect_text_overlap(img_path, save_path):
    img = load_image(img_path)
    cv2.imwrite("original_image_text_overlap.jpg", img)

    # denoised = denoise_image(img)
    # cv2.imwrite("denoised_image_text_overlap.jpg", denoised)

    gray = preprocess_image(img)
    cv2.imwrite("grayscale_image_text_overlap.jpg", gray)

    thresh = threshold_image(gray)
    cv2.imwrite("thresholded_image_text_overlap.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    cv2.imwrite("morphological_operations_text_overlap.jpg", thresh)

    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False
    computation_results = {}
    visited_contours = {}

    # Visualize contours
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("contours_text_overlap.jpg", img_copy)

    for i in range(len(contours)):
        if is_region_of_interest(contours[i]):
            x1, y1, w1, h1 = cv2.boundingRect(contours[i])
            crop_img1 = img[y1:y1+h1, x1:x1+w1]

            if contains_text(crop_img1):
                # Save the contour image with a name according to its index
                contour_img_path = f"/home/gefen/Website-Eye-Robot/contours/contour1_{i}.png"
                cv2.imwrite(contour_img_path, crop_img1)

                print(f"i: {i}")
                for j in range(i+1, len(contours)):
                    if is_region_of_interest(contours[j]) and j not in visited_contours:
                        x2, y2, w2, h2 = cv2.boundingRect(contours[j])
                        crop_img2 = img[y2:y2+h2, x2:x2+w2]

                        if contains_text(crop_img2):
                            if j in computation_results:
                                overlap_ratio = computation_results[j]
                            else:
                                overlap_ratio = compute_overlap_ratio(
                                    x1, y1, w1, h1, x2, y2, w2, h2)
                                computation_results[j] = overlap_ratio
                                print(f"j: {j}")

                            if overlap_ratio > OVERLAP_THRESHOLD:
                                visited_contours[j] = contours[j]
                                print("found")
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


def load_image(img_path):
    return cv2.imread(img_path)


# def denoise_image(img):
#     return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 11)


def apply_morphological_operations(thresh):
    kernel_size = 5
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (kernel_size, kernel_size))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return thresh


def find_contours(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def is_region_of_interest(contour):
    x, y, w, h = cv2.boundingRect(contour)

    if w * h < MIN_CONTOUR_SIZE:  # Adjust the minimum size as per your requirement
        return False

    aspect_ratio = w / h
    if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:  # Adjust the aspect ratio range
        return False

    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)

    if hull_area == 0 or area / hull_area < MIN_SOLIDITY:  # Adjust the solidity threshold
        return False

    return True


def contains_text(crop_img):
    crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(crop_img_gray,
                                       config='--psm 6 --oem 1')
    return re.search(r'\w', text)


def compute_overlap_ratio(x1, y1, w1, h1, x2, y2, w2, h2):
    area1 = w1 * h1
    area2 = w2 * h2

    inter_x = max(x1, x2)
    inter_y = max(y1, y2)
    inter_w = min(x1+w1, x2+w2) - inter_x
    inter_h = min(y1+h1, y2+h2) - inter_y

    if inter_w > 0 and inter_h > 0:
        print("intersection!!!")
        inter_area = inter_w * inter_h
        union_area = area1 + area2 - inter_area
        overlap_ratio = inter_area / union_area
    else:
        overlap_ratio = 0

    return overlap_ratio


def test_directory(directory_path, save_directory):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    for filename in os.listdir(directory_path):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(directory_path, filename)
            save_path = os.path.join(save_directory, filename)

            result = detect_text_overlap(img_path, save_path)
            if result:
                print(
                    f"TEXT_OVERLAP issue detected in {img_path}. Annotated image saved as {result}.")
            else:
                print(f"No TEXT_OVERLAP issue found in {img_path}.")


# Test the directory
directory_path = "/home/gefen/Website-Eye-Robot/TESTS/x/"
save_directory = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/TEXT_OVERLAP_ANNOTATED"
test_directory(directory_path, save_directory)

# detect_text_overlap("/home/gefen/Website-Eye-Robot/screenshots_375x667/2_1_0.png", "TEXT_OVERLAP.png")

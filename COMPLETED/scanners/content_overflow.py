import pytesseract
import cv2
import numpy as np
import re

# for testing
import os

# Constants
MIN_CONTOUR_SIZE = 10
MIN_ASPECT_RATIO = 2
MAX_ASPECT_RATIO = 1000
MIN_SOLIDITY = 0
OVERFLOW_THRESHOLD = 0.1


def detect_content_overflow(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_content_overflow.jpg", img)

    gray = preprocess_image(img)
    cv2.imwrite("grayscale_image_content_overflow.jpg", gray)

    thresh = threshold_image(gray)
    cv2.imwrite("thresholded_image_content_overflow.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    cv2.imwrite("morphological_operations_content_overflow.jpg", thresh)

    contours = find_contours(thresh)
    img_copy = img.copy()
    found_issue = False

    # Visualize contours
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 2)
    cv2.imwrite("contours_content_overflow.jpg", img_copy)

    for contour in contours:
        if is_region_of_interest(contour):
            x, y, w, h = cv2.boundingRect(contour)
            crop_img = img[y:y+h, x:x+w]
            cv2.imwrite(
                f"/home/gefen/Website-Eye-Robot/contours/{str(contour)}.jpg", crop_img)

            if contains_text(crop_img) and is_content_overflow(crop_img, contours):
                found_issue = True
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 2)

    if found_issue:
        # print("Found CONTENT_OVERFLOW issue")
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        # print("Not found CONTENT_OVERFLOW issue")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(1, 1))
    # gray = clahe.apply(gray)
    return gray


def threshold_image(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 13, 5)


def apply_morphological_operations(thresh):
    kernel_size =3
    kernel_shape = cv2.MORPH_RECT
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))
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


def is_content_overflow(img, contours):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)  # Threshold the image

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        # check if contour is at the top level of hierarchy
        if hierarchy[0][i][3] == -1:
            x, y, w, h = cv2.boundingRect(contours[i])
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Perform OCR on each bounding box and get boxes
    boxes = pytesseract.image_to_boxes(img)
    boxes = boxes.split("\n")

    # Check if text is overflowing its container by aspect ratio
    for box in boxes:
        # parse box information
        box_values = box.split(" ")
        if len(box_values) >= 6:  # Check if there are enough values to unpack
            char, x1, y1, x2, y2 = box_values[:5]
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            w1 = x2 - x1  # width of character
            h1 = y2 - y1  # height of character
            ar1 = w1 / h1  # aspect ratio of character

            for i in range(len(contours)):
                # check if contour is at the top level of hierarchy
                if hierarchy[0][i][3] == -1:
                    x3, y3, w3, h3 = cv2.boundingRect(contours[i])
                    ar3 = w3 / h3  # aspect ratio of bounding box

                    # check if character is inside bounding box
                    if x1 >= x3 and y1 >= y3 and x2 <= x3 + w3 and y2 <= y3 + h3:
                        # check if aspect ratios are significantly different
                        if abs(ar1 - ar3) > 0.5:  # adjust this threshold according to your font size and shape
                            print("Text is overflowing!")
                            print("Character:", char)
                            print("Character aspect ratio:", ar1)
                            print("Bounding box aspect ratio:", ar3)
                            return True


def test_directory(directory_path, save_directory):
    # Create the save directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            # Construct the full paths for the input image and save path
            img_path = os.path.join(directory_path, filename)
            save_path = os.path.join(save_directory, filename)

            # Call the detect_content_overflow function
            result = detect_content_overflow(img_path, save_path)
            if result:
                print(
                    f"CONTENT_OVERFLOW issue detected in {img_path}. Annotated image saved as {result}.")
            else:
                print(f"No CONTENT_OVERFLOW issue found in {img_path}.")


# Test the directory
directory_path = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/CONTENT_OVERFLOW/"
save_directory = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/CONTENT_OVERFLOW_ANNOTATED"
test_directory(directory_path, save_directory)

# detect_content_overflow(
#     "9.jpg", "CONTENT_OVERFLOW.png")

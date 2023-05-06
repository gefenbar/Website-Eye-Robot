import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import re

# matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    # The minimum area of a contour to be considered as a region of interest
    MIN_CONTOUR_SIZE = 600  # 1-1000
    # The minimum and maximum ratio of width to height of a contour to be considered as a region of interest
    MIN_ASPECT_RATIO = 0.1  # 0.1-10
    MAX_ASPECT_RATIO = 100  # 10-1000
    # The minimum ratio of contour area to convex hull area of a contour to be considered as a region of interest
    MIN_SOLIDITY = 0  # 0-1
    # The threshold for the difference between the mean color and the peak color of a region to be considered as having low color contrast
    COLOR_DIFF_THRESHOLD = 90  # adjust based on chosen color space

    # Load the image
    img = cv2.imread(img_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Apply noise removal to the grayscale image using Gaussian blur
    gray = cv2.GaussianBlur(gray, (1, 1), 0)

    # Apply adaptive thresholding to the grayscale image
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Define the kernel size and shape for morphological operations
    kernel_size = 11
    kernel_shape = cv2.MORPH_ELLIPSE

    # Create the kernel for morphological operations
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))

    # Apply morphological closing operation
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Apply morphological opening operation
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Find contours in the thresholded image
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_copy = img.copy()
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w * h < MIN_CONTOUR_SIZE:
            continue
        aspect_ratio = w / h
        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
            continue
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area
        if solidity < MIN_SOLIDITY:
            continue

        # Crop the region of interest from the image
        crop_img = img[y:y+h, x:x+w]

        # Enhance contrast of cropped image using CLAHE
        crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
        crop_img_gray = clahe.apply(crop_img_gray)

        # Apply text recognition using pytesseract
        text = pytesseract.image_to_string(crop_img_gray, config='--psm 6')

        # Check if the region contains text using regular expression
        if re.search(r'\w', text):
            # Draw a green rectangle around the region of interest
            # cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Compute the mean and peak color of the cropped region
            mean_color = np.mean(crop_img, axis=(0, 1))
            peak_color = np.max(crop_img, axis=(0, 1))

            # Compute the color difference between the mean and peak
            color_diff = np.linalg.norm(mean_color - peak_color)

            if color_diff < COLOR_DIFF_THRESHOLD:
                found_issue = True
                # Draw a red rectangle around the region of interest
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (128, 0, 128), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues found")
        return ""


color_contrast(
    '/home/gefen/Website-Eye-Robot/image_62.png', 'current_results.png')

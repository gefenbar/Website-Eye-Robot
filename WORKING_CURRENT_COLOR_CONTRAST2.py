
import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    # The minimum area of a contour to be considered as a region of interest
    MIN_CONTOUR_SIZE = 1  # 1-1000
    # The minimum and maximum ratio of width to height of a contour to be considered as a region of interest
    MIN_ASPECT_RATIO = 0.1  # 0.1-10
    MAX_ASPECT_RATIO = 1000  # 10-1000
    # The minimum ratio of contour area to convex hull area of a contour to be considered as a region of interest
    MIN_SOLIDITY = 0  # 0-1
    # The threshold for the difference between the mean color and the peak color of a region to be considered as having low color contrast
    COLOR_DIFF_THRESHOLD = 30  # adjust based on LAB color space range

    img = cv2.imread(img_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equ = cv2.equalizeHist(gray)

    # Example of using cv2.threshold_otsu
    _, thresh = cv2.threshold(
        equ, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    kernel_size = 10
    kernel_shape = cv2.MORPH_ELLIPSE
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

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
        # Recognize text within the cropped region
        text = pytesseract.image_to_string(crop_img)

        crop_img_lab = cv2.cvtColor(crop_img, cv2.COLOR_BGR2LAB)
        mean_lab = cv2.mean(crop_img_lab)
        peak_lab = np.amax(crop_img_lab, axis=(0, 1))
        mean_lab = np.array(mean_lab)
        peak_lab = np.array(peak_lab)
        color_diff = np.linalg.norm(mean_lab[:3] - peak_lab.reshape(1, 3))

        if color_diff < COLOR_DIFF_THRESHOLD:
            # If the region has low color contrast, draw a red rectangle around it and set found_issue to True
            found_issue = True
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 0, 255), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues found")
        return ""


color_contrast(
    '/home/gefen/Website-Eye-Robot/test3.png', 'current_results.png')

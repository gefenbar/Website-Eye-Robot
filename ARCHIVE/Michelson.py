import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    MIN_CONTOUR_SIZE = 3
    MIN_ASPECT_RATIO = 3
    MAX_ASPECT_RATIO = 100
    MIN_SOLIDITY = 0.3
    # Change this value to adjust the threshold for Michelson contrast
    CONTRAST_THRESHOLD = 0.2
    img = cv2.imread(img_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equ = cv2.equalizeHist(gray)
    block_size = 5
    thresh = cv2.adaptiveThreshold(
        equ, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
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

        # Calculate Michelson contrast for the cropped region
        I_max = int(np.max(crop_img))
        I_min = int(np.min(crop_img))
        michelson_contrast = (I_max - I_min) / (I_max + I_min)

        if michelson_contrast < CONTRAST_THRESHOLD and text:
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            found_issue = True

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Save the image with the identified problematic regions
    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues")
        return ""


color_contrast('test1.png', 'y.png')

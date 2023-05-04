
import os
import pytesseract
from itertools import chain
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    MIN_CONTOUR_SIZE = 5
    MIN_ASPECT_RATIO = 5
    MAX_ASPECT_RATIO = 40
    MIN_SOLIDITY = 0.6
    COLOR_DIFF_THRESHOLD = 30

    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equ = cv2.equalizeHist(gray)
    block_size = 75
    thresh = cv2.adaptiveThreshold(
        equ, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, block_size, 3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

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

        mean_color = np.mean(crop_img, axis=(0, 1))
        hist, bins = np.histogram(crop_img.ravel(), bins=range(256))
        peak_color = np.argmax(hist)
        color_diff = np.abs(mean_color[0] - peak_color)

        if color_diff < COLOR_DIFF_THRESHOLD and text:
            fig_hist = plt.figure(figsize=(25, 5))
            plt.subplot(121), plt.imshow(
                cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
            plt.title('Original Image'), plt.xticks([]), plt.yticks([])
            plt.subplot(122), plt.hist(crop_img.ravel(), bins=range(256))
            plt.title('Histogram'), plt.xticks([]), plt.yticks([])
            fig_hist.savefig(f"histogram_{x}_{y}.png")
            plt.close(fig_hist)

            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            found_issue = True

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        return ""


color_contrast('/home/gefen/Website-Eye-Robot/xxx/9.png', 'test.png')

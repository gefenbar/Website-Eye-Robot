import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    MIN_CONTOUR_SIZE = 0
    MIN_ASPECT_RATIO = 0
    MAX_ASPECT_RATIO = 100
    MIN_SOLIDITY = 0
    COLOR_DIFF_THRESHOLD = 20

    img = cv2.imread(img_path)
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
    i = 0
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

        # Create a figure to plot the histogram of the region
        fig_hist = plt.figure(figsize=(5, 5))
        mean_color = np.mean(crop_img, axis=(0, 1))
        hist, bins = np.histogram(crop_img, bins=range(256))
        peak_color = np.argmax(hist)

        # Plot the histogram
        plt.bar(bins[:-1], hist, width=1)
        plt.xlim(min(bins), max(bins))
        plt.ylim(0, max(hist))
        plt.title('Histogram of Text Region')
        plt.xlabel('Color Intensity')
        plt.ylabel('Frequency')

        color_diff = np.abs(mean_color[0] - peak_color)
        if color_diff < COLOR_DIFF_THRESHOLD and text:
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            found_issue = True

            # Save the figure with the histogram of the region
            fig_hist.savefig(f'/home/gefen/Website-Eye-Robot/histograms{i}.jpg')
            plt.close(fig_hist)
            i += 1
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Save the image with the identified problematic regions
    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues")
        return ""


color_contrast('test3.png', 'H.png')

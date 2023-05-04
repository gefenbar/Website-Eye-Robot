import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    MIN_CONTOUR_SIZE = 1
    MIN_ASPECT_RATIO = 4
    MAX_ASPECT_RATIO = 1165
    MIN_SOLIDITY = 0
    COLOR_DIFF_THRESHOLD = 25
    img = cv2.imread(img_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find text regions using Tesseract OCR
    text_boxes = pytesseract.image_to_boxes(gray)
    text_boxes = text_boxes.split('\n')
    text_boxes = [box.split() for box in text_boxes]
    img_copy = img.copy()
    # Create a figure to plot the histograms of the regions
    fig_hist = plt.figure(figsize=(25, 5))
    for box in text_boxes:
        x, y, w, h = box[1:5]
        if int(w) * int(h) < MIN_CONTOUR_SIZE:
            continue
        aspect_ratio = int(w) / int(h)
        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
            continue
        area = int(w) * int(h)
        if area < MIN_SOLIDITY:
            continue
        # Crop the region of interest from the image
        crop_img = gray[int(y):int(y)+int(h), int(x):int(x)+int(w)]
        # Create histogram for the region
        hist, bins = np.histogram(crop_img, bins=range(256))
        peak_color = np.argmax(hist)
        mean_color = np.mean(crop_img)
        color_diff = np.abs(mean_color - peak_color)
        if color_diff < COLOR_DIFF_THRESHOLD:
            cv2.rectangle(img_copy, (int(x), int(y)),
                          (int(x)+int(w), int(y)+int(h)), (0, 0, 255), 2)
            found_issue = True
        cv2.rectangle(img, (int(x), int(y)), (int(
            x)+int(w), int(y)+int(h)), (0, 255, 0), 2)

    # Save the figure with the histograms of the regions
    fig_hist.savefig("histogram.png")

    # Save the image with the identified problematic regions
    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        return ""


color_contrast('test3.png', 'new.png')

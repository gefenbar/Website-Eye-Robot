import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tensorflow import keras

matplotlib.use('agg')


def color_contrast(img_path, save_path):
    found_issue = False
    # The minimum area of a contour to be considered as a region of interest
    MIN_CONTOUR_SIZE = 1  # 1-1000
    # The minimum and maximum ratio of width to height of a contour to be considered as a region of interest
    MIN_ASPECT_RATIO = 1  # 0.1-10
    MAX_ASPECT_RATIO = 1000  # 10-1000
    # The minimum ratio of contour area to convex hull area of a contour to be considered as a region of interest
    MIN_SOLIDITY = 0  # 0-1
    # The threshold for the difference between the mean color and the peak color of a region to be considered as having low color contrast
    COLOR_DIFF_THRESHOLD = 20  # 0-255

    img = cv2.imread(img_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equ = cv2.equalizeHist(gray)
    block_size = 35
    thresh = cv2.adaptiveThreshold(
        equ, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_copy = img.copy()

    # Load the OCR model
    ocr_model = keras.models.load_model('letters_model.h5')

    # Create a figure to plot the histograms of the regions
    fig_hist = plt.figure(figsize=(25, 5))

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
        roi = gray[y:y+h, x:x+w]

        # OCR on the region of interest
        text = ocr_model.predict(np.expand_dims(roi, axis=0))
        text = keras.backend.get_value(keras.backend.ctc_decode(
            text, input_length=np.ones(text.shape[0])*text.shape[1])[0][0])
        text = ''.join([chr(i) for i in np.squeeze(text)])

        # If the region has no text, skip it
        if not text:
            continue

        # Calculate the mean color and the peak color of the region
        mean_color = cv2.mean(img[y:y+h, x:x+w])
        hist, bins = np.histogram(roi.ravel(), 256, [0, 256])
        peak_color = bins[np.argmax(hist)]

        # If the difference between the mean color and the peak color is less than the threshold, the region has low color contrast
        color_diff = abs(mean_color[0] - peak_color)
        if color_diff < COLOR_DIFF_THRESHOLD:
            found_issue = True

            # Draw a rectangle around the region of interest in the image
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)

            # Plot the histogram of the region
            plt.subplot(1, len(contours), contours.index(contour) + 1)
            plt.hist(roi.ravel(), 256, [0, 256])
            plt.title(f'Region {contours.index(contour) + 1}')

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        return ""


color_contrast('/home/gefen/Website-Eye-Robot/screenshots_1920x1080/0_3_800.png', 'gpt.png')

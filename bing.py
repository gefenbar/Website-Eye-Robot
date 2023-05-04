import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from keras.models import load_model
from keras.preprocessing.image import img_to_array

matplotlib.use('agg')

# Load pre-trained Keras model for text recognition
model = load_model('letters_model.h5')


def color_contrast(img_path, save_path):
    found_issue = False

    # The minimum area of a contour to be considered as a region of interest
    MIN_CONTOUR_SIZE = 500  # 1-1000

    # The minimum and maximum ratio of width to height of a contour to be considered as a region of interest
    MIN_ASPECT_RATIO = 5  # 0.1-10
    MAX_ASPECT_RATIO = 1000  # 10-1000

    # The minimum ratio of contour area to convex hull area of a contour to be considered as a region of interest
    MIN_SOLIDITY = 0.4  # 0-1
    COLOR_DIFF_THRESHOLD = 20
    img = cv2.imread(img_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    equ = cv2.equalizeHist(gray)

    block_size = 5

    thresh = cv2.adaptiveThreshold(
        equ, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size, 2)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_copy = img.copy()

    # Create a figure to plot the histograms of the regions
    fig_hist = plt.figure(figsize=(25, 5))

    text_regions = []

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

        # Recognize text within the cropped region using Keras model
        text = recognize_text(crop_img)

        if text:
            text_regions.append((x, y, w, h, crop_img))

    for x, y, w, h, crop_img in text_regions:
        mean_color = np.mean(crop_img, axis=(0, 1))
        hist, bins = np.histogram(crop_img, bins=range(256))
        peak_color = np.argmax(hist)

        color_diff = np.abs(mean_color[0] - peak_color)

        if color_diff < COLOR_DIFF_THRESHOLD:
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            found_issue = True

        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Save the figure with the histograms of the regions
    fig_hist.savefig("histogram.png")

    # Save the image with the identified problematic regions
    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues")
        return ""


def recognize_text(crop_img):
    # Preprocess cropped image for text recognition using Keras model
    crop_img_preprocessed = preprocess_image(crop_img)

    # Use Keras model to recognize text within cropped image
    text_probs = model.predict(crop_img_preprocessed)

    # Convert predicted text probabilities from one-hot encoding to string
    text = one_hot_to_string(text_probs)

    return text


def preprocess_image(crop_img):
    # Convert cropped image to grayscale
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Resize cropped image to match input size of Keras model
    gray_resized = cv2.resize(
        gray, (model.input_shape[1], model.input_shape[2]))

    # Normalize pixel values
    gray_normalized = gray_resized / 255.0

    # Expand dimensions to match input shape of Keras model
    gray_preprocessed = np.expand_dims(gray_normalized, axis=-1)
    gray_preprocessed = np.expand_dims(gray_preprocessed, axis=0)

    return gray_preprocessed


def one_hot_to_string(one_hot):
    # Define mapping of one-hot encoding to characters
    char_map = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # Convert one-hot encoding to index
    index = np.argmax(one_hot, axis=-1)

    # Check if index is a single value or an array
    if np.isscalar(index):
        # Convert single index value to character
        text = char_map[index]
    else:
        # Convert array of index values to characters
        text = ''.join([char_map[i] for i in index])
    return text


color_contrast(
    '/home/gefen/Website-Eye-Robot/screenshots_1920x1080/0_2_800.png', 'working.png')

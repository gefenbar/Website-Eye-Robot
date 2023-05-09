import pytesseract
import cv2
import numpy as np
import re


def detect_small_text(img_path, save_path):
    # Load and resize the image
    img = load_and_resize_image(img_path)
    height, width = img.shape[:2]

    # Calculate the minimum and maximum height of a region to be considered as containing small text
    MIN_HEIGHT, MAX_HEIGHT = calculate_min_max_height(height)

    # Preprocess the image
    gray = preprocess_image(img)

    # Apply adaptive thresholding to the grayscale image
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Apply morphological operations to the thresholded image
    thresh = apply_morphological_operations(thresh)

    # Find contours in the thresholded image
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_copy = img.copy()
    found_issue = False
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h < MIN_HEIGHT or h > MAX_HEIGHT:
            continue
        cropped_img = img[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cropped_img, lang='eng')
        if not text.strip():
            continue

        # Check if the text is a letter or word or sentence using regex pattern matching.
        pattern = re.compile(r'^\w+$')
        if pattern.match(text):
            found_issue = True
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 127), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues found")
        return ""


def load_and_resize_image(img_path):
    # Load the image
    img = cv2.imread(img_path)

    # # Resize the image
    # scale_percent = 100  # percent of original size
    # width = int(img.shape[1] * scale_percent / 100)
    # height = int(img.shape[0] * scale_percent / 100)
    # dim = (width, height)
    # img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    return img


def calculate_min_max_height(height):
    # The minimum height of a region to be considered as containing small text
    reference_height = 1080
    min_height = 0
    max_height = 25
    ratio = height / reference_height

    MIN_HEIGHT = int(ratio * min_height)  # adjust based on image resolution

    # The maximum height of a region to be considered as containing small text
    MAX_HEIGHT = int(ratio * max_height)  # adjust based on image resolution

    return MIN_HEIGHT, MAX_HEIGHT


def preprocess_image(img):
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply histogram equalization to the grayscale image
    gray = cv2.equalizeHist(gray)
    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(1, 1))
    gray = clahe.apply(gray)

    # Apply noise removal to the grayscale image using Gaussian blur
    gray = cv2.GaussianBlur(gray, (1, 3), 0)

    # Sharpen the image using a kernel
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    gray = cv2.filter2D(gray, -1, kernel)

    return gray


def apply_morphological_operations(thresh):
    # Define the kernel size and shape for morphological operations
    kernel_size = 1
    kernel_shape = cv2.MORPH_ELLIPSE

    # Create the kernel for morphological operations
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))

    # Apply morphological closing operation
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Apply morphological opening operation
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return thresh


detect_small_text(
    "/home/gefen/Website-Eye-Robot/screenshots_1366x768/1_1_0.png", "SMALL_TEXT.png")

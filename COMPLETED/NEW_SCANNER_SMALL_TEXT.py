import pytesseract
import cv2
import numpy as np

def detect_small_text(img_path, save_path):
    # The minimum height of a region to be considered as containing small text
    MIN_HEIGHT = 1 # adjust based on image resolution
    # The maximum height of a region to be considered as containing small text
    MAX_HEIGHT = 4 # adjust based on image resolution

    # Load the image
    img = cv2.imread(img_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(16, 16))
    gray = clahe.apply(gray)

    # Apply noise removal to the grayscale image using Gaussian blur
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to the grayscale image
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Define the kernel size and shape for morphological operations
    kernel_size = 5
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
    found_issue = False
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h < MIN_HEIGHT or h > MAX_HEIGHT:
            continue
        cropped_img = img[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cropped_img, lang='eng')
        if not text.strip():
            found_issue = True
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 127), 2)
    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("no issues found")
        return ""

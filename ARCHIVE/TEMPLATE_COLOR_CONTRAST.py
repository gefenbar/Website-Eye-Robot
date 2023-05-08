import os
import time
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')

def color_contrast(img_path, save_path):
    found_issue = False

    # Define constants
    # Minimum size of contour. Any contour smaller than this size will be ignored
    MIN_CONTOUR_SIZE = 1200
    # Minimum aspect ratio of bounding box of contour. Any contour with aspect ratio smaller than this will be ignored
    MIN_ASPECT_RATIO = 0.7
    # Maximum aspect ratio of bounding box of contour. Any contour with aspect ratio larger than this will be ignored
    MAX_ASPECT_RATIO = 8
    # Minimum solidity of contour. Any contour with solidity smaller than this will be ignored
    MIN_SOLIDITY = 0.7
    # Color difference threshold. Any text region with color difference smaller than this will be marked as a potential issue
    COLOR_DIFF_THRESHOLD = 100

    # Load the image
    img = cv2.imread(img_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization to the image
    equ = cv2.equalizeHist(gray)

    # Apply adaptive thresholding to the image
    block_size = 15  # Increase block size for better capture of larger text regions
    thresh = cv2.adaptiveThreshold(
        equ, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block_size, 5)

    # Apply morphological operations to connect broken text regions and remove small noise regions
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Get the contours of the text regions
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a copy of the original image for visualization
    img_copy = img.copy()

    # Create a figure with three subplots: one for the image, one for the grayscale histogram, and one for the colored histogram
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(25, 5))

    # Plot the original image in the left subplot
    ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax1.set_title('Original Image')

    # Plot the grayscale histogram in the middle subplot
    ax2.hist(gray.ravel(), 256, [0, 256])
    ax2.set_title('Grayscale Histogram')

    # Plot the colored histogram in the right subplot
    color = ('blue', 'green', 'red')
    for i, col in enumerate(color):
        hist = cv2.calcHist([img], [i], None, [256], [0, 256])
        ax3.plot(hist, color=col)
    ax3.set_title('Colored Histogram')

    # Create a directory to store the histograms if it does not exist
    if not os.path.exists('/home/gefen/PROGRAMMING/Website-Eye-Robot/histograms'):
        os.makedirs('/home/gefen/PROGRAMMING/Website-Eye-Robot/histograms')

    # Generate a unique filename using the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"/home/gefen/PROGRAMMING/Website-Eye-Robot/histograms/image_{timestamp}.png"

    # Save the figure with the unique filename
    plt.savefig(filename)

    # Loop through each contour and get the bounding rectangle
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Filter out small contours
        if w * h < MIN_CONTOUR_SIZE:
            continue

        # Check aspect ratio
        aspect_ratio = w / h
        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
            continue

        # Check solidity
        area = cv2.contourArea(contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area
        if solidity < MIN_SOLIDITY:
            continue

        # Crop the text region and apply OCR
        crop_img = img[y:y+h, x:x+w]

        # Calculate the mean color of the cropped image
        mean_color = np.mean(crop_img, axis=(0, 1))

        # Calculate the histogram of colors in the cropped image
        hist, bins = np.histogram(crop_img, bins=range(256))

        # Find the peak color in the histogram
        peak_color = np.argmax(hist)

        # Calculate the distance between the mean color and the peak color
        color_diff = np.abs(mean_color[0] - peak_color)

        # If the color difference is below the threshold, mark the text region
        if color_diff < COLOR_DIFF_THRESHOLD:
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
            found_issue = True

        # Draw bounding boxes on all text regions
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    if found_issue:
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        return ""


# testing area

color_contrast('test2.png', "/home/gefen/Website-Eye-Robot/x.png")



# or


# color_contrast_images = []
# non_color_contrast_images = []

# color_directory = "/home/gefen/PROGRAMMING/Website-Eye-Robot/Color_Contrast/"
# non_color_directory = "/home/gefen/PROGRAMMING/Website-Eye-Robot/No_Color_Contrast/"

# # loop over all files in color directory
# for filename in os.listdir(color_directory):
#     if filename.endswith(".png"):
#         filepath = os.path.join(color_directory, filename)
#         new_filename = "color_" + filename
#         new_filepath = os.path.join(color_directory, new_filename)
#         color_contrast(filepath, new_filepath)
#         color_contrast_images.append(new_filepath)

# # loop over all files in non-color directory
# for filename in os.listdir(non_color_directory):
#     if filename.endswith(".png"):
#         filepath = os.path.join(non_color_directory, filename)
#         new_filename = "non_color_" + filename
#         new_filepath = os.path.join(non_color_directory, new_filename)
#         color_contrast(filepath, new_filepath)
#         non_color_contrast_images.append(new_filepath)

# # print the results
# print("Color contrast images:")
# for filepath in color_contrast_images:
#     print(filepath)

# print("Non-color contrast images:")
# for filepath in non_color_contrast_images:
#     print(filepath)

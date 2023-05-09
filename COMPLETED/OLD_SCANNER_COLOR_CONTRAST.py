import pytesseract
import cv2
import numpy as np
import re
#  included kmeans#  included kmeans#  included kmeans

# Constants
MIN_CONTOUR_SIZE = 600  # adjust based on image resolution and text size
MIN_ASPECT_RATIO = 0.1  # minimum width/height ratio of a text region
MAX_ASPECT_RATIO = 100  # maximum width/height ratio of a text region
MIN_SOLIDITY = 0.5  # minimum fraction of area/hull_area of a text region
COLOR_DIFF_THRESHOLD = 90  # minimum color difference between text and background

# Suggestion: Use a different color space that is more perceptually uniform and better reflects how humans perceive color differences
# For example: Lab or CIEDE2000 color space
# You can use cv2.cvtColor to convert from BGR to Lab or other color spaces


def detect_color_contrast(img_path, save_path):

    # Load and preprocess the image
    img_bgr = load_image(img_path)  # load the image in BGR format
    img_lab = convert_to_lab(img_bgr)  # convert the image to Lab format
    gray = preprocess_image(img_lab)  # preprocess the L channel of the image

    # Apply thresholding and morphological operations to the L channel
    thresh = threshold_image(gray)
    thresh = apply_morphological_operations(thresh)

    # Find contours in the thresholded image
    contours = find_contours(thresh)

    img_copy_bgr = img_bgr.copy()  # make a copy of the original BGR image
    img_copy_lab = img_lab.copy()  # make a copy of the converted Lab image
    found_issue = False
    for contour in contours:
        # Check if the contour is a region of interest (ROI)
        if is_region_of_interest(contour):
            x, y, w, h = cv2.boundingRect(contour)

            # Crop the ROI from both BGR and Lab images
            crop_img_bgr = img_copy_bgr[y:y+h, x:x+w]
            crop_img_lab = img_copy_lab[y:y+h, x:x+w]

            # Check if the ROI contains text using pytesseract on the BGR image
            if contains_text(crop_img_bgr):
                # Compute the color difference between the mean and peak color of the ROI using the Lab image
                color_diff_lab = compute_color_difference_lab(crop_img_lab)

                if color_diff_lab < COLOR_DIFF_THRESHOLD:
                    found_issue = True
                    # Draw a purple rectangle around the ROI on the BGR image
                    cv2.rectangle(img_copy_bgr, (x, y),
                                  (x+w, y+h), (255, 102, 0), 2)

    if found_issue:
        # save the BGR image with rectangles
        cv2.imwrite(save_path, img_copy_bgr)
        return save_path
    else:
        print("no issues found")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def convert_to_lab(img_bgr):
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2Lab)


def preprocess_image(img_lab):
    l, a, b = cv2.split(img_lab)  # split the Lab image into L,a,b channels
    # create a CLAHE object to apply contrast limiting adaptive histogram equalization to L channel
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    l = clahe.apply(l)  # enhance contrast in L channel
    # apply Gaussian blur to L channel to remove noise
    l = cv2.GaussianBlur(l, (1, 1), 0)
    return l


def threshold_image(gray):
    return cv2.adaptiveThreshold(gray,
                                 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                 11,
                                 7)


def apply_morphological_operations(thresh):
    kernel_size = 11
    kernel_shape = cv2.MORPH_ELLIPSE
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return thresh


def find_contours(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def is_region_of_interest(contour):
    x, y, w, h = cv2.boundingRect(contour)
    if w*h < MIN_CONTOUR_SIZE:  # check if the contour area is too small
        return False
    aspect_ratio = w/h  # calculate the aspect ratio of the contour
    # check if the aspect ratio is too low or too high
    if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
        return False
    area = cv2.contourArea(contour)  # calculate the area of the contour
    hull = cv2.convexHull(contour)  # calculate the convex hull of the contour
    hull_area = cv2.contourArea(hull)  # calculate the area of the convex hull
    solidity = float(area)/hull_area  # calculate the solidity of the contour
    if solidity < MIN_SOLIDITY:  # check if the solidity is too low
        return False
    return True


def contains_text(crop_img_bgr):
    # convert the cropped BGR image to grayscale
    crop_img_gray = cv2.cvtColor(crop_img_bgr, cv2.COLOR_BGR2GRAY)
    # use pytesseract to recognize text from grayscale image with page segmentation mode 6 (assume a single uniform block of text)
    text = pytesseract.image_to_string(crop_img_gray, config='--psm 6')
    # use regular expression to check if text contains any alphanumeric characters
    return re.search(r'\w', text)


def compute_color_difference_lab(crop_img_lab):

    # Suggestion: Use a different method to compute the mean and peak color of a region, such as k-means clustering or histogram analysis
    # For example: Use k-means clustering to find two dominant colors in a region and compute their distance in Lab space

    k = 2  # number of clusters (colors)
    # reshape the Lab image into a 3-column array
    data = crop_img_lab.reshape((-1, 3))
    # convert data type to float32 for k-means algorithm
    data = np.float32(data)

    # define criteria for k-means algorithm (type,max_iter,epsilon)
    criteria = (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    # define initial condition for k-means algorithm (random centers)
    flags = cv2.KMEANS_RANDOM_CENTERS
    # apply k-means algorithm and get labels and centers
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, flags)

    # compute mean color as average of centers
    mean_color = np.mean(centers, axis=0)
    # compute peak color as maximum of centers
    peak_color = np.max(centers, axis=0)

    # compute color difference as euclidean distance between mean and peak color
    color_diff = np.linalg.norm(mean_color-peak_color)

    return color_diff


# detect_color_contrast('/home/gefen/Website-Eye-Robot/screenshots_1366x768/1_1_0.png', 'asxjasbcjkasbjclsa.png')

import numpy as np
import cv2
from .helpers import sizeImage
def opening_filter(image, kernel_size=(2, 2)):
    """Applies morphological opening to remove small noise."""
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def area_crop(image, x, y, r):
    """Crop a square region centered at (x, y) with radius r."""
    print('Coordinates for crop:', x, y, r)
    y_flipped = image.shape[0] - y  # Flip y-axis (for MIAS dataset)
    return image[y_flipped - r:y_flipped + r, x - r:x + r]


def image_crop_dcm(image, y1, y4, x1, x2):
    """Crop a rectangular area in DICOM image format."""
    return image[y1:y4, x1:x2]


def draw_area(img, x, y, r):
    """Draws a red rectangle centered at (x, y) with size 2r x 2r on the image."""
    print('Coordinates:', x, y, r)
    y_flipped = img.shape[0] - y
    img_copy = np.copy(img)

    # Draw rectangle
    cv2.rectangle(img_copy, (x - r, y_flipped - r), (x + r, y_flipped + r), (255, 0, 0), 4)
    return img_copy


def affected_area_dcm(img, x1, y1, x2, y2, x3, y3, x4, y4):
    """Draws a polygon area (typically a rectangle) on DICOM image."""
    img_copy = np.copy(img)
    color = (255, 87, 51)  # RGB orange-ish
    coords = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

    for i in range(4):
        pt1 = coords[i]
        pt2 = coords[(i + 1) % 4]
        cv2.line(img_copy, pt1, pt2, color, 5)

    return img_copy

# Define a function to compute the optimal exponent factor based on pixel intensity distribution
def calculate_optimal_exponent(image, percentile=90, lower_bound=2, upper_bound=20, scaling_factor=0.97):
    # Calculate the specified percentile of pixel intensities
    intensity_percentile = np.percentile(image, percentile / 100.0 * np.max(image))

    # Suggest an exponent based on the computed percentile
    suggested_n = lower_bound + (upper_bound - lower_bound) * (1 - intensity_percentile)

    # Apply the scaling factor to adjust the suggested exponent
    suggested_n_new = suggested_n * scaling_factor
    print(f"Original suggested exponent: {suggested_n}")
    print(f"Using only {scaling_factor * 100}% of the suggested exponent. The new suggested exponent is: {suggested_n_new}")

    # Ensure the new exponent is within the specified range
    return max(lower_bound, min(upper_bound, suggested_n_new))

def DoG_filter(img, k1=1.0, k2=1.0):
    """Applies Difference of Gaussians (DoG) filter."""
    dog_low = cv2.GaussianBlur(img, (3, 3), 0)
    dog_high = cv2.GaussianBlur(img, (5, 5), 0)
    dog = k1 * dog_low - k2 * dog_high
    return dog

# I normalize the cropped image and with Logarithmic tranf. I scale it from 0 to 1
def normalize_image(img):
    img_norm = (img - img.min()) / (img.max() - img.min()+1e-9)
    return img_norm

# opening filter
def opening_filter(image):
    # Realiza la operación de apertura morfológica
    kernel = np.ones((2,2), np.uint8)  # Definir un kernel de 3x3
    opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    return opening  # Asegúrate de retornar el resultado


# Anscombe transformation
def anscombe(img):
    img_anscombe= 2.0*np.sqrt(img + 3.0/8.0)
    sizeImage(img_anscombe)
    return(img_anscombe)


# Intensity using the cosine function
def cosine_function(img):
    img_cosine= 1-np.cos((np.pi/2)*(img/255.0))
    sizeImage(img_cosine)
    return(img_cosine)

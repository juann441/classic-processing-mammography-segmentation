import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import blob_dog, blob_doh, blob_log
from skimage.color import rgb2gray

def detect_blobs(image, method='LoG', min_sigma=1, max_sigma=5, threshold=0.02):
    """
    Detect blobs using LoG, DoG or DoH.

    Parameters:
        image (2D array): Input image (grayscale or RGB).
        method (str): 'LoG', 'DoG' or 'DoH'.
        min_sigma (float): Minimum sigma for blob detection.
        max_sigma (float): Maximum sigma for blob detection.
        threshold (float): Threshold for blob detection.

    Returns:
        blobs (ndarray): Array of detected blobs.
    """

    if image.ndim == 3:
        image = rgb2gray(image)

    if method == 'LoG':
        blobs = blob_log(image, min_sigma=min_sigma, max_sigma=max_sigma, threshold=threshold)
        blobs[:, 2] = blobs[:, 2] * np.sqrt(2)  # Adjust radius
    elif method == 'DoG':
        blobs = blob_dog(image, min_sigma=min_sigma, max_sigma=max_sigma, threshold=threshold)
        blobs[:, 2] = blobs[:, 2] * np.sqrt(2)
    elif method == 'DoH':
        blobs = blob_doh(image, min_sigma=min_sigma, max_sigma=max_sigma, threshold=threshold)
    else:
        raise ValueError("Méthode invalide : choisir parmi 'LoG', 'DoG' ou 'DoH'")

    return blobs

def plot_blobs(image, blobs, color='red', figsize=(8, 8), dpi=100, title='Blobs detected'):
    """Overlay the detected blobs on the image."""
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.imshow(image, cmap='gray')
    for blob in blobs:
        y, x, r = blob
        c = plt.Circle((x, y), r, color=color, linewidth=1.5, fill=False)
        ax.add_patch(c)
    ax.set_title(f"{title} ({len(blobs)} blobs)")
    ax.axis('off')
    plt.show()

def interactive_blobs_cv(img, blobs):
    """
    Interactive OpenCV window to inspect blobs one by one.

    Controls:
        - Press any key to go to the next blob.
        - Press ESC to exit.
    """
    img_rgb = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    index = 0
    while index < len(blobs):
        blob = blobs[index]
        y, x, r = map(int, blob)
        display = img_rgb.copy()
        cv2.circle(display, (x, y), r, (0, 0, 255), 1)
        cv2.putText(display, f"{index+1}/{len(blobs)}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Blobs Viewer (ESC to quit)", display)
        key = cv2.waitKey(0)
        if key == 27:  # ESC
            break
        index += 1
    cv2.destroyAllWindows()

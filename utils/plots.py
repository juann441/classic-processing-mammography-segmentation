import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

# === Basic image plotting functions ===

def plot_image_with_title(image, title, cmap='gray', size=100):
    fig, ax = plt.subplots(dpi=size)
    ax.imshow(image, cmap=cmap)
    ax.set_title(str(title))
    ax.axis('off')
    plt.show()

def plot_two_images(image1, image2, title1, title2, size=100):
    fig, ax = plt.subplots(1, 2, dpi=size)
    ax[0].imshow(image1, cmap='gray')
    ax[0].set_title(str(title1))
    ax[0].axis('off')
    ax[1].imshow(image2, cmap='gray')
    ax[1].set_title(str(title2))
    ax[1].axis('off')
    plt.show()

def plot_three_images(image1, image2, image3, title1, title2, title3, size=100):
    fig, ax = plt.subplots(1, 3, dpi=size)
    titles = [title1, title2, title3]
    for i, img in enumerate([image1, image2, image3]):
        ax[i].imshow(img, cmap='gray')
        ax[i].set_title(str(titles[i]), fontsize=5)
        ax[i].axis('off')
    plt.show()


# === Plot 10 images with optional colormap switching ===

custom_cmap = ListedColormap(["blue", "green", "yellow", "red", "white"])

def plot_ten_images(imgs, titles, size=(18, 6), dpi=200):
    assert len(imgs) == 10 and len(titles) == 10, "You must provide 10 images and 10 titles."

    fig, axes = plt.subplots(2, 5, figsize=size, dpi=dpi)
    fig.subplots_adjust(hspace=0.1, wspace=0)

    for i, (img, title) in enumerate(zip(imgs, titles)):
        ax = axes[i // 5, i % 5]

        if i == 3:  # Custom colormap for Multi-Otsu
            ax.imshow(img, cmap=custom_cmap)
        elif i == len(imgs) - 1:
            ax.imshow(img, cmap='seismic')
        else:
            ax.imshow(img, cmap='gray')

        ax.axis('off')
        ax.set_title(str(title), fontsize=10)

    plt.show()


# === Histogram plotting ===

def plot_histogram(img, n_bins=256, title='', range_vals=(0, 1)):
    h = img.ravel()
    plt.hist(h, bins=n_bins, range=range_vals, edgecolor='black')
    plt.title(str(title))
    plt.grid(True)
    plt.show()

def plot_two_histograms(img1, img2, n_bins=256, title1='', title2='', range_vals=(0, 1)):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    axs[0].hist(img1.ravel(), bins=n_bins, range=range_vals, edgecolor='black')
    axs[0].set_title(str(title1))
    axs[0].grid(True)
    axs[1].hist(img2.ravel(), bins=n_bins, range=range_vals, edgecolor='black')
    axs[1].set_title(str(title2))
    axs[1].grid(True)
    plt.show()

def visualize_image_and_histogram(image, n_bins=256, size=(12, 6), dpi=80, image_title='Image', hist_title='Histogram'):
    fig, axs = plt.subplots(1, 2, figsize=size, dpi=dpi)

    axs[0].imshow(image, cmap='gray')
    axs[0].set_title(image_title)
    axs[0].axis('off')

    axs[1].hist(image.ravel(), bins=n_bins, range=[0, 1], edgecolor='black')
    axs[1].set_title(hist_title)
    axs[1].set_xlabel('Intensity')
    axs[1].set_ylabel('Frequency')
    axs[1].grid(True)

    plt.tight_layout()
    plt.show()

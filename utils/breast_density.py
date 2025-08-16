
from .processing import calculate_optimal_exponent, DoG_filter, cosine_function, anscombe, opening_filter, normalize_image

import numpy as np
import matplotlib.pyplot as plt
from skimage.filters import threshold_multiotsu
from io import BytesIO
from PIL import Image 
from matplotlib.backends.backend_agg import FigureCanvasAgg



def multi_Otsu_4zonesv2(img_power, dpi=100, mean_ponderate=1.15, render=False):

    # === Calcul exponent optimal et transformation
    optimal_n = calculate_optimal_exponent(
        img_power, percentile=90, lower_bound=2, upper_bound=20, scaling_factor=0.15
    )
    img_power = img_power ** optimal_n

    # === Thresholding
    thresholds = threshold_multiotsu(img_power)
    otsu_threshold1, otsu_threshold2 = thresholds

    # === Zones
    z1 = img_power < otsu_threshold1
    z2 = (img_power >= otsu_threshold1) & (img_power < otsu_threshold2)
    z3 = img_power >= otsu_threshold2

    # === Metrics
    a1, a2, a3 = np.sum(z1), np.sum(z2), np.sum(z3)
    pdm_z3 = (a3 / (a2 + a3)) * 100 if (a2 + a3) > 0 else 0

    l2 = np.sum(img_power[z2])
    l3 = np.sum(img_power[z3])
    pltd_z3 = (l3 / (l2 + l3)) * 100 if (l2 + l3) > 0 else 0

    avg_classical = np.mean(img_power[z3]) if a3 > 0 else 0

    alpha = 6
    weights = np.exp(alpha * img_power[z3])
    avg_weighted = (
        np.sum(img_power[z3] * weights) / np.sum(weights) if np.sum(weights) > 0 else 0
    )

    interval_min = min(avg_weighted * mean_ponderate, 1.0)
    interval_max = 1.0
    mask_interval = (img_power >= interval_min) & (img_power <= interval_max)
    avg_intensity_interval = (
        np.mean(img_power[mask_interval]) if np.any(mask_interval) else 0
    )

    # === Segmentation colors
    regions = np.digitize(img_power, bins=thresholds)
    segmentation_colors = plt.cm.jet(regions / regions.max())
    segmentation_colors[mask_interval] = [1, 1, 1, 1]

    # === Plot histogramme compact (uniquement si render=True)
    fig_hist = None
    if render:
        fig_hist, ax_hist = plt.subplots(figsize=(2.5, 2), dpi=100)
        ax_hist.hist(img_power.ravel(), bins=60, color="skyblue", edgecolor="black")
        ax_hist.set_title("Intensity Histogram", fontsize=8)
        ax_hist.tick_params(axis="both", labelsize=6)

        ax_hist.axvline(otsu_threshold1, color="red", linestyle="--", label=f"T1: {otsu_threshold1:.2f}")
        ax_hist.axvline(otsu_threshold2, color="red", linestyle="--", label=f"T2: {otsu_threshold2:.2f}")
        ax_hist.axvline(interval_min, color="green", linestyle="--", label=f"Min: {interval_min:.2f}")
        ax_hist.axvline(interval_max, color="green", linestyle="--", label=f"Max: {interval_max:.2f}")
        ax_hist.legend(fontsize=6)
        plt.tight_layout()

    # === Résultats numériques
    results = {
        "PDM_Z3": round(pdm_z3, 3),
        "PLTD_Z3": round(pltd_z3, 3),
        "PL_Z3_classical": round(avg_classical, 3),
        "PL_Z3_weighted": round(avg_weighted, 3),
        "RIPM_min": round(interval_min, 3),
        "RIPM_max": round(interval_max, 3),
        "RIPM_avg": round(avg_intensity_interval, 3),
    }

    return (
        img_power,              # image transformée (après power)
        segmentation_colors,    # couleurs de segmentation
        regions,                # index de régions
        otsu_threshold1,
        otsu_threshold2,
        interval_min,
        interval_max,
        results,
        optimal_n,               # image brute avant transformation
        fig_hist              # histogramme prêt pour Tkinter
    )



def next_step(img_power,segmentation_colors, regions, otsu_threshold1, otsu_threshold2, interval_min, interval_max, results,optimal_n) :
    imag_multiOtsu_copy1 = np.copy(img_power)
    intervalo_min, interval_max =interval_min, interval_max  #0.72, 1  # Reemplaza con los valores reales de tu función multi_Otsu3
    print(" Probable intensity interval for microcalcifications from multi_Otsu_4zones:","(", interval_max ,";",interval_max,")")
    # Apply thresholding based on the probable interval
    imag_multiOtsu_copy1[imag_multiOtsu_copy1 < intervalo_min] = 0
    imag_multiOtsu_copy1[imag_multiOtsu_copy1 >= intervalo_min] = 1
    # Display the resulting image
    imag_multiOtsu_norm = normalize_image(imag_multiOtsu_copy1)
    # Opening Filter
    imag_opening = opening_filter(imag_multiOtsu_copy1).astype(np.float32)  # Convert to float32 if necessary
    imag_opening_norm = normalize_image(imag_opening)
    #Convolution between the Otsu mask refined with the opening filter and the image corresponding to the mammogram crop
    imag_crop_norm_copy = np.copy(img_power)
    imag_crop_norm_copy[imag_opening_norm == 0] = 0
    # Anscombe transformation
    imag_anscombe = anscombe(imag_crop_norm_copy)
    imag_anscombe_norm = normalize_image(imag_anscombe)
    # Cosine function
    imag_cosine= cosine_function(imag_anscombe_norm)
    imag_cosine_norm = normalize_image(imag_cosine)
    # DoG filter
    img_dog = DoG_filter(imag_cosine_norm, k1=1.1, k2=0.9)
    img_dog_norm = normalize_image(img_dog)
    # Final image
    final_image= img_dog_norm*imag_crop_norm_copy
    final_image_norm = normalize_image(final_image)
    return final_image_norm
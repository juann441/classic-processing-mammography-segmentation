import os
import numpy as np
from skimage import io
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut

def load_image(path):
    """
    Charge une image à partir d’un fichier JPG, PNG ou DICOM.

    Args:
        path (str): Chemin vers le fichier image.

    Returns:
        np.ndarray: Image en niveaux de gris normalisée entre [0, 1].
    """
    ext = os.path.splitext(path)[1].lower()

    if ext in [".jpg", ".jpeg", ".png", ".pgm", ".tif", ".tiff"]:
        image = io.imread(path, as_gray=True)
        image = image.astype(np.float32)
        image = (image - image.min()) / (image.max() - image.min() + 1e-8)
        return image

    elif ext in [".dcm"]:
        ds = pydicom.dcmread(path)

        # Appliquer VOI LUT si disponible (contraste)
        image = apply_voi_lut(ds.pixel_array, ds) if 'VOILUTFunction' in ds else ds.pixel_array

        # Convertir à float et normaliser
        image = image.astype(np.float32)
        image = (image - np.min(image)) / (np.max(image) - np.min(image) + 1e-8)
        return image

    else:
        raise ValueError(f"Format de fichier non supporté : {ext}")

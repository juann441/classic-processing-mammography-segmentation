
import numpy as np
import csv

import csv
import csv
import os

def get_annotation_for_image(csv_path, filename):
    """
    Recherche les coordonnées et le rayon associés à une image dans un fichier CSV.

    Args:
        csv_path (str): Chemin du fichier CSV.
        filename (str): Nom du fichier image (ex: 'mdb001.pgm' ou 'mdb001').

    Returns:
        list[dict]: Liste des annotations correspondantes (il peut y en avoir plusieurs).
    """
    basename = os.path.splitext(os.path.basename(filename))[0]  # 'mdb001.pgm' → 'mdb001'
    annotations = []
    print(basename)

    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            # Nettoyage de BOM + trimming général
            reader.fieldnames = [name.strip().lstrip('\ufeff') for name in reader.fieldnames]

            for row in reader:
                row = {k.strip(): v for k, v in row.items()}

                if row.get("Name", "").strip() == basename:
                    annotations.append({
                        "x": int(row["Coordinate_x"]),
                        "y": int(row["Coordinate_y"]),
                        "radius": int(row["Radius"]),
                        "abnormality": row.get("Abnormality", ""),
                        "severity": row.get("Severity", "")
                    })
    except Exception as e:
        print(f"[Erreur] Lecture du CSV échouée: {e}")

    return annotations


def sizeImage(image):
    """
    Affiche les dimensions de l’image et la plage des valeurs de pixels.
    """
    print(f"Dimensions de l’image : {image.shape}")
    print(f"Valeur min : {image.min()}")
    print(f"Valeur max : {image.max()}")


def rgb_to_y(matrix_rgb):
    """
    Conversion d’une image RGB vers la composante Y (luminance) de l’espace YIQ.

    Entrée :
        - matrix_rgb : image RGB (H, W, 3)

    Sortie :
        - matrix_y : image en niveaux de gris (H, W)
    """
    matrix_rgb = np.asarray(matrix_rgb)
    coefficients = np.array([0.299, 0.587, 0.114])
    matrix_y = np.dot(matrix_rgb[..., :3], coefficients)
    return matrix_y

def classify_suspicion_level(density):
    """
    Classifies the suspicion level of a lesion based on its estimated malignancy risk percentage.
    """
    if density > 2 and density <= 10:
        return (
            "Category 4A: Low but sufficient suspicion (>2% to 10%).\n"
        )
    elif density > 10 and density <= 50:
        return (
            "Category 4B: Moderate suspicion (>10% to 50%).\n"
        )
    elif density > 50 and density < 95:
        return (
            "Category 4C: High suspicion (>50% to <95%).\n"
        )
    else:
        return (
            "Outside BI-RADS 4A–4C range.\n"
            "- Either benign (<2%) or extremely suspicious (>95%).\n"
            "- Further assessment or different category may apply.\n"
        )

# 🔬 Détection automatique des microcalcifications mammaires

![Interface](./screenshots/interface.png)

## 🧠 Objectif

Ce projet vise à développer un outil d'aide au diagnostic pour les médecins radiologues, permettant de **localiser automatiquement les microcalcifications** dans les images de mammographie. Ces dépôts de calcium, souvent invisibles à l'œil nu, peuvent être un **signe précoce du cancer du sein**. L'application permet d’assister les praticiens en fournissant une visualisation rapide et dynamique des zones suspectes.

---

## 🛠 Fonctionnalités principales

- ✅ Chargement d'images mammographiques (PGM, PNG, JPG, DICOM)
- 🖼 Recadrage manuel de la zone d’intérêt via une fenêtre OpenCV
- 🎚 Interface Tkinter avec sliders interactifs pour ajuster les paramètres de segmentation
- 🧪 Algorithme de segmentation basé sur le seuillage multi-Otsu pondéré
- 🔍 Affichage synchronisé de :
  - Image originale
  - Zone croppée
  - Résultat de segmentation (superposition couleur)
  - Blobs détectés (surlignés en rose)
- 📊 Affichage de métriques (PDM, PLTD, RIPM...) en bas de l’interface
- 💾 Sauvegarde possible des images de résultats

---

## 📁 Arborescence

```
microcalcification-project/
├── data/                         # Images d’entrée
├── notebooks/
│   └── main_analysis.ipynb       # Notebook principal (analyse hors interface)
├── utils/
│   ├── processing.py             # Pré-traitements (normalisation, filtrage)
│   ├── plots.py                  # Fonctions d’affichage
│   ├── blobs.py                  # Détection de blobs (LoG, DoH, etc.)
│   ├── breast_density.py         # Segmentation Multi-Otsu, densité mammaire
│   └── helpers.py                # Fonctions utilitaires
├── interface.py                  # Script principal de l’IHM
├── requirements.txt              # Dépendances Python
├── README.md                     # Ce fichier
└── screenshots/
    └── interface.png             # Capture d’écran de l’interface
```

---

## ▶️ Lancer l'application

Assurez-vous d'avoir Python 3.8+ installé. Puis :

```bash
pip install -r requirements.txt
python interface.py
```

---

## 🔧 Dépendances principales

- `numpy`, `opencv-python`, `matplotlib`
- `scikit-image` (Multi-Otsu, filtrage)
- `PIL` (pour le chargement d’images)
- `pydicom` (lecture des fichiers .dcm)
- `tkinter` (interface graphique)

---

## ✍️ Remarques

- Le **paramètre `optim_exposant`** permet d’ajuster le contraste local utilisé pour la segmentation.
- Le **paramètre `mean_ponderate`** influe sur la pondération moyenne appliquée aux couches du seuillage Multi-Otsu.
- Les métriques affichées sont issues d’études sur la **densité mammaire et l’évaluation de la qualité de la segmentation**.

---

## 👨‍⚕️ Cas d’usage

Ce projet n’est **pas un dispositif médical certifié**, mais peut servir de **base à des outils cliniques** futurs, ou à des **études de recherche** en imagerie médicale.

---

## 🧑‍💻 Auteur

Juan Reyes — Étudiant en informatique & vision par ordinateur  
Projet développé durant un stage à l’Université Nationale du Sud (Bahía Blanca, Argentine)

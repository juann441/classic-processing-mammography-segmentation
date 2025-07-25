# 🩻 Détection automatique des microcalcifications sur mammographies

> Interface interactive pour l'aide au diagnostic des microcalcifications, réalisée avec **Python, OpenCV et Tkinter**.

---

## 🎯 Objectif

Ce projet vise à fournir aux **radiologues** une aide au diagnostic visuel supplémentaire pour la **localisation rapide et précise des microcalcifications** sur des mammographies. Ces calcifications peuvent être des **indicateurs précoces du cancer du sein**, d’où l’importance de leur détection automatique.

---

## 🖼️ Aperçu de l'interface

![Aperçu de l'interface](./interface_example.png)

- 📂 Chargement d’une image mammographique (format JPG, PNG, PGM, DICOM…)
- ✂️ Recadrage manuel de la région d’intérêt (ROI)
- 📊 Segmentation dynamique avec réglage de deux paramètres :
  - `optim_exposant` : pondération d’optimisation d'exposant
  - `mean_ponderate` : pondération de moyenne locale
- 🎯 Résultats affichés sous forme d’images et de métriques
- 💾 Option de sauvegarde des résultats

---

## ⚙️ Fonctionnalités principales

- Interface utilisateur graphique (Tkinter + OpenCV)
- Recadrage interactif de la zone d’analyse
- Algorithme de **segmentation Multi-Otsu** optimisé
- Détection de zones suspectes colorisées en **rose**
- Calcul de **métriques quantitatives** pour l’aide au diagnostic :
  - `PLTD`, `PDM`, `PL_classical`, `PL_weighted`
  - `RIPM_min`, `RIPM_max`, `RIPM_avg`...

---

## 📁 Arborescence du projet
microcalcification-project/
├── assets/ # Images d’entrée
├── notebooks/
│ └── main_analysis.ipynb # Notebook principal (analyse hors interface)
├── utils/
│ ├── processing.py # Pré-traitements (normalisation, filtrage)
│ ├── plots.py # Fonctions d’affichage
│ ├── blobs.py # Détection de blobs (LoG, DoH, etc.)
│ ├── breast_density.py # Segmentation Multi-Otsu, densité mammaire
│ └── helpers.py # Fonctions utilitaires
├── gui/
│ ├── app.py # Script principal de l’IHM
├── run_app.py # 
├── requirements.txt # Dépendances Python
├── README.md # Ce fichier
└── exemple_interface.png
---

## ▶️ Lancer l'application

Assurez-vous d'avoir Python 3.8+ installé. Puis :

bash
pip install -r requirements.txt
python run_app.py

## 🔧 Dépendances principales
numpy, opencv-python, matplotlib

scikit-image (Multi-Otsu, filtrage)

PIL (pour le chargement d’images)

pydicom (lecture des fichiers .dcm)

tkinter (interface graphique)

## ✍️ Remarques
Le paramètre optim_exposant permet d’ajuster le contraste local utilisé pour la segmentation.

Le paramètre mean_ponderate influe sur la pondération moyenne appliquée aux couches du seuillage Multi-Otsu.

Les métriques affichées sont issues d’études sur la densité mammaire et l’évaluation de la qualité de la segmentation.

## 👨‍⚕️ Cas d’usage
Ce projet n’est pas un dispositif médical certifié, mais peut servir de base à des outils cliniques futurs, ou à des études de recherche en imagerie médicale.

## 🧑‍💻 Auteur
Juan Reyes — Étudiant en informatique & vision par ordinateur
Projet développé durant un stage à l’Université Nationale du Sud (Bahía Blanca, Argentine)

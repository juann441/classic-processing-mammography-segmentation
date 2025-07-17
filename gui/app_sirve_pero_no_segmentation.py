from utils.io_utils import load_image
from utils.plots import *
from utils.processing import *
from utils.breast_density import *
from utils.blobs import *
from utils.helpers import *

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np


class MicrocalcificationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Détection de Microcalcifications")
        self.root.geometry("1000x700")

        self.image_path = None
        self.image_loaded = None
        self.image_cropped = None
        self.image_segmented = None
        self.crop_coords = []

        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        self.frame_top = ttk.Frame(self.root)
        self.frame_top.pack(pady=10)

        self.load_btn = ttk.Button(self.frame_top, text="📂 Ouvrir une image", command=self.load_image)
        self.load_btn.grid(row=0, column=0, padx=5)

        self.crop_btn = ttk.Button(self.frame_top, text="✂️ Recadrer", command=self.crop_image, state=tk.DISABLED)
        self.crop_btn.grid(row=0, column=1, padx=5)

        self.segment_btn = ttk.Button(self.frame_top, text="🧠 Segmenter", command=self.segment_image, state=tk.DISABLED)
        self.segment_btn.grid(row=0, column=2, padx=5)

        self.reset_btn = ttk.Button(self.frame_top, text="🔄 Réinitialiser", command=self.reset_all)
        self.reset_btn.grid(row=0, column=3, padx=5)

        self.canvas = tk.Canvas(self.root, width=960, height=500, bg='gray')
        self.canvas.pack()

    def load_image(self):
        path = filedialog.askopenfilename(title="Sélectionner une image",
                                          filetypes=[("Images", "*.jpg *.jpeg *.png *.pgm *.tif *.tiff *.dcm")])
        if not path:
            return

        self.image_path = path
        self.image_loaded = load_image(path)
        self.display_image(self.image_loaded)
        self.crop_btn.config(state=tk.NORMAL)

    def display_image(self, image_np):
        image_pil = Image.fromarray((image_np * 255).astype(np.uint8))
        image_pil = image_pil.resize((480, 480))
        self.photo = ImageTk.PhotoImage(image_pil)
        self.canvas.delete("all")
        self.canvas.create_image(480, 250, image=self.photo)
        self.img_ref = self.photo  # pour éviter garbage collection

    def reset_all(self):
        self.image_path = None
        self.image_loaded = None
        self.image_cropped = None
        self.image_segmented = None
        self.crop_coords = []
        self.canvas.delete("all")
        self.crop_btn.config(state=tk.DISABLED)
        self.segment_btn.config(state=tk.DISABLED)

    def crop_image(self):
        self.display_image(self.image_loaded)
        self.crop_coords = []
        self.rect_id = None

        image_display_size = 480
        image_top_left_x = 480 - image_display_size // 2  # = 240
        image_top_left_y = 250 - image_display_size // 2  # = 10

        def canvas_to_image_coords(canvas_x, canvas_y):
            """Convertit les coords du canvas en coords dans l'image."""
            img_x = canvas_x - image_top_left_x
            img_y = canvas_y - image_top_left_y
            return img_x, img_y

        def on_press(event):
            x, y = event.x, event.y
            self.crop_coords = [(x, y)]
            if self.rect_id:
                self.canvas.delete(self.rect_id)

        def on_drag(event):
            if len(self.crop_coords) == 1:
                x0, y0 = self.crop_coords[0]
                x1, y1 = event.x, event.y
                if self.rect_id:
                    self.canvas.coords(self.rect_id, x0, y0, x1, y1)
                else:
                    self.rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, outline='yellow', width=2)

        def on_release(event):
            if len(self.crop_coords) == 1:
                x1_canvas, y1_canvas = self.crop_coords[0]
                x2_canvas, y2_canvas = event.x, event.y

                # Convertir en coords dans l'image affichée
                x1_img, y1_img = canvas_to_image_coords(x1_canvas, y1_canvas)
                x2_img, y2_img = canvas_to_image_coords(x2_canvas, y2_canvas)

                # Normaliser
                x1_img, x2_img = sorted([x1_img, x2_img])
                y1_img, y2_img = sorted([y1_img, y2_img])

                # Clamp dans l'image affichée
                x1_img = max(0, min(image_display_size - 1, x1_img))
                x2_img = max(0, min(image_display_size - 1, x2_img))
                y1_img = max(0, min(image_display_size - 1, y1_img))
                y2_img = max(0, min(image_display_size - 1, y2_img))

                # Redimensionner vers l'image réelle
                scale_x = self.image_loaded.shape[1] / image_display_size
                scale_y = self.image_loaded.shape[0] / image_display_size
                xmin = int(x1_img * scale_x)
                xmax = int(x2_img * scale_x)
                ymin = int(y1_img * scale_y)
                ymax = int(y2_img * scale_y)

                # Vérification que la zone n'est pas vide
                if xmax <= xmin or ymax <= ymin:
                    print("Zone de crop invalide, annulation.")
                    # Ne rien faire ou afficher un message d'erreur ici si tu veux
                    return

                self.image_cropped = self.image_loaded[ymin:ymax, xmin:xmax]

                # Affiche côte-à-côte pour debug (original + crop)
                self.show_two_images(self.image_loaded, self.image_cropped)

                self.segment_btn.config(state=tk.NORMAL)

                self.canvas.unbind("<ButtonPress-1>")
                self.canvas.unbind("<B1-Motion>")
                self.canvas.unbind("<ButtonRelease-1>")


        self.canvas.bind("<ButtonPress-1>", on_press)
        self.canvas.bind("<B1-Motion>", on_drag)
        self.canvas.bind("<ButtonRelease-1>", on_release)

    def show_two_images(self, img1, img2):
        def prep(img):
            return ImageTk.PhotoImage(Image.fromarray((img * 255).astype(np.uint8)).resize((480, 480)))

        photo1 = prep(img1)
        photo2 = prep(img2)

        self.canvas.delete("all")
        # Affiche img1 à gauche (x=240), img2 à droite (x=720)
        self.canvas.create_image(240, 250, image=photo1)
        self.canvas.create_image(720, 250, image=photo2)
        self.img_refs = [photo1, photo2]  # pour éviter garbage collection

    def segment_image(self):
        if self.image_cropped is None:
            return

        seg_color, regions, th1, th2, i_min, i_max, results = multi_Otsu_4zonesv2(self.image_cropped)
        segmented_img = next_step(self.image_cropped, seg_color, regions, th1, th2, i_min, i_max, results)

        self.image_segmented = segmented_img
        self.show_three_images(self.image_loaded, self.image_cropped, segmented_img)

    def show_three_images(self, img1, img2, img3):
        def prep(img): 
            return ImageTk.PhotoImage(Image.fromarray((img * 255).astype(np.uint8)).resize((320, 320)))

        photo1 = prep(img1)
        photo2 = prep(img2)
        photo3 = prep(img3)

        self.canvas.delete("all")
        self.canvas.create_image(160, 250, image=photo1)
        self.canvas.create_image(480, 250, image=photo2)
        self.canvas.create_image(800, 250, image=photo3)
        self.img_refs = [photo1, photo2, photo3]  # éviter garbage collection

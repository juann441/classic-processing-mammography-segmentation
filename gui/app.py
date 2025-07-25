# Importación de funciones personalizadas
from utils.io_utils import load_image
from utils.plots import *
from utils.processing import *
from utils.breast_density import *
from utils.blobs import *
from utils.helpers import *
import os

# Importación de bibliotecas estándar
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class MicrocalcificationGUI:
    def __init__(self):
        # Inicialización de la ventana principal
        self.root = tk.Tk()
        self.root.title("Detección de Microcalcificaciones ")
        self.root.geometry("1000x700")

        # Variables de estado
        self.image_path = None
        self.image_loaded = None
        self.image_loaded_original = None
        self.image_cropped = None
        self.show_overlay = True  # True = superposición, False = solo máscara
        self.optim_exposant_var = tk.DoubleVar()
        self.mean_ponderate_var = tk.DoubleVar(value=1.15)
        self.segment_after_id = None
        self.crop_info_csv = None
        self.x = 0
        self.y = 0
        self.r = 0

        self.image_segmented = None
        self.crop_coords = []
        self.crop_coords_interpoles = ()

        # Crear interfaz
        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        # Parte superior de la interfaz con botones principales
        self.frame_top = ttk.Frame(self.root)
        self.frame_top.pack(pady=10)

        # Botón para cargar imagen
        self.load_btn = ttk.Button(self.frame_top, text="📂 Abrir archivo", command=self.load_image)
        self.load_btn.grid(row=0, column=0, padx=5)

        # Botón para recortar
        self.crop_btn = ttk.Button(self.frame_top, text="✂️ Recortar", command=self.choose_crop_mode, state=tk.DISABLED)
        self.crop_btn.grid(row=0, column=1, padx=5)

        # Botón para segmentar
        self.segment_btn = ttk.Button(self.frame_top, text="🧠 Segmentar", command=self.segment_image, state=tk.DISABLED)
        self.segment_btn.grid(row=0, column=2, padx=5)

        # Botón para reiniciar
        self.reset_btn = ttk.Button(self.frame_top, text="🔄 Reiniciar", command=self.reset_all)
        self.reset_btn.grid(row=0, column=3, padx=5)

        # Botón para alternar visualización
        self.toggle_view_btn = ttk.Button(self.frame_top, text="🔀 Cambiar Vista", command=self.toggle_view, state=tk.DISABLED)
        self.toggle_view_btn.grid(row=0, column=4, padx=5)

        # Botón para guardar imagen
        self.save_btn = ttk.Button(self.frame_top, text="💾 Guardar imagen", command=self.save_image)
        self.save_btn.grid(row=0, column=5, padx=5)

        # Canvas principal para mostrar imágenes
        self.canvas = tk.Canvas(self.root, width=960, height=500, bg='gray')
        self.canvas.pack()

        # Frame con sliders para los parámetros
        self.frame_sliders = ttk.Frame(self.root)
        self.frame_sliders.pack(pady=10)

        # Slider para optim_exposant
        self.optim_label = ttk.Label(self.frame_sliders, text="optim_exposant")
        self.optim_label.grid(row=0, column=0, padx=5)

        self.optim_slider = ttk.Scale(
            self.frame_sliders, from_=0, to=1, variable=self.optim_exposant_var,
            orient=tk.HORIZONTAL, command=self.on_optim_slider_change)
        self.optim_slider.grid(row=0, column=1, padx=5)

        self.optim_entry = ttk.Entry(self.frame_sliders, width=6)
        self.optim_entry.grid(row=0, column=2, padx=5)
        self.optim_entry.insert(0, "0.0")
        self.optim_entry.bind("<Return>", self.on_optim_entry_change)

        # Slider para mean_ponderate
        self.mean_label = ttk.Label(self.frame_sliders, text="mean_ponderate")
        self.mean_label.grid(row=0, column=3, padx=5)

        self.mean_slider = ttk.Scale(
            self.frame_sliders, from_=1.05, to=1.20, variable=self.mean_ponderate_var,
            orient=tk.HORIZONTAL, command=self.on_mean_slider_change)
        self.mean_slider.grid(row=0, column=4, padx=5)

        self.mean_entry = ttk.Entry(self.frame_sliders, width=6)
        self.mean_entry.grid(row=0, column=5, padx=5)
        self.mean_entry.insert(0, "1.15")
        self.mean_entry.bind("<Return>", self.on_mean_entry_change)

        self.reset_sliders_btn = ttk.Button(self.frame_sliders, text="🔧 Reiniciar sliders", command=self.reset_sliders)
        self.reset_sliders_btn.grid(row=0, column=6, padx=10)

        # Frame para los visuales de análisis
        self.frame_analysis = ttk.Frame(self.root)
        self.frame_analysis.pack(pady=10)

        # Frame para mostrar resultados textuales
        self.frame_text = ttk.Frame(self.root)
        self.frame_text.pack(pady=10)

        self.text_results = tk.Text(self.frame_text, width=100, height=12, wrap="word", state=tk.DISABLED)
        self.text_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.frame_text, command=self.text_results.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_results.configure(yscrollcommand=scrollbar.set)

    # Cargar imagen desde el explorador
    def load_image(self):
        path = filedialog.askopenfilename(title="Seleccionar imagen",
                                        filetypes=[("Images", "*.jpg *.jpeg *.png *.pgm *.tif *.tiff *.dcm")])
        if not path:
            return

        self.image_path = path
        self.image_loaded = load_image(path)
        # 🔴 Sauvegarde de l’image originale avant toute modification
        self.image_loaded_original = self.image_loaded.copy()

        self.display_image(self.image_loaded)
        self.crop_btn.config(state=tk.NORMAL)
        self.segment_btn.config(state=tk.DISABLED)

        # 🔁 Toujours recharger les annotations
        csv_path = "mamografias_mias_2025/Data_base_mias.csv"
        self.annotations = get_annotation_for_image(csv_path, path)  # ← ✔️ réinitialisé

        file_name = os.path.basename(self.image_path)
        self.root.title(f"Analyse microcalcifications – {file_name}")

        if self.annotations:
            print(f"Annotation(s) trouvée(s) pour {path}:")
            for ann in self.annotations:
                print(f"  ➤ x: {ann['x']}, y: {ann['y']}, r: {ann['radius']}, abn: {ann['abnormality']}, sev: {ann['severity']}")
                # Tu peux ici appeler une fonction qui dessine le cercle par exemple
                # self.draw_annotation(ann["x"], ann["y"], ann["radius"])

        file_name = os.path.basename(self.image_path)
        self.root.title(f"Analyse microcalcifications – {file_name}")

    # Mostrar imagen en canvas
    def display_image(self, image_np):
        image_pil = Image.fromarray((image_np * 255).astype(np.uint8))
        image_pil = image_pil.resize((480, 480))
        self.photo = ImageTk.PhotoImage(image_pil)
        self.canvas.delete("all")
        self.canvas.create_image(480, 250, image=self.photo)
        self.img_ref = self.photo  # evitar garbage collection

    

    def choose_crop_mode(self):
        # Fenêtre popup de choix
        popup = tk.Toplevel(self.root)
        popup.title("Choisir méthode de recadrage")
        popup.geometry("300x120")
        popup.resizable(False, False)

        label = ttk.Label(popup, text="Méthode de recadrage :", font=("Segoe UI", 10))
        label.pack(pady=10)

        def handle_auto_crop():
            popup.destroy()
            if self.annotations:
                crop_data = self.annotations[0]  # on prend la première annotation trouvée
                self.auto_crop_from_csv(crop_data)
                return

            print("[Info] Aucune annotation trouvée. Passage en mode manuel.")
            self.crop_image()

        ttk.Button(popup, text="Recadrage automatique (CSV)", command=handle_auto_crop).pack(pady=5)
        ttk.Button(popup, text="Recadrage manuel", command=lambda: [popup.destroy(), self.crop_image()]).pack(pady=5)


    def auto_crop_from_csv(self, crop_data):
        try:
            # Récupérer les coordonnées depuis le CSV
            self.x = int(crop_data['x'])  # ⚠️ CSV: colonne 'Coordinate_x'
            self.y = int(crop_data['y'])  # ⚠️ CSV: colonne 'Coordinate_y'
            self.r = int(crop_data['radius'])  # ⚠️ CSV: colonne 'Radius'

            x, y, r = self.x, self.y, self.r
            y = self.image_loaded_original.shape[0] - y  # Inverser Y si origine en haut à gauche

            # Clamp pour éviter les débordements
            xmin = max(0, x - r)
            xmax = min(self.image_loaded_original.shape[1], x + r)
            ymin = max(0, y - r)
            ymax = min(self.image_loaded_original.shape[0], y + r)

            # Enregistrer les coordonnées du rectangle interpolées (comme dans crop_image)
            self.crop_coords_interpoles = ((xmin, ymin), (xmax, ymax))

            # Recadrer l'image
            self.image_cropped = self.image_loaded_original[ymin:ymax, xmin:xmax]
            self.show_two_images(self.image_loaded_original, self.image_cropped)

            # Appliquer la segmentation
            self.segment_image()

        except Exception as e:
            print(f"[Erreur] Recadrage auto échoué : {e}")
            print("→ Passage en mode manuel.")
            self.crop_image()



    # Reiniciar todo
    def reset_all(self):
        self.image_path = None
        self.image_loaded = None
        self.image_cropped = None
        self.image_loaded_original = None
        self.image_segmented = None
        self.crop_coords = []
        self.canvas.delete("all")
        self.crop_btn.config(state=tk.DISABLED)
        self.segment_btn.config(state=tk.DISABLED)
        self.segment_after_id = None
        self.crop_info_csv = None
        self.x = 0
        self.y = 0
        self.r = 0
        self.crop_coords_interpoles = ()

    # Actualizar los resultados en el cuadro de texto
    def update_results_text(self, results):
        self.text_results.config(state=tk.NORMAL)
        self.text_results.delete(1.0, tk.END)
        self.text_results.insert(tk.END, results)
        self.text_results.config(state=tk.DISABLED)

    # Programar segmentación con retraso
    def schedule_segment_image(self):
        if self.segment_after_id is not None:
            self.root.after_cancel(self.segment_after_id)
        self.segment_after_id = self.root.after(500, self.segment_image)

    def crop_image(self):
        self.display_image(self.image_loaded_original)
        self.crop_coords = []
        self.rect_id = None
        

        image_display_size = 480
        image_top_left_x = 480 - image_display_size // 2  # = 240
        image_top_left_y = 250 - image_display_size // 2  # = 10

        def canvas_to_image_coords(canvas_x, canvas_y):
            """Conversion de las cordenadas del canvas en cordenadas de la imagen"""
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
                scale_x = self.image_loaded_original.shape[1] / image_display_size
                scale_y = self.image_loaded_original.shape[0] / image_display_size
                xmin = int(x1_img * scale_x)
                xmax = int(x2_img * scale_x)
                ymin = int(y1_img * scale_y)
                ymax = int(y2_img * scale_y)

                self.crop_coords_interpoles = ((xmin, ymin), (xmax, ymax))

                # Vérification que la zone n'est pas vide
                if xmax <= xmin or ymax <= ymin:
                    print("CROP no valido.")
                    return

                self.image_cropped = self.image_loaded_original[ymin:ymax, xmin:xmax]

                # Affiche côte-à-côte l’image originale et le crop pour debug
                self.show_two_images(self.image_loaded_original, self.image_cropped)
                
                # Lance automatiquement la segmentation et affichage des 3 images
                self.segment_image()

                self.canvas.unbind("<ButtonPress-1>")
                self.canvas.unbind("<B1-Motion>")
                self.canvas.unbind("<ButtonRelease-1>")

        self.canvas.bind("<ButtonPress-1>", on_press)
        self.canvas.bind("<B1-Motion>", on_drag)
        self.canvas.bind("<ButtonRelease-1>", on_release)

    def toggle_view(self):
        if not hasattr(self, 'img_power') or not hasattr(self, 'seg_color_img'):
            print("No hay imagenes para segmentar.")
            return

        # ⬇️ Inverser l’état d’abord
        self.show_overlay = not self.show_overlay

        # ⬇️ Puis choisir l’image à afficher
        img4 = self.overlay_img if self.show_overlay else self.seg_only_img

        def prep(img):
            if img.dtype != np.uint8:
                img_disp = (img * 255).astype(np.uint8)
            else:
                img_disp = img
            pil_img = Image.fromarray(img_disp).resize((240, 240))
            return ImageTk.PhotoImage(pil_img)
        
        photo1 = prep(self.image_loaded)
        self.image_loaded_original = self.image_loaded.copy()
        photo2 = prep(self.img_power)
        photo3 = prep(self.seg_color_img)
        photo4 = prep(img4)

        self.canvas.delete("all")
        self.canvas.create_image(120, 250, image=photo1)
        self.canvas.create_image(360, 250, image=photo2)
        self.canvas.create_image(600, 250, image=photo3)
        self.canvas.create_image(840, 250, image=photo4)
        self.img_refs = [photo1, photo2, photo3, photo4]


    def show_image_on_canvas(self, img_rgb_float):
        # img_rgb_float : float [0..1], shape (H,W,3)
        img_uint8 = (img_rgb_float * 255).astype(np.uint8)
        img_pil = Image.fromarray(img_uint8).resize((320, 320))
        photo = ImageTk.PhotoImage(img_pil)
        self.canvas.delete("all")
        self.canvas.create_image(800, 250, image=photo)
        self.img_ref = photo  # éviter GC

    
    def on_optim_slider_change(self, val):
        val = float(val)
        self.optim_entry.delete(0, tk.END)
        self.optim_entry.insert(0, f"{val:.3f}")
        self.schedule_segment_image()


    def on_optim_entry_change(self, event):
        try:
            val = float(self.optim_entry.get())
            min_val = float(self.optim_slider.cget("from"))
            max_val = float(self.optim_slider.cget("to"))
            if min_val <= val <= max_val:
                self.optim_exposant_var.set(val)
                self.segment_image()
            else:
                print(f"Valor fuera del intervalo [{min_val}, {max_val}]")
        except ValueError:
            print("Valor no valido para optim_exposant")

    def on_mean_slider_change(self, val):
        val = float(val)
        self.mean_entry.delete(0, tk.END)
        self.mean_entry.insert(0, f"{val:.3f}")
        self.schedule_segment_image()  # ← ici aussi


    def on_mean_entry_change(self, event):
        try:
            val = float(self.mean_entry.get())
            if 1.05 <= val <= 1.20:
                self.mean_ponderate_var.set(val)
                self.segment_image()
            else:
                print("mean_ponderate fuera del intervalo [1.05, 1.20]")
        except ValueError:
            print("Valor no valido para mean_ponderate")



    def create_segment_only_image(self, mask):
        # Imagen en negro con pixeles segmentados en rosa (RGB: 255,105,180)
        # mask 2D binaria (0/1)
        h, w = mask.shape
        img = np.zeros((h, w, 3), dtype=np.uint8)
        pink = np.array([255, 105, 180], dtype=np.uint8)  # rosa
        img[mask == 1] = pink
        return img.astype(np.float32) / 255.

    def create_overlay_image(self, img_gray, mask):
        # img_gray: imagen crop a escala de grises normalizada [0..1]
        # mask: binaire 0/1
        # imagen rgb con pixeles rosa transparentes

        h, w = img_gray.shape
        img_rgb = np.stack([img_gray]*3, axis=-1)  # gris en RGB

        pink = np.array([255, 105, 180], dtype=np.uint8) / 255.  # rose normalizado
        alpha = 0.8  # transparencia

        overlay = img_rgb.copy()

        # Para los pixeles segmentados, mezcla de color rosa y gris con alpha
        overlay[mask == 1] = (1 - alpha) * img_rgb[mask == 1] + alpha * pink

        return overlay

    def reset_sliders(self):
        # Valores default
        default_optim = self.optim_slider.cget("from") + 0.5
        default_mean = 1.15

        # Update de los
        self.optim_exposant_var.set(default_optim)
        self.mean_ponderate_var.set(default_mean)

        # Update de los campos de texto
        self.optim_entry.delete(0, tk.END)
        self.optim_entry.insert(0, f"{default_optim:.3f}")

        self.mean_entry.delete(0, tk.END)
        self.mean_entry.insert(0, f"{default_mean:.3f}")

        # Lanza la segmentacion despues de un corto tiempo 50ms
        self.schedule_segment_image()

    def colorier_pixels_sur_image_loaded(self):
        if self.crop_coords_interpoles is None or len(self.crop_coords_interpoles) != 2:
            print("Erreur : crop_coords invalide", self.crop_coords_interpoles)
            return

        (x1, y1), (x2, y2) = self.crop_coords_interpoles
        h_crop, w_crop = y2 - y1, x2 - x1

        # Vérification masque
        if self.mask_segmented is None:
            print("Erreur : masque segmenté manquant")
            return

        # Redimensionner le masque si jamais le crop a changé de taille
        mask = self.mask_segmented
        if mask.shape[:2] != (h_crop, w_crop):
            print("Redimensionnement du masque pour correspondre au crop")
            mask = cv2.resize(mask, (w_crop, h_crop), interpolation=cv2.INTER_NEAREST)

        # Copier l’image originale
        image_colored = self.image_loaded_original.copy()

        # Convertir en couleur si image originale est en niveaux de gris
        if len(image_colored.shape) == 2 or image_colored.shape[2] == 1:
            image_colored = cv2.cvtColor(image_colored, cv2.COLOR_GRAY2BGR)

        # Appliquer la couleur rouge sur les pixels où mask > 0
        image_colored[y1:y2, x1:x2][mask > 0] = [255, 0, 0]

        ### >>>> AJOUT POUR LA BOÎTE ENGLOBANTE <<<< ###
        ys, xs = np.where(mask > 0)
        if len(xs) > 0 and len(ys) > 0:
            # Coordonnées de la boîte dans l’image entière (pas juste le crop)
            x_min, x_max = x1 + np.min(xs), x1 + np.max(xs)
            y_min, y_max = y1 + np.min(ys), y1 + np.max(ys)
            # Ajouter un padding autour de la boîte (par exemple 5 pixels)
            padding = 5
            height, width = image_colored.shape[:2]
            x_min = max(0, x_min - padding)
            x_max = min(width - 1, x_max + padding)
            y_min = max(0, y_min - padding)
            y_max = min(height - 1, y_max + padding)

            # Dessiner un rectangle vert (ou rouge)
            cv2.rectangle(image_colored, (x_min, y_min), (x_max, y_max), color=(0, 255, 0), thickness=2)

        # Mettre à jour l’attribut image affichée
        self.image_loaded = image_colored

            
    def segment_image(self):
        if self.image_cropped is None:
            return

        # Multi-otsu
        img_power, seg_color, regions, th1, th2, i_min, i_max, results, optimal_n, vis_img = multi_Otsu_4zonesv2(
            self.image_cropped,
            mean_ponderate=self.mean_ponderate_var.get(),
            render=True
        )

        # Si première fois : initialiser le slider optim_exposant
        if self.optim_slider['from'] == 0 and self.optim_slider['to'] == 1:
            ## Cambiar intervalo de exponente (no sirve)
            from_val = max(0, optimal_n - 0.5)
            to_val = optimal_n + 0.5
            self.optim_slider.config(from_=from_val, to=to_val)
            self.optim_exposant_var.set(optimal_n)
            self.optim_entry.delete(0, tk.END)
            self.optim_entry.insert(0, f"{optimal_n:.3f}")

        # Lire la valeur d’exposant
        exposant = self.optim_exposant_var.get()

        # Étape suivante
        segmented_img = next_step(img_power, seg_color, regions, th1, th2, i_min, i_max, results, exposant)
        self.image_segmented = segmented_img
        self.mask_segmented = (segmented_img > 0).astype(np.uint8)
        self.colorier_pixels_sur_image_loaded()

        # Création des images (rose seule et superposée)
        self.seg_only_img = self.create_segment_only_image(self.mask_segmented)
        self.overlay_img = self.create_overlay_image(self.image_cropped, self.mask_segmented)
        self.img_power = img_power
        self.seg_color_img = seg_color

        
        self.show_four_images(self.image_loaded, img_power, seg_color, self.overlay_img)


#####
#####
        self.update_results_text(results)


        # Affichage de la visualisation sous les sliders
        if hasattr(self, 'canvas_vis'):
            self.canvas_vis.destroy()

        self.canvas_vis = tk.Canvas(self.root, width=800, height=300)
        self.canvas_vis.pack(pady=5)
        self.canvas_vis.create_image(400, 150, image=vis_img)
        self.vis_img_ref = vis_img  # éviter le garbage collection

        # Activer le bouton de toggle
        self.toggle_view_btn.config(state=tk.NORMAL)
        # Appelé à la fin de segment_image()
        self.show_overlay = True
        self.toggle_view_btn.config(text="🎨 Mask view")  

    def show_two_images(self, img1, img2):
        def prep(img):
            return ImageTk.PhotoImage(Image.fromarray((img * 255).astype(np.uint8)).resize((480, 480)))

        photo1 = prep(img1)
        photo2 = prep(img2)

        self.canvas.delete("all")
        self.canvas.create_image(240, 250, image=photo1)
        self.canvas.create_image(720, 250, image=photo2)
        self.img_refs = [photo1, photo2]
        

    def show_four_images(self, img1, img_power, img_otsu_color, img_overlay):
        def prep(img):
            # Assure que img est float 0..1 ou uint8 0..255
            if img.dtype != np.uint8:
                img_disp = (img * 255).astype(np.uint8)
            else:
                img_disp = img
            pil_img = Image.fromarray(img_disp).resize((240, 240))
            return ImageTk.PhotoImage(pil_img)

        photo1 = prep(img1)
        
        photo2 = prep(img_power)
        photo3 = prep(img_otsu_color)
        photo4 = prep(img_overlay)

        self.canvas.delete("all")
        # Positions centrées sur l'axe Y=250, espacées de 240 pixels (largeur image)
        self.canvas.create_image(120, 250, image=photo1)
        self.canvas.create_image(360, 250, image=photo2)
        self.canvas.create_image(600, 250, image=photo3)
        self.canvas.create_image(840, 250, image=photo4)
        self.img_refs = [photo1, photo2, photo3, photo4]  # Pour éviter le garbage collection

    def save_image(self):
        if not hasattr(self, 'img_refs') or len(self.img_refs) < 4:
            messagebox.showerror("Erreur", "Aucune image disponible à enregistrer.")
            return

        # Fenêtre pop-up avec boutons
        popup = tk.Toplevel(self.root)
        popup.title("Guardar imagen")
        popup.geometry("400x200")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text="Seleccionar imagen :", font=('Arial', 11)).pack(pady=10)

        def save_selected(img_np, label):
            popup.destroy()
            if img_np is None:
                messagebox.showerror("Erreur", f"{label} non disponible.")
                return

            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("Fichiers PNG", "*.png")],
                title=f"Enregistrer {label}"
            )
            if not filepath:
                return

            try:
                # Préparation image
                if img_np.dtype != np.uint8:
                    img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
                img_pil = Image.fromarray(img_np) if img_np.ndim == 3 else Image.fromarray(img_np, mode="L")
                img_pil.save(filepath)
                messagebox.showinfo("Succès", f"{label} enregistrée avec succès !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'enregistrement :\n{str(e)}")

        # Boutons pour chaque image
        ttk.Button(popup, text="1️⃣ Imagen original", command=lambda: save_selected(self.image_loaded, "Image Originale")).pack(pady=2)
        ttk.Button(popup, text="2️⃣ Image Power Filter", command=lambda: save_selected(self.img_power, "Image Puissance")).pack(pady=2)
        ttk.Button(popup, text="3️⃣ Multi-Otsu", command=lambda: save_selected(self.seg_color_img, "Segmentation Multi-Otsu")).pack(pady=2)
        ttk.Button(
            popup,
            text="4️⃣ Segmentacion Final",
            command=lambda: save_selected(self.overlay_img if self.show_overlay else self.seg_only_img, "Segmentation Finale")
        ).pack(pady=2)
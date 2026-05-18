# client_src/views/card.py
import tkinter as tk
import os
from PIL import Image, ImageTk

class WelcomeCard(tk.Canvas):
    def __init__(self, parent, controller, on_start_callback=None):
        # Création du Canvas aux dimensions exactes de ta carte (300x500)
        super().__init__(parent, width=300, height=500, bg="#22252a", highlightthickness=0)
        self.controller = controller
        self.on_start_callback = on_start_callback
        self.swiping = False

        # Configuration du curseur pour inviter au clic
        self.config(cursor="hand2")

        # Chemin vers ton dessin
        chemin_carte = os.path.join("client_src", "rsc", "img", "card", "bienvenue.png")
        
        try:
            img_carte = Image.open(chemin_carte)
            # Sécurité au cas où le fichier n'est pas pile à la bonne taille
            img_carte = img_carte.resize((300, 500), Image.Resampling.LANCZOS)
            self.tk_img_carte = ImageTk.PhotoImage(img_carte)
            
            # Affichage du dessin au centre du Canvas
            self.card_item = self.create_image(150, 250, image=self.tk_img_carte)
            
            # Liaison du clic pour déclencher le Swipe
            self.tag_bind(self.card_item, "<Button-1>", lambda e: self.declencher_swipe())
            
        except Exception as e:
            print(f"[NOTE] Impossible de charger la carte de bienvenue : {e}")
            # Visuel de secours si l'image est manquante
            self.rect_item = self.create_rectangle(10, 10, 290, 490, fill="#2d3139", outline="#3a3f47", width=2)
            self.text_item = self.canvas.create_text(
                150, 250, 
                text="BIENVENUE\n\n[ Cliquez pour swiper ]", 
                font=("Segoe UI", 14, "bold"), fill="#ffffff", justify="center"
            )
            self.tag_bind(self.rect_item, "<Button-1>", lambda e: self.declencher_swipe())

    def declencher_swipe(self):
        """Lance l'animation de glissement vers la gauche (style Tinder)"""
        if self.swiping:
            return
        self.swiping = True
        
        # Désactive le curseur main pendant l'animation
        self.config(cursor="")
        
        # On lance l'animation de translation x, y et rotation légère
        self.anim_swipe(0)

    def anim_swipe(self, etape):
        # 12 étapes d'animation pour un effet fluide et rapide
        if etape < 12:
            # On déplace vers la gauche (-35px par frame) et légèrement vers le haut
            vitesse_x = -35
            vitesse_y = -5
            
            self.move(tk.ALL, vitesse_x, vitesse_y)
            # Petit effet d'effacement progressif (fondu) si supporté, sinon juste déplacement
            self.after(20, self.anim_swipe, etape + 1)
        else:
            # L'animation est finie, la carte est hors de l'écran.
            # On appelle la fonction de l'application pour dire "La partie commence vraiment !"
            if self.on_start_callback:
                self.on_start_callback()
            
            # On fait disparaître le widget Canvas proprement
            self.pack_forget()
            self.destroy()
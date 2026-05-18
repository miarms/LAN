# client_src/views/dice.py
import tkinter as tk
import os
from PIL import Image, ImageTk 
import random 

RACES = {
    "Boomer": {"FOR": 11, "DEX": 7, "CON": 13, "INT": 8, "SAG": 10, "CHA": 11, "PV": 100, "ENERGIE": 100, "PIECES": 130},
    "Gen Z": {"FOR": 8, "DEX": 14, "CON": 8, "INT": 13, "SAG": 8, "CHA": 10, "PV": 90, "ENERGIE": 110, "PIECES": 100},
    "Provincial": {"FOR": 14, "DEX": 8, "CON": 14, "INT": 9, "SAG": 9, "CHA": 6, "PV": 110, "ENERGIE": 100, "PIECES": 100},
    "Urbain": {"FOR": 10, "DEX": 15, "CON": 9, "INT": 10, "SAG": 6, "CHA": 10, "PV": 100, "ENERGIE": 90, "PIECES": 100},
    "Tanguy": {"FOR": 9, "DEX": 12, "CON": 10, "INT": 14, "SAG": 8, "CHA": 7, "PV": 100, "ENERGIE": 100, "PIECES": 60},
    "Karen": {"FOR": 10, "DEX": 9, "CON": 12, "INT": 6, "SAG": 6, "CHA": 17, "PV": 100, "ENERGIE": 100, "PIECES": 110},
    "Chill Guy": {"FOR": 8, "DEX": 6, "CON": 13, "INT": 10, "SAG": 15, "CHA": 8, "PV": 110, "ENERGIE": 90, "PIECES": 100}
}
CLASSES = {
    "Syndicaliste": {"FOR": 2, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 20, "ENERGIE": -10, "PIECES": 0},
    "Influenceur": {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 2, "PV": 0, "ENERGIE": 0, "PIECES": 10},
    "Gourou": {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 2, "CHA": 0, "PV": 0, "ENERGIE": 10, "PIECES": 0},
    "Bobo Ecolo": {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 2, "CHA": 0, "PV": 10, "ENERGIE": 0, "PIECES": -10},
    "Fils de": {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 2, "PV": 0, "ENERGIE": 0, "PIECES": 30},
    "Cadre Superieur": {"FOR": 0, "DEX": 0, "CON": 2, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10, "ENERGIE": 10, "PIECES": 0},
    "Consultant": {"FOR": 0, "DEX": 0, "CON": 0, "INT": 2, "SAG": 0, "CHA": 0, "PV": -10, "ENERGIE": 20, "PIECES": 0},
    "Adepte de Yoga": {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 0, "ENERGIE": 20, "PIECES": -10},
    "Stagiaire": {"FOR": 0, "DEX": 0, "CON": 0, "INT": 2, "SAG": 0, "CHA": 0, "PV": 0, "ENERGIE": 0, "PIECES": -20},
    "Leche-botte": {"FOR": 0, "DEX": 0, "CON": 2, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10, "ENERGIE": 0, "PIECES": 10},
    "Teletravailleur": {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10, "ENERGIE": 0, "PIECES": 0},
    "Commercial": {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 0, "ENERGIE": -10, "PIECES": 20}
}

class DiceModule(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.controller = controller
        self.en_cours = False
        
        self.lbl_title = tk.Label(self, text="LANCER DE DÉS", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0")
        self.lbl_title.pack(pady=(0, 10))
        
        # --- CANVAS POUR LE DÉ TRANSPARENT ---
        self.canvas = tk.Canvas(self, width=140, height=140, bg="#22252a", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.canvas.config(cursor="hand2")
        
        chemin_img = os.path.join("client_src", "rsc", "img", "dice.png")
        try:
            img_virgil = Image.open(chemin_img)
            img_virgil = img_virgil.resize((140, 140), Image.Resampling.LANCZOS)
            self.tk_image_base = ImageTk.PhotoImage(img_virgil)
            
            # Dessin du d20
            self.img_item = self.canvas.create_image(70, 70, image=self.tk_image_base)
            
            # MODIFICATION : y passe de 68 à 76 (descendu) et fill passe à "black" (noir)
            self.text_item = self.canvas.create_text(70, 76, text="—", font=("Segoe UI", 22, "bold"), fill="black")
            
            self.canvas.tag_bind(self.img_item, "<Button-1>", lambda e: self.lancer_le_de())
            self.canvas.tag_bind(self.text_item, "<Button-1>", lambda e: self.lancer_le_de())
            
        except Exception as e:
            print(f"[NOTE] Image absente : {e}")
            self.text_item = self.canvas.create_text(70, 70, text="🎲", font=("Segoe UI", 44), fill="#ffffff")
            self.canvas.tag_bind(self.text_item, "<Button-1>", lambda e: self.lancer_le_de())
        
        self.lbl_instruction = tk.Label(self, text="Cliquez sur le dé pour lancer", font=("Segoe UI", 9), bg="#22252a", fg="#86868B")
        self.lbl_instruction.pack(pady=(5, 0))
        
        self.lbl_dernier_lancer = tk.Label(self, text="", font=("Segoe UI", 9, "italic"), bg="#22252a", fg="#00e5ff")
        self.lbl_dernier_lancer.pack()

    def lancer_le_de(self):
        if self.en_cours: return
        self.en_cours = True
        self.lbl_dernier_lancer.config(text="")
        
        def anim_tick(i):
            if i < 8:
                r = random.randint(1, 20)
                # MODIFICATION : fill="black" pendant l'animation
                self.canvas.itemconfig(self.text_item, text=str(r), fill="black")
                self.after(60, anim_tick, i + 1)
            else:
                final = random.randint(1, 20)
                # MODIFICATION : fill="black" pour le résultat final
                self.canvas.itemconfig(self.text_item, text=str(final), fill="black")
                self.lbl_dernier_lancer.config(text=f"Résultat : {final}")
                self.en_cours = False
        
        anim_tick(0)
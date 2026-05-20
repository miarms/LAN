import tkinter as tk
import os
from PIL import Image, ImageTk 
import random 

# --- DICTIONNAIRES DE CRÉATION ---
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
    def __init__(self, parent, controller, inventory_module=None):
        super().__init__(parent, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.controller = controller
        self.inventory = inventory_module
        self.en_cours = False
        
        self.ca_cible = 12
        self.combat_callback = None # Permet au monstre d'écouter le résultat du dé
        
        self.lbl_title = tk.Label(self, text="DÉ D'ACTION", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0")
        self.lbl_title.pack(pady=(0, 10))
        
        self.canvas = tk.Canvas(self, width=140, height=140, bg="#22252a", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.canvas.config(cursor="hand2")
        
        chemin_img = os.path.join("client_src", "rsc", "img", "dice.png")
        try:
            img = Image.open(chemin_img).resize((140, 140), Image.Resampling.LANCZOS)
            self.tk_image_base = ImageTk.PhotoImage(img)
            self.img_item = self.canvas.create_image(70, 70, image=self.tk_image_base)
            self.text_item = self.canvas.create_text(70, 76, text="—", font=("Segoe UI", 22, "bold"), fill="black")
            self.canvas.tag_bind(self.img_item, "<Button-1>", lambda e: self.lancer_combat())
            self.canvas.tag_bind(self.text_item, "<Button-1>", lambda e: self.lancer_combat())
        except:
            self.text_item = self.canvas.create_text(70, 70, text="🎲", font=("Segoe UI", 44), fill="#ffffff")
            self.canvas.tag_bind(self.text_item, "<Button-1>", lambda e: self.lancer_combat())

        self.lbl_dernier_lancer = tk.Label(self, text="En attente...", font=("Segoe UI", 9), bg="#22252a", fg="#f1c40f")
        self.lbl_dernier_lancer.pack(pady=(5, 0))

    def lancer_combat(self):
        if self.en_cours: return
        self.en_cours = True
        
        d20 = random.randint(1, 20)
        bonus_attaque = self.inventory.bonus_equipement if self.inventory else 0
        total_toucher = d20 + bonus_attaque
        
        def anim_tick(i):
            if i < 8:
                self.canvas.itemconfig(self.text_item, text=str(random.randint(1, 20)), fill="black")
                self.after(50, anim_tick, i + 1)
            else:
                if d20 == 1:
                    self.canvas.itemconfig(self.text_item, text="1", fill="#ff5e57")
                    self.lbl_dernier_lancer.config(text="ÉCHEC CRITIQUE ! (1 naturel)", fg="#ff5e57")
                    self.en_cours = False
                    if self.combat_callback: self.combat_callback(False, 0)
                elif d20 == 20:
                    self.canvas.itemconfig(self.text_item, text="20", fill="#f1c40f")
                    jet_str, _ = self.analyser_arme()
                    nb_des, faces = self.decoder_jet(jet_str)
                    degats = sum(random.randint(1, faces) for _ in range(nb_des * 2)) + bonus_attaque
                    self.lbl_dernier_lancer.config(text=f"COUP CRITIQUE ! Dégâts: {degats}", fg="#f1c40f")
                    self.en_cours = False
                    if self.combat_callback: self.combat_callback(True, degats)
                else:
                    if total_toucher >= self.ca_cible:
                        self.canvas.itemconfig(self.text_item, text=str(d20), fill="#00ff66")
                        jet_str, _ = self.analyser_arme()
                        nb_des, faces = self.decoder_jet(jet_str)
                        degats = sum(random.randint(1, faces) for _ in range(nb_des)) + bonus_attaque
                        self.lbl_dernier_lancer.config(text=f"Touché ! (D20: {d20} + {bonus_attaque} vs CA {self.ca_cible})", fg="#00e5ff")
                        self.en_cours = False
                        if self.combat_callback: self.combat_callback(True, degats)
                    else:
                        self.canvas.itemconfig(self.text_item, text=str(d20), fill="#ff5e57")
                        self.lbl_dernier_lancer.config(text=f"Raté... (D20: {d20} + {bonus_attaque} vs CA {self.ca_cible})", fg="#ff5e57")
                        self.en_cours = False
                        if self.combat_callback: self.combat_callback(False, 0)
        anim_tick(0)

    def lancer_fuite(self, callback_fuite):
        """Lance un D20 pur pour la fuite."""
        if self.en_cours: return
        self.en_cours = True
        d20 = random.randint(1, 20)
        
        def anim_tick(i):
            if i < 8:
                self.canvas.itemconfig(self.text_item, text=str(random.randint(1, 20)), fill="black")
                self.after(50, anim_tick, i + 1)
            else:
                couleur = "#00ff66" if d20 >= 11 else "#ff5e57"
                self.canvas.itemconfig(self.text_item, text=str(d20), fill=couleur)
                self.lbl_dernier_lancer.config(text=f"Jet de fuite : {d20}", fg=couleur)
                self.en_cours = False
                callback_fuite(d20)
        anim_tick(0)

    def calculer_degats_bruts(self, jet_str):
        """Calcule les dégâts du monstre en silence"""
        nb_des, faces = self.decoder_jet(jet_str)
        return sum(random.randint(1, faces) for _ in range(nb_des))

    def analyser_arme(self):
        if not self.inventory: return "1d2", "Mains nues"
        for main in ["Main Droite", "Main Gauche"]:
            arme = self.inventory.slots.get(main)
            if arme and arme != "(Bloqué)" and arme in self.inventory.db_equip:
                return self.inventory.db_equip[arme].get("Jet_Des", "1d2"), arme
        return "1d2", "Mains nues"

    def decoder_jet(self, jet_str):
        try:
            if "d" in jet_str.lower():
                p = jet_str.lower().split("d")
                return int(p[0]), int(p[1])
        except: pass
        return 1, 2
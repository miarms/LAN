import tkinter as tk
import os

# Tentative d'import sécurisée de pandas
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Attention: Pandas n'est pas installé. L'inventaire sera vide.")

class InventoryModule(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#22252a")
        self.controller = controller
        self.mode = "EQUIPEMENT"
        
        # Initialisation des données
        self.slots = {"Tête": None, "Armure": None, "Main Droite": None, "Main Gauche": None, "Bottes": None}
        self.consommables = []
        self.equipements_db = None

        if HAS_PANDAS:
            csv_path = os.path.join("db", "Jeu Mia - Équipements.csv")
            if os.path.exists(csv_path):
                self.equipements_db = pd.read_csv(csv_path)
        
        # UI
        self.slot_frame = tk.Frame(self, bg="#22252a")
        self.slot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.btn_toggle = tk.Button(
            self, text="Voir Potions 🧪", font=("Segoe UI", 9),
            bg="#3a3f47", fg="#ffffff", relief=tk.FLAT, command=self.toggle_mode
        )
        self.btn_toggle.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        self.rafraichir_affichage()

    def toggle_mode(self):
        self.mode = "POTIONS" if self.mode == "EQUIPEMENT" else "EQUIPEMENT"
        self.btn_toggle.config(text="Voir Équipement 🛡️" if self.mode == "POTIONS" else "Voir Potions 🧪")
        self.rafraichir_affichage()

    def rafraichir_affichage(self):
        # Nettoyage
        for widget in self.slot_frame.winfo_children():
            widget.destroy()

        # Affichage
        if self.mode == "EQUIPEMENT":
            for slot_name, item_name in self.slots.items():
                frame = tk.Frame(self.slot_frame, bg="#2d3139", pady=5, padx=5)
                frame.pack(fill=tk.X, pady=2)
                tk.Label(frame, text=f"{slot_name} :", bg="#2d3139", fg="#a0a5b0").pack(side=tk.LEFT)
                val = item_name or "Vide"
                tk.Label(frame, text=val, bg="#2d3139", fg="#ffffff").pack(side=tk.RIGHT)
        else:
            tk.Label(self.slot_frame, text="POTIONS & DIVERS", bg="#22252a", fg="#00e5ff").pack(pady=5)
            for item in self.consommables:
                tk.Label(self.slot_frame, text=f"• {item}", bg="#22252a", fg="#ffffff").pack(anchor="w", padx=10)

    def equiper(self, slot, item_name):
        """Met à jour le slot et rafraîchit l'affichage"""
        if slot in self.slots:
            self.slots[slot] = item_name
            self.rafraichir_affichage()
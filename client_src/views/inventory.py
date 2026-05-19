import tkinter as tk

class InventoryModule(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#22252a")
        self.controller = controller
        
        # Mode : 'EQUIPEMENT' ou 'POTIONS'
        self.mode = "EQUIPEMENT"
        
        # Slots d'équipement par défaut
        self.slots = {"Tête": None, "Armure": None, "Arme": None, "Bottes": None}
        self.consommables = []

        # 1. ZONE SUPÉRIEURE : Squelette d'équipement
        self.slot_frame = tk.Frame(self, bg="#22252a")
        self.slot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 2. BOUTON DE BASCULE (Bas à droite)
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
        for widget in self.slot_frame.winfo_children():
            widget.destroy()

        if self.mode == "EQUIPEMENT":
            for slot_name in self.slots:
                frame = tk.Frame(self.slot_frame, bg="#2d3139", pady=5, padx=5)
                frame.pack(fill=tk.X, pady=2)
                tk.Label(frame, text=f"{slot_name} :", bg="#2d3139", fg="#a0a5b0").pack(side=tk.LEFT)
                val = self.slots[slot_name] or "Vide"
                tk.Label(frame, text=val, bg="#2d3139", fg="#ffffff").pack(side=tk.RIGHT)
        else:
            tk.Label(self.slot_frame, text="POTIONS & DIVERS", bg="#22252a", fg="#00e5ff").pack(pady=5)
            for item in self.consommables:
                tk.Label(self.slot_frame, text=f"• {item}", bg="#22252a", fg="#ffffff").pack(anchor="w", padx=10)

    # Méthodes pour le MJ
    def equiper(self, slot, item_name):
        if slot in self.slots:
            self.slots[slot] = item_name
            self.rafraichir_affichage()

    def ajouter_potion(self, item_name):
        self.consommables.append(item_name)
        self.rafraichir_affichage()
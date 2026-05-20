import tkinter as tk
import csv
import os

class InventoryModule(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#22252a")
        self.controller = controller
        
        self.bonus_equipement = 0
        self.slots = {"Tête": None, "Armure": None, "Main Droite": None, "Main Gauche": None, "Bottes": None}
        self.consommables = []

        self.db_equip = {}
        self.db_conso = {}
        
        self.infobulle_fenetre = None 
        
        self.charger_donnees_csv()

        # Zone d'affichage unique
        self.display_frame = tk.Frame(self, bg="#22252a")
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.rafraichir_affichage()

    def charger_donnees_csv(self):
        # 1. Équipements
        chemin_equip = os.path.join("db", "Jeu Mia - Équipements.csv")
        if os.path.exists(chemin_equip):
            with open(chemin_equip, mode='r', encoding='utf-8-sig') as f:
                lignes = f.readlines()
            if lignes:
                separateur = ';' if ';' in lignes[0] else ','
                reader = csv.DictReader(lignes, delimiter=separateur)
                for row in reader:
                    cle_nom = next((k for k in row.keys() if k and k.strip() == "Nom"), None)
                    if cle_nom and row[cle_nom]:
                        self.db_equip[row[cle_nom].strip()] = row

        # 2. Marchands (Consommables)
        chemin_conso = os.path.join("db", "Jeu Mia - Marchants.csv")
        if os.path.exists(chemin_conso):
            with open(chemin_conso, mode='r', encoding='utf-8-sig') as f:
                lignes = f.readlines()
            if lignes:
                separateur = ';' if ';' in lignes[0] else ','
                reader = csv.DictReader(lignes, delimiter=separateur)
                for row in reader:
                    cle_nom = next((k for k in row.keys() if k and k.strip() == "Nom"), None)
                    if cle_nom and row[cle_nom]:
                        self.db_conso[row[cle_nom].strip()] = row

    # ==========================================
    # LOGIQUE D'ÉQUIPEMENT ET STATISTIQUES
    # ==========================================
    def equiper_objet(self, nom_objet):
        if nom_objet not in self.db_equip:
            return

        donnees = self.db_equip[nom_objet]
        emplacement = donnees["Emplacement"]
        
        if emplacement == "Arme":
            mains = donnees["Mains_Requises"]
            if mains == "2":
                self.slots["Main Droite"] = nom_objet
                self.slots["Main Gauche"] = "(Bloqué)"
            else:
                if self.slots["Main Droite"] is None or self.slots["Main Droite"] == "(Bloqué)":
                    self.slots["Main Droite"] = nom_objet
                else:
                    self.slots["Main Gauche"] = nom_objet
        elif emplacement in self.slots:
            self.slots[emplacement] = nom_objet
            
        self.calculer_bonus_total()
        self.rafraichir_affichage()

    def calculer_bonus_total(self):
        total = 0
        for slot_name, nom_objet in self.slots.items():
            if nom_objet and nom_objet != "(Bloqué)" and nom_objet in self.db_equip:
                bonus_str = self.db_equip[nom_objet].get("Bonus_Fixe", "0")
                try:
                    total += int(bonus_str)
                except ValueError:
                    pass
        self.bonus_equipement = total

    def ajouter_consommable(self, nom_objet):
        if nom_objet in self.db_conso:
            self.consommables.append(nom_objet)
            self.rafraichir_affichage()

    # ==========================================
    # LOGIQUE DES INFOBULLES
    # ==========================================
    def afficher_infobulle(self, event, nom_objet):
        self.cacher_infobulle(None)
        if nom_objet == "(Bloqué)" or not nom_objet or nom_objet == "Vide":
            return
            
        texte = self.generer_texte_infobulle(nom_objet)
        if not texte: return

        x, y = event.x_root + 15, event.y_root + 15
        self.infobulle_fenetre = tk.Toplevel(self)
        self.infobulle_fenetre.wm_overrideredirect(True)
        self.infobulle_fenetre.wm_geometry(f"+{x}+{y}")
        
        lbl = tk.Label(self.infobulle_fenetre, text=texte, justify=tk.LEFT, 
                       bg="#1a1c20", fg="#ffffff", relief=tk.SOLID, bd=1, 
                       highlightbackground="#00e5ff", highlightthickness=1,
                       font=("Segoe UI", 9), padx=10, pady=8, wraplength=250)
        lbl.pack()

    def cacher_infobulle(self, event):
        if self.infobulle_fenetre:
            self.infobulle_fenetre.destroy()
            self.infobulle_fenetre = None

    def generer_texte_infobulle(self, nom_objet):
        if nom_objet in self.db_equip:
            d = self.db_equip[nom_objet]
            texte = f"{d['Nom'].upper()}\n"
            texte += f"[{d['Emplacement']}]\n"
            if d['Emplacement'] == "Arme":
                texte += f"Mains : {d['Mains_Requises']} | Type : {d.get('Type_Degats', 'Aucun')}\n"
                texte += f"Dégâts : {d.get('Jet_Des', '0')} (+{d.get('Bonus_Fixe', '0')})\n"
            else:
                texte += f"Bonus : +{d.get('Bonus_Fixe', '0')}\n"
            if d.get('Description'):
                texte += f"\n\"{d['Description']}\""
            return texte
            
        elif nom_objet in self.db_conso:
            d = self.db_conso[nom_objet]
            texte = f"{d['Nom'].upper()}\n"
            texte += f"[{d.get('Categorie', 'Objet')}]\n"
            texte += f"Effet : {d.get('Effet_Principal', '-')} ({d.get('Valeur', '0')})\n"
            if d.get('Description'):
                texte += f"\n\"{d['Description']}\""
            return texte
        return ""

    # ==========================================
    # GESTION VISUELLE ÉPURÉE
    # ==========================================
    def rafraichir_affichage(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # 1. SECTION ÉQUIPEMENT
        tk.Label(self.display_frame, text="SQUELETTE D'ÉQUIPEMENT", bg="#22252a", fg="#a0a5b0", font=("Segoe UI", 8, "bold")).pack(pady=(0, 5))
        
        for slot_name in self.slots:
            frame = tk.Frame(self.display_frame, bg="#2d3139", pady=3, padx=5)
            frame.pack(fill=tk.X, pady=1)
            
            tk.Label(frame, text=f"{slot_name}", bg="#2d3139", fg="#ffffff", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            
            val = self.slots[slot_name]
            couleur = "#00e5ff" if val and val != "(Bloqué)" else "#e74c3c" if val == "(Bloqué)" else "#86868B"
            texte_affiche = val if val else "Vide"
            
            lbl_val = tk.Label(frame, text=texte_affiche, bg="#2d3139", fg=couleur, font=("Segoe UI", 9))
            lbl_val.pack(side=tk.RIGHT)
            
            if val and val != "(Bloqué)":
                lbl_val.bind("<Enter>", lambda e, n=val: self.afficher_infobulle(e, n))
                lbl_val.bind("<Leave>", self.cacher_infobulle)
            
        # Puissance Totale
        tk.Label(
            self.display_frame, text=f"⚔️ PUISSANCE BONUS : +{self.bonus_equipement}", 
            bg="#22252a", fg="#f1c40f", font=("Segoe UI", 10, "bold")
        ).pack(pady=(5, 10))
        
        # Ligne de séparation
        tk.Frame(self.display_frame, height=1, bg="#3a3f47").pack(fill=tk.X, pady=5)

        # 2. SECTION POTIONS / SAC
        tk.Label(self.display_frame, text="SAC À DOS", bg="#22252a", fg="#a0a5b0", font=("Segoe UI", 8, "bold")).pack(pady=(5, 5))
        
        if not self.consommables:
            tk.Label(self.display_frame, text="Vide...", bg="#22252a", fg="#86868B", font=("Segoe UI", 9, "italic")).pack(pady=5)
        else:
            for item in self.consommables:
                lbl_item = tk.Label(self.display_frame, text=f"• {item}", bg="#22252a", fg="#ffffff", font=("Segoe UI", 9))
                lbl_item.pack(anchor="w", padx=10, pady=1)
                
                lbl_item.bind("<Enter>", lambda e, n=item: self.afficher_infobulle(e, n))
                lbl_item.bind("<Leave>", self.cacher_infobulle)
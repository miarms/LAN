# client_src/views/monster.py
import tkinter as tk
import csv
import os
import random

class MonsterCard(tk.Frame):
    def __init__(self, parent, controller, dice_module):
        super().__init__(parent, bg="#22252a")
        self.controller = controller
        self.dice_module = dice_module  # On a besoin du dé pour lui envoyer la CA !
        self.monstres = []
        
        self.charger_donnees_csv()

        self.lbl_title = tk.Label(self, text="", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ff5e57")
        self.lbl_title.pack(pady=(0, 15))

        self.card_content = tk.Frame(self, bg="#22252a")
        self.card_content.pack(fill=tk.BOTH, expand=True)

        self.buttons_container = tk.Frame(self, bg="#22252a")
        self.buttons_container.pack(fill=tk.X, pady=5)

    def charger_donnees_csv(self):
        chemin_csv = os.path.join("db", "Jeu Mia - Monstres.csv")
        print(f"[DEBUG MONSTRES] Tentative de lecture de : {chemin_csv}")
        
        if not os.path.exists(chemin_csv):
            print("[ERREUR] Le fichier est introuvable !")
            return
            
        lignes_nettoyees = []
        
        with open(chemin_csv, mode='r', encoding='utf-8-sig') as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne: 
                    continue
                
                # 🛠️ CORRECTION MAGIQUE : On retire la "coquille" de guillemets géants
                if ligne.startswith('"') and ligne.endswith('"') and ligne.count('"') >= 2:
                    ligne = ligne[1:-1] # On coupe le 1er et dernier guillemet
                    ligne = ligne.replace('""', '"') # On répare les guillemets intérieurs
                
                lignes_nettoyees.append(ligne)
                
        if not lignes_nettoyees:
            print("[ERREUR] Le fichier est vide !")
            return
            
        separateur = ';' if ';' in lignes_nettoyees[0] else ','
        reader = csv.DictReader(lignes_nettoyees, delimiter=separateur)
        
        for row in reader:
            # Recherche souple de la colonne "Nom"
            cle_nom = next((k for k in row.keys() if k and "nom" in k.lower().strip()), None)
            if cle_nom and row.get(cle_nom):
                self.monstres.append(row)
                
        print(f"[DEBUG MONSTRES] SUCCÈS ! J'ai chargé {len(self.monstres)} monstres prêts au combat.")

    def generer_rencontre(self, nom_specifique=None):
        """Pioche un monstre et l'affiche à l'écran."""
        # On nettoie la zone avant d'afficher un nouveau monstre
        for widget in self.card_content.winfo_children(): widget.destroy()
        for widget in self.buttons_container.winfo_children(): widget.destroy()

        if not self.monstres:
            tk.Label(self.card_content, text="Erreur : Aucun monstre trouvé dans la BDD.", fg="#ff5e57", bg="#22252a").pack()
            return

        # Sélection du monstre
        if nom_specifique:
            monstre = next((m for m in self.monstres if m.get(list(m.keys())[0], "").strip() == nom_specifique), None)
            if not monstre:
                monstre = random.choice(self.monstres)
        else:
            monstre = random.choice(self.monstres)

        # Extraction des données
        keys = list(monstre.keys())
        nom = monstre.get(keys[0], "Inconnu")
        ca = monstre.get("CA", "10")
        pv = monstre.get("PV", "10")
        degats = monstre.get("Degats", "1d3")
        desc = monstre.get("Description", "")

        # Mise à jour du titre
        self.lbl_title.config(text=f"⚠️ UN MONSTRE APPARAÎT : {nom.upper()} ⚠️")

        # Affichage de la fiche
        fiche = f"[{nom.upper()}]\n\n"
        fiche += f"❤️ PV : {pv}   |   🛡️ CA : {ca}\n"
        fiche += f"⚔️ Dégâts : {degats}\n\n"
        fiche += f"\"{desc}\""
        
        tk.Label(
            self.card_content, text=fiche, font=("Segoe UI", 12, "bold"),
            bg="#2d3139", fg="#ffffff", width=32, height=15, relief=tk.FLAT, wraplength=280, justify="center"
        ).pack(pady=10)

        # 🔥 LIAISON MAGIQUE : On transmet la CA de ce monstre au module de dés
        try:
            self.dice_module.ca_cible = int(ca)
        except ValueError:
            pass

        # Création des boutons d'action
        btn_combattre = tk.Button(
            self.buttons_container, text="⚔️ Combattre (Lancez le dé 🎲)", font=("Segoe UI", 11, "bold"),
            bg="#ff5e57", fg="#ffffff", activebackground="#ff3f34", activeforeground="#ffffff",
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2", 
            command=lambda: self.dice_module.lancer_combat()
        )
        btn_combattre.pack(fill=tk.X, pady=5)
        
        btn_fuir = tk.Button(
            self.buttons_container, text="🏃 Tenter de fuir", font=("Segoe UI", 11),
            bg="#2d3139", fg="#a0a5b0", activebackground="#3a3f47", activeforeground="#ffffff",
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2", 
            command=lambda: print("Test de fuite...")
        )
        btn_fuir.pack(fill=tk.X, pady=5)
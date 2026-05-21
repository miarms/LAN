# client_src/views/monster.py
import tkinter as tk
import csv
import os
import random

class MonsterCard(tk.Frame):
    def __init__(self, parent, controller, dice_module, game_view):
        super().__init__(parent, bg="#22252a")
        self.controller = controller
        self.dice_module = dice_module
        self.game_view = game_view
        self.monstres = []
        self.en_combat = False
        
        self.charger_donnees_csv()

        self.lbl_title = tk.Label(self, text="", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ff5e57")
        self.lbl_title.pack(pady=(0, 10))

        self.fiche_frame = tk.Frame(self, bg="#2d3139", relief=tk.FLAT, padx=15, pady=15)
        self.fiche_frame.pack(pady=5)
        
        self.lbl_nom = tk.Label(self.fiche_frame, text="", font=("Segoe UI", 14, "bold"), bg="#2d3139", fg="#ffffff")
        self.lbl_nom.pack()
        
        self.lbl_stats = tk.Label(self.fiche_frame, text="", font=("Segoe UI", 12, "bold"), bg="#2d3139", fg="#a0a5b0")
        self.lbl_stats.pack(pady=5)
        
        self.lbl_desc = tk.Label(self.fiche_frame, text="", font=("Segoe UI", 10, "italic"), bg="#2d3139", fg="#ffffff", wraplength=260, justify="center")
        self.lbl_desc.pack(pady=10)

        self.lbl_feedback = tk.Label(self, text="À vous de jouer !", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#00e5ff")
        self.lbl_feedback.pack(pady=5)

        self.buttons_container = tk.Frame(self, bg="#22252a")
        self.buttons_container.pack(fill=tk.X, pady=5)

    def charger_donnees_csv(self):
        chemin_csv = os.path.join("db", "Jeu Mia - Monstres.csv")
        if not os.path.exists(chemin_csv): return
        lignes_nettoyees = []
        with open(chemin_csv, mode='r', encoding='utf-8-sig') as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne: continue
                if ligne.startswith('"') and ligne.endswith('"') and ligne.count('"') >= 2:
                    ligne = ligne[1:-1]
                    ligne = ligne.replace('""', '"')
                lignes_nettoyees.append(ligne)
        if not lignes_nettoyees: return
        separateur = ';' if ';' in lignes_nettoyees[0] else ','
        reader = csv.DictReader(lignes_nettoyees, delimiter=separateur)
        for row in reader:
            cle_nom = next((k for k in row.keys() if k and "nom" in k.lower().strip()), None)
            if cle_nom and row.get(cle_nom):
                self.monstres.append(row)

    # =========================================================
    # 🔥 LA FONCTION QUI TE MANQUAIT EST LÀ 🔥
    # =========================================================
    def generer_rencontre_via_serveur(self, nom, ca, pv, degats, desc):
        """Reçoit l'ordre du MJ (serveur) et affiche le monstre"""
        self.nom = nom
        self.ca = int(ca)
        self.pv_max = int(pv)
        self.pv_actuel = self.pv_max
        self.degats_str = degats
        self.desc = desc
        self.en_combat = True
        
        # Mise à jour de l'UI
        self.lbl_title.config(text="⚠️ UN MONSTRE APPARAÎT ⚠️", fg="#ff5e57")
        self.lbl_feedback.config(text="C'est votre tour ! Attaquez !", fg="#00e5ff")
        
        self.maj_ui_fiche()
        self.creer_boutons_combat()
        
        # Le monstre prend le contrôle du Dé !
        self.dice_module.ca_cible = self.ca
        self.dice_module.combat_callback = self.resolution_tour_joueur

    # =========================================================
    # LE RESTE DU MOTEUR DE COMBAT
    # =========================================================
    def maj_ui_fiche(self):
        self.lbl_nom.config(text=f"[{self.nom.upper()}]")
        self.lbl_stats.config(text=f"❤️ PV : {self.pv_actuel} / {self.pv_max}   |   🛡️ CA : {self.ca}")
        self.lbl_desc.config(text=f"⚔️ Dégâts monstre : {self.degats_str}\n\n\"{self.desc}\"")

    def creer_boutons_combat(self):
        for w in self.buttons_container.winfo_children(): w.destroy()
        
        btn_combattre = tk.Button(
            self.buttons_container, text="⚔️ Attaquer (D20 + Dégâts)", font=("Segoe UI", 11, "bold"),
            bg="#ff5e57", fg="#ffffff", activebackground="#ff3f34", activeforeground="#ffffff",
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2", command=self.lancer_attaque
        )
        btn_combattre.pack(fill=tk.X, pady=5)
        
        btn_fuir = tk.Button(
            self.buttons_container, text="🏃 Tenter de fuir (D20 >= 11)", font=("Segoe UI", 11),
            bg="#2d3139", fg="#a0a5b0", activebackground="#3a3f47", activeforeground="#ffffff",
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2", command=self.tenter_fuite
        )
        btn_fuir.pack(fill=tk.X, pady=5)
        
    def lancer_attaque(self):
        if not self.en_combat: return
        self.lbl_feedback.config(text="Vous attaquez...", fg="#ffffff")
        for w in self.buttons_container.winfo_children(): w.config(state=tk.DISABLED)
        self.dice_module.lancer_combat()
        
    def resolution_tour_joueur(self, touche, degats_infliges):
        if not self.en_combat: return
        
        if touche:
            self.pv_actuel -= degats_infliges
            if self.pv_actuel <= 0:
                self.pv_actuel = 0
                self.maj_ui_fiche()
                self.victoire()
                return
            else:
                self.maj_ui_fiche()
                self.lbl_feedback.config(text=f"Touché ! (-{degats_infliges} PV au monstre). Au tour de l'ennemi...", fg="#00ff66")
        else:
            self.lbl_feedback.config(text="Votre attaque rate ! Le monstre riposte...", fg="#ff5e57")
            
        # Après ton attaque, on attend 2 secondes puis c'est au monstre
        self.after(2000, self.tour_du_monstre)

    def tour_du_monstre(self):
        if not self.en_combat: return
        degats_subis = self.dice_module.calculer_degats_bruts(self.degats_str)
        self.lbl_feedback.config(text=f"🩸 {self.nom} vous frappe et vous perdez {degats_subis} PV !", fg="#ff5e57")
        
        # Fait perdre des PV au joueur sur la jauge en haut
        self.game_view.subir_degats(degats_subis) 
        
        # On redonne la main au joueur
        for w in self.buttons_container.winfo_children(): w.config(state=tk.NORMAL)
        
    def tenter_fuite(self):
        if not self.en_combat: return
        self.lbl_feedback.config(text="Vous courez ! Lancement du dé...", fg="#ffffff")
        for w in self.buttons_container.winfo_children(): w.config(state=tk.DISABLED)
        self.dice_module.lancer_fuite(callback=self.resolution_fuite)
        
    def resolution_fuite(self, d20):
        if d20 >= 11:
            self.lbl_feedback.config(text=f"Fuite réussie ! (D20: {d20})", fg="#00ff66")
            self.en_combat = False
            # On termine la rencontre et le serveur piochera une autre carte
            self.after(2000, self.game_view.terminer_rencontre)
        else:
            self.lbl_feedback.config(text=f"Fuite ratée ! (D20: {d20}). Le monstre vous attrape !", fg="#ff5e57")
            self.after(2000, self.tour_du_monstre)
            
    def victoire(self):
        self.en_combat = False
        self.lbl_title.config(text="🎉 VICTOIRE ! 🎉", fg="#f1c40f")
        self.lbl_feedback.config(text=f"{self.nom} a été vaincu !", fg="#f1c40f")
        
        for w in self.buttons_container.winfo_children(): w.destroy()
        
        # Ce bouton envoie "FIN_COMBAT" au serveur via terminer_rencontre
        btn_suite = tk.Button(
            self.buttons_container, text="Continuer l'Aventure ➡️", font=("Segoe UI", 11, "bold"),
            bg="#00ff66", fg="#1a1c20", activebackground="#00cc55", activeforeground="#1a1c20",
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2", command=self.game_view.terminer_rencontre
        )
        btn_suite.pack(fill=tk.X, pady=5)
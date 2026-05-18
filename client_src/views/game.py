import tkinter as tk

class GameView(tk.Frame):
    def __init__(self, parent, controller):
        # Fond Anthracite Pur pour toute la fenêtre
        super().__init__(parent, bg="#1a1c20")
        self.controller = controller
        
        # Max théorique pour le calcul visuel des barres
        self.max_pv = 150
        self.max_en = 150
        
        # --- 1. BANDEAU SUPÉRIEUR (Tableau de bord Anthracite) ---
        self.top_bar = tk.Frame(self, bg="#22252a", padx=20, pady=15)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        
        # Pseudo du Joueur (Blanc épuré)
        self.lbl_player = tk.Label(self.top_bar, text="Aventurier", font=("Segoe UI", 13, "bold"), bg="#22252a", fg="#ffffff")
        self.lbl_player.pack(side=tk.LEFT, padx=(0, 30))
        
        # --- SECTION JAUGE PV ---
        tk.Label(self.top_bar, text="PV :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        
        # Conteneur fond de la jauge PV (Gris foncé)
        self.pv_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.pv_bar_bg.pack(side=tk.LEFT, padx=5)
        self.pv_bar_bg.pack_propagate(False)
        
        # Remplissage de la jauge PV (Vert Néon du plus bel effet)
        self.pv_bar_fill = tk.Frame(self.pv_bar_bg, bg="#00ff66")
        self.pv_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1) # Remplissage initial
        
        # Texte numérique PV
        self.pv_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.pv_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        # --- SECTION JAUGE ÉNERGIE ---
        tk.Label(self.top_bar, text="ÉNERGIE :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        
        # Conteneur fond de la jauge Énergie
        self.en_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.en_bar_bg.pack(side=tk.LEFT, padx=5)
        self.en_bar_bg.pack_propagate(False)
        
        # Remplissage de la jauge Énergie (Cyan/Bleu Électrique)
        self.en_bar_fill = tk.Frame(self.en_bar_bg, bg="#00e5ff")
        self.en_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1)
        
        # Texte numérique Énergie
        self.en_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.en_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        # Portefeuille (À droite, Or/Jaune)
        self.pieces_lbl = tk.Label(self.top_bar, text="0 🪙", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ffd32a")
        self.pieces_lbl.pack(side=tk.RIGHT, padx=10)

        # Fine ligne de démarcation sous le bandeau
        sep = tk.Frame(self, height=1, bg="#2d3139")
        sep.pack(fill=tk.X, side=tk.TOP)

        # --- CONTENEUR CENTRAL SPLIT ---
        self.main_area = tk.Frame(self, bg="#1a1c20")
        self.main_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # --- 2. JOURNAL DE NARRATION (GAUCHE) ---
        self.left_panel = tk.Frame(self.main_area, bg="#22252a", padx=15, pady=15)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(self.left_panel, text="JOURNAL DU DONJON", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", padx=5, pady=(0, 10))
        
        # Zone de texte sombre, écriture blanche, curseur blanc
        self.text_area = tk.Text(
            self.left_panel, wrap=tk.WORD, state=tk.DISABLED, 
            bg="#22252a", fg="#ffffff", font=("Segoe UI", 11),
            bd=0, highlightthickness=0, insertbackground="white"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- 3. PANNEAU DES BOUTONS D'ACTION (DROITE) ---
        self.right_panel = tk.Frame(self.main_area, bg="#22252a", padx=25, pady=25, width=320)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(15, 0))
        self.right_panel.pack_propagate(False)
        
        self.lbl_action_title = tk.Label(self.right_panel, text="DÉCISION REQUISE", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#a0a5b0")
        self.lbl_action_title.pack(anchor="w", pady=(0, 20))
        
        self.buttons_container = tk.Frame(self.right_panel, bg="#22252a")
        self.buttons_container.pack(fill=tk.X, expand=True, anchor="n")

    # --- MÉTHODES DE MISE À JOUR ---
    def ajouter_narration(self, texte):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, texte + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def mettre_a_jour_stats(self, pv, energie, pieces):
        """Met à jour les chiffres ET étire dynamiquement les barres de progression"""
        val_pv = int(pv)
        val_en = int(energie)
        
        # Mise à jour des textes
        self.pv_lbl.config(text=str(val_pv))
        self.en_lbl.config(text=str(val_en))
        self.pieces_lbl.config(text=f"{pieces} 🪙")
        
        # Calcul des ratios pour le remplissage des barres (capé entre 0.0 et 1.0)
        ratio_pv = max(0.0, min(val_pv / self.max_pv, 1.0))
        ratio_en = max(0.0, min(val_en / self.max_en, 1.0))
        
        # Redimensionnement des rectangles colorés
        self.pv_bar_fill.place_configure(relwidth=ratio_pv)
        self.en_bar_fill.place_configure(relwidth=ratio_en)

    def configurer_nom_joueur(self, pseudo, race, classe):
        self.lbl_player.config(text=f"{pseudo} ({race} {classe})")

    def generer_choix_boutons(self, titre_action, liste_options):
        """Génère des boutons sombres et épurés de style gaming premium"""
        for widget in self.buttons_container.winfo_children():
            widget.destroy()
            
        self.lbl_action_title.config(text=titre_action.upper(), fg="#a0a5b0")
        
        for idx, option in enumerate(liste_options, 1):
            btn = tk.Button(
                self.buttons_container, text=f"{idx}. {option}", font=("Segoe UI", 11),
                bg="#2d3139", fg="#ffffff", activebackground="#3a3f47", activeforeground="#ffffff",
                relief=tk.FLAT, bd=0, pady=12, anchor="w", padx=15, cursor="hand2"
            )
            btn.config(command=lambda b_id=idx: self.clic_action(b_id))
            btn.pack(fill=tk.X, pady=5)

    def clic_action(self, bouton_id):
        for widget in self.buttons_container.winfo_children():
            widget.config(state=tk.DISABLED)
        self.lbl_action_title.config(text="TRANSMISSION...", fg="#00e5ff")
        self.controller.envoyer_choix_action(bouton_id)
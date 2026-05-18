import tkinter as tk

# Références pour calculer les statistiques de l'infobulle en local
RACES = {
    "Boomer":     {"FOR": 11, "DEX": 7,  "CON": 13, "INT": 8,  "SAG": 10, "CHA": 11, "PV": 100, "ENERGIE": 100, "PIECES": 130},
    "Gen Z":      {"FOR": 8,  "DEX": 14, "CON": 8,  "INT": 13, "SAG": 8,  "CHA": 10, "PV": 90,  "ENERGIE": 110, "PIECES": 100},
    "Provincial": {"FOR": 14, "DEX": 8,  "CON": 14, "INT": 9,  "SAG": 9,  "CHA": 6,  "PV": 110, "ENERGIE": 100, "PIECES": 100},
    "Urbain":     {"FOR": 10, "DEX": 15, "CON": 9,  "INT": 10, "SAG": 6,  "CHA": 10, "PV": 100, "ENERGIE": 90,  "PIECES": 100},
    "Tanguy":     {"FOR": 9,  "DEX": 12, "CON": 10, "INT": 14, "SAG": 8,  "CHA": 7,  "PV": 100, "ENERGIE": 100, "PIECES": 60},
    "Karen":      {"FOR": 10, "DEX": 9,  "CON": 12, "INT": 6,  "SAG": 6,  "CHA": 17, "PV": 100, "ENERGIE": 100, "PIECES": 110},
    "Chill Guy":  {"FOR": 8,  "DEX": 6,  "CON": 13, "INT": 10, "SAG": 15, "CHA": 8,  "PV": 110, "ENERGIE": 90,  "PIECES": 100}
}

CLASSES = {
    "Syndicaliste":    {"FOR": 2, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 20,  "ENERGIE": -10, "PIECES": 0},
    "Influenceur":     {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 2, "PV": 0,   "ENERGIE": 0,   "PIECES": 10},
    "Gourou":          {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 2, "CHA": 0, "PV": 0,   "ENERGIE": 10,  "PIECES": 0},
    "Bobo Ecolo":      {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 2, "CHA": 0, "PV": 10,  "ENERGIE": 0,   "PIECES": -10},
    "Fils de":         {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 2, "PV": 0,   "ENERGIE": 0,   "PIECES": 30},
    "Cadre Superieur": {"FOR": 0, "DEX": 0, "CON": 2, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10,  "ENERGIE": 10,  "PIECES": 0},
    "Consultant":      {"FOR": 0, "DEX": 0, "CON": 0, "INT": 2, "SAG": 0, "CHA": 0, "PV": -10, "ENERGIE": 20,  "PIECES": 0},
    "Adepte de Yoga":  {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 0,   "ENERGIE": 20,  "PIECES": -10},
    "Stagiaire":       {"FOR": 0, "DEX": 0, "CON": 0, "INT": 2, "SAG": 0, "CHA": 0, "PV": 0,   "ENERGIE": 0,   "PIECES": -20},
    "Leche-botte":     {"FOR": 0, "DEX": 0, "CON": 2, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10,  "ENERGIE": 0,   "PIECES": 10},
    "Teletravailleur": {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10,  "ENERGIE": 0,   "PIECES": 0},
    "Commercial":      {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 0,   "ENERGIE": -10, "PIECES": 20}
}

class GameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1c20")
        self.controller = controller
        
        self.max_pv = 150
        self.max_en = 150
        
        # Variables pour stocker l'infobulle et les caractéristiques
        self.tooltip = None
        self.stats_completes = {}
        
        # --- 1. BANDEAU SUPÉRIEUR ---
        self.top_bar = tk.Frame(self, bg="#22252a", padx=20, pady=15)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        
        # Pseudo du Joueur (On ajoute un curseur d'aide pour indiquer qu'on peut le survoler)
        self.lbl_player = tk.Label(self.top_bar, text="Aventurier", font=("Segoe UI", 13, "bold"), bg="#22252a", fg="#ffffff", cursor="question_arrow")
        self.lbl_player.pack(side=tk.LEFT, padx=(0, 30))
        
        # --- LIAISON DES ÉVÉNEMENTS DE SURVOL ---
        self.lbl_player.bind("<Enter>", self.afficher_infobulle)
        self.lbl_player.bind("<Leave>", self.masquer_infobulle)
        
        # --- SECTION JAUGE PV ---
        tk.Label(self.top_bar, text="PV :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        self.pv_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.pv_bar_bg.pack(side=tk.LEFT, padx=5)
        self.pv_bar_bg.pack_propagate(False)
        self.pv_bar_fill = tk.Frame(self.pv_bar_bg, bg="#00ff66")
        self.pv_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1)
        self.pv_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.pv_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        # --- SECTION JAUGE ÉNERGIE ---
        tk.Label(self.top_bar, text="ÉNERGIE :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        self.en_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.en_bar_bg.pack(side=tk.LEFT, padx=5)
        self.en_bar_bg.pack_propagate(False)
        self.en_bar_fill = tk.Frame(self.en_bar_bg, bg="#00e5ff")
        self.en_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1)
        self.en_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.en_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        # Portefeuille
        self.pieces_lbl = tk.Label(self.top_bar, text="0 🪙", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ffd32a")
        self.pieces_lbl.pack(side=tk.RIGHT, padx=10)

        # Ligne de démarcation
        sep = tk.Frame(self, height=1, bg="#2d3139")
        sep.pack(fill=tk.X, side=tk.TOP)

        # --- CONTENEUR CENTRAL SPLIT ---
        self.main_area = tk.Frame(self, bg="#1a1c20")
        self.main_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # --- 2. JOURNAL DE NARRATION (GAUCHE) ---
        self.left_panel = tk.Frame(self.main_area, bg="#22252a", padx=15, pady=15)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(self.left_panel, text="JOURNAL DU DONJON", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", padx=5, pady=(0, 10))
        
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

    # --- MÉTHODES DE L'INFOBULLE (HOVER COMPOSANT) ---
    def afficher_infobulle(self, event):
        """Crée un encadré flottant anthracite pour afficher les caractéristiques"""
        if not self.stats_completes: return
        
        # Création de la fenêtre éphémère borderless
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.config(bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        
        # Positionnement automatique juste en dessous du curseur de la souris
        x = event.x_root + 15
        y = event.y_root + 15
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Titre de l'encadré
        tk.Label(self.tooltip, text="CARACTÉRISTIQUES", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#00e5ff").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        # Boucle d'affichage de la grille des statistiques
        for idx, (stat, val) in enumerate(self.stats_completes.items(), 1):
            tk.Label(self.tooltip, text=stat, font=("Segoe UI", 10), bg="#22252a", fg="#a0a5b0").grid(row=idx, column=0, sticky="w", pady=2)
            tk.Label(self.tooltip, text=str(val), font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#ffffff").grid(row=idx, column=1, sticky="e", padx=(25, 0), pady=2)

    def masquer_infobulle(self, event):
        """Détruit l'encadré dès que la souris quitte la zone du nom"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    # --- MÉTHODES DE MISE À JOUR ---
    def ajouter_narration(self, texte):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, texte + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def mettre_a_jour_stats(self, pv, energie, pieces):
        val_pv = int(pv)
        val_en = int(energie)
        
        self.pv_lbl.config(text=str(val_pv))
        self.en_lbl.config(text=str(val_en))
        self.pieces_lbl.config(text=f"{pieces} 🪙")
        
        ratio_pv = max(0.0, min(val_pv / self.max_pv, 1.0))
        ratio_en = max(0.0, min(val_en / self.max_en, 1.0))
        
        self.pv_bar_fill.place_configure(relwidth=ratio_pv)
        self.en_bar_fill.place_configure(relwidth=ratio_en)

    def configurer_nom_joueur(self, pseudo, race, classe):
        """Affiche le nom et pré-calcule les stats pour l'infobulle"""
        self.lbl_player.config(text=f"{pseudo} ({race} {classe})")
        
        # Calcul et enregistrement des statistiques combinées pour l'infobulle
        if race in RACES and classe in CLASSES:
            self.stats_completes = {
                "FORCE (FOR)":     RACES[race]["FOR"] + CLASSES[classe]["FOR"],
                "DEXTÉRITÉ (DEX)": RACES[race]["DEX"] + CLASSES[classe]["DEX"],
                "CONSTITUTION (CON)": RACES[race]["CON"] + CLASSES[classe]["CON"],
                "INTELLIGENCE (INT)": RACES[race]["INT"] + CLASSES[classe]["INT"],
                "SAGESSE (SAG)":   RACES[race]["SAG"] + CLASSES[classe]["SAG"],
                "CHARISME (CHA)":  RACES[race]["CHA"] + CLASSES[classe]["CHA"]
            }

    def generer_choix_boutons(self, titre_action, liste_options):
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
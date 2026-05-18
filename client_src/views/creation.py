import tkinter as tk
from tkinter import ttk

RACES = {
    "Boomer":     {"FOR": 11, "DEX": 7,  "CON": 13, "INT": 8,  "SAG": 10, "CHA": 11, "PV": 100, "ENERGIE": 100, "PIECES": 130},
    "Gen Z":      {"FOR": 8,  "DEX": 14, "CON": 8,  "INT": 13, "SAG": 8,  "CHA": 10, "PV": 90,  "ENERGIE": 110, "PIECES": 100},
    "Provincial": {"FOR": 14, "DEX": 8,  "CON": 14, "INT": 9,  "SAG": 9,  "CHA": 6,  "PV": 110, "ENERGIE": 100, "PIECES": 100},
    "Urbain":     {"FOR": 10, "DEX": 15, "CON": 9,  "INT": 10, "SAG": 6,  "CHA": 10, "PV": 100, "ENERGIE": 90,  "PIECES": 100},
    "Tanguy":     {"FOR": 9,  "DEX": 12, "CON": 10, "INT": 14, "SAG": 8,  "CHA": 7,  "PV": 100, "ENERGIE": 100, "PIECES": 60},
    "Karen":      {"FOR": 10, "DEX": 9,  "CON": 12, "INT": 6,  "SAG": 6,  "CHA": 17, "PV": 100, "ENERGIE": 100, "PIECES": 110},
    "Chill Guy":  {"FOR": 8,  "DEX": 6,  "CON": 13, "INT": 10, "SAG": 15, "CHA": 8,  "PV": 110, "ENERGIE": 90,  "PIECES": 100}
}

RACE_DESCRIPTIONS = {
    "Boomer": "A de la thune, n'écoute jamais mais possède une endurance à toute épreuve.",
    "Gen Z": "Vit à travers son écran, ultra-rapide mais s'épuise si le Wi-Fi coupe.",
    "Provincial": "Robuste et authentique. Résiste à tout, sauf à la vie parisienne.",
    "Urbain": "Toujours pressé, évite la foule avec agilité mais stresse pour un rien.",
    "Tanguy": "Artiste du système D, refuse de quitter le nid familial pour économiser ses pièces.",
    "Karen": "Exige de parler au responsable. Un charisme terrifiant basé sur l'intimidation.",
    "Chill Guy": "Zen absolu. Rien ne l'atteint, il traverse les pires galères avec le sourire."
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

class CreationView(tk.Frame):
    def __init__(self, parent, controller):
        #1. ON INITIALISE LE MOTEUR TKINTER D'ABORD (Obligatoire)
        super().__init__(parent, bg="#1a1c20")
        self.controller = controller
        
        # 2. ENTIÈREMENT SÉCURISÉ : LE BLOC DE STYLE SOMBRE
        style = ttk.Style()
        style.theme_use('clam')

        # Configuration de la boîte fermée
        style.configure("TCombobox", 
                        fieldbackground="#2d3139", 
                        background="#2d3139",      
                        foreground="#ffffff",      
                        bordercolor="#1a1c20",     
                        arrowcolor="#ffffff")     

        # Forcer le fond sombre même quand le champ est actif
        style.map("TCombobox", fieldbackground=[("readonly", "#2d3139")])

        # Configuration de la liste déroulante (Le pop-up)
        self.option_add('*TCombobox*Listbox.background', '#2d3139')
        self.option_add('*TCombobox*Listbox.foreground', '#ffffff')
        self.option_add('*TCombobox*Listbox.selectBackground', '#3a3f47')
        self.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
        
        # 3. LE RESTE DE TON CODE (Titre, colonnes, etc.)
        titre = tk.Label(self, text="CRÉATION DE L'AVENTURIER", font=("Segoe UI", 24, "bold"), bg="#1a1c20", fg="#ffffff")
        titre.pack(pady=(40, 30))

        # Conteneur Principal
        self.main_container = tk.Frame(self, bg="#1a1c20")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        
        # =====================================================================
        # COLONNE GAUCHE : FORMULAIRE (Sur fond Gris Sombre)
        # =====================================================================
        self.left_card = tk.Frame(self.main_container, bg="#22252a", padx=30, pady=30)
        self.left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # 1. Pseudo
        tk.Label(self.left_card, text="NOM DE L'AVENTURIER", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 5))
        self.entry_pseudo = tk.Entry(self.left_card, font=("Segoe UI", 12), bg="#2d3139", fg="#ffffff", insertbackground="white", bd=0, relief=tk.FLAT)
        self.entry_pseudo.pack(fill=tk.X, ipady=10, pady=(0, 20))
        
        # 2. Race
        tk.Label(self.left_card, text="RACE D'ORIGINE", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 5))
        self.combo_race = ttk.Combobox(self.left_card, values=list(RACES.keys()), state="readonly", font=("Segoe UI", 11))
        self.combo_race.pack(fill=tk.X, ipady=4, pady=(0, 5))
        self.combo_race.bind("<<ComboboxSelected>>", self.declencher_mise_a_jour)
        
        self.lbl_race_desc = tk.Label(self.left_card, text="Choisissez une race...", font=("Segoe UI", 10), bg="#22252a", fg="#86868B", wraplength=350, justify="left")
        self.lbl_race_desc.pack(anchor="w", pady=(0, 20))
        
        # 3. Classe
        tk.Label(self.left_card, text="CLASSE SOCIALE", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 5))
        self.combo_classe = ttk.Combobox(self.left_card, values=list(CLASSES.keys()), state="readonly", font=("Segoe UI", 11))
        self.combo_classe.pack(fill=tk.X, ipady=4, pady=(0, 5))
        self.combo_classe.bind("<<ComboboxSelected>>", self.declencher_mise_a_jour)
        
        self.lbl_classe_bonus = tk.Label(self.left_card, text="Choisissez une classe...", font=("Segoe UI", 10, "italic"), bg="#22252a", fg="#86868B", wraplength=350, justify="left")
        self.lbl_classe_bonus.pack(anchor="w", pady=(0, 30))
        
        # 4. Bouton de Validation (Style Cyan Néon)
        self.btn_valider = tk.Button(
            self.left_card, text="CONFIRMER LE PROFIL", font=("Segoe UI", 12, "bold"),
            bg="#00e5ff", fg="#1a1c20", activebackground="#00b8cc", activeforeground="#1a1c20",
            relief=tk.FLAT, bd=0, pady=12, cursor="hand2",
            command=self.envoyer_creation_serveur
        )
        self.btn_valider.pack(fill=tk.X)

        # =====================================================================
        # COLONNE DROITE : STATISTIQUES (Style Specs Techniques Dark)
        # =====================================================================
        self.right_card = tk.Frame(self.main_container, bg="#22252a", padx=35, pady=30)
        self.right_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        tk.Label(self.right_card, text="CARACTÉRISTIQUES", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ffffff").pack(anchor="w", pady=(0, 20))
        
        self.grid_frame = tk.Frame(self.right_card, bg="#22252a")
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stat_labels = {}
        liste_caracs = ["PV", "ENERGIE", "PIECES", "FOR", "DEX", "CON", "INT", "SAG", "CHA"]
        
        for idx, carac in enumerate(liste_caracs):
            lbl_nom = tk.Label(self.grid_frame, text=carac, font=("Segoe UI", 11), bg="#22252a", fg="#a0a5b0")
            lbl_nom.grid(row=idx, column=0, sticky="w", pady=10)
            
            lbl_val = tk.Label(self.grid_frame, text="—", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
            lbl_val.grid(row=idx, column=1, sticky="e", padx=40, pady=10)
            
            self.stat_labels[carac] = lbl_val
            
            # Ligne de séparation subtile
            if idx < len(liste_caracs) - 1:
                sep = tk.Frame(self.grid_frame, height=1, bg="#2d3139")
                sep.grid(row=idx, column=0, columnspan=2, sticky="ew", pady=(22, 0))

    def declencher_mise_a_jour(self, event):
        race_choisie = self.combo_race.get()
        classe_choisie = self.combo_classe.get()
        
        if race_choisie in RACE_DESCRIPTIONS:
            self.lbl_race_desc.config(text=RACE_DESCRIPTIONS[race_choisie], fg="#ffffff")
            
        if classe_choisie in CLASSES:
            bonus_list = []
            for stat, value in CLASSES[classe_choisie].items():
                if value != 0:
                    signe = "+" if value > 0 else ""
                    bonus_list.append(f"{signe}{value} {stat}")
            self.lbl_classe_bonus.config(text="Modificateurs : " + ", ".join(bonus_list), fg="#00e5ff")

        stats_finales = {k: 0 for k in self.stat_labels.keys()}
        if race_choisie in RACES:
            for k in stats_finales: stats_finales[k] += RACES[race_choisie].get(k, 0)
        if classe_choisie in CLASSES:
            for k in stats_finales: stats_finales[k] += CLASSES[classe_choisie].get(k, 0)
                
        for carac, label_widget in self.stat_labels.items():
            label_widget.config(text=str(stats_finales[carac]))

    def envoyer_creation_serveur(self):
        pseudo = self.entry_pseudo.get().strip()
        race = self.combo_race.get()
        classe = self.combo_classe.get()
        if not pseudo or not race or not classe: return
            
        # Calcul des stats pour initialisation immédiate de l'UI Game
        pv = RACES[race]["PV"] + CLASSES[classe]["PV"]
        en = RACES[race]["ENERGIE"] + CLASSES[classe]["ENERGIE"]
        pi = RACES[race]["PIECES"] + CLASSES[classe]["PIECES"]
        
        self.controller.valider_personnage(pseudo, race, classe, pv, en, pi)
        self.btn_valider.config(state=tk.DISABLED, text="TRANSMISSION MJ...", bg="#2d3139", fg="#86868B")
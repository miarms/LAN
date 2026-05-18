import tkinter as tk
from client_src.views.dice import DiceModule

class GameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1c20")
        self.controller = controller
        
        self.max_pv = 150
        self.max_en = 150
        self.stats_completes = {}
        
        # --- 1. BANDEAU SUPÉRIEUR (Anthracite) ---
        self.top_bar = tk.Frame(self, bg="#22252a", padx=20, pady=15)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        
        self.lbl_player = tk.Label(self.top_bar, text="Aventurier", font=("Segoe UI", 13, "bold"), bg="#22252a", fg="#ffffff", cursor="question_arrow")
        self.lbl_player.pack(side=tk.LEFT, padx=(0, 30))
        
        self.lbl_player.bind("<Enter>", self.afficher_infobulle)
        self.lbl_player.bind("<Leave>", self.masquer_infobulle)
        
        # Jauge PV
        tk.Label(self.top_bar, text="PV :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        self.pv_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.pv_bar_bg.pack(side=tk.LEFT, padx=5)
        self.pv_bar_bg.pack_propagate(False)
        self.pv_bar_fill = tk.Frame(self.pv_bar_bg, bg="#00ff66")
        self.pv_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1)
        self.pv_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.pv_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        # Jauge Énergie
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

        # --- 3. COLONNE DE DROITE (CORRIGÉE EN ANTHRACITE) ---
        self.right_area = tk.Frame(self.main_area, bg="#1a1c20", width=320)
        self.right_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(15, 0))
        self.right_area.pack_propagate(False)

        # Panneau des décisions (FOND SOMBRE REPARÉ)
        self.right_panel = tk.Frame(self.right_area, bg="#22252a", padx=25, pady=25)
        self.right_panel.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        self.lbl_action_title = tk.Label(self.right_panel, text="DÉCISION REQUISE", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#a0a5b0")
        self.lbl_action_title.pack(anchor="w", pady=(0, 20))
        
        self.buttons_container = tk.Frame(self.right_panel, bg="#22252a")
        self.buttons_container.pack(fill=tk.X, expand=True, anchor="n")

        # Séparateur discret
        sep_dark = tk.Frame(self.right_area, height=1, bg="#2d3139")
        sep_dark.pack(fill=tk.X, pady=15)

        # Module Dé intégré juste en dessous
        self.dice_module = DiceModule(parent=self.right_area, controller=controller)
        self.dice_module.pack(side=tk.TOP, fill=tk.X, expand=False)

    # --- MÉTHODES DE L'INFOBULLE ---
    def afficher_infobulle(self, event):
        if not self.stats_completes: return
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.config(bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        
        x = event.x_root + 15
        y = event.y_root + 15
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        tk.Label(self.tooltip, text="CARACTÉRISTIQUES", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#00e5ff").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        for idx, (stat, val) in enumerate(self.stats_completes.items(), 1):
            tk.Label(self.tooltip, text=stat, font=("Segoe UI", 10), bg="#22252a", fg="#a0a5b0").grid(row=idx, column=0, sticky="w", pady=2)
            tk.Label(self.tooltip, text=str(val), font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#ffffff").grid(row=idx, column=1, sticky="e", padx=(25, 0), pady=2)

    def masquer_infobulle(self, event):
        if hasattr(self, 'tooltip') and self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    # --- ENVOIS ET MISES A JOUR ---
    def ajouter_narration(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def mettre_a_jour_stats(self, pv, energie, pieces):
        val_pv, val_en = int(pv), int(energie)
        self.pv_lbl.config(text=str(val_pv))
        self.en_lbl.config(text=str(val_en))
        self.pieces_lbl.config(text=f"{pieces} 🪙")
        
        self.pv_bar_fill.place_configure(relwidth=max(0.0, min(val_pv / self.max_pv, 1.0)))
        self.en_bar_fill.place_configure(relwidth=max(0.0, min(val_en / self.max_en, 1.0)))

    def configurer_nom_joueur(self, pseudo, race, classe):
        self.lbl_player.config(text=f"{pseudo} ({race} {classe})")
        from client_src.views.dice import RACES, CLASSES # Import local sécurisé
        if race in RACES and classe in CLASSES:
            self.stats_completes = {
                "FORCE (FOR)": RACES[race]["FOR"] + CLASSES[classe]["FOR"],
                "DEXTÉRITÉ (DEX)": RACES[race]["DEX"] + CLASSES[classe]["DEX"],
                "CONSTITUTION (CON)": RACES[race]["CON"] + CLASSES[classe]["CON"],
                "INTELLIGENCE (INT)": RACES[race]["INT"] + CLASSES[classe]["INT"],
                "SAGESSE (SAG)": RACES[race]["SAG"] + CLASSES[classe]["SAG"],
                "CHARISME (CHA)": RACES[race]["CHA"] + CLASSES[classe]["CHA"]
            }

    def generer_choix_boutons(self, titre_action, liste_options):
        for widget in self.buttons_container.winfo_children(): widget.destroy()
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
        for widget in self.buttons_container.winfo_children(): widget.config(state=tk.DISABLED)
        self.lbl_action_title.config(text="TRANSMISSION...", fg="#00e5ff")
        self.controller.envoyer_choix_action(bouton_id)
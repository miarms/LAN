import tkinter as tk
import os
from PIL import Image, ImageTk
from client_src.views.dice import DiceModule, RACES, CLASSES
from client_src.views.card import WelcomeCard
from client_src.views.inventory import InventoryModule

class GameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1c20")
        self.controller = controller
        
        self.max_pv = 150
        self.max_en = 150
        self.current_pv = 100 # Sauvegarde locale des PV du joueur
        self.stats_completes = {}
        self.swipe_en_cours = False
        self.lbl_carte_centrale = None 
        
        # =====================================================================
        # 1. BANDEAU SUPÉRIEUR
        # =====================================================================
        self.top_bar = tk.Frame(self, bg="#22252a", padx=20, pady=15)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        
        self.lbl_player = tk.Label(self.top_bar, text="Aventurier", font=("Segoe UI", 13, "bold"), bg="#22252a", fg="#ffffff", cursor="question_arrow")
        self.lbl_player.pack(side=tk.LEFT, padx=(0, 30))
        self.lbl_player.bind("<Enter>", self.afficher_infobulle)
        self.lbl_player.bind("<Leave>", self.masquer_infobulle)
        
        tk.Label(self.top_bar, text="PV :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        self.pv_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.pv_bar_bg.pack(side=tk.LEFT, padx=5)
        self.pv_bar_bg.pack_propagate(False)
        self.pv_bar_fill = tk.Frame(self.pv_bar_bg, bg="#00ff66")
        self.pv_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1)
        self.pv_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.pv_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        tk.Label(self.top_bar, text="ÉNERGIE :", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#a0a5b0").pack(side=tk.LEFT, padx=(10, 5))
        self.en_bar_bg = tk.Frame(self.top_bar, width=120, height=14, bg="#3a3f47")
        self.en_bar_bg.pack(side=tk.LEFT, padx=5)
        self.en_bar_bg.pack_propagate(False)
        self.en_bar_fill = tk.Frame(self.en_bar_bg, bg="#00e5ff")
        self.en_bar_fill.place(x=0, y=0, relwidth=0.6, relheight=1)
        self.en_lbl = tk.Label(self.top_bar, text="100", font=("Segoe UI", 11, "bold"), bg="#22252a", fg="#ffffff")
        self.en_lbl.pack(side=tk.LEFT, padx=(5, 20))
        
        self.pieces_lbl = tk.Label(self.top_bar, text="0 🪙", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ffd32a")
        self.pieces_lbl.pack(side=tk.RIGHT, padx=10)

        sep = tk.Frame(self, height=1, bg="#2d3139")
        sep.pack(fill=tk.X, side=tk.TOP)

        # =====================================================================
        # 2. COLONNES (Gauche, Centre, Droite)
        # =====================================================================
        self.main_area = tk.Frame(self, bg="#1a1c20")
        self.main_area.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # --- GAUCHE ---
        self.left_column = tk.Frame(self.main_area, bg="#1a1c20", width=320)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        self.left_column.pack_propagate(False)

        self.mj_panel = tk.Frame(self.left_column, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.mj_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        tk.Label(self.mj_panel, text="MAÎTRE DU JEU", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w")
        try:
            img_mj = Image.open(os.path.join("client_src", "rsc", "img", "MJ.png")).resize((160, 160), Image.Resampling.LANCZOS)
            self.tk_img_mj = ImageTk.PhotoImage(img_mj)
            tk.Label(self.mj_panel, image=self.tk_img_mj, bg="#22252a").pack(pady=10)
        except: pass
        self.mj_bubble_frame = tk.Frame(self.mj_panel, bg="#2d3139", padx=12, pady=12)
        self.mj_bubble_frame.pack(fill=tk.X, side=tk.TOP, padx=5)
        self.lbl_mj_speech = tk.Label(self.mj_bubble_frame, text="Regardez ce que le destin vous réserve...", font=("Segoe UI", 10, "italic"), bg="#2d3139", fg="#ffffff", wraplength=250)
        self.lbl_mj_speech.pack(fill=tk.BOTH, expand=True)

        self.history_panel = tk.Frame(self.left_column, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.history_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        tk.Label(self.history_panel, text="HISTORIQUE", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 5))
        self.text_area = tk.Text(self.history_panel, wrap=tk.WORD, state=tk.DISABLED, bg="#22252a", fg="#ffffff", font=("Segoe UI", 10), bd=0, highlightthickness=0)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # --- CENTRE ---
        self.center_column = tk.Frame(self.main_area, bg="#22252a", padx=25, pady=25, highlightbackground="#3a3f47", highlightthickness=1)
        self.center_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        tk.Label(self.center_column, text="ZONE DE JEU / CARTES", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 15))
        
        self.card_display_area = tk.Frame(self.center_column, bg="#22252a")
        self.card_display_area.pack(fill=tk.BOTH, expand=True)
        
        def action_apres_swipe():
            self.lbl_action_title.pack(anchor="n", pady=(10, 15))
            self.buttons_container.pack(fill=tk.X, anchor="n")
        self.welcome_card = WelcomeCard(parent=self.card_display_area, controller=self.controller, on_start_callback=action_apres_swipe)
        self.welcome_card.pack(expand=True, pady=10)
        
        self.lbl_action_title = tk.Label(self.card_display_area, text="DÉCISION REQUISE", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ffffff")
        self.buttons_container = tk.Frame(self.card_display_area, bg="#22252a")

        # --- DROITE ---
        self.right_column = tk.Frame(self.main_area, bg="#1a1c20", width=260)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))
        self.right_column.pack_propagate(False)

        self.inventory_panel = tk.Frame(self.right_column, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.inventory_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        tk.Label(self.inventory_panel, text="🎒 INVENTAIRE", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 10))
        self.inventory_module = InventoryModule(parent=self.inventory_panel, controller=self.controller)
        self.inventory_module.pack(fill=tk.BOTH, expand=True)

        self.dice_panel = tk.Frame(self.right_column, bg="#1a1c20")
        self.dice_panel.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(0, 10))
        self.dice_module = DiceModule(parent=self.dice_panel, controller=controller, inventory_module=self.inventory_module)
        self.dice_module.pack(fill=tk.X, expand=False)
        
        # --- INIT CARTE MONSTRE ---
        from client_src.views.monster import MonsterCard
        self.monster_card = MonsterCard(parent=self.card_display_area, controller=self.controller, dice_module=self.dice_module, game_view=self)
        
        # CRASH TEST (Inventaire pour tester l'attaque)
        self.inventory_module.equiper_objet("Bonnes vieilles godasses")
        self.inventory_module.equiper_objet("Excalibur")

    # =====================================================================
    # MÉTHODES UTILES
    # =====================================================================
    def configurer_nom_joueur(self, pseudo, race, classe):
        self.lbl_player.config(text=f"{pseudo} ({race} {classe})")
        if race in RACES and classe in CLASSES:
            self.current_pv = RACES[race]["PV"] + CLASSES[classe]["PV"]
            self.stats_completes = {
                "FORCE (FOR)": RACES[race]["FOR"] + CLASSES[classe]["FOR"],
                "DEXTÉRITÉ (DEX)": RACES[race]["DEX"] + CLASSES[classe]["DEX"],
                "CONSTITUTION (CON)": RACES[race]["CON"] + CLASSES[classe]["CON"],
                "INTELLIGENCE (INT)": RACES[race]["INT"] + CLASSES[classe]["INT"],
                "SAGESSE (SAG)": RACES[race]["SAG"] + CLASSES[classe]["SAG"],
                "CHARISME (CHA)": RACES[race]["CHA"] + CLASSES[classe]["CHA"]
            }

    def mettre_a_jour_stats(self, pv, energie, pieces):
        self.current_pv = int(pv)
        self.pv_lbl.config(text=str(self.current_pv))
        self.en_lbl.config(text=str(int(energie)))
        self.pieces_lbl.config(text=f"{pieces} 🪙")
        self.pv_bar_fill.place_configure(relwidth=max(0.0, min(self.current_pv / self.max_pv, 1.0)))
        self.en_bar_fill.place_configure(relwidth=max(0.0, min(int(energie) / self.max_en, 1.0)))

    def subir_degats(self, degats):
        """Fonction appelée par le monstre quand il frappe le joueur"""
        nouveau_pv = max(0, self.current_pv - degats)
        self.mettre_a_jour_stats(nouveau_pv, int(self.en_lbl.cget("text")), int(self.pieces_lbl.cget("text").split()[0]))
        self.ajouter_narration(f"Vous perdez {degats} PV !")
        
    def afficher_infobulle(self, event):
        if not self.stats_completes: return
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.config(bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        x, y = event.x_root + 15, event.y_root + 15
        self.tooltip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tooltip, text="CARACTÉRISTIQUES", font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#00e5ff").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        for idx, (stat, val) in enumerate(self.stats_completes.items(), 1):
            tk.Label(self.tooltip, text=stat, font=("Segoe UI", 10), bg="#22252a", fg="#a0a5b0").grid(row=idx, column=0, sticky="w", pady=2)
            tk.Label(self.tooltip, text=str(val), font=("Segoe UI", 10, "bold"), bg="#22252a", fg="#ffffff").grid(row=idx, column=1, sticky="e", padx=(25, 0), pady=2)

    def masquer_infobulle(self, event):
        if hasattr(self, 'tooltip') and self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def ajouter_narration(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    # =====================================================================
    # LE "NETTOYEUR" (Empêche d'avoir 2 cartes en même temps !)
    # =====================================================================
    def nettoyer_zone_centrale(self):
        # 1. On cache la carte de bienvenue
        if hasattr(self, 'welcome_card') and self.welcome_card.winfo_ismapped():
            self.welcome_card.pack_forget()
            
        # 2. On cache la carte Monstre
        if hasattr(self, 'monster_card') and self.monster_card.winfo_ismapped():
            self.monster_card.pack_forget()
            
        # 3. On détruit l'image Trahison
        if self.lbl_carte_centrale is not None:
            self.lbl_carte_centrale.destroy()
            self.lbl_carte_centrale = None
            
        # 4. On vide les boutons
        for widget in self.buttons_container.winfo_children():
            widget.destroy()
            
        # 5. On remet la structure de base vide
        self.lbl_action_title.config(text="EN ATTENTE...", fg="#ffffff")
        self.lbl_action_title.pack(anchor="n", pady=(10, 15))
        self.buttons_container.pack(fill=tk.X, anchor="n")

    def terminer_rencontre(self):
        """Appelée quand on bat le monstre ou qu'on fuit"""
        self.nettoyer_zone_centrale()
        self.lbl_action_title.config(text="LE CALME REVIENT... EN ATTENTE DU MJ", fg="#a0a5b0")

    # =====================================================================
    # AFFICHAGE DES TRAHISONS
    # =====================================================================
    def afficher_carte_trahison(self, nom, effet, cout, fichier_img, est_le_traitre=True):
        self.nettoyer_zone_centrale() # <- LE SECRET EST LÀ !

        if est_le_traitre:
            self.lbl_action_title.config(text="🔥 TRAHIR VOTRE ALLIÉ ?", fg="#ff5e57")
            chemin_img = os.path.join("client_src", "rsc", "img", "card", "trahisons", fichier_img)
        else:
            self.lbl_action_title.config(text="🔮 SUSPENSE... UN COUP BAS SE PRÉPARE !", fg="#f39c12")
            chemin_img = os.path.join("client_src", "rsc", "img", "card", "dos-carte.png")

        try:
            img = Image.open(chemin_img).resize((300, 500), Image.Resampling.LANCZOS)
            self.tk_img_courante = ImageTk.PhotoImage(img)
            self.lbl_carte_centrale = tk.Label(self.card_display_area, image=self.tk_img_courante, bg="#22252a")
        except:
            txt_secu = f"[{nom.upper()}]\n\n{effet}\n\nCoût : {cout}" if est_le_traitre else "[CARTE CACHÉE]\n\nL'autre joueur prend une décision..."
            self.lbl_carte_centrale = tk.Label(self.card_display_area, text=txt_secu, font=("Segoe UI", 12, "bold"), bg="#2d3139", fg="#ffffff", width=30, height=15)
            
        self.lbl_carte_centrale.pack(before=self.buttons_container, pady=10)

        if est_le_traitre:
            tk.Button(
                self.buttons_container, text=f"⚡ Activer l'effet ({cout})", font=("Segoe UI", 11, "bold"),
                bg="#ff5e57", fg="#ffffff", relief=tk.FLAT, bd=0, pady=12, command=lambda: self.decision_trahison("ACTIVER", nom)
            ).pack(fill=tk.X, pady=5)

            tk.Button(
                self.buttons_container, text="🚫 Ignorer la carte", font=("Segoe UI", 11),
                bg="#2d3139", fg="#a0a5b0", relief=tk.FLAT, bd=0, pady=12, command=lambda: self.decision_trahison("IGNORER", nom)
            ).pack(fill=tk.X, pady=5)

    def decision_trahison(self, choix, nom_carte):
        for widget in self.buttons_container.winfo_children(): widget.config(state=tk.DISABLED)
        self.lbl_action_title.config(text="TRANSMISSION AU MJ...", fg="#00e5ff")
        if self.controller.client_socket:
            try: self.controller.client_socket.sendall(f"TRAHISON:CHOIX|{choix}|{nom_carte}\n".encode('utf-8'))
            except: pass
# client_src/views/game.py
import tkinter as tk
import os
from PIL import Image, ImageTk
from client_src.views.dice import DiceModule
from client_src.views.card import WelcomeCard

class GameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1a1c20")
        self.controller = controller
        
        self.max_pv = 150
        self.max_en = 150
        self.stats_completes = {}
        self.swipe_en_cours = False
        self.lbl_carte_centrale = None # Ajout pour tracker l'image de la carte en cours
        
        # =====================================================================
        # 1. BANDEAU SUPÉRIEUR : INFO JOUEUR
        # =====================================================================
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

        # =====================================================================
        # CONTENEUR CENTRAL DES 3 COLONNES
        # =====================================================================
        self.main_area = tk.Frame(self, bg="#1a1c20")
        self.main_area.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # --- COLONNE GAUCHE : STACK [MJ CARD + BULLE] + [HISTORIQUE] ---
        self.left_column = tk.Frame(self.main_area, bg="#1a1c20", width=320)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        self.left_column.pack_propagate(False)

        self.mj_panel = tk.Frame(self.left_column, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.mj_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(self.mj_panel, text="MAÎTRE DU JEU", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w")
        
        chemin_mj = os.path.join("client_src", "rsc", "img", "MJ.png")
        try:
            img_mj = Image.open(chemin_mj)
            img_mj = img_mj.resize((160, 160), Image.Resampling.LANCZOS)
            self.tk_img_mj = ImageTk.PhotoImage(img_mj)
            self.lbl_mj_image = tk.Label(self.mj_panel, image=self.tk_img_mj, bg="#22252a")
            self.lbl_mj_image.pack(pady=10)
        except Exception as e:
            self.lbl_mj_image = tk.Label(self.mj_panel, text="💬", font=("Segoe UI", 24), bg="#22252a", fg="#86868B")
            self.lbl_mj_image.pack(pady=10)

        self.mj_bubble_frame = tk.Frame(self.mj_panel, bg="#2d3139", padx=12, pady=12, highlightbackground="#3a3f47", highlightthickness=1)
        self.mj_bubble_frame.pack(fill=tk.X, side=tk.TOP, padx=5)
        
        self.lbl_mj_speech = tk.Label(self.mj_bubble_frame, text="Regardez ce que le destin vous réserve...", font=("Segoe UI", 10, "italic"), bg="#2d3139", fg="#ffffff", wraplength=250, justify="center")
        self.lbl_mj_speech.pack(fill=tk.BOTH, expand=True)

        self.history_panel = tk.Frame(self.left_column, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.history_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        tk.Label(self.history_panel, text="HISTORIQUE DES ACTIONS", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 5))
        self.text_area = tk.Text(self.history_panel, wrap=tk.WORD, state=tk.DISABLED, bg="#22252a", fg="#ffffff", font=("Segoe UI", 10), bd=0, highlightthickness=0, insertbackground="white")
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)

        # ---------------------------------------------------------------------
        # COLONNE CENTRALE : ZONE DES CARTES & DÉCISIONS
        # ---------------------------------------------------------------------
        self.center_column = tk.Frame(self.main_area, bg="#22252a", padx=25, pady=25, highlightbackground="#3a3f47", highlightthickness=1)
        self.center_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(self.center_column, text="ZONE DE JEU / CARTES", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 15))
        
        # Conteneur pour intégrer tes visuels de cartes ou choix actuels
        self.card_display_area = tk.Frame(self.center_column, bg="#22252a")
        self.card_display_area.pack(fill=tk.BOTH, expand=True)
        
        # --- LOGIQUE DE LA CARTE DE BIENVENUE INSTANTANÉE ---
        def action_apres_swipe():
            self.lbl_action_title.pack(anchor="n", pady=(10, 15))
            self.buttons_container.pack(fill=tk.X, anchor="n")
        
        self.welcome_card = WelcomeCard(
            parent=self.card_display_area, 
            controller=self.controller, 
            on_start_callback=action_apres_swipe
        )
        self.welcome_card.pack(expand=True, pady=10)
        
        # Les éléments de décisions standards du serveur sont masqués au début (ils attendent le swipe)
        self.lbl_action_title = tk.Label(self.card_display_area, text="DÉCISION REQUISE", font=("Segoe UI", 12, "bold"), bg="#22252a", fg="#ffffff")
        self.buttons_container = tk.Frame(self.card_display_area, bg="#22252a")

        # --- COLONNE DROITE : STACK [DÉ] + [INVENTAIRE] ---
        self.right_column = tk.Frame(self.main_area, bg="#1a1c20", width=260)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))
        self.right_column.pack_propagate(False)

        self.dice_panel = tk.Frame(self.right_column, bg="#1a1c20")
        self.dice_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))
        self.dice_module = DiceModule(parent=self.dice_panel, controller=controller)
        self.dice_module.pack(fill=tk.BOTH, expand=True)

        self.inventory_panel = tk.Frame(self.right_column, bg="#22252a", padx=15, pady=15, highlightbackground="#3a3f47", highlightthickness=1)
        self.inventory_panel.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        tk.Label(self.inventory_panel, text="MENU POUR INVENTAIRE", font=("Segoe UI", 9, "bold"), bg="#22252a", fg="#a0a5b0").pack(anchor="w", pady=(0, 5))
        self.lbl_inv_placeholder = tk.Label(self.inventory_panel, text="🎒 [Inventaire Vide]", font=("Segoe UI", 11, "italic"), bg="#22252a", fg="#86868B")
        self.lbl_inv_placeholder.pack(expand=True)

    # =====================================================================
    # INTERACTION : ANIMATION DE SWIPE TINDER
    # =====================================================================
    def declencher_swipe_tinder(self):
        """Lance l'animation de propulsion de la carte vers la droite"""
        if self.swipe_en_cours: return
        self.swipe_en_cours = True
        
        def anim_loop():
            current_coords = self.welcome_canvas.coords(self.card_item)
            if current_coords and current_coords[0] < 600:
                self.welcome_canvas.move(self.card_item, 30, -4)
                if hasattr(self, 'text_item'): 
                    self.welcome_canvas.move(self.text_item, 30, -4)
                self.after(12, anim_loop)
            else:
                self.welcome_canvas.pack_forget()
                self.lbl_action_title.pack(anchor="n", pady=(10, 15))
                self.buttons_container.pack(fill=tk.X, anchor="n")

        anim_loop()

    # =====================================================================
    # MÉTHODES DE LOGIQUE
    # =====================================================================
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

    def mettre_a_jour_stats(self, pv, energie, pieces):
        val_pv, val_en = int(pv), int(energie)
        self.pv_lbl.config(text=str(val_pv))
        self.en_lbl.config(text=str(val_en))
        self.pieces_lbl.config(text=f"{pieces} 🪙")
        self.pv_bar_fill.place_configure(relwidth=max(0.0, min(val_pv / self.max_pv, 1.0)))
        self.en_bar_fill.place_configure(relwidth=max(0.0, min(val_en / self.max_en, 1.0)))

    def configurer_nom_joueur(self, pseudo, race, classe):
        self.lbl_player.config(text=f"{pseudo} ({race} {classe})")
        from client_src.views.dice import RACES, CLASSES
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
        self.lbl_action_title.config(text=titre_action.upper(), fg="#ffffff")
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

    # =====================================================================
    # NOUVELLES MÉTHODES : GESTION DES TRAHISONS
    # =====================================================================
    def nettoyer_zone_centrale(self):
        """Nettoie l'image et les boutons sans casser ta structure de base."""
        self.lbl_action_title.config(text="EN ATTENTE DU MJ...", fg="#ffffff")
        
        # On vide les boutons existants
        for widget in self.buttons_container.winfo_children():
            widget.destroy()
            
        # On supprime l'image de la carte si elle est affichée
        if self.lbl_carte_centrale is not None:
            self.lbl_carte_centrale.destroy()
            self.lbl_carte_centrale = None
            
        # On s'assure que les conteneurs sont bien affichés
        self.lbl_action_title.pack(anchor="n", pady=(10, 15))
        self.buttons_container.pack(fill=tk.X, anchor="n")

    def afficher_carte_trahison(self, nom, effet, cout, fichier_img, est_le_traitre=True):
        self.nettoyer_zone_centrale()
        
        # Sécurité : on cache la carte de bienvenue si elle traînait encore
        if hasattr(self, 'welcome_card') and self.welcome_card.winfo_ismapped():
            self.welcome_card.pack_forget()

        if est_le_traitre:
            self.lbl_action_title.config(text="🔥 TRAHIR VOTRE ALLIÉ ?", fg="#ff5e57")
            chemin_img = os.path.join("client_src", "rsc", "img", "card", "trahisons", fichier_img)
        else:
            self.lbl_action_title.config(text="🔮 SUSPENSE... UN COUP BAS SE PRÉPARE !", fg="#f39c12")
            chemin_img = os.path.join("client_src", "rsc", "img", "card", "dos-carte.png")

        # Chargement et affichage de la carte au centre (300x500 pixels)
        try:
            img = Image.open(chemin_img).resize((300, 500), Image.Resampling.LANCZOS)
            self.tk_img_courante = ImageTk.PhotoImage(img)
            self.lbl_carte_centrale = tk.Label(self.card_display_area, image=self.tk_img_courante, bg="#22252a")
            self.lbl_carte_centrale.pack(before=self.buttons_container, pady=10)
        except Exception as e:
            # Texte de secours si l'image png n'est pas encore créée
            txt_secu = f"[{nom.upper()}]\n\n{effet}\n\nCoût : {cout}" if est_le_traitre else "[CARTE CACHÉE]\n\nL'autre joueur prend une décision..."
            self.lbl_carte_centrale = tk.Label(self.card_display_area, text=txt_secu, font=("Segoe UI", 12, "bold"),
                               bg="#2d3139", fg="#ffffff", width=30, height=15, relief=tk.FLAT)
            self.lbl_carte_centrale.pack(before=self.buttons_container, pady=10)

        # Génération des boutons UNIQUEMENT pour le joueur qui peut trahir
        if est_le_traitre:
            btn_activer = tk.Button(
                self.buttons_container, text=f"⚡ Activer l'effet ({cout})", font=("Segoe UI", 11, "bold"),
                bg="#ff5e57", fg="#ffffff", activebackground="#ff3f34", activeforeground="#ffffff",
                relief=tk.FLAT, bd=0, pady=12, cursor="hand2", command=lambda: self.decision_trahison("ACTIVER", nom)
            )
            # Affichage reprenant ton style vertical
            btn_activer.pack(fill=tk.X, pady=5)

            btn_ignorer = tk.Button(
                self.buttons_container, text="🚫 Ignorer la carte", font=("Segoe UI", 11),
                bg="#2d3139", fg="#a0a5b0", activebackground="#3a3f47", activeforeground="#ffffff",
                relief=tk.FLAT, bd=0, pady=12, cursor="hand2", command=lambda: self.decision_trahison("IGNORER", nom)
            )
            btn_ignorer.pack(fill=tk.X, pady=5)

    def decision_trahison(self, choix, nom_carte):
        # On verrouille les boutons le temps que le serveur réponde
        for widget in self.buttons_container.winfo_children():
            widget.config(state=tk.DISABLED)
        self.lbl_action_title.config(text="TRANSMISSION DU CHOIX AU MJ...", fg="#00e5ff")
        
        # Envoi au serveur
        if self.controller.client_socket:
            try:
                paquet = f"TRAHISON:CHOIX|{choix}|{nom_carte}\n"
                self.controller.client_socket.sendall(paquet.encode('utf-8'))
            except: pass
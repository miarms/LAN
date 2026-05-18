import tkinter as tk
import os

class MenuView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e272e")
        self.controller = controller
        
        # 1. UN SEUL GÉANT CANVAS POUR TOUT LE MENU
        # Ce canvas va contenir l'image ET le bouton dessiné par-dessus
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#1e272e")
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Chargement de l'image de fond
        chemin_img = os.path.join("client_src", "rsc", "img", "menu_background.png")
        try:
            self.bg_image = tk.PhotoImage(file=chemin_img)
            # On place l'image dans le canvas (les coordonnées seront gérées dynamiquement)
            self.bg_item = self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.CENTER)
        except Exception as e:
            print(f"[ATTENTION] Fond d'écran absent : {e}")
            self.bg_item = None

        # 2. DESSIN DU BOUTON PLAY DIRECTEMENT SUR LE CANVAS (Zéro pixel carré !)
        # On leur attribue le tag "play_btn" pour les animer et les gérer ensemble
        self.cercle = self.canvas.create_oval(0, 0, 0, 0, fill="black", outline="black", tags="play_btn")
        self.triangle = self.canvas.create_text(0, 0, text="▶", fill="white", font=("Arial", 40, "bold"), tags="play_btn")
        
        # 3. BADGE DE STATUT (En haut à droite)
        self.status_label = tk.Label(
            self, 
            text="En attente de joueur...", 
            font=("Arial", 12, "bold"), 
            bg="#2f3640", 
            fg="#d2dae2", 
            padx=15, pady=8
        )
        self.status_label.place(relx=0.98, rely=0.02, anchor=tk.NE)

        # --- GESTION DES INTERACTIONS VIA LES TAGS ---
        self.canvas.tag_bind("play_btn", "<Enter>", self.survol_bouton)
        self.canvas.tag_bind("play_btn", "<Leave>", self.quitter_bouton)
        self.canvas.tag_bind("play_btn", "<Button-1>", lambda event: self.clic_play())
        
        # --- UX : REDIMENSIONNEMENT ET CENTRAGE DYNAMIQUE ---
        # Cette ligne ordonne à Python de recalculer le centre exact si on étire la fenêtre
        self.bind("<Configure>", self.recalculer_positions)

    def recalculer_positions(self, event):
        """Recentre instantanément l'image et le bouton dès que la taille de la fenêtre change"""
        largeur = event.width
        hauteur = event.height
        cx, cy = largeur // 2, hauteur // 2
        
        # 1. Recentre l'image de fond
        if self.bg_item:
            self.canvas.coords(self.bg_item, cx, cy)
            
        # 2. Recentre le cercle noir (rayon de 45 pixels pour un diamètre de 90)
        self.canvas.coords(self.cercle, cx - 45, cy - 45, cx + 45, cy + 45)
        
        # 3. Recentre le triangle blanc (avec le décalage optique de 3 pixels vers la droite)
        self.canvas.coords(self.triangle, cx + 3, cy)

    def survol_bouton(self, event):
        """Le bouton s'éclaire légèrement au survol"""
        self.canvas.itemconfig(self.cercle, fill="#2c3e50", outline="#2c3e50")
        self.canvas.config(cursor="hand2")

    def quitter_bouton(self, event):
        """Le bouton redevient noir pur"""
        self.canvas.itemconfig(self.cercle, fill="black", outline="black")
        self.canvas.config(cursor="")

    def clic_play(self):
        print("[ACTION] Clic sur Play : Connexion au serveur LAN...")
        self.modifier_statut("Connexion au serveur...", couleur_fond="#f39c12")
        self.controller.connecter_au_serveur()

    def modifier_statut(self, nouveau_texte, couleur_fond="#27ae60", couleur_texte="white"):
        """Permet de modifier le badge de statut à distance"""
        self.status_label.config(text=nouveau_texte, bg=couleur_fond, fg=couleur_texte)
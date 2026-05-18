import tkinter as tk
import socket
import threading
import queue
from client_src.views.menu import MenuView
from client_src.views.creation import CreationView
from client_src.views.game import GameView

SERVEUR_IP = '127.0.0.1' 
PORT = 5555

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Le Donjon de la Discorde - Édition LAN")
        self.geometry("1024x768") 
        self.minsize(800, 600)    
        self.resizable(True, True) 
        
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.views = {}
        self.client_socket = None
        self.msg_queue = queue.Queue()
        
        self.mon_pseudo = ""
        self.ma_race = ""
        self.ma_classe = ""
        
        self.charger_vues()
        self.afficher_vue("MenuView")
        self.verifier_messages_reseau()

    def charger_vues(self):
        self.views["MenuView"] = MenuView(parent=self.container, controller=self)
        self.views["MenuView"].grid(row=0, column=0, sticky="nsew")
        
        self.views["CreationView"] = CreationView(parent=self.container, controller=self)
        self.views["CreationView"].grid(row=0, column=0, sticky="nsew")
        
        self.views["GameView"] = GameView(parent=self.container, controller=self)
        self.views["GameView"].grid(row=0, column=0, sticky="nsew")
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def afficher_vue(self, nom_vue):
        vue = self.views[nom_vue]
        vue.tkraise()

    def connecter_au_serveur(self):
        threading.Thread(target=self._ecoute_reseau_thread, daemon=True).start()

    def _ecoute_reseau_thread(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVEUR_IP, PORT))
            while True:
                donnees = self.client_socket.recv(4096).decode('utf-8')
                if not donnees: break
                self.msg_queue.put(donnees)
        except:
            self.msg_queue.put("ORDRE:ERREUR_CONNEXION")

    def valider_personnage(self, pseudo, race, classe, pv, energie, pieces):
        """Sauvegarde les choix locaux, initialise l'UI de jeu et prévient le serveur"""
        self.mon_pseudo = pseudo
        self.ma_race = race
        self.ma_classe = classe
        
        # CORRECTION : On injecte directement TES statistiques réelles dans le bandeau de jeu
        self.views["GameView"].configurer_nom_joueur(pseudo, race, classe)
        self.views["GameView"].mettre_a_jour_stats(pv, energie, pieces)
        
        if self.client_socket:
            try:
                paquet = f"CREATION:{pseudo}|{race}|{classe}\n"
                self.client_socket.sendall(paquet.encode('utf-8'))
            except: pass

    def envoyer_choix_action(self, bouton_id):
        if self.client_socket:
            try:
                self.client_socket.sendall(str(bouton_id).encode('utf-8'))
            except: pass

    def verifier_messages_reseau(self):
        while not self.msg_queue.empty():
            paquet_brut = self.msg_queue.get()
            
            for ligne in paquet_brut.split('\n'):
                if not ligne.strip(): continue
                
                # CORRECTION : Si le serveur envoie une mise à jour de stats (ex: STATS:PV=90,EN=100,PI=120)
                if ligne.startswith("STATS:"):
                    try:
                        contenu = ligne.replace("STATS:", "")
                        parts = dict(item.split("=") for item in contenu.split(","))
                        self.views["GameView"].mettre_a_jour_stats(parts["PV"], parts["EN"], parts["PI"])
                    except:
                        pass
                
                elif "En attente du second aventurier" in ligne:
                    self.views["MenuView"].modifier_statut("Connecté ! En attente du J2...", couleur_fond="#f39c12")
                    
                elif "Les deux joueurs sont presents" in ligne:
                    self.views["MenuView"].modifier_statut("Joueur 2 trouvé !", couleur_fond="#27ae60")
                    self.after(1500, lambda: self.afficher_vue("CreationView"))
                    
                elif "Fiches de personnages synchronisees" in ligne:
                    self.afficher_vue("GameView")
                    self.views["GameView"].ajouter_narration("=== Bienvenue dans le Donjon de la Discorde ===")
                    
                elif "ERREUR_CONNEXION" in ligne:
                    self.views["MenuView"].modifier_statut("Serveur introuvable", couleur_fond="#ff5e57")
                    
                else:
                    # Évite d'afficher les lignes de commande pures dans le journal de narration
                    self.views["GameView"].ajouter_narration(ligne)
        
        self.after(100, self.verifier_messages_reseau)
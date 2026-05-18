import tkinter as tk
import socket
import threading
import queue
from client_src.views.menu import MenuView

# Mets l'IP de ton serveur ici (127.0.0.1 pour tester sur le même PC)
SERVEUR_IP = '127.0.0.1' 
PORT = 5555

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("Le Donjon de la Discorde - Édition LAN")
        self.geometry("1024x768") 
        self.minsize(800, 600)    
        self.resizable(True, True) 
        
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.views = {}
        self.client_socket = None
        self.msg_queue = queue.Queue() # File d'attente pour recevoir les messages du réseau
        
        self.charger_vues()
        self.afficher_vue("MenuView")
        
        # On lance une vérification de la boîte de réception réseau toutes les 100ms
        self.verifier_messages_reseau()

    def charger_vues(self):
        vue_menu = MenuView(parent=self.container, controller=self)
        self.views["MenuView"] = vue_menu
        vue_menu.grid(row=0, column=0, sticky="nsew")
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def afficher_vue(self, nom_vue):
        vue = self.views[nom_vue]
        vue.tkraise()

    # --- BRIQUE RÉSEAU ---
    def connecter_au_serveur(self):
        """Démarre le thread réseau en tâche de fond pour ne pas bloquer l'affichage graphique"""
        threading.Thread(target=self._ecoute_reseau_thread, daemon=True).start()

    def _ecoute_reseau_thread(self):
        """Ce code tourne en arrière-plan et écoute le serveur"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVEUR_IP, PORT))
            
            while True:
                donnees = self.client_socket.recv(1024).decode('utf-8')
                if not donnees:
                    break
                # On dépose le message brut reçu du serveur dans notre file d'attente
                self.msg_queue.put(donnees)
        except Exception as e:
            self.msg_queue.put(f"ORDRE:ERREUR_CONNEXION")

    def verifier_messages_reseau(self):
        """Vérifie la file d'attente et applique les changements graphiques en direct"""
        while not self.msg_queue.empty():
            message_serveur = self.msg_queue.get()
            
            # ANALYSE DU TEXTE DU SERVEUR
            if "En attente du second aventurier" in message_serveur:
                # Le joueur 1 est connecté mais attend le J2
                self.views["MenuView"].modifier_statut("Connecté ! En attente du J2...", couleur_fond="#f39c12")
                
            elif "Les deux joueurs sont presents" in message_serveur:
                # Le serveur confirme que tout le monde est là ! On passe au vert clair
                self.views["MenuView"].modifier_statut("Joueur 2 trouvé !", couleur_fond="#27ae60")
                
            elif "ERREUR_CONNEXION" in message_serveur:
                self.views["MenuView"].modifier_statut("Serveur éteint ou introuvable", couleur_fond="#ff5e57")
        
        # On redemande à Tkinter de revérifier dans 100 millisecondes
        self.after(100, self.verifier_messages_reseau)
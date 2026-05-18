# serveur.py
import socket
import threading
import os
from managers.trahison_manager import TrahisonManager

HOST = '0.0.0.0'
PORT = 55555

sockets_joueurs = []
verrou_joueurs = threading.Lock()

fiches_recues = 0
verrou_fiches = threading.Lock()

# Initialisation du gestionnaire de trahisons
trahison_mgr = TrahisonManager()

def lancer_partie():
    """Déclenche le changement d'écran chez les clients et envoie l'intro."""
    print("[JEU] Deux joueurs connectés. Lancement de l'ambiance.")
    diffuser_a_tous("HISTOIRE:Les deux joueurs sont presents\n")
    
    intro_texte = (
        "HISTOIRE:\n"
        "===============================================\n"
        "           LE DONJON DE LA DISCORDE            \n"
        "===============================================\n"
        "Les portes se referment. L'inconnu s'éveille.\n"
        "Pour survivre, explorez, gérez vos ressources\n"
        "et fiez-vous à vos dés. Restez vigilants.\n"
        "===============================================\n\n"
    )
    diffuser_a_tous(intro_texte)
    
    # On délègue le lancement du dilemme au manager de trahison
    trahison_mgr.lancer_dilemme_trahison(sockets_joueurs)

def diffuser_a_tous(message):
    with verrou_joueurs:
        for sock in sockets_joueurs:
            try:
                sock.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"[RESEAU] Erreur de diffusion : {e}")

def gerer_client(client_socket, client_address):
    global fiches_recues
    print(f"[RESEAU] Nouvelle connexion établie depuis : {client_address}")
    
    commencer_jeu = False
    with verrou_joueurs:
        if len(sockets_joueurs) < 2:
            sockets_joueurs.append(client_socket)
            if len(sockets_joueurs) == 1:
                client_socket.sendall("HISTOIRE:En attente du second aventurier\n".encode('utf-8'))
            if len(sockets_joueurs) == 2:
                commencer_jeu = True
        else:
            print(f"[RESEAU] Connexion refusée pour {client_address} : Session pleine (2/2).")
            try: client_socket.sendall("HISTOIRE:[ERREUR] Le donjon est complet.\n".encode('utf-8'))
            except: pass
            client_socket.close()
            return

    if commencer_jeu:
        lancer_partie()

    while True:
        try:
            donnees = client_socket.recv(1024)
            if not donnees: break
            
            requete = donnees.decode('utf-8').strip()
            print(f"[RESEAU] Reçu de {client_address} : {requete}")
            
            # Gestion de la création de fiche
            if requete.startswith("CREATION:"):
                with verrou_fiches:
                    fiches_recues += 1
                    print(f"[JEU] Fiche de personnage reçue ({fiches_recues}/2)")
                    if fiches_recues == 2:
                        diffuser_a_tous("HISTOIRE:Fiches de personnages synchronisees\n")
            
            # Réception du choix du dilemme (ACTIVER / IGNORER)
            if requete.startswith("TRAHISON:CHOIX|"):
                parts = requete.split("|")
                choix = parts[1]
                nom_carte = parts[2]
                
                res = trahison_mgr.resoudre_choix(choix, nom_carte)
                if res:
                    diffuser_a_tous(res["texte_histoire"])
                    diffuser_a_tous("TRAHISON:NETTOYER\n")
                    # TODO: Appliquer les malus réels sur les stats du joueur cible ici
                
        except ConnectionResetError: break
        except Exception as e:
            print(f"[ERREUR] Problème durant l'écoute de {client_address} : {e}")
            break

    print(f"[RESEAU] Joueur déconnecté : {client_address}")
    with verrou_joueurs:
        if client_socket in sockets_joueurs:
            sockets_joueurs.remove(client_socket)
    client_socket.close()

def demarrer_serveur():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        serveur.bind((HOST, PORT))
        serveur.listen(2)
        print(f"===============================================")
        print(f"[SERVEUR] MJ en ligne sur le port {PORT}...")
        print(f"===============================================")
        while True:
            client_sock, client_addr = serveur.accept()
            threading.Thread(target=gerer_client, args=(client_sock, client_addr), daemon=True).start()
    except Exception as e:
        print(f"[ERREUR] Impossible de lancer le serveur : {e}")

if __name__ == "__main__":
    demarrer_serveur()
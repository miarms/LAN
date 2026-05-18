# serveur.py
import socket
import threading
import csv
import random
import os

# Configuration réseau
HOST = '0.0.0.0'
PORT = 55555

sockets_joueurs = []
verrou_joueurs = threading.Lock()

# Compteur pour la synchronisation des fiches de personnages
fiches_recues = 0
verrou_fiches = threading.Lock()

# ---------------------------------------------------------------------
# FONCTIONS UTILITAIRES / GAME DESIGN
# ---------------------------------------------------------------------
def formater_nom_fichier(nom_carte):
    """Transforme le nom brut d'une carte en nom de fichier standardisé."""
    nom = nom_carte.lower()
    nom = nom.replace(" ", "-").replace("'", "-")
    accents = {"é": "e", "è": "e", "à": "a", "ù": "u", "ç": "c", "ô": "o", "â": "a", "î": "i"}
    for original, remplace in accents.items():
        nom = nom.replace(original, remplace)
    return f"{nom}.png"

# ---------------------------------------------------------------------
# CHARGEMENT DES DECKS DEPUIS LE DOSSIER db/
# ---------------------------------------------------------------------
deck_trahisons = []
chemin_trahisons = os.path.join("db", "Jeu Mia - Trahisons.csv")

try:
    with open(chemin_trahisons, mode="r", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            if ligne.get("Nom"):
                deck_trahisons.append(ligne)
    print(f"[DATA] {len(deck_trahisons)} cartes de trahison chargées depuis db/.")
except Exception as e:
    print(f"[ERREUR] Impossible de charger le fichier dans db/ : {e}")

# ---------------------------------------------------------------------
# LOGIQUE DU JEU & PROTOCOLE
# ---------------------------------------------------------------------
def distribuer_trahisons_secretes():
    """Pioche et envoie une carte de trahison unique à chaque joueur."""
    global deck_trahisons, sockets_joueurs
    print("[JEU] Déclenchement de la distribution des coups de traître...")
    
    with verrou_joueurs:
        for i, sock in enumerate(sockets_joueurs, 1):
            if deck_trahisons:
                carte_piochee = random.choice(deck_trahisons)
                nom = carte_piochee["Nom"]
                effet = carte_piochee["Effet"]
                cout = carte_piochee["Cout"]
                fichier_img = formater_nom_fichier(nom)
                
                # Envoi de la carte secrète
                commande_carte = f"TRAHISON:RECUE|{nom}|{effet}|{cout}|{fichier_img}\n"
                try:
                    sock.sendall(commande_carte.encode('utf-8'))
                    print(f"[RESEAU] Trahison secrète envoyée au Joueur {i} : {nom}")
                    
                    # Info discrète à l'autre joueur
                    autre_sock = sockets_joueurs[1] if i == 1 else sockets_joueurs[0]
                    autre_sock.sendall("HISTOIRE:[INFO] L'autre joueur a reçu une carte face cachée...\n".encode('utf-8'))
                except Exception as ex:
                    print(f"[ERREUR] Échec de l'envoi de la carte au Joueur {i} : {ex}")

def lancer_partie():
    """Déclenche le changement d'écran chez les clients et envoie l'intro."""
    print("[JEU] Deux joueurs connectés. Lancement de l'ambiance.")
    
    # 1. SIGNAL CRUCIAL : Dit à app.py de basculer sur l'écran de création !
    diffuser_a_tous("HISTOIRE:Les deux joueurs sont presents\n")
    
    # 2. Envoi du texte d'ambiance
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
    
    # 3. Distribution des cartes de trahison
    distribuer_trahisons_secretes()

def diffuser_a_tous(message):
    """Envoie un message réseau à tous les joueurs connectés."""
    with verrou_joueurs:
        for sock in sockets_joueurs:
            try:
                sock.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"[RESEAU] Erreur de diffusion : {e}")

# ---------------------------------------------------------------------
# GESTION DES CONNEXIONS CLIENTS
# ---------------------------------------------------------------------
def gerer_client(client_socket, client_address):
    global fiches_recues
    print(f"[RESEAU] Nouvelle connexion établie depuis : {client_address}")
    
    commencer_jeu = False
    with verrou_joueurs:
        if len(sockets_joueurs) < 2:
            sockets_joueurs.append(client_socket)
            
            # Si c'est le premier joueur, on lui envoie le signal d'attente requis par app.py
            if len(sockets_joueurs) == 1:
                client_socket.sendall("HISTOIRE:En attente du second aventurier\n".encode('utf-8'))
                
            if len(sockets_joueurs) == 2:
                commencer_jeu = True
        else:
            print(f"[RESEAU] Connexion refusée pour {client_address} : Session pleine (2/2).")
            try:
                client_socket.sendall("HISTOIRE:[ERREUR] Le donjon est complet.\n".encode('utf-8'))
            except:
                pass
            client_socket.close()
            return

    if commencer_jeu:
        lancer_partie()

    # Boucle d'écoute
    while True:
        try:
            donnees = client_socket.recv(1024)
            if not donnees:
                break
            
            requete = donnees.decode('utf-8').strip()
            print(f"[RESEAU] Reçu de {client_address} : {requete}")
            
            # SIGNAL CRUCIAL : Quand un joueur valide sa fiche de perso
            if requete.startswith("CREATION:"):
                with verrou_fiches:
                    fiches_recues += 1
                    print(f"[JEU] Fiche de personnage reçue ({fiches_recues}/2)")
                    if fiches_recues == 2:
                        # Dit à app.py que tout le monde est prêt -> Bascule sur l'écran de jeu final !
                        diffuser_a_tous("HISTOIRE:Fiches de personnages synchronisees\n")
            
            if requete.startswith("UTILISER_TRAHISON"):
                pass
                
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"[ERREUR] Problème durant l'écoute de {client_address} : {e}")
            break

    print(f"[RESEAU] Joueur déconnecté : {client_address}")
    with verrou_joueurs:
        if client_socket in sockets_joueurs:
            sockets_joueurs.remove(client_socket)
    client_socket.close()

# ---------------------------------------------------------------------
# DEMARRAGE DU SERVEUR
# ---------------------------------------------------------------------
def demarrer_serveur():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        serveur.bind((HOST, PORT))
        serveur.listen(2)
        print(f"===============================================")
        print(f"[SERVEUR] MJ en ligne sur le port {PORT}...")
        print(f"[SERVEUR] En attente de braves joueurs...")
        print(f"===============================================")
    except Exception as e:
        print(f"[ERREUR] Impossible de lancer le serveur : {e}")
        return

    try:
        while True:
            client_sock, client_addr = serveur.accept()
            thread = threading.Thread(target=gerer_client, args=(client_sock, client_addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[SERVEUR] Extinction du Donjon par le MJ.")
    finally:
        serveur.close()

if __name__ == "__main__":
    demarrer_serveur()
# serveur.py
import socket
import threading
import os
import time
import random 
from managers.trahison_manager import TrahisonManager
from managers.monster_manager import MonsterManager

HOST = '192.168.1.6'
PORT = 55555

sockets_joueurs = []
verrou_joueurs = threading.Lock()
fiches_recues = 0
verrou_fiches = threading.Lock()

trahison_mgr = TrahisonManager()
monster_mgr = MonsterManager() 

stats_joueurs = {
    0: {"PV": 150, "EN": 150, "PI": 0},
    1: {"PV": 150, "EN": 150, "PI": 0}
}

# 🔥 NOUVEAU : On mémorise la récompense du monstre en cours
monstre_actuel_recompense = 0

def envoyer_mise_a_jour_stats():
    if len(sockets_joueurs) == 2:
        for i in (0, 1):
            cmd = f"STATS:PV={stats_joueurs[i]['PV']},EN={stats_joueurs[i]['EN']},PI={stats_joueurs[i]['PI']}\n"
            try: sockets_joueurs[i].sendall(cmd.encode('utf-8'))
            except: pass

def declencher_evenement_aleatoire():
    global monstre_actuel_recompense
    
    print("\n[SERVEUR] 🎲 Le MJ est en train de piocher une carte...")
    diffuser_a_tous("HISTOIRE:Le vent tourne... Le MJ pioche une nouvelle carte.\n")
    
    type_event = random.choice(["TRAHISON", "MONSTRE"])
    print(f"[SERVEUR] 🃏 Carte piochée : {type_event} !")
    
    if type_event == "TRAHISON":
        trahison_mgr.lancer_dilemme_trahison(sockets_joueurs)
    else:
        monstre = monster_mgr.tirer_monstre()
        if monstre:
            cle_nom = next(k for k in monstre.keys() if "nom" in k.lower().strip())
            nom = monstre[cle_nom]
            ca = monstre.get("CA", "10")
            pv = monstre.get("PV", "10")
            degats = monstre.get("Degats", "1d3")
            desc = monstre.get("Description", "")
            
            # 🔥 LECTURE INTELLIGENTE DU CSV 🔥
            try:
                # On cherche ta colonne exacte "Recompense_Pieces" (10 pièces par défaut si vide)
                monstre_actuel_recompense = int(monstre.get("Recompense_Pieces", 10))
            except ValueError:
                monstre_actuel_recompense = 10
                
            print(f"[SERVEUR] 🐉 Le monstre envoyé est : {nom} (Butin: {monstre_actuel_recompense} pièces)")
            msg = f"MONSTRE:{nom}|{ca}|{pv}|{degats}|{desc}\n"
            diffuser_a_tous(msg)
        else:
            trahison_mgr.lancer_dilemme_trahison(sockets_joueurs)

def lancer_partie():
    print("[JEU] Deux joueurs connectés. Lancement de l'ambiance.")
    diffuser_a_tous("HISTOIRE:Les deux joueurs sont presents\n")
    intro_texte = (
        "HISTOIRE:\n"
        "===============================================\n"
        "           LE DONJON DE LA DISCORDE            \n"
        "===============================================\n"
    )
    diffuser_a_tous(intro_texte)

def diffuser_a_tous(message):
    with verrou_joueurs:
        for sock in sockets_joueurs:
            try: sock.sendall(message.encode('utf-8'))
            except: pass

def gerer_client(client_socket, client_address):
    global fiches_recues
    global monstre_actuel_recompense # On utilise la variable ici aussi
    print(f"[RESEAU] Connexion depuis : {client_address}")
    
    commencer_jeu = False
    with verrou_joueurs:
        if len(sockets_joueurs) < 2:
            sockets_joueurs.append(client_socket)
            if len(sockets_joueurs) == 1:
                client_socket.sendall("HISTOIRE:En attente du second aventurier\n".encode('utf-8'))
            if len(sockets_joueurs) == 2:
                commencer_jeu = True
        else:
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
            
            if requete.startswith("CREATION:"):
                with verrou_fiches:
                    parts = requete.split("|")
                    if len(parts) >= 7:
                        idx = sockets_joueurs.index(client_socket)
                        stats_joueurs[idx]["PV"] = int(parts[4])
                        stats_joueurs[idx]["EN"] = int(parts[5])
                        stats_joueurs[idx]["PI"] = int(parts[6])
                    fiches_recues += 1
                    
                    if fiches_recues >= 2:
                        diffuser_a_tous("HISTOIRE:Fiches de personnages synchronisees\n")
                        diffuser_a_tous("ORDRE:START_GAME\n") 
                        threading.Timer(4.0, declencher_evenement_aleatoire).start()
                        
            # 🔥 LE CLIENT GAGNE SON BUTIN 🔥
            if requete == "FIN_COMBAT":
                idx = sockets_joueurs.index(client_socket)
                
                # On ajoute les pièces au joueur qui a achevé le monstre
                stats_joueurs[idx]["PI"] += monstre_actuel_recompense
                
                # On annonce la couleur
                diffuser_a_tous(f"HISTOIRE:⚔️ VICTOIRE ! {monstre_actuel_recompense} pièces ont été récupérées sur le monstre !\n")
                diffuser_a_tous("HISTOIRE:Le calme revient... Le donjon attend votre prochain pas.\n")
                
                envoyer_mise_a_jour_stats() # La jauge en haut à droite va monter toute seule !
                
                # On remet le butin à zéro pour le prochain monstre
                monstre_actuel_recompense = 0 
                
                threading.Timer(4.0, declencher_evenement_aleatoire).start()
            
            if requete.startswith("TRAHISON:CHOIX|"):
                parts = requete.split("|")
                res = trahison_mgr.resoudre_choix(choix=parts[1], nom_carte=parts[2])
                if res:
                    diffuser_a_tous(res["texte_histoire"])
                    diffuser_a_tous("TRAHISON:NETTOYER\n")
                    if res["choix"] == "ACTIVER":
                        id_traitre, id_victime = res["id_traitre"], res["id_victime"]
                        for cout in res["impact_cout"]: stats_joueurs[id_traitre][cout["stat"]] -= cout["val"]
                        for effet in res["impact_effet"]:
                            stats_joueurs[id_victime][effet["stat"]] -= effet["val"]
                            if effet["vol"]: stats_joueurs[id_traitre][effet["stat"]] += effet["val"]
                        for i in (0, 1):
                            for s in ("PV", "EN", "PI"):
                                if stats_joueurs[i][s] < 0: stats_joueurs[i][s] = 0
                        envoyer_mise_a_jour_stats()
                    
                    threading.Timer(4.0, declencher_evenement_aleatoire).start()
                
        except ConnectionResetError: break
        except Exception as e: print(f"[ERREUR] {e}"); break

    with verrou_joueurs:
        if client_socket in sockets_joueurs:
            sockets_joueurs.remove(client_socket)
    client_socket.close()

def demarrer_serveur():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.settimeout(1.0) 
    try:
        serveur.bind((HOST, PORT))
        serveur.listen(2)
        print(f"[SERVEUR] MJ en ligne sur le port {PORT}...")
        while True:
            try:
                client_sock, client_addr = serveur.accept()
                threading.Thread(target=gerer_client, args=(client_sock, client_addr), daemon=True).start()
            except socket.timeout: continue
    except KeyboardInterrupt: pass
    finally: serveur.close()

if __name__ == "__main__":
    demarrer_serveur()
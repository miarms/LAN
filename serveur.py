# serveur.py
import socket
import threading
import os
from managers.trahison_manager import TrahisonManager

HOST = '192.168.1.6'
PORT = 55555

sockets_joueurs = []
verrou_joueurs = threading.Lock()
fiches_recues = 0
verrou_fiches = threading.Lock()

trahison_mgr = TrahisonManager()

# Le serveur garde en mémoire les stats officielles
stats_joueurs = {
    0: {"PV": 150, "EN": 150, "PI": 0},
    1: {"PV": 150, "EN": 150, "PI": 0}
}

def envoyer_mise_a_jour_stats():
    """Diffuse l'ordre aux interfaces clients de mettre à jour les jauges."""
    if len(sockets_joueurs) == 2:
        for i in (0, 1):
            cmd = f"STATS:PV={stats_joueurs[i]['PV']},EN={stats_joueurs[i]['EN']},PI={stats_joueurs[i]['PI']}\n"
            try:
                sockets_joueurs[i].sendall(cmd.encode('utf-8'))
            except: pass

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
    trahison_mgr.lancer_dilemme_trahison(sockets_joueurs)

def diffuser_a_tous(message):
    with verrou_joueurs:
        for sock in sockets_joueurs:
            try: sock.sendall(message.encode('utf-8'))
            except Exception as e: pass

def gerer_client(client_socket, client_address):
    global fiches_recues
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
                    # Si on reçoit bien les stats du client
                    if len(parts) >= 6:
                        idx = sockets_joueurs.index(client_socket)
                        stats_joueurs[idx]["PV"] = int(parts[3])
                        stats_joueurs[idx]["EN"] = int(parts[4])
                        stats_joueurs[idx]["PI"] = int(parts[5])
                        
                    fiches_recues += 1
                    if fiches_recues == 2:
                        diffuser_a_tous("HISTOIRE:Fiches de personnages synchronisees\n")
            
            # --- RESOLUTION MATHEMATIQUE DES TRAHISONS ---
            if requete.startswith("TRAHISON:CHOIX|"):
                parts = requete.split("|")
                res = trahison_mgr.resoudre_choix(choix=parts[1], nom_carte=parts[2])
                
                if res:
                    diffuser_a_tous(res["texte_histoire"])
                    diffuser_a_tous("TRAHISON:NETTOYER\n")
                    
                    if res["choix"] == "ACTIVER":
                        id_traitre = res["id_traitre"]
                        id_victime = res["id_victime"]
                        
                        # 1. Le traître paie son ou ses coûts
                        for cout in res["impact_cout"]:
                            stats_joueurs[id_traitre][cout["stat"]] -= cout["val"]
                            
                        # 2. La victime subit les multiples effets (ex: PV et Energie)
                        for effet in res["impact_effet"]:
                            stats_joueurs[id_victime][effet["stat"]] -= effet["val"]
                            
                            # Si c'est un vol, le montant déduit est reversé au traître
                            if effet["vol"]:
                                stats_joueurs[id_traitre][effet["stat"]] += effet["val"]
                        
                        # 3. Sécurité vitale : on empêche les jauges de descendre sous 0
                        for i in (0, 1):
                            for s in ("PV", "EN", "PI"):
                                if stats_joueurs[i][s] < 0: 
                                    stats_joueurs[i][s] = 0
                                    
                        # On réplique la magie sur l'interface de ton game.py !
                        envoyer_mise_a_jour_stats()
                
        except ConnectionResetError: break
        except Exception as e: print(f"[ERREUR] {e}"); break

    print(f"[RESEAU] Joueur déconnecté : {client_address}")
    with verrou_joueurs:
        if client_socket in sockets_joueurs:
            sockets_joueurs.remove(client_socket)
    client_socket.close()

def demarrer_serveur():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 1. On empêche le serveur de faire un blocage infini (1 seconde max)
    serveur.settimeout(1.0) 
    
    try:
        serveur.bind((HOST, PORT))
        serveur.listen(2)
        print(f"[SERVEUR] MJ en ligne sur le port {PORT}...")
        
        while True:
            try:
                client_sock, client_addr = serveur.accept()
                threading.Thread(target=gerer_client, args=(client_sock, client_addr), daemon=True).start()
            except socket.timeout:
                # 2. Le timeout s'active chaque seconde. 
                # Le code passe ici silencieusement et repart dans le 'while True', 
                # ce qui laisse la fenêtre ouverte pour capter ton Ctrl+C !
                continue
                
    except KeyboardInterrupt:
        # 3. Interception propre de ton Ctrl+C
        print("\n[SERVEUR] Arrêt forcé par le MJ (Ctrl+C). Coupure des connexions...")
    except Exception as e: 
        print(f"[ERREUR] : {e}")
    finally:
        # 4. On ferme proprement le port réseau pour éviter les erreurs "Address already in use" au prochain lancement
        serveur.close()
        print("[SERVEUR] Hors ligne.")

if __name__ == "__main__":
    demarrer_serveur()
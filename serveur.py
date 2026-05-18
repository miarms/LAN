import socket

PORT = 5555
SERVEUR_IP = '0.0.0.0' 

RACES = {
    "Boomer":     {"FOR": 11, "DEX": 7,  "CON": 13, "INT": 8,  "SAG": 10, "CHA": 11, "PV": 100, "ENERGIE": 100, "PIECES": 130},
    "Gen Z":      {"FOR": 8,  "DEX": 14, "CON": 8,  "INT": 13, "SAG": 8,  "CHA": 10, "PV": 90,  "ENERGIE": 110, "PIECES": 100},
    "Provincial": {"FOR": 14, "DEX": 8,  "CON": 14, "INT": 9,  "SAG": 9,  "CHA": 6,  "PV": 110, "ENERGIE": 100, "PIECES": 100},
    "Urbain":     {"FOR": 10, "DEX": 15, "CON": 9,  "INT": 10, "SAG": 6,  "CHA": 10, "PV": 100, "ENERGIE": 90,  "PIECES": 100},
    "Tanguy":     {"FOR": 9,  "DEX": 12, "CON": 10, "INT": 14, "SAG": 8,  "CHA": 7,  "PV": 100, "ENERGIE": 100, "PIECES": 60},
    "Karen":      {"FOR": 10, "DEX": 9,  "CON": 12, "INT": 6,  "SAG": 6,  "CHA": 17, "PV": 100, "ENERGIE": 100, "PIECES": 110},
    "Chill Guy":  {"FOR": 8,  "DEX": 6,  "CON": 13, "INT": 10, "SAG": 15, "CHA": 8,  "PV": 110, "ENERGIE": 90,  "PIECES": 100}
}

CLASSES = {
    "Syndicaliste":    {"FOR": 2, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 20,  "ENERGIE": -10, "PIECES": 0},
    "Influenceur":     {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 2, "PV": 0,   "ENERGIE": 0,   "PIECES": 10},
    "Gourou":          {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 2, "CHA": 0, "PV": 0,   "ENERGIE": 10,  "PIECES": 0},
    "Bobo Ecolo":      {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 2, "CHA": 0, "PV": 10,  "ENERGIE": 0,   "PIECES": -10},
    "Fils de":         {"FOR": 0, "DEX": 0, "CON": 0, "INT": 0, "SAG": 0, "CHA": 2, "PV": 0,   "ENERGIE": 0,   "PIECES": 30},
    "Cadre Superieur": {"FOR": 0, "DEX": 0, "CON": 2, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10,  "ENERGIE": 10,  "PIECES": 0},
    "Consultant":      {"FOR": 0, "DEX": 0, "CON": 0, "INT": 2, "SAG": 0, "CHA": 0, "PV": -10, "ENERGIE": 20,  "PIECES": 0},
    "Adepte de Yoga":  {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 0,   "ENERGIE": 20,  "PIECES": -10},
    "Stagiaire":       {"FOR": 0, "DEX": 0, "CON": 0, "INT": 2, "SAG": 0, "CHA": 0, "PV": 0,   "ENERGIE": 0,   "PIECES": -20},
    "Leche-botte":     {"FOR": 0, "DEX": 0, "CON": 2, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10,  "ENERGIE": 0,   "PIECES": 10},
    "Teletravailleur": {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 10,  "ENERGIE": 0,   "PIECES": 0},
    "Commercial":      {"FOR": 0, "DEX": 2, "CON": 0, "INT": 0, "SAG": 0, "CHA": 0, "PV": 0,   "ENERGIE": -10, "PIECES": 20}
}

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind((SERVEUR_IP, PORT))
serveur.listen(2)

print(f"[LAN] Serveur en attente sur le port {PORT}...")

sockets_joueurs = []
while len(sockets_joueurs) < 2:
    client_socket, client_address = serveur.accept()
    client_socket.sendall(b"En attente du second aventurier...\n")
    sockets_joueurs.append(client_socket)

print("[GAME] Les deux joueurs sont connectes. Notification envoyee.")
for sock in sockets_joueurs:
    sock.sendall(b"Les deux joueurs sont presents. Debut de la partie.\n")

fiches_personnages = {}

# Le serveur se met en attente des paquets de création des deux clients
for i, sock in enumerate(sockets_joueurs, 1):
    print(f"[ATTENTE] En attente de la fiche du Joueur {i}...")
    try:
        donnees = sock.recv(1024).decode('utf-8').strip()
        if donnees.startswith("CREATION:"):
            # Dépaquetage du format : CREATION:pseudo|race|classe
            payload = donnees.replace("CREATION:", "")
            pseudo, race, classe = payload.split("|")
            
            stats_r = RACES[race]
            stats_c = CLASSES[classe]
            
            fiches_personnages[i] = {
                "pseudo": pseudo, "race": race, "classe": classe,
                "PV": stats_r["PV"] + stats_c["PV"], 
                "ENERGIE": stats_r["ENERGIE"] + stats_c["ENERGIE"], 
                "PIECES": stats_r["PIECES"] + stats_c["PIECES"]
            }
            print(f"[SUCCES] Personnage Joueur {i} valide : {pseudo} ({race} {classe})")
    except Exception as e:
        print(f"[ERREUR] Perte de connexion avec le Joueur {i} : {e}")

print("\n[GAME] Toutes les fiches de personnages sont enregistrees :")
print(fiches_personnages)

for sock in sockets_joueurs:
    sock.sendall(b"Fiches de personnages synchronisees avec succes ! Fin de la demo.\n")
    sock.close()
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

def poser_question(socket_joueur, texte_question):
    socket_joueur.sendall(f"\n{texte_question} --> ".encode('utf-8'))
    return socket_joueur.recv(1024).decode('utf-8').strip()

# Diffusion d'un message à TOUS les joueurs en même temps
def diffuser(liste_sockets, message):
    for sock in liste_sockets:
        sock.sendall(f"{message}\n".encode('utf-8'))

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind((SERVEUR_IP, PORT))
serveur.listen(2)

print(f"[LAN] Serveur en attente sur le port {PORT}...")

sockets_joueurs = []
while len(sockets_joueurs) < 2:
    client_socket, client_address = serveur.accept()
    client_socket.sendall(b"Connecte ! En attente du second aventurier...\n")
    sockets_joueurs.append(client_socket)

print("[GAME] Lancement de la creation de personnage...")
fiches_personnages = {}

for i, sock in enumerate(sockets_joueurs):
    num_j = i + 1
    sock.sendall(f"\n--- CREATION DU JOUEUR {num_j} ---\n".encode('utf-8'))
    
    pseudo = poser_question(sock, "Quel est ton nom ?")
    
    liste_races = ", ".join(RACES.keys())
    sock.sendall(f"Races : {liste_races}\n".encode('utf-8'))
    race = poser_question(sock, "Choisis ta Race")
    while race not in RACES:
        race = poser_question(sock, "Race inconnue. Recommence")
        
    liste_classes = ", ".join(CLASSES.keys())
    sock.sendall(f"Classes : {liste_classes}\n".encode('utf-8'))
    classe = poser_question(sock, "Choisis ta Classe")
    while classe not in CLASSES:
        classe = poser_question(sock, "Classe inconnue. Recommence")

    stats_r = RACES[race]
    stats_c = CLASSES[classe]
    
    fiches_personnages[num_j] = {
        "pseudo": pseudo, "race": race, "classe": classe,
        "FOR": stats_r["FOR"] + stats_c["FOR"], "DEX": stats_r["DEX"] + stats_c["DEX"],
        "CON": stats_r["CON"] + stats_c["CON"], "INT": stats_r["INT"] + stats_c["INT"],
        "SAG": stats_r["SAG"] + stats_c["SAG"], "CHA": stats_r["CHA"] + stats_c["CHA"],
        "PV": stats_r["PV"] + stats_c["PV"], "ENERGIE": stats_r["ENERGIE"] + stats_c["ENERGIE"],
        "PIECES": stats_r["PIECES"] + stats_c["PIECES"],
    }
    
    f = fiches_personnages[num_j]
    recap = f"\n[FICHE] {pseudo} ({race} {classe})\nStats: FOR:{f['FOR']} DEX:{f['DEX']} CON:{f['CON']} INT:{f['INT']} SAG:{f['SAG']} CHA:{f['CHA']}\nJauges: PV:{f['PV']} ENERGIE:{f['ENERGIE']} PIECES:{f['PIECES']}\n"
    sock.sendall(recap.encode('utf-8'))
    sock.sendall(b"Attente de l'autre joueur...\n")

# =========================================================================
#  PIÈCE 1 : LE DONJON DE LA DISCORDE COMMENCE COMMENCE ICI !
# =========================================================================
diffuser(sockets_joueurs, "\n" + "="*50)
diffuser(sockets_joueurs, "       PIECE 1 : LA DISPUTE DU BUS BONDÉ")
diffuser(sockets_joueurs, "="*50 + "\n")

desc = ("Le serveur (MJ) plante le décor :\n"
        "Vous êtes ensemble dans un bus à 8h30. Il fait 40°C, l'odeur est suspecte.\n"
        "SOUDAIN, un unique siège se libère. Il n'y en aura pas pour tout le monde.\n"
        "Si personne ne s'assoit, une intelligence artificielle (Un PNJ Boomer) va le prendre.")
diffuser(sockets_joueurs, desc)

# Tour du Joueur 1
j1_nom = fiches_personnages[1]["pseudo"]
diffuser(sockets_joueurs, f"\n[TOUR DE {j1_nom}]")
sockets_joueurs[1].sendall(b"En attente de l'action du Joueur 1...\n")

choix_j1 = poser_question(
    sockets_joueurs[0], 
    "Que fais-tu ? (Options: 1-Foncer sur le siege [DEX] / 2-Laisser la place à ton pote)"
)

# Tour du Joueur 2
j2_nom = fiches_personnages[2]["pseudo"]
diffuser(sockets_joueurs, f"\n[TOUR DE {j2_nom}]")
sockets_joueurs[0].sendall(b"En attente de l'action du Joueur 2...\n")

choix_j2 = poser_question(
    sockets_joueurs[1], 
    "Que fais-tu ? (Options: 1-Foncer sur le siege [DEX] / 2-S'en foutre et scroller)"
)

# Résolution des choix par le serveur (Le MJ calcule)
diffuser(sockets_joueurs, "\n--- RÉSOLUTION DU MJ ---")
if choix_j1 == "1" and choix_j2 == "1":
    diffuser(sockets_joueurs, f"⚔️ {j1_nom} et {j2_nom} se sont jetés sur le même siège ! C'est le choc.")
    # On fait perdre 10 PV à cause du choc physique
    fiches_personnages[1]["PV"] -= 10
    fiches_personnages[2]["PV"] -= 10
    diffuser(sockets_joueurs, f"Résultat : Vous perdez tous les deux 10 PV. Le PNJ s'est assis pendant votre bagarre.")
elif choix_j1 == "1" and choix_j2 != "1":
    diffuser(sockets_joueurs, f"👑 {j1_nom} a profité du calme de {j2_nom} pour piquer la place ! Sa jauge d'Énergie remonte de 20.")
    fiches_personnages[1]["ENERGIE"] += 20
else:
    diffuser(sockets_joueurs, "🛋️ Vous avez été trop lents ou trop gentils. Un PNJ a pris le siège en ricanant.")

# Affichage des jauges mises à jour pour finir le test
diffuser(sockets_joueurs, f"\nÉtat final -> {j1_nom} (PV:{fiches_personnages[1]['PV']}, Énergie:{fiches_personnages[1]['ENERGIE']}) | {j2_nom} (PV:{fiches_personnages[2]['PV']}, Énergie:{fiches_personnages[2]['ENERGIE']})")

# Maintenant on peut fermer proprement
for sock in sockets_joueurs:
    sock.sendall(b"\nFin de la demo ! Le donjon ferme ses portes.\n")
    sock.close()
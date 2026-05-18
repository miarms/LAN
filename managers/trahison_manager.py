# managers/trahison_manager.py
import csv
import random
import os

class TrahisonManager:
    def __init__(self, chemin_csv=None):
        if chemin_csv is None:
            # Cherche le dossier db/ à la racine du projet
            chemin_csv = os.path.join("db", "Jeu Mia - Trahisons.csv")
        self.chemin_csv = chemin_csv
        self.deck_trahisons = []
        self.trahison_en_cours = None  # Stocke le dilemme actif
        self.charger_deck()

    def charger_deck(self):
        """Charge le fichier CSV des coups de traître."""
        try:
            with open(self.chemin_csv, mode="r", encoding="utf-8") as f:
                lecteur = csv.DictReader(f)
                for ligne in lecteur:
                    if ligne.get("Nom"):
                        self.deck_trahisons.append(ligne)
            print(f"[TRAHISON] {len(self.deck_trahisons)} cartes chargées avec succès.")
        except Exception as e:
            print(f"[TRAHISON] [ERREUR] Impossible de charger le CSV : {e}")

    def formater_nom_fichier(self, nom_carte):
        """Règle de nommage automatique pour les images des cartes."""
        nom = nom_carte.lower().replace(" ", "-").replace("'", "-")
        accents = {"é": "e", "è": "e", "à": "a", "ù": "u", "ç": "c", "ô": "o", "â": "a", "î": "i"}
        for original, remplace in accents.items():
            nom = nom.replace(original, remplace)
        return f"{nom}.png"

    def lancer_dilemme_trahison(self, sockets_joueurs):
        """
        Sélectionne une carte, désigne un traître au hasard,
        et envoie les deux visions différentes (Face Découverte / Face Cachée).
        """
        if not self.deck_trahisons or len(sockets_joueurs) < 2:
            return

        # 1. Pioche d'une carte au hasard
        carte = random.choice(self.deck_trahisons)
        
        # 2. Attribution des rôles (0 pour Joueur 1, 1 pour Joueur 2)
        index_traitre = random.randint(0, 1)
        index_victime = 1 if index_traitre == 0 else 0
        
        sock_traitre = sockets_joueurs[index_traitre]
        sock_victime = sockets_joueurs[index_victime]

        # Sauvegarde de la trahison active pour valider le choix plus tard
        self.trahison_en_cours = {
            "carte": carte,
            "index_traitre": index_traitre,
            "index_victime": index_victime,
            "sock_traitre": sock_traitre,
            "sock_victime": sock_victime
        }

        fichier_img = self.formater_nom_fichier(carte["Nom"])

        # 3. Envoi au Traître (TRAHISON:DECOUVERTE)
        msg_traitre = f"TRAHISON:DECOUVERTE|{carte['Nom']}|{carte['Effet']}|{carte['Cout']}|{fichier_img}\n"
        sock_traitre.sendall(msg_traitre.encode('utf-8'))

        # 4. Envoi à la Victime (TRAHISON:CACHEE)
        msg_victime = f"TRAHISON:CACHEE|{carte['Nom']}\n"
        sock_victime.sendall(msg_victime.encode('utf-8'))
        
        print(f"[TRAHISON] Dilemme lancé. Joueur {index_traitre + 1} est le traître avec '{carte['Nom']}'.")

    def resoudre_choix(self, choix, nom_carte):
        """
        Gère la réponse du traître (ACTIVER ou IGNORER) 
        et retourne les textes ou modifications de stats associés.
        """
        if not self.trahison_en_cours or self.trahison_en_cours["carte"]["Nom"] != nom_carte:
            return None

        carte = self.trahison_en_cours["carte"]
        j_traitre = self.trahison_en_cours["index_traitre"] + 1
        j_victime = self.trahison_en_cours["index_victime"] + 1

        resultat = {
            "choix": choix,
            "effet_technique": carte["Effet"],
            "cout": carte["Cout"],
            "index_victime": self.trahison_en_cours["index_victime"],
            "index_traitre": self.trahison_en_cours["index_traitre"]
        }

        if choix == "ACTIVER":
            resultat["texte_histoire"] = (
                f"HISTOIRE:⚡ [TRAHISON] Le Joueur {j_traitre} a décidé d'activer la carte : {carte['Nom']} !\n"
                f"HISTOIRE:💀 Effet appliqué sur le Joueur {j_victime} : {carte['Effet']} (Coût : {carte['Cout']})\n"
            )
        else:
            resultat["texte_histoire"] = (
                f"HISTOIRE:🚫 [INFO] Le Joueur {j_traitre} a inspecté une carte de trahison et a choisi de l'ignorer.\n"
            )

        # On réinitialise le dilemme après résolution
        self.trahison_en_cours = None
        return resultat
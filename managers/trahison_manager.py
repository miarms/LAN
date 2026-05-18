# managers/trahison_manager.py
import csv
import random
import os
import re

class TrahisonManager:
    def __init__(self, chemin_csv=None):
        if chemin_csv is None:
            chemin_csv = os.path.join("db", "Jeu Mia - Trahisons.csv")
        self.chemin_csv = chemin_csv
        self.deck_trahisons = []
        self.trahison_en_cours = None
        self.charger_deck()

    def charger_deck(self):
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
        nom = nom_carte.lower().replace(" ", "-").replace("'", "-")
        accents = {"é": "e", "è": "e", "à": "a", "ù": "u", "ç": "c", "ô": "o", "â": "a", "î": "i"}
        for original, remplace in accents.items():
            nom = nom.replace(original, remplace)
        return f"{nom}.png"

    def analyser_texte_stats(self, texte):
        """Extrait intelligemment TOUTES les modifications de stats d'une phrase."""
        impacts = []
        if not texte or texte.lower() == "0 cout": 
            return impacts
            
        texte_min = texte.lower()
        
        # Le regex [-+]? ignore les signes. match.group(1) sera TOUJOURS positif.
        # --- ÉNERGIE ---
        match_en = re.search(r'[-+]?\s*(\d+)\s*(energie|énergie)', texte_min)
        if match_en:
            impacts.append({"stat": "EN", "val": int(match_en.group(1))})
            
        # --- PV ---
        match_pv = re.search(r'[-+]?\s*(\d+)\s*(pv|vie)', texte_min)
        if match_pv:
            impacts.append({"stat": "PV", "val": int(match_pv.group(1))})
            
        # --- PIÈCES ---
        match_pi = re.search(r'[-+]?\s*(\d+)\s*(piece|pièce|or|pièces)', texte_min)
        if match_pi:
            impacts.append({"stat": "PI", "val": int(match_pi.group(1))})
            
        # --- DÉTECTION DU VOL ---
        mots_vol = ["vole", "prend", "donne", "paie"]
        est_un_vol = any(mot in texte_min for mot in mots_vol)
        
        for imp in impacts:
            imp["vol"] = est_un_vol
            
        return impacts

    def lancer_dilemme_trahison(self, sockets_joueurs):
        if not self.deck_trahisons or len(sockets_joueurs) < 2: return

        carte = random.choice(self.deck_trahisons)
        index_traitre = random.randint(0, 1)
        index_victime = 1 if index_traitre == 0 else 0
        
        self.trahison_en_cours = {
            "carte": carte,
            "index_traitre": index_traitre,
            "index_victime": index_victime,
            "sock_traitre": sockets_joueurs[index_traitre],
            "sock_victime": sockets_joueurs[index_victime]
        }

        fichier_img = self.formater_nom_fichier(carte["Nom"])
        msg_traitre = f"TRAHISON:DECOUVERTE|{carte['Nom']}|{carte['Effet']}|{carte['Cout']}|{fichier_img}\n"
        self.trahison_en_cours["sock_traitre"].sendall(msg_traitre.encode('utf-8'))

        msg_victime = f"TRAHISON:CACHEE|{carte['Nom']}\n"
        self.trahison_en_cours["sock_victime"].sendall(msg_victime.encode('utf-8'))

    def resoudre_choix(self, choix, nom_carte):
        if not self.trahison_en_cours or self.trahison_en_cours["carte"]["Nom"] != nom_carte:
            return None

        carte = self.trahison_en_cours["carte"]
        id_traitre = self.trahison_en_cours["index_traitre"]
        id_victime = self.trahison_en_cours["index_victime"]

        resultat = {
            "choix": choix,
            "id_traitre": id_traitre,
            "id_victime": id_victime,
            "impact_cout": [],
            "impact_effet": []
        }

        if choix == "ACTIVER":
            resultat["impact_cout"] = self.analyser_texte_stats(carte["Cout"])
            resultat["impact_effet"] = self.analyser_texte_stats(carte["Effet"])
            
            resultat["texte_histoire"] = (
                f"HISTOIRE:⚡ [COUP BAS] Le Joueur {id_traitre + 1} a activé : {carte['Nom']} !\n"
                f"HISTOIRE:💀 Conséquence : {carte['Effet']}\n"
            )
        else:
            resultat["texte_histoire"] = f"HISTOIRE:🚫 [ESQUIVE] Une tentative de coup bas a été abandonnée...\n"

        self.trahison_en_cours = None
        return resultat
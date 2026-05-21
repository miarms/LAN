# managers/monster_manager.py
import csv
import random
import os

class MonsterManager:
    def __init__(self):
        self.chemin_csv = os.path.join("db", "Jeu Mia - Monstres.csv")
        self.monstres = []
        self.charger_monstres()

    def charger_monstres(self):
        if not os.path.exists(self.chemin_csv):
            print(f"[SERVEUR] [ERREUR] Fichier introuvable: {self.chemin_csv}")
            return
            
        lignes_nettoyees = []
        with open(self.chemin_csv, mode='r', encoding='utf-8-sig') as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne: continue
                if ligne.startswith('"') and ligne.endswith('"') and ligne.count('"') >= 2:
                    ligne = ligne[1:-1].replace('""', '"')
                lignes_nettoyees.append(ligne)
                
        if not lignes_nettoyees: return
        separateur = ';' if ';' in lignes_nettoyees[0] else ','
        reader = csv.DictReader(lignes_nettoyees, delimiter=separateur)
        
        for row in reader:
            cle_nom = next((k for k in row.keys() if k and "nom" in k.lower().strip()), None)
            if cle_nom and row.get(cle_nom):
                self.monstres.append(row)
                
        print(f"[SERVEUR] {len(self.monstres)} Monstres chargés pour le MJ.")

    def tirer_monstre(self):
        if not self.monstres: return None
        return random.choice(self.monstres)
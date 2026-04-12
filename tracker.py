import json
import os
from datetime import datetime, timedelta

# Configuration du fichier de sauvegarde
FICHIER_DATA = "data.json"

def charger_donnees():
    if os.path.exists(FICHIER_DATA):
        try:
            with open(FICHIER_DATA, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def sauvegarder_donnees(date_str, cycle):
    data = {"derniere_date": date_str, "duree_cycle": cycle}
    with open(FICHIER_DATA, "w") as f:
        json.dump(data, f)
    print("✅ Données sauvegardées !")

# --- DEBUT DU PROGRAMME ---
print("--- 🌸 Bienvenue dans ton Tracker de Cycle 🌸 ---")

donnees = charger_donnees()

if donnees:
    print("📖 Données récupérées de la dernière session.")
    derniere_date = datetime.strptime(donnees["derniere_date"], "%Y-%m-%d")
    duree_cycle = donnees["duree_cycle"]
    
    # Option pour réinitialiser si on veut changer de cycle
    choix = input("Voulez-vous mettre à jour vos données ? (o/n) : ").lower()
    if choix == 'o':
        donnees = None # On force la redemande ci-dessous

if not donnees:
    # --- SAISIE UTILISATRICE ---
    while True:
        date_input = input("Entrez le 1er jour de vos dernières règles (JJ/MM/AAAA) : ")
        try:
            derniere_date = datetime.strptime(date_input, "%d/%m/%Y")
            break
        except ValueError:
            print("❌ Format incorrect (ex: 20/05/2024).")

    while True:
        try:
            duree_cycle = int(input("Durée moyenne de votre cycle (ex: 28) : "))
            break
        except ValueError:
            print("❌ Merci d'entrer un nombre entier.")
    
    # Sauvegarde immédiate
    sauvegarder_donnees(derniere_date.strftime("%Y-%m-%d"), duree_cycle)

# --- CALCULS ET AFFICHAGE ---
aujourdhui = datetime.now()
jours_ecoules = (aujourdhui - derniere_date).days
prochaine_date = derniere_date + timedelta(days=duree_cycle)

print("\n" + "="*35)
print(f"📍 Aujourd'hui : {aujourdhui.strftime('%d/%m/%Y')}")
print(f"📅 Jour du cycle : {jours_ecoules + 1}")
print(f"🚀 Prochaines règles : {prochaine_date.strftime('%d/%m/%Y')}")

# Logique des phases
if jours_ecoules < 0:
    print("Statut : La date est dans le futur !")
elif jours_ecoules <= 5:
    print("Statut : Phase Menstruelle 🩸")
elif jours_ecoules <= 13:
    print("Statut : Phase Folliculaire ✨")
elif jours_ecoules == 14:
    print("Statut : Ovulation 🥚 (Fertilité maximale)")
elif jours_ecoules <= duree_cycle:
    print("Statut : Phase Lutéale 🌙")
else:
    retard = jours_ecoules - duree_cycle
    print(f"Statut : Cycle terminé depuis {retard} jour(s). Nouveau cycle attendu !")
print("="*35)
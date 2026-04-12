from datetime import datetime, timedelta

print("--- Bienvenue dans ton Tracker de Cycle ---")

# 1. On demande la date à l'utilisatrice avec un format précis
while True:
    date_input = input("Entrez le 1er jour de vos dernières règles (JJ/MM/AAAA) : ")
    try:
        # On transforme le texte en objet 'datetime'
        derniere_date = datetime.strptime(date_input, "%d/%m/%Y")
        break # Si ça marche, on sort de la boucle
    except ValueError:
        print("Format incorrect. Merci d'utiliser le format Jour/Mois/Année (ex: 20/05/2024).")

# 2. On demande la durée du cycle (avec la sécurité qu'on a apprise !)
while True:
    try:
        duree_cycle = int(input("Durée moyenne de votre cycle (ex: 28) : "))
        break
    except ValueError:
        print("Merci d'entrer un nombre entier.")

# 3. Les calculs
prochaine_date = derniere_date + timedelta(days=duree_cycle)
ovulation = derniere_date + timedelta(days=duree_cycle - 14)

print("\n" + "="*30)
print(f"RÉSUMÉ POUR LE CYCLE DU {derniere_date.strftime('%d %B %Y')}")
print(f"📅 Prochaines règles : {prochaine_date.strftime('%d/%m/%Y')}")
print(f"🥚 Ovulation estimée : {ovulation.strftime('%d/%m/%Y')}")
print("="*30)
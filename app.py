import customtkinter as ctk
import json
import os
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌸 Mon Tracker de Cycle")
        self.geometry("400x550")
        self.fichier_data = "data.json"

        # --- TITRE ---
        self.label_titre = ctk.CTkLabel(self, text="Mon Tracker", font=("Arial", 24, "bold"))
        self.label_titre.pack(pady=20)

        # --- INPUTS ---
        self.entry_date = ctk.CTkEntry(self, placeholder_text="Date (JJ/MM/AAAA)")
        self.entry_date.pack(pady=10)
        
        self.entry_cycle = ctk.CTkEntry(self, placeholder_text="Durée cycle (ex: 28)")
        self.entry_cycle.pack(pady=10)

        self.btn_save = ctk.CTkButton(self, text="Enregistrer & Calculer", command=self.action_calculer)
        self.btn_save.pack(pady=20)

        # --- AFFICHAGE ---
        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.label_status = ctk.CTkLabel(self.result_frame, text="Entrez vos données", font=("Arial", 16))
        self.label_status.pack(pady=20)

        self.label_prochaine = ctk.CTkLabel(self.result_frame, text="", font=("Arial", 14))
        self.label_prochaine.pack(pady=5)

        # Charger les données au démarrage
        self.charger_et_afficher()

    def charger_et_afficher(self):
        if os.path.exists(self.fichier_data):
            with open(self.fichier_data, "r") as f:
                data = json.load(f)
                self.calculer_logique(data["derniere_date"], data["duree_cycle"])

    def action_calculer(self):
        date_str = self.entry_date.get()
        cycle_str = self.entry_cycle.get()
        
        try:
            # Validation de la date
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            cycle_int = int(cycle_str)
            
            # Sauvegarde
            with open(self.fichier_data, "w") as f:
                json.dump({"derniere_date": date_obj.strftime("%Y-%m-%d"), "duree_cycle": cycle_int}, f)
            
            self.calculer_logique(date_obj.strftime("%Y-%m-%d"), cycle_int)
        except ValueError:
            self.label_status.configure(text="❌ Erreur de format !")

    def calculer_logique(self, date_brute, duree_cycle):
        derniere_date = datetime.strptime(date_brute, "%Y-%m-%d")
        aujourdhui = datetime.now()
        
        jours_totaux = (aujourdhui - derniere_date).days
        jour_actuel = (jours_totaux % duree_cycle) + 1
        prochaine = derniere_date + timedelta(days=((jours_totaux // duree_cycle) + 1) * duree_cycle)

        self.label_status.configure(text=f"Jour du cycle : {jour_actuel}")
        self.label_prochaine.configure(text=f"Prochaines règles : {prochaine.strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()
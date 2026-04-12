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

        self.entry_regles_duree = ctk.CTkEntry(self, placeholder_text="Durée des règles (ex: 5)")
        self.entry_regles_duree.pack(pady=10)

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

    def calculer_logique(self, date_brute, duree_cycle, duree_regles=5):
        derniere_date = datetime.strptime(date_brute, "%Y-%m-%d")
        aujourdhui = datetime.now()
        
        # Calculs de base
        jours_totaux = (aujourdhui - derniere_date).days
        nb_cycles_passes = jours_totaux // duree_cycle
        debut_cycle_actuel = derniere_date + timedelta(days=nb_cycles_passes * duree_cycle)
        jour_actuel = (jours_totaux % duree_cycle) + 1
        
        # Dates des phases
        fin_regles = debut_cycle_actuel + timedelta(days=duree_regles - 1)
        ovulation = debut_cycle_actuel + timedelta(days=duree_cycle - 14)
        prochaine = debut_cycle_actuel + timedelta(days=duree_cycle)

        # --- LOGIQUE DE COULEUR ---
        couleur_statut = "white" # Par défaut
        message_statut = f"Jour du cycle : {jour_actuel}"

        if debut_cycle_actuel <= aujourdhui <= fin_regles:
            couleur_statut = "#FF4B4B" # Rouge/Rose vif pour les règles
            message_statut += " 🩸 (Période de règles)"
        elif (ovulation - timedelta(days=2)) <= aujourdhui <= (ovulation + timedelta(days=1)):
            couleur_statut = "#FFD700" # Or pour la fertilité haute
            message_statut += " 🥚 (Fenêtre de fertilité)"
        
        # Mise à jour des labels
        self.label_status.configure(text=message_statut, text_color=couleur_statut)
        
        texte_phases = (
            f"🩸 Règles : du {debut_cycle_actuel.strftime('%d/%m')} au {fin_regles.strftime('%d/%m')}\n"
            f"✨ Phase Folliculaire : jusqu'au {ovulation.strftime('%d/%m')}\n"
            f"🥚 Ovulation : {ovulation.strftime('%d/%m')}\n"
            f"🌙 Phase Lutéale : dès le {(ovulation + timedelta(days=1)).strftime('%d/%m')}\n"
            f"🚀 Prochaines règles : {prochaine.strftime('%d/%m')}"
        )
        self.label_prochaine.configure(text=texte_phases, justify="left")

if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()
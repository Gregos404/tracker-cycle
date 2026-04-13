import customtkinter as ctk
import json
import os
import calendar
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONSEILS_PHASES = {
    "Menstruelle": {"titre": "🩸 Phase Menstruelle", "conseil": "Repos & Fer (lentilles, épinards).", "couleur": "#FF4B4B"},
    "Folliculaire": {"titre": "✨ Phase Folliculaire", "conseil": "Créativité & Nouveaux projets.", "couleur": "#85D2FF"},
    "Ovulation": {"titre": "🥚 Ovulation", "conseil": "Force physique & Aliments frais.", "couleur": "#FFD700"},
    "Lutéale": {"titre": "🌙 Phase Lutéale", "conseil": "Ancrage & Glucides complexes.", "couleur": "#BA85FF"}
}

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌸 Mon Tracker Pro")
        self.geometry("450x850") # Fenêtre plus grande pour le calendrier
        self.fichier_data = "data.json"
        self.fichier_historique = "Mon Calendrier-2026-04-13.txt"

        # --- TITRE & INPUTS ---
        ctk.CTkLabel(self, text="Mon Calendrier Cycle", font=("Arial", 22, "bold")).pack(pady=15)
        
        self.entry_date = ctk.CTkEntry(self, placeholder_text="Date (JJ/MM/AAAA)")
        self.entry_date.pack(pady=5)
        
        moyenne = self.analyser_historique_reel()
        self.entry_cycle = ctk.CTkEntry(self, placeholder_text=f"Cycle (Moyenne: {moyenne})")
        self.entry_cycle.insert(0, str(moyenne))
        self.entry_cycle.pack(pady=5)

        self.entry_regles_duree = ctk.CTkEntry(self, placeholder_text="Durée règles")
        self.entry_regles_duree.insert(0, "5")
        self.entry_regles_duree.pack(pady=5)

        ctk.CTkButton(self, text="Calculer & Visualiser", command=self.action_calculer).pack(pady=15)

        # --- ZONE CALENDRIER ---
        self.cal_container = ctk.CTkFrame(self, fg_color="#2B2B2B")
        self.cal_container.pack(pady=10, padx=20, fill="x")
        self.labels_jours = [] # Pour stocker les cases du calendrier

        # --- STATUS & CONSEILS ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Arial", 16, "bold"))
        self.label_status.pack(pady=5)
        
        self.advice_frame = ctk.CTkFrame(self, border_width=1)
        self.advice_frame.pack(pady=10, padx=20, fill="x")
        self.label_advice_titre = ctk.CTkLabel(self.advice_frame, text="", font=("Arial", 14, "bold"))
        self.label_advice_titre.pack(pady=5)
        self.label_advice_texte = ctk.CTkLabel(self.advice_frame, text="", wraplength=380)
        self.label_advice_texte.pack(pady=5, padx=10)

        self.charger_et_afficher()

    def dessiner_calendrier(self, debut_cycle, duree_cycle, duree_regles):
        # Nettoyer l'ancien calendrier
        for widget in self.cal_container.winfo_children():
            widget.destroy()

        maintenant = datetime.now()
        cal = calendar.monthcalendar(maintenant.year, maintenant.month)
        noms_jours = ["L", "M", "M", "J", "V", "S", "D"]

        # En-tête des jours
        for i, jour in enumerate(noms_jours):
            ctk.CTkLabel(self.cal_container, text=jour, width=40, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=2, pady=2)

        # Calcul des dates charnières
        fin_regles = debut_cycle + timedelta(days=duree_regles - 1)
        ovulation_j = debut_cycle + timedelta(days=duree_cycle - 14)
        debut_luteale = ovulation_j + timedelta(days=1)

        for r, semaine in enumerate(cal):
            for c, jour in enumerate(semaine):
                if jour == 0: continue 
                
                date_jour = datetime(maintenant.year, maintenant.month, jour)
                bg_color = "#3D3D3D" # Gris par défaut
                text_color = "white"
                border_width = 0
                border_color = None

                # 1. Attribution des couleurs par phase
                if debut_cycle <= date_jour <= fin_regles:
                    bg_color = CONSEILS_PHASES["Menstruelle"]["couleur"]
                elif fin_regles < date_jour < (ovulation_j - timedelta(days=2)):
                    bg_color = CONSEILS_PHASES["Folliculaire"]["couleur"]
                    text_color = "black"
                elif (ovulation_j - timedelta(days=2)) <= date_jour <= (ovulation_j + timedelta(days=1)):
                    bg_color = CONSEILS_PHASES["Ovulation"]["couleur"]
                    text_color = "black"
                elif (ovulation_j + timedelta(days=1)) < date_jour < (debut_cycle + timedelta(days=duree_cycle)):
                    bg_color = CONSEILS_PHASES["Lutéale"]["couleur"]

                # 2. Surlignage du jour actuel (Bordure blanche épaisse)
                if date_jour.date() == maintenant.date():
                    border_width = 2
                    border_color = "white"

                # VERSION CORRIGÉE : Uniquement le CTkButton pour supporter les bordures
                case = ctk.CTkButton(self.cal_container, 
                                     text=str(jour), 
                                     width=45, 
                                     height=45, 
                                     fg_color=bg_color, 
                                     text_color=text_color, 
                                     hover=False,           # Désactive l'effet au survol
                                     corner_radius=5, 
                                     border_width=border_width, 
                                     border_color=border_color)
                case.grid(row=r+1, column=c, padx=2, pady=2)

    def calculer_logique(self, date_brute, duree_cycle, duree_regles):
        derniere_date = datetime.strptime(date_brute, "%Y-%m-%d")
        aujourdhui = datetime.now()
        
        jours_totaux = (aujourdhui - derniere_date).days
        nb_cycles = jours_totaux // duree_cycle
        debut_actuel = derniere_date + timedelta(days=nb_cycles * duree_cycle)
        jour_actuel = (jours_totaux % duree_cycle) + 1
        
        # Dessiner le calendrier visuel
        self.dessiner_calendrier(debut_actuel, duree_cycle, duree_regles)

        # Status & Conseils
        ovulation = debut_actuel + timedelta(days=duree_cycle - 14)
        if jour_actuel <= duree_regles: phase = "Menstruelle"
        elif jour_actuel <= (duree_cycle - 15): phase = "Folliculaire"
        elif (ovulation - timedelta(days=1)) <= aujourdhui <= (ovulation + timedelta(days=1)): phase = "Ovulation"
        else: phase = "Lutéale"

        info = CONSEILS_PHASES[phase]
        self.label_status.configure(text=f"Jour {jour_actuel} - {info['titre']}", text_color=info['couleur'])
        self.label_advice_titre.configure(text=info["titre"], text_color=info["couleur"])
        self.label_advice_texte.configure(text=info["conseil"])

    # --- GARDER LES FONCTIONS ANALYSER_HISTORIQUE_REEL ET CONVERTIR_DATE_FR ICI ---
    def convertir_date_fr(self, date_str):
        mois_fr = {"janv.": "01", "févr.": "02", "mars": "03", "avr.": "04", "mai": "05", "juin": "06", "juil.": "07", "août": "08", "sept.": "09", "oct.": "10", "nov.": "11", "déc.": "12"}
        try:
            p = date_str.split(' ')
            return datetime.strptime(f"{p[0].zfill(2)}/{mois_fr.get(p[1].lower(), '01')}/{p[2]}", "%d/%m/%Y")
        except: return None

    def analyser_historique_reel(self):
        dates = []
        if os.path.exists(self.fichier_historique):
            with open(self.fichier_historique, "r", encoding="utf-8") as f:
                for l in f:
                    if "Début des règles" in l:
                        d = self.convertir_date_fr(l.split('\t')[0].strip())
                        if d: dates.append(d)
            dates.sort()
            ecarts = [(dates[i+1]-dates[i]).days for i in range(len(dates)-1) if 20 < (dates[i+1]-dates[i]).days < 45]
            if ecarts: return round(sum(ecarts)/len(ecarts))
        return 28

    def charger_et_afficher(self):
        if os.path.exists(self.fichier_data):
            with open(self.fichier_data, "r") as f:
                d = json.load(f)
                self.calculer_logique(d["derniere_date"], d["duree_cycle"], d.get("duree_regles", 5))

    def action_calculer(self):
        try:
            d_obj = datetime.strptime(self.entry_date.get(), "%d/%m/%Y")
            c_int, r_int = int(self.entry_cycle.get()), int(self.entry_regles_duree.get())
            with open(self.fichier_data, "w") as f:
                json.dump({"derniere_date": d_obj.strftime("%Y-%m-%d"), "duree_cycle": c_int, "duree_regles": r_int}, f)
            self.calculer_logique(d_obj.strftime("%Y-%m-%d"), c_int, r_int)
        except: self.label_status.configure(text="❌ Erreur format")

if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()
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
        self.title("🌸 Mon Tracker Pro V4")
        self.geometry("450x900")
        
        self.fichier_data = "data.json"
        self.fichier_historique = "Mon Calendrier-2026-04-13.txt"
        
        # --- ETAT DE NAVIGATION ---
        self.aujourdhui = datetime.now()
        self.mois_visu = self.aujourdhui.month
        self.annee_visu = self.aujourdhui.year

        # --- TITRE & INPUTS ---
        ctk.CTkLabel(self, text="Mon Calendrier Cycle", font=("Arial", 22, "bold")).pack(pady=10)
        
        self.entry_date = ctk.CTkEntry(self, placeholder_text="Date (JJ/MM/AAAA)")
        self.entry_date.pack(pady=5)
        
        moyenne = self.analyser_historique_reel()
        self.entry_cycle = ctk.CTkEntry(self, placeholder_text=f"Cycle (Moyenne: {moyenne})")
        self.entry_cycle.insert(0, str(moyenne))
        self.entry_cycle.pack(pady=5)

        self.entry_regles_duree = ctk.CTkEntry(self, placeholder_text="Durée règles")
        self.entry_regles_duree.insert(0, "5")
        self.entry_regles_duree.pack(pady=5)

        ctk.CTkButton(self, text="Enregistrer & Calculer", command=self.action_calculer).pack(pady=10)

        # --- BARRE DE NAVIGATION DU MOIS ---
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=10)

        self.btn_prev = ctk.CTkButton(self.nav_frame, text="<", width=40, command=self.mois_precedent)
        self.btn_prev.grid(row=0, column=0, padx=10)

        self.label_mois = ctk.CTkLabel(self.nav_frame, text="", font=("Arial", 18, "bold"), width=180)
        self.label_mois.grid(row=0, column=1)

        self.btn_next = ctk.CTkButton(self.nav_frame, text=">", width=40, command=self.mois_suivant)
        self.btn_next.grid(row=0, column=2, padx=10)

        # --- ZONE CALENDRIER ---
        self.cal_container = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=10)
        self.cal_container.pack(pady=5, padx=20, fill="x")

        # --- STATUS & CONSEILS ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Arial", 16, "bold"))
        self.label_status.pack(pady=10)
        
        self.advice_frame = ctk.CTkFrame(self, border_width=1)
        self.advice_frame.pack(pady=10, padx=20, fill="x")
        self.label_advice_titre = ctk.CTkLabel(self.advice_frame, text="", font=("Arial", 14, "bold"))
        self.label_advice_titre.pack(pady=5)
        self.label_advice_texte = ctk.CTkLabel(self.advice_frame, text="", wraplength=380)
        self.label_advice_texte.pack(pady=5, padx=10)

        self.charger_et_afficher()

    def mois_precedent(self):
        self.mois_visu -= 1
        if self.mois_visu == 0:
            self.mois_visu = 12
            self.annee_visu -= 1
        self.charger_et_afficher()

    def mois_suivant(self):
        self.mois_visu += 1
        if self.mois_visu == 13:
            self.mois_visu = 1
            self.annee_visu += 1
        self.charger_et_afficher()

    def dessiner_calendrier(self, derniere_date_saisie, duree_cycle, duree_regles):
        for widget in self.cal_container.winfo_children():
            widget.destroy()

        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.label_mois.configure(text=f"{mois_noms[self.mois_visu-1]} {self.annee_visu}")

        cal = calendar.monthcalendar(self.annee_visu, self.mois_visu)
        noms_jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

        for i, jour in enumerate(noms_jours):
            ctk.CTkLabel(self.cal_container, text=jour, width=45, font=("Arial", 11, "bold")).grid(row=0, column=i, pady=5)

        for r, semaine in enumerate(cal):
            for c, jour in enumerate(semaine):
                if jour == 0: continue
                
                date_ciblée = datetime(self.annee_visu, self.mois_visu, jour)
                
                # Logique pour trouver le début du cycle correspondant à cette date précise
                diff_jours = (date_ciblée - derniere_date_saisie).days
                nb_cycles = diff_jours // duree_cycle
                debut_du_cycle_pour_cette_date = derniere_date_saisie + timedelta(days=nb_cycles * duree_cycle)
                
                # Position dans le cycle
                jour_dans_cycle = (diff_jours % duree_cycle) + 1
                ovulation_j = debut_du_cycle_pour_cette_date + timedelta(days=duree_cycle - 14)
                fin_regles = debut_du_cycle_pour_cette_date + timedelta(days=duree_regles - 1)

                bg_color = "#3D3D3D"
                text_color = "white"
                border_width = 0
                border_color = None

                # Couleurs par phase
                if 1 <= jour_dans_cycle <= duree_regles:
                    bg_color = CONSEILS_PHASES["Menstruelle"]["couleur"]
                elif jour_dans_cycle < (duree_cycle - 15):
                    bg_color = CONSEILS_PHASES["Folliculaire"]["couleur"]
                    text_color = "black"
                elif (ovulation_j - timedelta(days=2)) <= date_ciblée <= (ovulation_j + timedelta(days=1)):
                    bg_color = CONSEILS_PHASES["Ovulation"]["couleur"]
                    text_color = "black"
                else:
                    bg_color = CONSEILS_PHASES["Lutéale"]["couleur"]

                # Surlignage aujourd'hui
                if date_ciblée.date() == self.aujourdhui.date():
                    border_width = 2
                    border_color = "white"

                case = ctk.CTkButton(self.cal_container, text=str(jour), width=45, height=45, fg_color=bg_color, 
                                     text_color=text_color, hover=False, corner_radius=8, 
                                     border_width=border_width, border_color=border_color)
                case.grid(row=r+1, column=c, padx=2, pady=2)

    def calculer_logique(self, date_brute, duree_cycle, duree_regles):
        derniere_date = datetime.strptime(date_brute, "%Y-%m-%d")
        
        # On redessine le calendrier avec les infos du mois visualisé
        self.dessiner_calendrier(derniere_date, duree_cycle, duree_regles)

        # Calcul pour le conseil (basé sur AUJOURD'HUI)
        jours_depuis_saisie = (self.aujourdhui - derniere_date).days
        jour_actuel = (jours_depuis_saisie % duree_cycle) + 1
        
        if jour_actuel <= duree_regles: phase = "Menstruelle"
        elif jour_actuel <= (duree_cycle - 15): phase = "Folliculaire"
        elif (duree_cycle - 16) < jour_actuel < (duree_cycle - 12): phase = "Ovulation"
        else: phase = "Lutéale"

        info = CONSEILS_PHASES[phase]
        self.label_status.configure(text=f"Aujourd'hui : Jour {jour_actuel} ({phase})", text_color=info['couleur'])
        self.label_advice_titre.configure(text=info["titre"], text_color=info["couleur"])
        self.label_advice_texte.configure(text=info["conseil"])

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
            # Réinitialiser la vue sur le mois de la saisie
            self.mois_visu = d_obj.month
            self.annee_visu = d_obj.year
            self.calculer_logique(d_obj.strftime("%Y-%m-%d"), c_int, r_int)
        except: self.label_status.configure(text="❌ Erreur format")

if __name__ == "__main__":
    app = TrackerApp()
    app.mainloop()
import customtkinter as ctk
import json
import os
import calendar
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Données enrichies basées sur l'article Atelier Nubio
CONSEILS_PHASES = {
    "Menstruelle": {
        "titre": "🩸 Phase Menstruelle (Jour 1 à 5)",
        "hormones": "Oestrogènes et progestérone au plus bas.",
        "objectifs": "Réconfort, minéraux et repos.",
        "aliments": "Fer (viande rouge, lentilles), Magnésium (chocolat noir, amandes), infusions de framboisier.",
        "couleur": "#FF4B4B"
    },
    "Folliculaire": {
        "titre": "✨ Phase Folliculaire (Jour 6 à 13)",
        "hormones": "Montée progressive des oestrogènes.",
        "objectifs": "Énergie, probiotiques et fraîcheur.",
        "aliments": "Légumes verts, aliments fermentés (kéfir, choucroute), graines de lin et de courge.",
        "couleur": "#85D2FF"
    },
    "Ovulation": {
        "titre": "🥚 Ovulation (Jour 14)",
        "hormones": "Pic de LH et d'oestrogènes.",
        "objectifs": "Soutenir le foie pour éliminer les oestrogènes.",
        "aliments": "Fibres ++, légumes crucifères (brocoli, chou-fleur), fruits frais, hydratation maximale.",
        "couleur": "#FFD700"
    },
    "Lutéale": {
        "titre": "🌙 Phase Lutéale (Jour 15 à 28+)",
        "hormones": "Pic de progestérone.",
        "objectifs": "Satiété, sucres lents et limitation de l'inflammation.",
        "aliments": "Glucides complexes (patate douce, riz complet), Oméga-3 (petits poissons gras), magnésium.",
        "couleur": "#BA85FF"
    }
}

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌸 Mon Tracker Expert V4.1")
        self.geometry("480x950")
        
        self.fichier_data = "data.json"
        self.fichier_historique = "Mon Calendrier-2026-04-13.txt"
        
        self.aujourdhui = datetime.now()
        self.mois_visu = self.aujourdhui.month
        self.annee_visu = self.aujourdhui.year

        # --- HEADER ---
        ctk.CTkLabel(self, text="Mon Guide de Cycle", font=("Arial", 22, "bold")).pack(pady=10)
        
        # --- INPUTS ---
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=5)

        self.entry_date = ctk.CTkEntry(input_frame, placeholder_text="Date (JJ/MM/AAAA)", width=150)
        self.entry_date.grid(row=0, column=0, padx=5)
        
        moyenne = self.analyser_historique_reel()
        self.entry_cycle = ctk.CTkEntry(input_frame, placeholder_text=f"Cycle: {moyenne}", width=100)
        self.entry_cycle.insert(0, str(moyenne))
        self.entry_cycle.grid(row=0, column=1, padx=5)

        self.entry_regles_duree = ctk.CTkEntry(input_frame, placeholder_text="Règles", width=80)
        self.entry_regles_duree.insert(0, "5")
        self.entry_regles_duree.grid(row=0, column=2, padx=5)

        ctk.CTkButton(self, text="Enregistrer & Calculer", command=self.action_calculer).pack(pady=10)

        # --- NAVIGATION ---
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=5)
        self.btn_prev = ctk.CTkButton(self.nav_frame, text="<", width=40, command=self.mois_precedent)
        self.btn_prev.grid(row=0, column=0, padx=10)
        self.label_mois = ctk.CTkLabel(self.nav_frame, text="", font=("Arial", 18, "bold"), width=180)
        self.label_mois.grid(row=0, column=1)
        self.btn_next = ctk.CTkButton(self.nav_frame, text=">", width=40, command=self.mois_suivant)
        self.btn_next.grid(row=0, column=2, padx=10)

        # --- CALENDRIER ---
        self.cal_container = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=10)
        self.cal_container.pack(pady=5, padx=20, fill="x")

        # --- STATUS ---
        self.label_status = ctk.CTkLabel(self, text="", font=("Arial", 16, "bold"))
        self.label_status.pack(pady=5)
        
        # --- ZONE CONSEILS EXPERTS ---
        self.advice_frame = ctk.CTkFrame(self, border_width=1)
        self.advice_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.label_advice_titre = ctk.CTkLabel(self.advice_frame, text="", font=("Arial", 15, "bold"))
        self.label_advice_titre.pack(pady=5)

        self.advice_view = ctk.CTkTextbox(self.advice_frame, font=("Arial", 13), fg_color="transparent", height=250)
        self.advice_view.pack(pady=5, padx=10, fill="both", expand=True)

        self.charger_et_afficher()

    def mois_precedent(self):
        self.mois_visu -= 1
        if self.mois_visu == 0: self.mois_visu = 12; self.annee_visu -= 1
        self.charger_et_afficher()

    def mois_suivant(self):
        self.mois_visu += 1
        if self.mois_visu == 13: self.mois_visu = 1; self.annee_visu += 1
        self.charger_et_afficher()

    def dessiner_calendrier(self, derniere_date_saisie, duree_cycle, duree_regles):
        for widget in self.cal_container.winfo_children(): widget.destroy()
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.label_mois.configure(text=f"{mois_noms[self.mois_visu-1]} {self.annee_visu}")
        cal = calendar.monthcalendar(self.annee_visu, self.mois_visu)
        for i, jour_nom in enumerate(["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]):
            ctk.CTkLabel(self.cal_container, text=jour_nom, width=45, font=("Arial", 11, "bold")).grid(row=0, column=i, pady=5)

        for r, semaine in enumerate(cal):
            for c, jour in enumerate(semaine):
                if jour == 0: continue
                date_ciblée = datetime(self.annee_visu, self.mois_visu, jour)
                diff = (date_ciblée - derniere_date_saisie).days
                jour_cycle = (diff % duree_cycle) + 1
                ovul = derniere_date_saisie + timedelta(days=(diff // duree_cycle) * duree_cycle + duree_cycle - 14)
                
                bg = "#3D3D3D"; txt = "white"; brd_w = 0; brd_c = None
                if 1 <= jour_cycle <= duree_regles: bg = CONSEILS_PHASES["Menstruelle"]["couleur"]
                elif jour_cycle < (duree_cycle - 15): bg = CONSEILS_PHASES["Folliculaire"]["couleur"]; txt = "black"
                elif (ovul - timedelta(days=2)) <= date_ciblée <= (ovul + timedelta(days=1)): bg = CONSEILS_PHASES["Ovulation"]["couleur"]; txt = "black"
                else: bg = CONSEILS_PHASES["Lutéale"]["couleur"]

                if date_ciblée.date() == self.aujourdhui.date(): brd_w = 2; brd_c = "white"
                
                btn = ctk.CTkButton(self.cal_container, text=str(jour), width=45, height=45, fg_color=bg, text_color=txt, 
                                     hover=False, corner_radius=8, border_width=brd_w, border_color=brd_c)
                btn.grid(row=r+1, column=c, padx=2, pady=2)

    def calculer_logique(self, date_brute, duree_cycle, duree_regles):
        derniere_date = datetime.strptime(date_brute, "%Y-%m-%d")
        self.dessiner_calendrier(derniere_date, duree_cycle, duree_regles)
        jour_actuel = ((self.aujourdhui - derniere_date).days % duree_cycle) + 1
        
        if jour_actuel <= duree_regles: phase = "Menstruelle"
        elif jour_actuel <= (duree_cycle - 15): phase = "Folliculaire"
        elif (duree_cycle - 16) < jour_actuel < (duree_cycle - 12): phase = "Ovulation"
        else: phase = "Lutéale"

        info = CONSEILS_PHASES[phase]
        self.label_status.configure(text=f"Aujourd'hui : Jour {jour_actuel}", text_color=info['couleur'])
        self.label_advice_titre.configure(text=info["titre"], text_color=info["couleur"])
        
        detail = f"🔬 HORMONES :\n{info['hormones']}\n\n🎯 OBJECTIFS :\n{info['objectifs']}\n\n🥗 À PRIVILÉGIER :\n{info['aliments']}"
        self.advice_view.configure(state="normal")
        self.advice_view.delete("1.0", "end")
        self.advice_view.insert("1.0", detail)
        self.advice_view.configure(state="disabled")

    def convertir_date_fr(self, s):
        m = {"janv.":"01","févr.":"02","mars":"03","avr.":"04","mai":"05","juin":"06","juil.":"07","août":"08","sept.":"09","oct.":"10","nov.":"11","déc.":"12"}
        try: p = s.split(' '); return datetime.strptime(f"{p[0].zfill(2)}/{m.get(p[1].lower(), '01')}/{p[2]}", "%d/%m/%Y")
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
            self.mois_visu, self.annee_visu = d_obj.month, d_obj.year
            self.calculer_logique(d_obj.strftime("%Y-%m-%d"), c_int, r_int)
        except: self.label_status.configure(text="❌ Erreur format")

if __name__ == "__main__":
    app = TrackerApp(); app.mainloop()
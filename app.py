import customtkinter as ctk
import json
import os
import calendar
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONSEILS_PHASES = {
    "Menstruelle": {"titre": "🩸 Phase Menstruelle", "objectifs": "Repos & Minéraux", "aliments": "Fer, Magnésium", "couleur": "#FF4B4B"},
    "Folliculaire": {"titre": "✨ Phase Folliculaire", "objectifs": "Énergie & Créativité", "aliments": "Verts, Probiotiques", "couleur": "#85D2FF"},
    "Ovulation": {"titre": "🥚 Ovulation", "objectifs": "Soutien Foie", "aliments": "Crucifères, Fibres", "couleur": "#FFD700"},
    "Lutéale": {"titre": "🌙 Phase Lutéale", "objectifs": "Satiété", "aliments": "Sucres lents, Oméga-3", "couleur": "#BA85FF"}
}

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌸 Tracker V6.4 - Réactivité Totale")
        self.geometry("500x1000")
        
        self.fichier_data = "data.json"
        self.aujourdhui = datetime.now()
        self.mois_visu = self.aujourdhui.month
        self.annee_visu = self.aujourdhui.year
        
        self.date_selectionnee = self.aujourdhui.strftime("%d/%m/%Y")
        self.cycles_historique = [] 
        self.symptomes_data = {}

        # --- UI ---
        ctk.CTkLabel(self, text="Mon Guide de Cycle", font=("Arial", 22, "bold")).pack(pady=10)
        
        self.sel_frame = ctk.CTkFrame(self, fg_color="#333333")
        self.sel_frame.pack(pady=5, padx=20, fill="x")
        self.label_sel = ctk.CTkLabel(self.sel_frame, text=f"Sélection : {self.date_selectionnee}", font=("Arial", 14, "bold"))
        self.label_sel.pack(pady=5)

        btn_action_frame = ctk.CTkFrame(self.sel_frame, fg_color="transparent")
        btn_action_frame.pack(pady=5)
        
        ctk.CTkButton(btn_action_frame, text="🩸 Début Règles", fg_color="#FF4B4B", command=self.marquer_debut, width=140).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_action_frame, text="🏁 Fin Règles", fg_color="#7D2222", command=self.marquer_fin, width=140).grid(row=0, column=1, padx=5)

        # Navigation
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=5)
        ctk.CTkButton(self.nav_frame, text="<", width=40, command=self.mois_precedent).grid(row=0, column=0, padx=10)
        self.label_mois = ctk.CTkLabel(self.nav_frame, text="", font=("Arial", 18, "bold"), width=180)
        self.label_mois.grid(row=0, column=1)
        ctk.CTkButton(self.nav_frame, text=">", width=40, command=self.mois_suivant).grid(row=0, column=2, padx=10)

        self.cal_container = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=10)
        self.cal_container.pack(pady=5, padx=20, fill="x")

        # Symptômes
        self.symp_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.symp_frame.pack(pady=5)
        for icon in ["⚡", "😊", "😔", "🔋", "😴", "❌"]:
            ctk.CTkButton(self.symp_frame, text=icon, width=45, fg_color="#3D3D3D", command=lambda i=icon: self.ajouter_symptome(i)).pack(side="left", padx=2)

        # Conseils
        self.advice_frame = ctk.CTkFrame(self, border_width=1)
        self.advice_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.label_advice_titre = ctk.CTkLabel(self.advice_frame, text="", font=("Arial", 15, "bold"))
        self.label_advice_titre.pack(pady=5)
        self.advice_view = ctk.CTkTextbox(self.advice_frame, font=("Arial", 13), fg_color="transparent", height=150)
        self.advice_view.pack(pady=5, padx=10, fill="both", expand=True)

        self.charger_data()

    def marquer_debut(self):
        date_iso = datetime.strptime(self.date_selectionnee, "%d/%m/%Y").strftime("%Y-%m-%d")
        # Remplace si un cycle existe déjà à cette date précise
        self.cycles_historique = [c for c in self.cycles_historique if c['debut'] != date_iso]
        self.cycles_historique.append({"debut": date_iso, "fin": None, "cycle": 28})
        self.cycles_historique.sort(key=lambda x: x['debut'])
        self.sauvegarder_data()
        self.action_calculer()

    def marquer_fin(self):
        date_iso = datetime.strptime(self.date_selectionnee, "%d/%m/%Y").strftime("%Y-%m-%d")
        # Trouve le cycle en cours pour lui attribuer cette fin
        for cycle in reversed(self.cycles_historique):
            if cycle['debut'] <= date_iso:
                cycle['fin'] = date_iso # Écrase l'ancienne fin si elle existait
                break
        self.sauvegarder_data()
        self.action_calculer()

    def obtenir_phase_pour_date(self, date_c):
        # 1. Quel cycle gère cette date ?
        cycle_actuel = None
        for c in reversed(self.cycles_historique):
            if datetime.strptime(c['debut'], "%Y-%m-%d") <= date_c:
                cycle_actuel = c
                break
        
        if not cycle_actuel: return None
        
        debut = datetime.strptime(cycle_actuel['debut'], "%Y-%m-%d")
        
        # 2. Si un autre cycle commence après, on s'arrête
        prochain = next((c for c in self.cycles_historique if datetime.strptime(c['debut'], "%Y-%m-%d") > debut), None)
        if prochain and date_c >= datetime.strptime(prochain['debut'], "%Y-%m-%d"):
            return None

        # 3. Logique élastique :
        # Si 'fin' est renseignée, la phase folliculaire commence après 'fin'
        if cycle_actuel.get('fin'):
            fin = datetime.strptime(cycle_actuel['fin'], "%Y-%m-%d")
            if debut <= date_c <= fin:
                return "Menstruelle"
            
            # Recalcul des phases à partir de la fin réelle
            jours_apres_fin = (date_c - fin).days
            if jours_apres_fin <= 7: return "Folliculaire"
            if jours_apres_fin <= 10: return "Ovulation"
            return "Lutéale"
        else:
            # Si pas de fin, calcul standard (prévision 5j de règles)
            diff = (date_c - debut).days
            if 0 <= diff < 5: return "Menstruelle"
            if diff < 13: return "Folliculaire"
            if diff < 16: return "Ovulation"
            return "Lutéale"

    def dessiner_calendrier(self):
        for widget in self.cal_container.winfo_children(): widget.destroy()
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.label_mois.configure(text=f"{mois_noms[self.mois_visu-1]} {self.annee_visu}")
        
        cal = calendar.monthcalendar(self.annee_visu, self.mois_visu)
        for i, jour_nom in enumerate(["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]):
            ctk.CTkLabel(self.cal_container, text=jour_nom, width=45, font=("Arial", 11, "bold")).grid(row=0, column=i)

        for r, semaine in enumerate(cal):
            for c, jour in enumerate(semaine):
                if jour == 0: continue
                date_c = datetime(self.annee_visu, self.mois_visu, jour)
                bg, txt, brd_w, brd_c = "#3D3D3D", "white", 0, None
                
                phase = self.obtenir_phase_pour_date(date_c)
                if phase:
                    bg = CONSEILS_PHASES[phase]["couleur"]
                    if phase in ["Folliculaire", "Ovulation"]: txt = "black"

                date_s = date_c.strftime("%d/%m/%Y")
                if date_s == self.date_selectionnee: brd_w, brd_c = 2, "#1F6AA5" # Sélection
                elif date_c.date() == self.aujourdhui.date(): brd_w, brd_c = 2, "white" # Aujourd'hui
                
                txt_btn = f"{jour}\n{self.symptomes_data.get(date_c.strftime('%Y-%m-%d'), '')}"
                btn = ctk.CTkButton(self.cal_container, text=txt_btn, width=45, height=55, fg_color=bg, text_color=txt, 
                                     hover=True, corner_radius=8, border_width=brd_w, border_color=brd_c,
                                     command=lambda d=date_s: self.clic_date_calendrier(d))
                btn.grid(row=r+1, column=c, padx=2, pady=2)

    def charger_data(self):
        if os.path.exists(self.fichier_data):
            try:
                with open(self.fichier_data, "r") as f:
                    d = json.load(f)
                    self.cycles_historique = d.get("historique", [])
                    self.symptomes_data = d.get("symptomes", {})
            except: self.cycles_historique = []
        self.action_calculer()

    def action_calculer(self):
        self.dessiner_calendrier()
        phase = self.obtenir_phase_pour_date(self.aujourdhui)
        if phase:
            info = CONSEILS_PHASES[phase]
            self.label_advice_titre.configure(text=f"Aujourd'hui : {phase}", text_color=info['couleur'])
            self.advice_view.configure(state="normal")
            self.advice_view.delete("1.0", "end")
            self.advice_view.insert("1.0", f"🎯 {info['objectifs']}\n🥗 {info['aliments']}")
            self.advice_view.configure(state="disabled")

    def clic_date_calendrier(self, d):
        self.date_selectionnee = d
        self.label_sel.configure(text=f"Sélection : {self.date_selectionnee}")
        self.dessiner_calendrier()

    def ajouter_symptome(self, emoji):
        cle = datetime.strptime(self.date_selectionnee, "%d/%m/%Y").strftime("%Y-%m-%d")
        if emoji == "❌": self.symptomes_data.pop(cle, None)
        else: self.symptomes_data[cle] = emoji
        self.sauvegarder_data()
        self.action_calculer()

    def sauvegarder_data(self):
        with open(self.fichier_data, "w") as f:
            json.dump({"historique": self.cycles_historique, "symptomes": self.symptomes_data}, f)

    def mois_precedent(self):
        self.mois_visu -= 1
        if self.mois_visu == 0: self.mois_visu = 12; self.annee_visu -= 1
        self.dessiner_calendrier()

    def mois_suivant(self):
        self.mois_visu += 1
        if self.mois_visu == 13: self.mois_visu = 1; self.annee_visu += 1
        self.dessiner_calendrier()

if __name__ == "__main__":
    app = TrackerApp(); app.mainloop()
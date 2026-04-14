import customtkinter as ctk
import json
import os
import calendar
from datetime import datetime, timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONSEILS_PHASES = {
    "Menstruelle": {"titre": "🩸 Phase Menstruelle", "hormones": "Basses", "objectifs": "Repos", "aliments": "Fer, Magnésium", "couleur": "#FF4B4B"},
    "Folliculaire": {"titre": "✨ Phase Folliculaire", "hormones": "Montée Estrogènes", "objectifs": "Énergie", "aliments": "Vert, Fermenté", "couleur": "#85D2FF"},
    "Ovulation": {"titre": "🥚 Ovulation", "hormones": "Pic LH", "objectifs": "Détox Foie", "aliments": "Fibres, Brocoli", "couleur": "#FFD700"},
    "Lutéale": {"titre": "🌙 Phase Lutéale", "hormones": "Progestérone", "objectifs": "Satiété", "aliments": "Sucres lents", "couleur": "#BA85FF"}
}

class TrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌸 Mon Tracker Mobile Expert V5.2")
        self.geometry("500x980")
        
        self.fichier_data = "data.json"
        self.fichier_historique = "Mon Calendrier-2026-04-13.txt"
        
        self.aujourdhui = datetime.now()
        self.mois_visu = self.aujourdhui.month
        self.annee_visu = self.aujourdhui.year
        
        # --- VARIABLES DE SELECTION (Crucial) ---
        self.date_selectionnee = self.aujourdhui.strftime("%d/%m/%Y")
        self.derniere_date_regles = ""
        self.duree_cycle_mem = 28
        self.symptomes_data = {}

        # --- HEADER ---
        ctk.CTkLabel(self, text="Mon Guide de Cycle", font=("Arial", 22, "bold")).pack(pady=10)
        
        # --- ZONE DE SELECTION ---
        self.sel_frame = ctk.CTkFrame(self, fg_color="#333333")
        self.sel_frame.pack(pady=5, padx=20, fill="x")
        self.label_sel = ctk.CTkLabel(self.sel_frame, text=f"Jour sélectionné : {self.date_selectionnee}", font=("Arial", 14, "bold"))
        self.label_sel.pack(pady=5)

        btn_action_frame = ctk.CTkFrame(self.sel_frame, fg_color="transparent")
        btn_action_frame.pack(pady=5)
        
        self.btn_regles = ctk.CTkButton(btn_action_frame, text="Marquer début règles", fg_color="#FF4B4B", 
                                        command=self.marquer_debut_regles, width=160)
        self.btn_regles.grid(row=0, column=0, padx=5)
        
        self.entry_cycle = ctk.CTkEntry(btn_action_frame, width=60)
        self.entry_cycle.grid(row=0, column=1, padx=5)

        # --- NAVIGATION ---
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(pady=5)
        ctk.CTkButton(self.nav_frame, text="<", width=40, command=self.mois_precedent).grid(row=0, column=0, padx=10)
        self.label_mois = ctk.CTkLabel(self.nav_frame, text="", font=("Arial", 18, "bold"), width=180)
        self.label_mois.grid(row=0, column=1)
        ctk.CTkButton(self.nav_frame, text=">", width=40, command=self.mois_suivant).grid(row=0, column=2, padx=10)

        # --- CALENDRIER ---
        self.cal_container = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=10)
        self.cal_container.pack(pady=5, padx=20, fill="x")

        # --- BARRE DE SYMPTÔMES ---
        ctk.CTkLabel(self, text="Ajouter une note au jour sélectionné :", font=("Arial", 11)).pack(pady=2)
        self.symp_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.symp_frame.pack(pady=5)
        
        for icon in ["⚡", "😊", "😔", "🔋", "😴", "❌"]:
            btn = ctk.CTkButton(self.symp_frame, text=icon, width=45, fg_color="#3D3D3D", 
                                command=lambda i=icon: self.ajouter_symptome(i))
            btn.pack(side="left", padx=5)

        # --- CONSEILS ---
        self.advice_frame = ctk.CTkFrame(self, border_width=1)
        self.advice_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.label_advice_titre = ctk.CTkLabel(self.advice_frame, text="", font=("Arial", 15, "bold"))
        self.label_advice_titre.pack(pady=5)
        self.advice_view = ctk.CTkTextbox(self.advice_frame, font=("Arial", 13), fg_color="transparent")
        self.advice_view.pack(pady=5, padx=10, fill="both", expand=True)

        self.charger_data()

    def clic_date_calendrier(self, date_selectionnee):
        """Sélectionne une date sans forcément changer les règles"""
        self.date_selectionnee = date_selectionnee
        self.label_sel.configure(text=f"Jour sélectionné : {self.date_selectionnee}")
        self.dessiner_calendrier() # Pour mettre à jour la bordure de sélection

    def marquer_debut_regles(self):
        """Définit la date sélectionnée comme le nouveau J1"""
        self.derniere_date_regles = datetime.strptime(self.date_selectionnee, "%d/%m/%Y").strftime("%Y-%m-%d")
        self.duree_cycle_mem = int(self.entry_cycle.get())
        self.sauvegarder_data()
        self.action_calculer()

    def ajouter_symptome(self, emoji):
        """Ajoute l'emoji à la date sélectionnée (et pas forcément aujourd'hui)"""
        cle = datetime.strptime(self.date_selectionnee, "%d/%m/%Y").strftime("%Y-%m-%d")
        if emoji == "❌":
            if cle in self.symptomes_data: del self.symptomes_data[cle]
        else:
            self.symptomes_data[cle] = emoji
        self.sauvegarder_data()
        self.action_calculer()

    def mois_precedent(self):
        self.mois_visu -= 1
        if self.mois_visu == 0: self.mois_visu = 12; self.annee_visu -= 1
        self.dessiner_calendrier()

    def mois_suivant(self):
        self.mois_visu += 1
        if self.mois_visu == 13: self.mois_visu = 1; self.annee_visu += 1
        self.dessiner_calendrier()

    def dessiner_calendrier(self):
        for widget in self.cal_container.winfo_children(): widget.destroy()
        
        derniere_date = datetime.strptime(self.derniere_date_regles, "%Y-%m-%d")
        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.label_mois.configure(text=f"{mois_noms[self.mois_visu-1]} {self.annee_visu}")
        
        cal = calendar.monthcalendar(self.annee_visu, self.mois_visu)
        for i, jour_nom in enumerate(["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]):
            ctk.CTkLabel(self.cal_container, text=jour_nom, width=45, font=("Arial", 11, "bold")).grid(row=0, column=i, pady=5)

        for r, semaine in enumerate(cal):
            for c, jour in enumerate(semaine):
                if jour == 0: continue
                date_ciblée = datetime(self.annee_visu, self.mois_visu, jour)
                diff = (date_ciblée - derniere_date).days
                jour_cycle = (diff % self.duree_cycle_mem) + 1
                ovul = derniere_date + timedelta(days=(diff // self.duree_cycle_mem) * self.duree_cycle_mem + self.duree_cycle_mem - 14)
                
                # Couleurs
                bg = "#3D3D3D"; txt = "white"; brd_w = 0; brd_c = None
                if 1 <= jour_cycle <= 5: bg = CONSEILS_PHASES["Menstruelle"]["couleur"]
                elif jour_cycle < (self.duree_cycle_mem - 15): bg = CONSEILS_PHASES["Folliculaire"]["couleur"]; txt = "black"
                elif (ovul - timedelta(days=2)) <= date_ciblée <= (ovul + timedelta(days=1)): bg = CONSEILS_PHASES["Ovulation"]["couleur"]; txt = "black"
                else: bg = CONSEILS_PHASES["Lutéale"]["couleur"]

                # Bordure de sélection (Bleue) vs Aujourd'hui (Blanche)
                date_str_slash = date_ciblée.strftime("%d/%m/%Y")
                if date_str_slash == self.date_selectionnee:
                    brd_w = 2; brd_c = "#1F6AA5" # Bleu sélection
                elif date_ciblée.date() == self.aujourdhui.date():
                    brd_w = 2; brd_c = "white" # Blanc aujourd'hui
                
                # Texte + Emoji
                texte_btn = str(jour)
                cle_symp = date_ciblée.strftime("%Y-%m-%d")
                if cle_symp in self.symptomes_data:
                    texte_btn = f"{jour}\n{self.symptomes_data[cle_symp]}"

                btn = ctk.CTkButton(self.cal_container, text=texte_btn, width=45, height=55, fg_color=bg, text_color=txt, 
                                     hover=True, corner_radius=8, border_width=brd_w, border_color=brd_c,
                                     command=lambda d=date_str_slash: self.clic_date_calendrier(d))
                btn.grid(row=r+1, column=c, padx=2, pady=2)

    def action_calculer(self):
        derniere_date = datetime.strptime(self.derniere_date_regles, "%Y-%m-%d")
        jour_actuel = ((self.aujourdhui - derniere_date).days % self.duree_cycle_mem) + 1
        
        phase = "Menstruelle" if jour_actuel <= 5 else "Folliculaire" if jour_actuel <= (self.duree_cycle_mem - 15) else "Ovulation" if (self.duree_cycle_mem - 16) < jour_actuel < (self.duree_cycle_mem - 12) else "Lutéale"

        info = CONSEILS_PHASES[phase]
        self.label_advice_titre.configure(text=f"Aujourd'hui : Jour {jour_actuel} ({phase})", text_color=info['couleur'])
        detail = f"🔬 HORMONES :\n{info['hormones']}\n\n🎯 OBJECTIFS :\n{info['objectifs']}\n\n🥗 À PRIVILÉGIER :\n{info['aliments']}"
        self.advice_view.configure(state="normal")
        self.advice_view.delete("1.0", "end")
        self.advice_view.insert("1.0", detail)
        self.advice_view.configure(state="disabled")
        self.dessiner_calendrier()

    def sauvegarder_data(self):
        with open(self.fichier_data, "w") as f:
            json.dump({"derniere_date": self.derniere_date_regles, "duree_cycle": self.duree_cycle_mem, "symptomes": self.symptomes_data}, f)

    def charger_data(self):
        if os.path.exists(self.fichier_data):
            with open(self.fichier_data, "r") as f:
                d = json.load(f)
                self.derniere_date_regles = d["derniere_date"]
                self.duree_cycle_mem = d["duree_cycle"]
                self.symptomes_data = d.get("symptomes", {})
                self.entry_cycle.insert(0, str(self.duree_cycle_mem))
                self.action_calculer()

    def analyser_historique_reel(self):
        # ... (Garder ta fonction de parsing du fichier .txt ici)
        return 28

if __name__ == "__main__":
    app = TrackerApp(); app.mainloop()
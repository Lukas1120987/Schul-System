import customtkinter as ctk
import json
import os
from collections import Counter

class Modul:
    def __init__(self, parent, nutzername, user_data=None):
        self.frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#ffffff")  # moderner dunkler Hintergrund
        self.nutzername = nutzername
        self.user_data = user_data or {}

        # Scrollbar und Canvas, falls später mehr Daten kommen
        self.canvas = ctk.CTkCanvas(self.frame, bg="#ffffff", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="#ffffff")

        self.scrollable_frame.bind(
            "<MouseWheel>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.zeige_statistiken()

    def get_frame(self):
        return self.frame

    def zeige_statistiken(self):
        # Titel
        titel = ctk.CTkLabel(self.scrollable_frame, text="📈 Statistiken", font=ctk.CTkFont(size=24, weight="bold"))
        titel.pack(pady=(10, 20))

        # Daten laden
        nutzer_daten = self.lade_json("data/users.json", {})
        nachrichten = self.lade_json("data/messages.json", [])
        notifications = self.lade_json("data/notifications.json", {})

        # Statistiken berechnen
        nutzeranzahl = len(nutzer_daten)
        gruppen_counter = Counter([daten.get("group", "Unbekannt") for daten in nutzer_daten.values()])
        nachrichtenanzahl = len(nachrichten)
        durchschnittslänge = int(sum(len(n["inhalt"]) for n in nachrichten) / nachrichtenanzahl) if nachrichtenanzahl else 0
        absender_counter = Counter([n["absender"] for n in nachrichten])
        meistgenutzt = absender_counter.most_common(1)[0] if absender_counter else ("-", 0)
        ungelesene_benachrichtigungen = sum(
            not eintrag.get("gelesen", False)
            for einträge in notifications.values()
            for eintrag in einträge
        )

        # Textliche Statistiken
        self.stat_zeile(f"👤 Gesamtzahl Nutzer: {nutzeranzahl}")
        self.stat_zeile(f"📬 Nachrichten gesamt: {nachrichtenanzahl}")
        self.stat_zeile(f"📝 Durchschnittliche Nachrichtenlänge: {durchschnittslänge} Zeichen")
        self.stat_zeile(f"👑 Meistgenutzter Absender: {meistgenutzt[0]} ({meistgenutzt[1]} Nachrichten)")
        self.stat_zeile(f"🔔 Ungelesene Benachrichtigungen: {ungelesene_benachrichtigungen}")

        # Visualisierung Gruppenverteilung
        self.visualisiere_balken(gruppen_counter, titel="👥 Nutzer nach Gruppen")

        # Visualisierung Absenderhäufigkeit Top 5
        top_absender = dict(absender_counter.most_common(5))
        self.visualisiere_balken(top_absender, titel="📤 Top 5 Absender")

    def stat_zeile(self, text):
        label = ctk.CTkLabel(self.scrollable_frame, text=text, font=ctk.CTkFont(size=16), anchor="w", justify="left")
        label.pack(fill="x", padx=25, pady=5)

    def lade_json(self, dateipfad, standardwert):
        if not os.path.exists(dateipfad):
            return standardwert
        try:
            with open(dateipfad, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden von {dateipfad}: {e}")
            return standardwert

    def visualisiere_balken(self, daten: dict, titel: str):
        """Zeichnet einfache horizontale Balken mit CTk Frames"""
        if not daten:
            return
        max_wert = max(daten.values())
        if max_wert == 0:
            max_wert = 1  # Division durch 0 vermeiden

        titel_label = ctk.CTkLabel(self.scrollable_frame, text=titel, font=ctk.CTkFont(size=18, weight="bold"))
        titel_label.pack(pady=(20, 10), anchor="w", padx=20)

        for schluessel, wert in daten.items():
            zeile_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#FFFFFF", corner_radius=8)
            zeile_frame.pack(fill="x", padx=25, pady=6)

            beschriftung = ctk.CTkLabel(zeile_frame, text=f"{schluessel} ({wert})", width=120, anchor="w")
            beschriftung.pack(side="left", padx=(10, 5))

            balken_laenge = int(200 * wert / max_wert)  # max 200px breit
            balken = ctk.CTkFrame(zeile_frame, fg_color="#000000", width=balken_laenge, height=24, corner_radius=8)
            balken.pack(side="left", pady=4)


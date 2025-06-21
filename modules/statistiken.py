import customtkinter as ctk
import json
import os
from collections import Counter

class Modul:
    def __init__(self, parent, nutzername, user_data=None):
        self.frame = ctk.CTkFrame(parent, corner_radius=10)
        self.nutzername = nutzername
        self.user_data = user_data or {}

        self.zeige_statistiken()

    def get_frame(self):
        return self.frame

    def zeige_statistiken(self):
        # Titel
        ctk.CTkLabel(self.frame, text="📈 Statistiken", font=("Arial", 22, "bold")).pack(pady=(10, 5))

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

        # Statistiken anzeigen
        self.stat_zeile(f"👤 Gesamtzahl Nutzer: {nutzeranzahl}")
        for gruppe, anzahl in gruppen_counter.items():
            self.stat_zeile(f"   📚 {gruppe}: {anzahl}")

        self.stat_zeile(f"📬 Nachrichten gesamt: {nachrichtenanzahl}")
        self.stat_zeile(f"📝 Durchschnittliche Nachrichtenlänge: {durchschnittslänge} Zeichen")
        self.stat_zeile(f"👑 Meistgenutzter Absender: {meistgenutzt[0]} ({meistgenutzt[1]} Nachrichten)")
        self.stat_zeile(f"🔔 Ungelesene Benachrichtigungen: {ungelesene_benachrichtigungen}")

    def stat_zeile(self, text):
        ctk.CTkLabel(self.frame, text=text, font=("Arial", 16), anchor="w", justify="left").pack(fill="x", padx=20, pady=3)

    def lade_json(self, dateipfad, standardwert):
        if not os.path.exists(dateipfad):
            return standardwert
        try:
            with open(dateipfad, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return standardwert

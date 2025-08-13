import tkinter as tk
from tkinter import messagebox
import json
import os
import threading
import time
from datetime import datetime, timedelta

class Modul:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)

        # Dateien
        self.messages_file = "messages.json"
        self.notifications_file = "notifications.json"

        # Einstellungen
        self.message_retention_days = tk.IntVar(value=30)
        self.notification_retention_days = tk.IntVar(value=30)
        self.auto_delete_enabled = tk.BooleanVar(value=False)

        # UI erstellen
        self.create_ui()

        # Hintergrundtask starten
        self.stop_event = threading.Event()
        self.bg_thread = threading.Thread(target=self.run_background_task, daemon=True)
        self.bg_thread.start()

    def create_ui(self):
        tk.Label(self.frame, text="Nachrichten-Speicherdauer (Tage):").pack()
        tk.Entry(self.frame, textvariable=self.message_retention_days).pack()

        tk.Label(self.frame, text="Benachrichtigungen-Speicherdauer (Tage):").pack()
        tk.Entry(self.frame, textvariable=self.notification_retention_days).pack()

        tk.Checkbutton(self.frame, text="Auto-Delete aktivieren",
                       variable=self.auto_delete_enabled).pack(pady=5)

        tk.Button(self.frame, text="Jetzt bereinigen", command=self.auto_delete).pack(pady=5)

        self.banner_label = tk.Label(self.frame, text="", fg="red", font=("Arial", 12, "bold"))
        self.banner_label.pack(pady=10)

    def run_background_task(self):
        while not self.stop_event.is_set():
            if self.auto_delete_enabled.get():
                self.auto_delete()
            self.check_for_banner()
            time.sleep(60)  # alle 60 Sekunden prüfen

    def check_for_banner(self):
        messages = self.load_json(self.messages_file, [])
        notifications = self.load_json(self.notifications_file, {})

        msg_count = len(messages) if isinstance(messages, list) else 0
        notif_count = sum(len(v) for v in notifications.values()) if isinstance(notifications, dict) else 0

        if msg_count > 100 or notif_count > 200:
            self.banner_label.config(
                text=f"Achtung! {msg_count} Nachrichten, {notif_count} Benachrichtigungen – bitte bereinigen!"
            )
        else:
            self.banner_label.config(text="")

    def auto_delete(self):
        jetzt = datetime.now()

        # Nachrichten bereinigen
        messages = self.load_json(self.messages_file, [])
        messages = self.filter_by_age(messages, self.message_retention_days.get(), jetzt)
        self.save_json(self.messages_file, messages)

        # Benachrichtigungen bereinigen
        notifications = self.load_json(self.notifications_file, {})
        notifications = self.filter_by_age(notifications, self.notification_retention_days.get(), jetzt)
        self.save_json(self.notifications_file, notifications)

    def filter_by_age(self, data, max_days, jetzt):
        date_formats = ["%d.%m.%Y %H:%M", "%Y-%m-%dT%H:%M"]

        def parse_datum(datum_str):
            for fmt in date_formats:
                try:
                    return datetime.strptime(datum_str, fmt)
                except ValueError:
                    continue
            return None

        if isinstance(data, dict):
            neue_daten = {}
            for key, value in data.items():
                if isinstance(value, list):
                    gefiltert = []
                    for eintrag in value:
                        datum = parse_datum(eintrag.get("datum", ""))
                        if datum and (jetzt - datum) <= timedelta(days=max_days):
                            gefiltert.append(eintrag)
                        elif not datum:
                            gefiltert.append(eintrag)
                    neue_daten[key] = gefiltert
                else:
                    neue_daten[key] = value
            return neue_daten

        elif isinstance(data, list):
            neue_daten = []
            for eintrag in data:
                datum = parse_datum(eintrag.get("datum", ""))
                if datum and (jetzt - datum) <= timedelta(days=max_days):
                    neue_daten.append(eintrag)
                elif not datum:
                    neue_daten.append(eintrag)
            return neue_daten

        return data

    def load_json(self, filepath, default):
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return default
        return default

    def save_json(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stop_event.set()

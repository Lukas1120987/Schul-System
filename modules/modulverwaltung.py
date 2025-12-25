import customtkinter as ctk
import json
import os
from ordner import get_data_path

MODUL_PATH = os.path.join(get_data_path(), "data/modules.json")

ctk.set_appearance_mode("system")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")


class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data

        self.frame = ctk.CTkFrame(master, corner_radius=12)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        if not user_data.get("is_admin"):
            ctk.CTkLabel(
                self.frame,
                text="Nur Admins können Module verwalten.",
                text_color="red",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=30)
            return

        self.module_config = self.load_config()
        self.check_vars = {}

        # Titel
        ctk.CTkLabel(
            self.frame,
            text="Modulverwaltung",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 20))

        # Scrollbarer Bereich
        self.scroll = ctk.CTkScrollableFrame(self.frame, corner_radius=10)
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)

        for modul, daten in self.module_config.items():
            row = ctk.CTkFrame(self.scroll, corner_radius=8)
            row.pack(fill="x", pady=5, padx=5)

            var = ctk.BooleanVar(value=daten.get("aktiv", False))
            self.check_vars[modul] = var

            ctk.CTkLabel(
                row,
                text=modul,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            ).pack(side="left", padx=(10, 5))

            ctk.CTkLabel(
                row,
                text=daten.get("beschreibung", ""),
                font=ctk.CTkFont(size=11),
                anchor="w"
            ).pack(side="left", padx=5, expand=True, fill="x")

            ctk.CTkSwitch(
                row,
                variable=var,
                text=""
            ).pack(side="right", padx=10)

        # Speichern Button
        self.save_button = ctk.CTkButton(
            self.frame,
            text="Änderungen speichern",
            command=self.save_config,
            height=40
        )
        self.save_button.pack(pady=(15, 5))

        # Status Text
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=(0, 10))

    def get_frame(self):
        return self.frame

    def load_config(self):
        try:
            with open(MODUL_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Fehler beim Laden:", e)
            return {}

    def save_config(self):
        for modul in self.module_config:
            self.module_config[modul]["aktiv"] = self.check_vars[modul].get()

        try:
            with open(MODUL_PATH, "w", encoding="utf-8") as f:
                json.dump(self.module_config, f, indent=4, ensure_ascii=False)

            self.status_label.configure(
                text="Gespeichert. Änderungen werden beim nächsten Start wirksam.",
                text_color="green"
            )
        except Exception as e:
            self.status_label.configure(
                text=f"Fehler beim Speichern: {e}",
                text_color="red"
            )

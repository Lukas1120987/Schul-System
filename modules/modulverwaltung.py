import tkinter as tk
import json

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data

        self.frame = tk.Frame(master, bg="white")

        if not user_data.get("is_admin"):
            tk.Label(self.frame, text="Nur Admins können Module verwalten.",
                     font=("Segoe UI", 12), fg="red", bg="white").pack(pady=20)
            return

        self.module_config = self.load_config()

        tk.Label(self.frame, text="Modulverwaltung", font=("Segoe UI", 16, "bold"),
                 bg="white").pack(pady=10)

        self.check_vars = {}

        for modul, daten in self.module_config.items():
            var = tk.BooleanVar(value=daten.get("aktiv", False))
            self.check_vars[modul] = var
            cb = tk.Checkbutton(self.frame, text=f"{modul} – {daten.get('beschreibung', '')}",
                                variable=var, font=("Segoe UI", 10), anchor="w",
                                bg="white", onvalue=True, offvalue=False)
            cb.pack(fill="x", padx=20, pady=2)

        tk.Button(self.frame, text="Änderungen speichern", command=self.save_config,
                  bg="#1ABC9C", fg="white", font=("Segoe UI", 10)).pack(pady=20)

    def get_frame(self):
        return self.frame

    def load_config(self):
        try:
            with open("data/modules.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def save_config(self):
        for modul in self.module_config:
            self.module_config[modul]["aktiv"] = self.check_vars[modul].get()
        with open("data/modules.json", "w", encoding="utf-8") as f:
            json.dump(self.module_config, f, indent=4)
        tk.Label(self.frame, text="Gespeichert. Änderungen werden beim nächsten Start wirksam.",
                 fg="green", bg="white", font=("Segoe UI", 10)).pack(pady=5)

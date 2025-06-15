import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar

class Modul:
    def __init__(self, parent, username, user_data):
        self.parent = parent
        self.username = username
        self.user_data = user_data
        self.group = user_data.get("group", "all")
        self.second_group = user_data.get("second_group", "")
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(parent, bg="white")
        self.data_file = "data/kalender.json"
        self.users_file = "data/users.json"

        self.create_widgets()
        self.load_dates()
        self.update_display()

    def get_frame(self):
        return self.frame

    def create_widgets(self):
        title = tk.Label(self.frame, text="Kalender", font=("Segoe UI", 18), bg="white")
        title.pack(pady=10)

        self.calendar = Calendar(self.frame, selectmode="day", date_pattern="dd.mm.yyyy")
        self.calendar.pack(pady=10)

        tk.Button(self.frame, text="Anzeigen", command=self.update_display).pack(pady=5)

        self.display = tk.Text(self.frame, width=90, height=15, state="disabled", bg="#f9f9f9")
        self.display.pack(pady=10)

        if self.is_admin:
            add_frame = tk.LabelFrame(self.frame, text="Neuen Termin hinzufügen", bg="white")
            add_frame.pack(pady=10, padx=10, fill="x")

            self.entry_title = tk.Entry(add_frame, width=30)
            self.entry_title.insert(0, "Titel")
            self.entry_title.pack(pady=2)

            self.entry_desc = tk.Entry(add_frame, width=50)
            self.entry_desc.insert(0, "Beschreibung")
            self.entry_desc.pack(pady=2)

            self.entry_category = tk.Entry(add_frame, width=30)
            self.entry_category.insert(0, "Kategorie (z. B. Klausur)")
            self.entry_category.pack(pady=2)

            # Wenn aus Verwaltung, zeige Dropdown für Gruppenwahl
            if self.group.lower() == "verwaltung":
                self.group_list = self.get_all_groups()
                self.selected_target = tk.StringVar()
                self.selected_target.set("alle")  # Default-Wert
                tk.Label(add_frame, text="Zielgruppe:", bg="white").pack(pady=(5,0))
                self.target_dropdown = ttk.Combobox(add_frame, values=self.group_list, textvariable=self.selected_target, state="readonly")
                self.target_dropdown.pack(pady=2)
            else:
                # Bei anderen Admins: Nur Eingabe
                self.entry_target = tk.Entry(add_frame, width=30)
                self.entry_target.insert(0, "Zielgruppe (z. B. 10A, alle)")
                self.entry_target.pack(pady=2)

            tk.Button(add_frame, text="Termin speichern", command=self.save_entry).pack(pady=5)

    def get_all_groups(self):
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
            groups = {data.get("group", "") for data in users.values()}
            groups.update({data.get("second_group", "") for data in users.values()})
            return sorted(list(g for g in groups if g))
        except:
            return ["alle"]

    def load_dates(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.dates = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.dates = {}

    def save_dates(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.dates, f, indent=2)

    def get_selected_date_key(self):
        return self.calendar.get_date()  # Format: dd.mm.yyyy

    def update_display(self):
        key = self.get_selected_date_key()
        self.display.config(state="normal")
        self.display.delete(1.0, "end")

        if key in self.dates:
            for entry in self.dates[key]:
                target = entry.get("target", "").lower()
                if target in [self.group.lower(), self.second_group.lower(), "alle"]:
                    self.display.insert("end", f"- {entry['title']} ({entry['category']}): {entry['desc']}\n")
        else:
            self.display.insert("end", "Keine Termine für diesen Tag.")

        self.display.config(state="disabled")

    def save_entry(self):
        key = self.get_selected_date_key()
        entry = {
            "title": self.entry_title.get().strip(),
            "desc": self.entry_desc.get().strip(),
            "category": self.entry_category.get().strip(),
        }

        # Zielgruppe abhängig vom Admin-Typ
        if self.group.lower() == "verwaltung":
            entry["target"] = self.selected_target.get().strip()
        else:
            entry["target"] = self.entry_target.get().strip()

        if not all(entry.values()):
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen.")
            return

        self.dates.setdefault(key, []).append(entry)
        self.save_dates()
        self.update_display()
        messagebox.showinfo("Gespeichert", "Termin wurde gespeichert.")

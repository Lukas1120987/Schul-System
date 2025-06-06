import tkinter as tk
import json
import os

class Modul:
    def __init__(self, master, username=None, user_data=None):
        self.master = master
        self.frame = tk.Frame(master, bg="white")
        # ...

        self.username = username
        self.group = user_data["group"]

        self.frame = tk.Frame(master, bg="white")

        if self.group != "Verwaltung":
            tk.Label(self.frame, text="⛔ Kein Zugriff auf die Stundenplanverwaltung.", font=("Arial", 14), bg="white").pack(pady=20)
            return

        tk.Label(self.frame, text="🛠️ Stundenplan-Verwaltung", font=("Arial", 16), bg="white").pack(pady=10)

        self.groups = self.get_all_groups()
        self.selected_group = tk.StringVar(value=self.groups[0] if self.groups else "")

        self.dropdown = tk.OptionMenu(self.frame, self.selected_group, *self.groups, command=self.load_schedule)
        self.dropdown.pack(pady=5)

        self.table_frame = tk.Frame(self.frame, bg="white")
        self.table_frame.pack(pady=10)

        self.save_button = tk.Button(self.frame, text="💾 Stundenplan speichern", command=self.save_schedule)
        self.save_button.pack(pady=10)

        self.entries = {}
        self.load_schedule(self.selected_group.get())

    def get_frame(self):
        return self.frame

    def get_all_groups(self):
        if not os.path.exists("data/users.json"):
            return []

        with open("data/users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        groups = set()
        for user in users.values():
            if "group" in user:
                groups.add(user["group"])
        return sorted(groups)

    def load_schedule(self, group_name):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.entries = {}

        try:
            with open("data/schedule.json", "r", encoding="utf-8") as f:
                schedule_data = json.load(f)
        except FileNotFoundError:
            schedule_data = {}

        group_schedule = schedule_data.get(group_name, {})
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

        # Kopfzeile
        tk.Label(self.table_frame, text="Stunde", font=("Arial", 10, "bold"), width=10, borderwidth=1, relief="solid").grid(row=0, column=0)
        for col, day in enumerate(days):
            tk.Label(self.table_frame, text=day, font=("Arial", 10, "bold"), width=15, borderwidth=1, relief="solid").grid(row=0, column=col+1)

        # Eingabefelder
        for row in range(1, 9):  # Stunden 1-8
            tk.Label(self.table_frame, text=str(row), width=10, borderwidth=1, relief="solid").grid(row=row, column=0)
            for col, day in enumerate(days):
                subject = group_schedule.get(day, {}).get(str(row), "")
                entry = tk.Entry(self.table_frame, width=15)
                entry.insert(0, subject)
                entry.grid(row=row, column=col+1)
                self.entries[(day, str(row))] = entry

    def save_schedule(self):
        group = self.selected_group.get()
        updated_schedule = {}

        for (day, hour), entry in self.entries.items():
            updated_schedule.setdefault(day, {})[hour] = entry.get()

        try:
            with open("data/schedule.json", "r", encoding="utf-8") as f:
                all_schedules = json.load(f)
        except FileNotFoundError:
            all_schedules = {}

        all_schedules[group] = updated_schedule

        with open("data/schedule.json", "w", encoding="utf-8") as f:
            json.dump(all_schedules, f, indent=2)

        tk.messagebox.showinfo("Gespeichert", f"Stundenplan für Gruppe '{group}' wurde gespeichert.")

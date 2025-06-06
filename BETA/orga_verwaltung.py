import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="⚙️ Organisationsverwaltung", font=("Arial", 16), bg="white").pack(pady=10)

        if not self.is_admin:
            tk.Label(self.frame, text="Nur Administratoren können diese Einstellungen ändern.", fg="red", bg="white").pack()
            return

        self.ensure_files_exist()

        self.load_data()
        self.build_gui()

    def get_frame(self):
        return self.frame

    def ensure_files_exist(self):
        os.makedirs("data", exist_ok=True)

        if not os.path.exists("data/settings.json"):
            with open("data/settings.json", "w", encoding="utf-8") as f:
                json.dump({"start_date": "", "end_date": "", "lesson_duration": 45}, f, indent=2)

        if not os.path.exists("data/subjects.json"):
            with open("data/subjects.json", "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

        if not os.path.exists("data/rooms.json"):
            with open("data/rooms.json", "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

        if not os.path.exists("data/holidays.json"):
            with open("data/holidays.json", "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_data(self):
        with open("data/settings.json", "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        with open("data/subjects.json", "r", encoding="utf-8") as f:
            self.subjects = json.load(f)

        with open("data/rooms.json", "r", encoding="utf-8") as f:
            self.rooms = json.load(f)

        with open("data/holidays.json", "r", encoding="utf-8") as f:
            self.holidays = json.load(f)

    def build_gui(self):
        # Schuljahreszeitraum
        tk.Label(self.frame, text="📅 Schuljahreszeitraum", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10, 0))

        date_frame = tk.Frame(self.frame, bg="white")
        date_frame.pack(anchor="w", padx=20, pady=2)
        tk.Label(date_frame, text="Startdatum (YYYY-MM-DD):", bg="white").grid(row=0, column=0)
        self.entry_start_date = tk.Entry(date_frame)
        self.entry_start_date.grid(row=0, column=1)
        self.entry_start_date.insert(0, self.settings.get("start_date", ""))

        tk.Label(date_frame, text="Enddatum (YYYY-MM-DD):", bg="white").grid(row=1, column=0)
        self.entry_end_date = tk.Entry(date_frame)
        self.entry_end_date.grid(row=1, column=1)
        self.entry_end_date.insert(0, self.settings.get("end_date", ""))

        # Stundendauer
        tk.Label(self.frame, text="⏱️ Stundendauer (Minuten)", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_duration = tk.Entry(self.frame)
        self.entry_duration.pack(anchor="w", padx=20)
        self.entry_duration.insert(0, str(self.settings.get("lesson_duration", 45)))

        # Ferien/Feiertage
        tk.Label(self.frame, text="🏖️ Ferien & Feiertage (YYYY-MM-DD)", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10, 0))
        self.holiday_entry = tk.Entry(self.frame)
        self.holiday_entry.pack(anchor="w", padx=20)
        tk.Button(self.frame, text="Hinzufügen", command=self.add_holiday).pack(anchor="w", padx=20, pady=(0, 5))
        self.holiday_listbox = tk.Listbox(self.frame, height=5)
        self.holiday_listbox.pack(padx=20, fill="x")
        for h in self.holidays:
            self.holiday_listbox.insert(tk.END, h)

        tk.Button(self.frame, text="Ausgewähltes Datum löschen", command=self.delete_holiday).pack(anchor="w", padx=20)

        # Fächer
        tk.Label(self.frame, text="📘 Fächerverwaltung", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10, 0))
        self.subject_entry = tk.Entry(self.frame)
        self.subject_entry.pack(anchor="w", padx=20)
        tk.Button(self.frame, text="Fach hinzufügen", command=self.add_subject).pack(anchor="w", padx=20, pady=(0, 5))
        self.subject_listbox = tk.Listbox(self.frame, height=5)
        self.subject_listbox.pack(padx=20, fill="x")
        for s in self.subjects:
            self.subject_listbox.insert(tk.END, s)

        tk.Button(self.frame, text="Fach löschen", command=self.delete_subject).pack(anchor="w", padx=20)

        # Räume
        tk.Label(self.frame, text="🏫 Räume & Fachbindung", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10, 0))
        self.room_name_entry = tk.Entry(self.frame)
        self.room_name_entry.insert(0, "Raumname")
        self.room_name_entry.pack(anchor="w", padx=20)
        self.room_subject_entry = tk.Entry(self.frame)
        self.room_subject_entry.insert(0, "Optionales Fach")
        self.room_subject_entry.pack(anchor="w", padx=20)
        tk.Button(self.frame, text="Raum hinzufügen", command=self.add_room).pack(anchor="w", padx=20, pady=(0, 5))
        self.room_listbox = tk.Listbox(self.frame, height=5)
        self.room_listbox.pack(padx=20, fill="x")
        for r in self.rooms:
            display = f"{r['name']} ({r['subject']})" if r['subject'] else r['name']
            self.room_listbox.insert(tk.END, display)

        tk.Button(self.frame, text="Raum löschen", command=self.delete_room).pack(anchor="w", padx=20)

        # Speichern
        tk.Button(self.frame, text="💾 Alle Änderungen speichern", bg="green", fg="white", command=self.save_all).pack(pady=10)

    def add_holiday(self):
        date = self.holiday_entry.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
            if date not in self.holidays:
                self.holidays.append(date)
                self.holiday_listbox.insert(tk.END, date)
                self.holiday_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte ein gültiges Datum im Format YYYY-MM-DD eingeben.")

    def delete_holiday(self):
        selection = self.holiday_listbox.curselection()
        if selection:
            index = selection[0]
            del self.holidays[index]
            self.holiday_listbox.delete(index)

    def add_subject(self):
        subject = self.subject_entry.get().strip()
        if subject and subject not in self.subjects:
            self.subjects.append(subject)
            self.subject_listbox.insert(tk.END, subject)
            self.subject_entry.delete(0, tk.END)

    def delete_subject(self):
        selection = self.subject_listbox.curselection()
        if selection:
            index = selection[0]
            del self.subjects[index]
            self.subject_listbox.delete(index)

    def add_room(self):
        name = self.room_name_entry.get().strip()
        subject = self.room_subject_entry.get().strip()
        if name:
            self.rooms.append({"name": name, "subject": subject})
            display = f"{name} ({subject})" if subject else name
            self.room_listbox.insert(tk.END, display)
            self.room_name_entry.delete(0, tk.END)
            self.room_subject_entry.delete(0, tk.END)

    def delete_room(self):
        selection = self.room_listbox.curselection()
        if selection:
            index = selection[0]
            del self.rooms[index]
            self.room_listbox.delete(index)

    def save_all(self):
        self.settings["start_date"] = self.entry_start_date.get().strip()
        self.settings["end_date"] = self.entry_end_date.get().strip()
        try:
            self.settings["lesson_duration"] = int(self.entry_duration.get())
        except ValueError:
            messagebox.showerror("Fehler", "Stundendauer muss eine Zahl sein.")
            return

        with open("data/settings.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)

        with open("data/subjects.json", "w", encoding="utf-8") as f:
            json.dump(self.subjects, f, indent=2)

        with open("data/rooms.json", "w", encoding="utf-8") as f:
            json.dump(self.rooms, f, indent=2)

        with open("data/holidays.json", "w", encoding="utf-8") as f:
            json.dump(self.holidays, f, indent=2)

        messagebox.showinfo("Gespeichert", "Alle Änderungen wurden gespeichert.")

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="🧑‍🏫 Vertretungsverwaltung", font=("Arial", 16), bg="white").pack(pady=10)

        if not self.is_admin:
            tk.Label(self.frame, text="Nur Administratoren können dieses Modul verwenden.", fg="red", bg="white").pack()
            return

        self.ensure_files()
        self.load_data()
        self.build_gui()

    def get_frame(self):
        return self.frame

    def ensure_files(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists("data/vertretungen.json"):
            with open("data/vertretungen.json", "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_data(self):
        with open("data/users.json", "r", encoding="utf-8") as f:
            self.users = json.load(f)

        try:
            with open("data/subjects.json", "r", encoding="utf-8") as f:
                self.subjects = json.load(f)
        except:
            self.subjects = []

        try:
            with open("data/rooms.json", "r", encoding="utf-8") as f:
                self.rooms = json.load(f)
        except:
            self.rooms = []

        with open("data/vertretungen.json", "r", encoding="utf-8") as f:
            self.vertretungen = json.load(f)

        self.lehrer = [u for u in self.users if self.users[u].get("group") == "Lehrer"]
        self.klassen = sorted(set(self.users[u]["second_group"] for u in self.users if self.users[u].get("second_group")))

    def build_gui(self):
        # Abschnitt Auswahl
        frame_input = tk.Frame(self.frame, bg="white")
        frame_input.pack(pady=5)

        # Klasse
        tk.Label(frame_input, text="🎓 Klasse:", bg="white").grid(row=0, column=0, sticky="w")
        self.klasse_var = tk.StringVar()
        ttk.Combobox(frame_input, textvariable=self.klasse_var, values=self.klassen, state="readonly").grid(row=0, column=1, padx=5)

        # Datum
        tk.Label(frame_input, text="📅 Datum:", bg="white").grid(row=1, column=0, sticky="w")
        self.datum_entry = tk.Entry(frame_input)
        self.datum_entry.insert(0, str(date.today()))
        self.datum_entry.grid(row=1, column=1)

        # Stunde
        tk.Label(frame_input, text="⏰ Stunde:", bg="white").grid(row=2, column=0, sticky="w")
        self.stunde_var = tk.StringVar()
        ttk.Combobox(frame_input, textvariable=self.stunde_var, values=[str(i) for i in range(1, 9)], state="readonly").grid(row=2, column=1)

        # Lehrerwahl
        tk.Label(frame_input, text="👨‍🏫 Lehrer:", bg="white").grid(row=3, column=0, sticky="w")
        self.lehrer_var = tk.StringVar()
        ttk.Combobox(frame_input, textvariable=self.lehrer_var, values=self.lehrer, state="readonly").grid(row=3, column=1)

        # Fachwahl
        tk.Label(frame_input, text="📚 Fach:", bg="white").grid(row=4, column=0, sticky="w")
        self.fach_var = tk.StringVar()
        ttk.Combobox(frame_input, textvariable=self.fach_var, values=self.subjects, state="readonly").grid(row=4, column=1)

        # Raumwahl
        tk.Label(frame_input, text="🏫 Raum:", bg="white").grid(row=5, column=0, sticky="w")
        self.raum_var = tk.StringVar()
        ttk.Combobox(frame_input, textvariable=self.raum_var, values=[r["name"] for r in self.rooms], state="readonly").grid(row=5, column=1)

        # Buttons
        frame_buttons = tk.Frame(self.frame, bg="white")
        frame_buttons.pack(pady=10)

        tk.Button(frame_buttons, text="➕ Komplettvertretung", command=self.add_full).grid(row=0, column=0, padx=5)
        tk.Button(frame_buttons, text="👨‍🏫 Nur Lehrerwechsel", command=self.add_teacher).grid(row=0, column=1, padx=5)
        tk.Button(frame_buttons, text="🏫 Nur Raumwechsel", command=self.add_room).grid(row=0, column=2, padx=5)

        # Liste + Aktionen
        self.vertretungsliste = tk.Listbox(self.frame, height=8)
        self.vertretungsliste.pack(padx=20, pady=10, fill="x")

        tk.Button(self.frame, text="🗑️ Ausgewählte löschen", command=self.delete_entry).pack(pady=3)
        tk.Button(self.frame, text="💾 Speichern", command=self.save, bg="green", fg="white").pack(pady=5)

        self.refresh_list()

    def add_full(self):
        if not self.check_required(["klasse", "datum", "stunde", "lehrer"]):
            return
        entry = {
            "klasse": self.klasse_var.get(),
            "datum": self.datum_entry.get(),
            "stunde": self.stunde_var.get(),
            "lehrer": self.lehrer_var.get()
        }
        if self.fach_var.get(): entry["fach"] = self.fach_var.get()
        if self.raum_var.get(): entry["raum"] = self.raum_var.get()
        self.vertretungen.append(entry)
        self.refresh_list()

    def add_teacher(self):
        if not self.check_required(["klasse", "datum", "stunde", "lehrer"]):
            return
        self.vertretungen.append({
            "klasse": self.klasse_var.get(),
            "datum": self.datum_entry.get(),
            "stunde": self.stunde_var.get(),
            "lehrer": self.lehrer_var.get()
        })
        self.refresh_list()

    def add_room(self):
        if not self.check_required(["klasse", "datum", "stunde", "raum"]):
            return
        self.vertretungen.append({
            "klasse": self.klasse_var.get(),
            "datum": self.datum_entry.get(),
            "stunde": self.stunde_var.get(),
            "raum": self.raum_var.get()
        })
        self.refresh_list()

    def delete_entry(self):
        index = self.vertretungsliste.curselection()
        if index:
            del self.vertretungen[index[0]]
            self.refresh_list()

    def refresh_list(self):
        self.vertretungsliste.delete(0, tk.END)
        for eintrag in self.vertretungen:
            zeile = f"{eintrag['datum']} | {eintrag['klasse']} | {eintrag['stunde']} Std"
            if "lehrer" in eintrag: zeile += f" → {eintrag['lehrer']}"
            if "fach" in eintrag: zeile += f" ({eintrag['fach']})"
            if "raum" in eintrag: zeile += f", Raum {eintrag['raum']}"
            self.vertretungsliste.insert(tk.END, zeile)

    def save(self):
        with open("data/vertretungen.json", "w", encoding="utf-8") as f:
            json.dump(self.vertretungen, f, indent=2)
        messagebox.showinfo("Gespeichert", "Vertretungen wurden gespeichert.")

    def check_required(self, fields):
        for field in fields:
            if getattr(self, f"{field}_var", self.datum_entry).get().strip() == "":
                messagebox.showerror("Fehlende Eingabe", f"{field.capitalize()} fehlt.")
                return False
        return True

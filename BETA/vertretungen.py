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
        tk.Label(self.frame, text="🧑‍🏫 Vertretungen verwalten", font=("Arial", 16), bg="white").pack(pady=10)

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

        # Lehrer & Klassen
        self.lehrer = [u for u in self.users if self.users[u].get("group") == "Lehrer"]
        self.klassen = list(set(self.users[u]["second_group"] for u in self.users if self.users[u].get("second_group")))

    def build_gui(self):
        # Klasse wählen
        tk.Label(self.frame, text="🎓 Klasse", bg="white").pack(anchor="w", padx=10)
        self.klasse_var = tk.StringVar()
        self.klasse_dropdown = ttk.Combobox(self.frame, textvariable=self.klasse_var, values=self.klassen, state="readonly")
        self.klasse_dropdown.pack(anchor="w", padx=20, pady=2)

        # Datum
        tk.Label(self.frame, text="📅 Datum (YYYY-MM-DD)", bg="white").pack(anchor="w", padx=10)
        self.datum_entry = tk.Entry(self.frame)
        self.datum_entry.insert(0, str(date.today()))
        self.datum_entry.pack(anchor="w", padx=20, pady=2)

        # Stunde
        tk.Label(self.frame, text="⏰ Stunde (z. B. 1–8)", bg="white").pack(anchor="w", padx=10)
        self.stunde_var = tk.StringVar()
        self.stunde_dropdown = ttk.Combobox(self.frame, textvariable=self.stunde_var, values=[str(i) for i in range(1, 9)], state="readonly")
        self.stunde_dropdown.pack(anchor="w", padx=20, pady=2)

        # Neuer Lehrer
        tk.Label(self.frame, text="👨‍🏫 Vertretungslehrer", bg="white").pack(anchor="w", padx=10)
        self.lehrer_var = tk.StringVar()
        self.lehrer_dropdown = ttk.Combobox(self.frame, textvariable=self.lehrer_var, values=self.lehrer, state="readonly")
        self.lehrer_dropdown.pack(anchor="w", padx=20, pady=2)

        # Fach (optional)
        tk.Label(self.frame, text="📚 Fach (optional)", bg="white").pack(anchor="w", padx=10)
        self.fach_var = tk.StringVar()
        self.fach_dropdown = ttk.Combobox(self.frame, textvariable=self.fach_var, values=self.subjects, state="readonly")
        self.fach_dropdown.pack(anchor="w", padx=20, pady=2)

        # Raum (optional)
        tk.Label(self.frame, text="🏫 Raum (optional)", bg="white").pack(anchor="w", padx=10)
        self.raum_var = tk.StringVar()
        self.raum_dropdown = ttk.Combobox(self.frame, textvariable=self.raum_var, values=[r["name"] for r in self.rooms], state="readonly")
        self.raum_dropdown.pack(anchor="w", padx=20, pady=2)

        # Button hinzufügen
        tk.Button(self.frame, text="➕ Vertretung eintragen", command=self.add_vertretung).pack(pady=5)

        # Liste bestehender Vertretungen
        self.vertretungsliste = tk.Listbox(self.frame, height=8)
        self.vertretungsliste.pack(padx=20, pady=10, fill="x")
        self.refresh_list()

        # Löschen
        tk.Button(self.frame, text="🗑️ Ausgewählte Vertretung löschen", command=self.delete_vertretung).pack()

        # Speichern
        tk.Button(self.frame, text="💾 Speichern", bg="green", fg="white", command=self.save).pack(pady=10)

    def add_vertretung(self):
        klasse = self.klasse_var.get()
        datum = self.datum_entry.get()
        stunde = self.stunde_var.get()
        lehrer = self.lehrer_var.get()
        fach = self.fach_var.get()
        raum = self.raum_var.get()

        if not (klasse and datum and stunde and lehrer):
            messagebox.showerror("Fehler", "Bitte Klasse, Datum, Stunde und Lehrer angeben.")
            return

        eintrag = {
            "klasse": klasse,
            "datum": datum,
            "stunde": stunde,
            "lehrer": lehrer
        }
        if fach: eintrag["fach"] = fach
        if raum: eintrag["raum"] = raum

        self.vertretungen.append(eintrag)
        self.refresh_list()

    def delete_vertretung(self):
        index = self.vertretungsliste.curselection()
        if index:
            del self.vertretungen[index[0]]
            self.refresh_list()

    def refresh_list(self):
        self.vertretungsliste.delete(0, tk.END)
        for eintrag in self.vertretungen:
            zeile = f"{eintrag['datum']} – {eintrag['klasse']} – {eintrag['stunde']}. Std → {eintrag['lehrer']}"
            if 'fach' in eintrag: zeile += f" ({eintrag['fach']})"
            if 'raum' in eintrag: zeile += f", Raum {eintrag['raum']}"
            self.vertretungsliste.insert(tk.END, zeile)

    def save(self):
        with open("data/vertretungen.json", "w", encoding="utf-8") as f:
            json.dump(self.vertretungen, f, indent=2)
        messagebox.showinfo("Gespeichert", "Vertretungen gespeichert.")

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="📚 Unterrichtsverwaltung", font=("Arial", 16), bg="white").pack(pady=10)

        if not self.is_admin:
            tk.Label(self.frame, text="Nur Administratoren können diese Seite verwenden.", fg="red", bg="white").pack()
            return

        self.ensure_files()
        self.load_data()
        self.build_gui()

    def get_frame(self):
        return self.frame

    def ensure_files(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists("data/unterricht.json"):
            with open("data/unterricht.json", "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

    def load_data(self):
        with open("data/users.json", "r", encoding="utf-8") as f:
            self.users = json.load(f)
        with open("data/subjects.json", "r", encoding="utf-8") as f:
            self.subjects = json.load(f)
        with open("data/rooms.json", "r", encoding="utf-8") as f:
            self.rooms = json.load(f)
        with open("data/unterricht.json", "r", encoding="utf-8") as f:
            self.teaching_data = json.load(f)

        # Extrahiere Klassen (second_group)
        self.klassen = list(set(user.get("second_group") for user in self.users.values() if user.get("second_group")))

        # Extrahiere Lehrer
        self.lehrer = [name for name, info in self.users.items() if info.get("group") == "Lehrer"]

    def build_gui(self):
        # Klassenwahl
        tk.Label(self.frame, text="🎓 Klasse auswählen", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.klasse_var = tk.StringVar()
        self.klasse_dropdown = ttk.Combobox(self.frame, textvariable=self.klasse_var, values=self.klassen, state="readonly")
        self.klasse_dropdown.pack(anchor="w", padx=20, pady=(0, 10))
        self.klasse_dropdown.bind("<<ComboboxSelected>>", self.load_klasse_data)

        # Zuordnung Lehrer – Fach
        tk.Label(self.frame, text="👨‍🏫 Lehrer-Fach-Zuweisung", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.fach_var = tk.StringVar()
        self.fach_dropdown = ttk.Combobox(self.frame, textvariable=self.fach_var, values=self.subjects, state="readonly")
        self.fach_dropdown.pack(anchor="w", padx=20, pady=(0, 5))

        self.lehrer_var = tk.StringVar()
        self.lehrer_dropdown = ttk.Combobox(self.frame, textvariable=self.lehrer_var, values=self.lehrer, state="readonly")
        self.lehrer_dropdown.pack(anchor="w", padx=20, pady=(0, 5))

        self.raum_var = tk.StringVar()
        self.raum_dropdown = ttk.Combobox(self.frame, textvariable=self.raum_var, values=[r["name"] for r in self.rooms], state="readonly")
        self.raum_dropdown.pack(anchor="w", padx=20, pady=(0, 5))

        tk.Button(self.frame, text="Unterrichtseinheit hinzufügen", command=self.add_teaching).pack(anchor="w", padx=20, pady=5)

        # Liste anzeigen
        self.listbox = tk.Listbox(self.frame, height=8)
        self.listbox.pack(padx=20, fill="x", pady=5)

        tk.Button(self.frame, text="Ausgewählten Eintrag löschen", command=self.delete_teaching).pack(anchor="w", padx=20)

        # Speichern
        tk.Button(self.frame, text="💾 Speichern", bg="green", fg="white", command=self.save).pack(pady=10)

    def load_klasse_data(self, event=None):
        klasse = self.klasse_var.get()
        self.listbox.delete(0, tk.END)
        eintraege = self.teaching_data.get(klasse, [])
        for eintrag in eintraege:
            self.listbox.insert(tk.END, f"{eintrag['fach']} – {eintrag['lehrer']} – {eintrag['raum']}")

    def add_teaching(self):
        klasse = self.klasse_var.get()
        if not klasse:
            messagebox.showerror("Fehler", "Bitte eine Klasse auswählen.")
            return

        fach = self.fach_var.get()
        lehrer = self.lehrer_var.get()
        raum = self.raum_var.get()
        if not (fach and lehrer and raum):
            messagebox.showerror("Fehler", "Bitte Fach, Lehrer und Raum auswählen.")
            return

        eintrag = {"fach": fach, "lehrer": lehrer, "raum": raum}
        self.teaching_data.setdefault(klasse, []).append(eintrag)
        self.listbox.insert(tk.END, f"{fach} – {lehrer} – {raum}")

    def delete_teaching(self):
        index = self.listbox.curselection()
        klasse = self.klasse_var.get()
        if index and klasse in self.teaching_data:
            del self.teaching_data[klasse][index[0]]
            self.listbox.delete(index)

    def save(self):
        with open("data/unterricht.json", "w", encoding="utf-8") as f:
            json.dump(self.teaching_data, f, indent=2)
        messagebox.showinfo("Gespeichert", "Unterrichtszuweisungen gespeichert.")

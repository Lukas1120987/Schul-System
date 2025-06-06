import tkinter as tk
from tkinter import messagebox
import json
import os

GERÄTE_DATEI = "data/geraete.json"
USERS_DATEI = "data/users.json"

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.frame = tk.Frame(master, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.user_data = user_data

        self.is_admin = self.check_if_admin()

        self.initialisiere_geraete_datei()


        tk.Label(self.frame, text="📦 Geräteausleihe", font=("Arial", 16), bg="white").pack(pady=10)

        self.geraete_listbox = tk.Listbox(self.frame, width=40)
        self.geraete_listbox.pack(pady=10)

        btn_frame = tk.Frame(self.frame, bg="white")
        btn_frame.pack()

        tk.Button(btn_frame, text="ℹ️ Info", command=self.show_info).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📤 Ausleihen", command=self.ausleihen).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📥 Zurückgeben", command=self.zurueckgeben).pack(side=tk.LEFT, padx=5)

        if self.is_admin:
            tk.Button(self.frame, text="➕ Neues Gerät hinzufügen", command=self.add_device).pack(pady=10)

        self.lade_geraete()

    def get_frame(self):
        return self.frame

    def initialisiere_geraete_datei(self):
        if not os.path.exists(GERÄTE_DATEI):
            with open(GERÄTE_DATEI, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)


    def check_if_admin(self):
        if not os.path.exists(USERS_DATEI):
            return False
        with open(USERS_DATEI, "r", encoding="utf-8") as f:
            users = json.load(f)
            return users.get(self.username, {}).get("is_admin", False)

    def lade_geraete(self):
        self.geraete_listbox.delete(0, tk.END)
        if not os.path.exists(GERÄTE_DATEI):
            return
        with open(GERÄTE_DATEI, "r", encoding="utf-8") as f:
            geraete = json.load(f)
            for name, daten in geraete.items():
                status = "✅ Verfügbar" if daten["verfügbar"] else f"❌ Ausgeliehen von {daten['ausgeliehen_von']}"
                self.geraete_listbox.insert(tk.END, f"{name} - {status}")

    def get_selected_geraet(self):
        selection = self.geraete_listbox.curselection()
        if not selection:
            return None
        selected_text = self.geraete_listbox.get(selection[0])
        return selected_text.split(" - ")[0]

    def show_info(self):
        name = self.get_selected_geraet()
        if not name:
            messagebox.showerror("Fehler", "Bitte ein Gerät auswählen.")
            return
        with open(GERÄTE_DATEI, "r", encoding="utf-8") as f:
            daten = json.load(f).get(name)
        messagebox.showinfo(name, f"📃 Beschreibung:\n{daten['beschreibung']}\n\nStatus: {'Verfügbar' if daten['verfügbar'] else 'Ausgeliehen'}")

    def ausleihen(self):
        name = self.get_selected_geraet()
        if not name:
            return
        with open(GERÄTE_DATEI, "r", encoding="utf-8") as f:
            daten = json.load(f)
        if not daten[name]["verfügbar"]:
            messagebox.showwarning("Nicht verfügbar", "Gerät ist bereits ausgeliehen.")
            return
        daten[name]["verfügbar"] = False
        daten[name]["ausgeliehen_von"] = self.username
        with open(GERÄTE_DATEI, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=2)
        self.lade_geraete()

    def zurueckgeben(self):
        name = self.get_selected_geraet()
        if not name:
            return
        with open(GERÄTE_DATEI, "r", encoding="utf-8") as f:
            daten = json.load(f)
        if daten[name]["verfügbar"]:
            messagebox.showinfo("Info", "Gerät ist bereits verfügbar.")
            return
        if daten[name]["ausgeliehen_von"] != self.username and not self.is_admin:
            messagebox.showerror("Fehler", "Du kannst dieses Gerät nicht zurückgeben.")
            return
        daten[name]["verfügbar"] = True
        daten[name]["ausgeliehen_von"] = None
        with open(GERÄTE_DATEI, "w") as f:
            json.dump(daten, f, indent=2)
        self.lade_geraete()

    def add_device(self):
        win = tk.Toplevel(self.master)
        win.title("Neues Gerät hinzufügen")
        win.configure(bg="white")

        tk.Label(win, text="Gerätename", bg="white").pack(pady=(10, 0))
        name_entry = tk.Entry(win)
        name_entry.pack()

        tk.Label(win, text="Beschreibung", bg="white").pack(pady=(10, 0))
        beschr_entry = tk.Text(win, height=5, width=40)
        beschr_entry.pack()

        def save():
            name = name_entry.get().strip()
            beschreibung = beschr_entry.get("1.0", tk.END).strip()

            if not name or not beschreibung:
                messagebox.showerror("Fehler", "Alle Felder ausfüllen.", parent=win)
                return

            if os.path.exists(GERÄTE_DATEI):
                with open(GERÄTE_DATEI, "r", encoding="utf-8") as f:
                    daten = json.load(f)
            else:
                daten = {}

            if name in daten:
                messagebox.showerror("Fehler", "Gerät existiert bereits.", parent=win)
                return

            daten[name] = {
                "beschreibung": beschreibung,
                "verfügbar": True,
                "ausgeliehen_von": None
            }

            with open(GERÄTE_DATEI, "w", encoding="utf-8") as f:
                json.dump(daten, f, indent=2)
            messagebox.showinfo("Erfolg", "Gerät hinzugefügt.", parent=win)
            win.destroy()
            self.lade_geraete()

        tk.Button(win, text="Hinzufügen", command=save).pack(pady=10)

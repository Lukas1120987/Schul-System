import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from datetime import datetime

SPRECHSTUNDEN_DB = "data/sprechstunden.json"
SPRECHZEITEN_DB = "data/sprechzeiten.json"
USERS_DB = "data/users.json"
NOTIFICATIONS_DB = "data/notifications.json"

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.group = user_data["group"]
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="🗓️ Sprechstunden", font=("Arial", 16), bg="white").pack(pady=10)

        self.ensure_files()
        self.load_data()
        self.setup_ui()

    def get_frame(self):
        return self.frame

    def ensure_files(self):
        os.makedirs("data", exist_ok=True)
        for path, default in [(SPRECHSTUNDEN_DB, {}), (SPRECHZEITEN_DB, {}), (NOTIFICATIONS_DB, {})]:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f)

    def load_data(self):
        with open(SPRECHSTUNDEN_DB, "r", encoding="utf-8") as f:
            self.sprechstunden = json.load(f)

        with open(SPRECHZEITEN_DB, "r", encoding="utf-8") as f:
            self.sprechzeiten = json.load(f)

        with open(USERS_DB, "r", encoding="utf-8") as f:
            self.users = json.load(f)

        with open(NOTIFICATIONS_DB, "r", encoding="utf-8") as f:
            self.notifications = json.load(f)

        self.lehrer = [k for k, u in self.users.items() if u.get("group") == "Lehrer"]

    def setup_ui(self):
        if self.group == "Lehrer":
            self.setup_lehrer_ui()
        else:
            self.setup_schueler_ui()

    def setup_schueler_ui(self):
        frame = tk.LabelFrame(self.frame, text="Termin buchen", bg="white")
        frame.pack(padx=10, pady=10, fill="x")

        tk.Label(frame, text="Lehrkraft wählen:", bg="white").pack()
        self.lehrer_select = ttk.Combobox(frame, values=self.lehrer, state="readonly")
        self.lehrer_select.pack(pady=5)

        tk.Button(frame, text="Verfügbare Zeiten anzeigen", command=self.zeige_zeiten).pack(pady=5)
        self.zeiten_frame = tk.Frame(self.frame, bg="white")
        self.zeiten_frame.pack(fill="both", expand=True)

        self.meine_termine_frame = tk.LabelFrame(self.frame, text="Meine gebuchten Termine", bg="white")
        self.meine_termine_frame.pack(padx=10, pady=10, fill="x")
        self.update_meine_termine()

    def zeige_zeiten(self):
        for w in self.zeiten_frame.winfo_children():
            w.destroy()

        lehrer = self.lehrer_select.get()
        if not lehrer:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle eine Lehrkraft aus.")
            return

        zeiten = self.sprechzeiten.get(lehrer, [])
        gebuchte = self.sprechstunden.get(lehrer, {}).get(self.username, [])

        for zeit in zeiten:
            if zeit not in gebuchte:
                frame = tk.Frame(self.zeiten_frame, bg="white", bd=1, relief="solid")
                frame.pack(fill="x", pady=2)
                tk.Label(frame, text=zeit, bg="white").pack(side="left", padx=5)
                tk.Button(frame, text="Buchen", command=lambda z=zeit, l=lehrer: self.buche_termin(l, z)).pack(side="right", padx=5)

    def buche_termin(self, lehrer, zeit):
        self.sprechstunden.setdefault(lehrer, {}).setdefault(self.username, []).append(zeit)
        with open(SPRECHSTUNDEN_DB, "w", encoding="utf-8") as f:
            json.dump(self.sprechstunden, f, indent=2)
        self.zeige_zeiten()
        self.update_meine_termine()

    def update_meine_termine(self):
        for widget in self.meine_termine_frame.winfo_children():
            widget.destroy()

        buchungen = []
        for lehrer in self.lehrer:
            buchungen += [(lehrer, z) for z in self.sprechstunden.get(lehrer, {}).get(self.username, [])]

        for lehrer, zeit in buchungen:
            frame = tk.Frame(self.meine_termine_frame, bg="white", bd=1, relief="solid")
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=f"{zeit} bei {lehrer}", bg="white").pack(side="left", padx=5)
            tk.Button(frame, text="Absagen", command=lambda l=lehrer, z=zeit: self.absagen_termin_voll(l, z)).pack(side="right", padx=5)

    def absagen_termin_voll(self, lehrer, zeit):
        if lehrer in self.sprechstunden and self.username in self.sprechstunden[lehrer]:
            if zeit in self.sprechstunden[lehrer][self.username]:
                self.sprechstunden[lehrer][self.username].remove(zeit)
                if not self.sprechstunden[lehrer][self.username]:
                    del self.sprechstunden[lehrer][self.username]
                with open(SPRECHSTUNDEN_DB, "w", encoding="utf-8") as f:
                    json.dump(self.sprechstunden, f, indent=2)
                self.zeige_zeiten()
                self.update_meine_termine()

    def setup_lehrer_ui(self):
        frame = tk.LabelFrame(self.frame, text="Sprechzeiten verwalten", bg="white")
        frame.pack(padx=10, pady=10, fill="x")

        tk.Label(frame, text="Neue Zeit hinzufügen (z. B. Montag 14:00):", bg="white").pack()
        self.neue_zeit_entry = tk.Entry(frame)
        self.neue_zeit_entry.pack(pady=5)

        tk.Button(frame, text="Hinzufügen", command=self.zeit_hinzufuegen).pack(pady=5)

        self.zeiten_liste = tk.Listbox(frame)
        self.zeiten_liste.pack(pady=5, fill="x")
        self.update_zeiten_liste()

        tk.Button(frame, text="Ausgewählte Zeit löschen", command=self.zeit_loeschen).pack(pady=5)

        buchungen_frame = tk.LabelFrame(self.frame, text="Buchungen", bg="white")
        buchungen_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.buchungen_text = tk.Text(buchungen_frame, height=10)
        self.buchungen_text.pack(fill="both", expand=True)
        self.zeige_buchungen()

        tk.Button(buchungen_frame, text="Buchung absagen", command=self.buchung_absagen).pack(pady=5)

    def zeit_hinzufuegen(self):
        neue_zeit = self.neue_zeit_entry.get().strip()

        muster = r"^(Montag|Dienstag|Mittwoch|Donnerstag|Freitag)\s([0-2]?[0-9]):([0-5][0-9])$"
        match = re.match(muster, neue_zeit)
        if not neue_zeit:
            messagebox.showwarning("Fehler", "Bitte gib eine Zeit ein.")
            return
        if not match:
            messagebox.showerror("Ungültiges Format", "Bitte gib eine gültige Zeit wie 'Montag 14:00' ein.")
            return

        if neue_zeit in self.sprechzeiten.get(self.username, []):
            messagebox.showinfo("Bereits vorhanden", "Diese Zeit ist bereits eingetragen.")
            return

        self.sprechzeiten.setdefault(self.username, []).append(neue_zeit)
        with open(SPRECHZEITEN_DB, "w", encoding="utf-8") as f:
            json.dump(self.sprechzeiten, f, indent=2)
        self.neue_zeit_entry.delete(0, "end")
        self.update_zeiten_liste()

    def zeit_loeschen(self):
        auswahl = self.zeiten_liste.curselection()
        if auswahl:
            index = auswahl[0]
            del self.sprechzeiten[self.username][index]
            with open(SPRECHZEITEN_DB, "w", encoding="utf-8") as f:
                json.dump(self.sprechzeiten, f, indent=2)
            self.update_zeiten_liste()

    def update_zeiten_liste(self):
        self.zeiten_liste.delete(0, "end")
        for z in self.sprechzeiten.get(self.username, []):
            self.zeiten_liste.insert("end", z)

    def zeige_buchungen(self):
        self.buchungen_text.delete("1.0", "end")
        self.buchungen = self.sprechstunden.get(self.username, {})
        for schueler, zeiten in self.buchungen.items():
            for z in zeiten:
                self.buchungen_text.insert("end", f"{schueler}: {z}\n")

    def buchung_absagen(self):
        zeile = self.buchungen_text.get("sel.first", "sel.last").strip()
        if not zeile or ":" not in zeile:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle eine Buchung aus dem Textfeld aus.")
            return
        schueler, zeit = zeile.split(":", 1)
        schueler = schueler.strip()
        zeit = zeit.strip()
        if schueler in self.sprechstunden.get(self.username, {}) and zeit in self.sprechstunden[self.username][schueler]:
            self.sprechstunden[self.username][schueler].remove(zeit)
            if not self.sprechstunden[self.username][schueler]:
                del self.sprechstunden[self.username][schueler]
            with open(SPRECHSTUNDEN_DB, "w", encoding="utf-8") as f:
                json.dump(self.sprechstunden, f, indent=2)
            self.zeige_buchungen()
            self.send_notification(schueler, f"{self.username} hat den Termin am {zeit} abgesagt.")

    def send_notification(self, empfaenger, text):
        datum = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.notifications.setdefault(empfaenger, []).append({
            "text": text,
            "datum": datum,
            "gelesen": False
        })
        with open(NOTIFICATIONS_DB, "w", encoding="utf-8") as f:
            json.dump(self.notifications, f, indent=2)

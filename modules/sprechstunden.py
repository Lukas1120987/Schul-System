import customtkinter as ctk
from tkinter import messagebox
import json
import os
import re
from datetime import datetime

from ordner import get_data_path


SPRECHSTUNDEN_DB = os.path.join(get_data_path(), "data/sprechstunden.json")
SPRECHZEITEN_DB = os.path.join(get_data_path(), "data/sprechzeiten.json")
USERS_DB = os.path.join(get_data_path(), "data/users.json")
NOTIFICATIONS_DB = os.path.join(get_data_path(), "data/notifications.json")

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.group = user_data["group"]
        self.is_admin = user_data.get("is_admin", False)

        self.frame = ctk.CTkFrame(master, corner_radius=10)
        ctk.CTkLabel(self.frame, text="🗓️ Sprechstunden", font=("Arial", 18, "bold")).pack(pady=10)

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

    # ---------------- Schüler-UI ----------------
    def setup_schueler_ui(self):
        frame = ctk.CTkFrame(self.frame, corner_radius=10)
        frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(frame, text="Termin buchen:", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(frame, text="Lehrkraft wählen:").pack()

        self.lehrer_select = ctk.CTkComboBox(frame, values=self.lehrer, state="readonly")
        self.lehrer_select.pack(pady=5)

        ctk.CTkButton(frame, text="Verfügbare Zeiten anzeigen", command=self.zeige_zeiten).pack(pady=5)

        self.zeiten_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.zeiten_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.meine_termine_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.meine_termine_frame.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(self.meine_termine_frame, text="Meine gebuchten Termine", font=("Arial", 14, "bold")).pack()
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
                frame = ctk.CTkFrame(self.zeiten_frame, corner_radius=8)
                frame.pack(fill="x", pady=2, padx=5)
                ctk.CTkLabel(frame, text=zeit).pack(side="left", padx=5)
                ctk.CTkButton(frame, text="Buchen", width=80, 
                              command=lambda z=zeit, l=lehrer: self.buche_termin(l, z)).pack(side="right", padx=5)

    def buche_termin(self, lehrer, zeit):
        self.sprechstunden.setdefault(lehrer, {}).setdefault(self.username, []).append(zeit)
        with open(SPRECHSTUNDEN_DB, "w", encoding="utf-8") as f:
            json.dump(self.sprechstunden, f, indent=2)
        self.zeige_zeiten()
        self.update_meine_termine()

    def update_meine_termine(self):
        for widget in self.meine_termine_frame.winfo_children():
            if not isinstance(widget, ctk.CTkLabel):  # Überschrift behalten
                widget.destroy()

        buchungen = []
        for lehrer in self.lehrer:
            buchungen += [(lehrer, z) for z in self.sprechstunden.get(lehrer, {}).get(self.username, [])]

        for lehrer, zeit in buchungen:
            frame = ctk.CTkFrame(self.meine_termine_frame, corner_radius=8)
            frame.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(frame, text=f"{zeit} bei {lehrer}").pack(side="left", padx=5)
            ctk.CTkButton(frame, text="Absagen", width=80, 
                          command=lambda l=lehrer, z=zeit: self.absagen_termin_voll(l, z)).pack(side="right", padx=5)

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

    # ---------------- Lehrer-UI ----------------
    def setup_lehrer_ui(self):
        frame = ctk.CTkFrame(self.frame, corner_radius=10)
        frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(frame, text="Sprechzeiten verwalten", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(frame, text="Neue Zeit hinzufügen (z. B. Montag 14:00):").pack()

        self.neue_zeit_entry = ctk.CTkEntry(frame, placeholder_text="Montag 14:00")
        self.neue_zeit_entry.pack(pady=5, fill="x", padx=5)

        ctk.CTkButton(frame, text="Hinzufügen", command=self.zeit_hinzufuegen).pack(pady=5)

        self.zeiten_liste = ctk.CTkTextbox(frame, height=120)
        self.zeiten_liste.pack(pady=5, fill="x", padx=5)
        self.update_zeiten_liste()

        ctk.CTkButton(frame, text="Ausgewählte Zeit löschen", command=self.zeit_loeschen).pack(pady=5)

        buchungen_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        buchungen_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(buchungen_frame, text="Buchungen", font=("Arial", 14, "bold")).pack()
        self.buchungen_text = ctk.CTkTextbox(buchungen_frame, height=200)
        self.buchungen_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.zeige_buchungen()

        ctk.CTkButton(buchungen_frame, text="Buchung absagen", command=self.buchung_absagen).pack(pady=5)

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
        # letzte Zeile aus Textbox löschen
        lines = self.zeiten_liste.get("0.0", "end").splitlines()
        if lines:
            letzte = lines[-2] if len(lines) > 1 else lines[0]
            if letzte.strip() in self.sprechzeiten.get(self.username, []):
                self.sprechzeiten[self.username].remove(letzte.strip())
                with open(SPRECHZEITEN_DB, "w", encoding="utf-8") as f:
                    json.dump(self.sprechzeiten, f, indent=2)
                self.update_zeiten_liste()

    def update_zeiten_liste(self):
        self.zeiten_liste.delete("0.0", "end")
        for z in self.sprechzeiten.get(self.username, []):
            self.zeiten_liste.insert("end", z + "\n")

    def zeige_buchungen(self):
        self.buchungen_text.delete("0.0", "end")
        self.buchungen = self.sprechstunden.get(self.username, {})
        for schueler, zeiten in self.buchungen.items():
            for z in zeiten:
                self.buchungen_text.insert("end", f"{schueler}: {z}\n")

    def buchung_absagen(self):
        try:
            zeile = self.buchungen_text.get("sel.first", "sel.last").strip()
        except Exception:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle eine Buchung aus dem Textfeld aus.")
            return

        if not zeile or ":" not in zeile:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle eine gültige Buchung aus.")
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

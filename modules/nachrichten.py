import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class Modul:
    def __init__(self, parent, nutzername, user_data=None):
        self.frame = tk.Frame(parent)
        self.nutzername = nutzername
        self.user_data = user_data or {}

        self.baue_gui()

    def get_frame(self):
        return self.frame

    def baue_gui(self):
        # Widgets aufräumen
        for widget in self.frame.winfo_children():
            widget.destroy()

        def lade_nutzer():
            try:
                with open("data/users.json", "r", encoding="utf-8") as f:
                    nutzer_daten = json.load(f)
                return [nutzer for nutzer in nutzer_daten.keys()]
            except (FileNotFoundError, json.JSONDecodeError):
                return []

        def lade_nachrichten():
            try:
                with open("data/messages.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return []

        def filter_nachrichten(event=None):
            suchbegriff = suche_entry.get().lower()
            liste.delete(*liste.get_children())
            for nachricht in lade_nachrichten():
                empfänger = nachricht.get("empfänger")
                betreff = nachricht.get("betreff", "").lower()
                inhalt = nachricht.get("inhalt", "").lower()

                if empfänger == self.nutzername and (suchbegriff in betreff or suchbegriff in inhalt):
                    liste.insert("", "end", values=(
                        nachricht.get("datum", ""),
                        nachricht.get("absender", ""),
                        nachricht.get("betreff", "")
                    ))

        def zeige_nachricht(event):
            ausgewählt = liste.selection()
            if ausgewählt:
                item = liste.item(ausgewählt[0])
                betreff = item["values"][2]
                for nachricht in lade_nachrichten():
                    if nachricht.get("empfänger") == self.nutzername and nachricht.get("betreff") == betreff:
                        messagebox.showinfo(
                            f"Nachricht von {nachricht.get('absender')}",
                            f"Betreff: {betreff}\n\n{nachricht.get('inhalt')}"
                        )
                        break

        def senden():
            empfänger = empfänger_entry.get()
            betreff = betreff_entry.get()
            inhalt = textfeld.get("1.0", tk.END).strip()
            if not empfänger or not betreff or not inhalt:
                messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllt werden.")
                return

            neue_nachricht = {
                "absender": self.nutzername,
                "empfänger": empfänger,
                "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "betreff": betreff,
                "inhalt": inhalt
            }

            nachrichten = lade_nachrichten()
            nachrichten.append(neue_nachricht)

            with open("data/messages.json", "w", encoding="utf-8") as f:
                json.dump(nachrichten, f, indent=2, ensure_ascii=False)

            # === BENACHRICHTIGUNG ERZEUGEN ===
            benachrichtigung = {
                "empfänger": empfänger,
                "titel": f"Neue Nachricht von {self.nutzername}",
                "text": f"Betreff: {betreff}",
                "gelesen": False #,
               # "zeit": datetime.now().strftime("%d.%m.%Y %H:%M")
            }

            try:
                with open("data/message_notifications.json", "r", encoding="utf-8") as f:
                    benachrichtigungen = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                benachrichtigungen = []
                print("TEST")

            benachrichtigungen.append(benachrichtigung)

            with open("data/message_notifications.json", "w", encoding="utf-8") as f:
                json.dump(benachrichtigungen, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Gesendet", "Nachricht erfolgreich gesendet.")
            empfänger_entry.delete(0, tk.END)
            betreff_entry.delete(0, tk.END)
            textfeld.delete("1.0", tk.END)
            filter_nachrichten()

        def autocomplete_empfänger(event=None):
            empfänger_input = empfänger_entry.get().lower()
            empfänger_vorschläge.delete(0, tk.END)
            if empfänger_input:
                for nutzer in lade_nutzer():
                    if nutzer.lower().startswith(empfänger_input):
                        empfänger_vorschläge.insert(tk.END, nutzer)

        def set_empfänger(event):
            empfänger_entry.delete(0, tk.END)
            empfänger_entry.insert(0, empfänger_vorschläge.get(tk.ACTIVE))

        # GUI Aufbau
        tk.Label(self.frame, text="Nachrichten", font=("Arial", 16)).pack(pady=10)

        oben = tk.Frame(self.frame)
        oben.pack(pady=10)

        tk.Label(oben, text="Suche:").pack(side=tk.LEFT)
        suche_entry = tk.Entry(oben)
        suche_entry.pack(side=tk.LEFT, fill="x", padx=5)
        suche_entry.bind("<KeyRelease>", filter_nachrichten)

        liste = ttk.Treeview(self.frame, columns=("Datum", "Von", "Betreff"), show="headings", height=10)
        for col in ("Datum", "Von", "Betreff"):
            liste.heading(col, text=col)
        liste.pack(fill="both", expand=True, padx=10, pady=10)
        liste.bind("<<TreeviewSelect>>", zeige_nachricht)

        unten = tk.Frame(self.frame)
        unten.pack(pady=20)

        empfänger_entry = tk.Entry(unten)
        empfänger_entry.insert(0, "Empfänger")
        empfänger_entry.pack(fill="x", padx=5, pady=5)
        empfänger_entry.bind("<KeyRelease>", autocomplete_empfänger)

        empfänger_vorschläge = tk.Listbox(unten, height=2)
        empfänger_vorschläge.pack(fill="x", padx=5, pady=5)
        empfänger_vorschläge.bind("<Double-1>", set_empfänger)

        betreff_entry = tk.Entry(unten)
        betreff_entry.insert(0, "Betreff")
        betreff_entry.pack(fill="x", padx=5, pady=5)

        textfeld = tk.Text(unten, height=5)
        textfeld.pack(fill="both", expand=True, padx=5)

        tk.Button(unten, text="Senden", command=senden, width=20).pack(pady=5)

        filter_nachrichten()  # Initiales Laden

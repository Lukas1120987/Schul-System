import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class Modul:
    def __init__(self, parent, nutzername, user_data=None):
        self.frame = tk.Frame(parent, bg="#f0f2f5")
        self.nutzername = nutzername
        self.user_data = user_data or {}

        self.baue_gui()

    def get_frame(self):
        return self.frame

    def baue_gui(self):
        def lade_nutzer():
            try:
                with open("data/users.json", "r", encoding="utf-8") as f:
                    nutzer_daten = json.load(f)
                return list(nutzer_daten.keys())
            except:
                return []

        def lade_nachrichten():
            try:
                with open("data/messages.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []

        def filter_nachrichten(event=None):
            suchbegriff = suche_entry.get().lower()
            self.nachrichtenliste.delete(*self.nachrichtenliste.get_children())
            self.anzeigen_nachrichten = []

            for i, nachricht in enumerate(lade_nachrichten()):
                if nachricht.get("empfänger") != self.nutzername:
                    continue
                betreff = nachricht.get("betreff", "").lower()
                inhalt = nachricht.get("inhalt", "").lower()
                if suchbegriff in betreff or suchbegriff in inhalt:
                    self.nachrichtenliste.insert("", "end", iid=str(i), values=(
                        nachricht.get("datum", ""),
                        nachricht.get("absender", ""),
                        nachricht.get("betreff", "")
                    ))
                    self.anzeigen_nachrichten.append(nachricht)

        def zeige_nachricht(event):
            ausgewählt = self.nachrichtenliste.selection()
            if ausgewählt:
                index = int(ausgewählt[0])
                nachricht = lade_nachrichten()[index]
                messagebox.showinfo(
                    f"Nachricht von {nachricht['absender']}",
                    f"Betreff: {nachricht['betreff']}\n\n{nachricht['inhalt']}"
                )

        def senden():
            empfänger = empfänger_entry.get().strip()
            betreff = betreff_entry.get().strip()
            inhalt = textfeld.get("1.0", tk.END).strip()

            if not empfänger or not betreff or not inhalt:
                messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllt werden.")
                return

            if empfänger not in lade_nutzer():
                messagebox.showerror("Fehler", f"Der Nutzer '{empfänger}' existiert nicht.")
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

            benachrichtigung = {
                "text": f"Neue Nachricht von {self.nutzername} \n Betreff: {betreff} \n Inhalt der Nachricht: \n {inhalt}",
                #"text": f"Betreff: {betreff}",
                "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "gelesen": False
            }

            try:
                with open("data/notifications.json", "r", encoding="utf-8") as f:
                    benachrichtigungen = json.load(f)
            except:
                benachrichtigungen = {}

            # Falls der Empfänger noch keinen Eintrag hat, erstelle eine neue Liste
            if empfänger not in benachrichtigungen:
                benachrichtigungen[empfänger] = []

            benachrichtigungen[empfänger].append(benachrichtigung)

            with open("data/notifications.json", "w", encoding="utf-8") as f:
                json.dump(benachrichtigungen, f, indent=2, ensure_ascii=False)


            messagebox.showinfo("Erfolg", "Nachricht erfolgreich gesendet.")
            empfänger_entry.delete(0, tk.END)
            betreff_entry.delete(0, tk.END)
            textfeld.delete("1.0", tk.END)
            filter_nachrichten()

        def autocomplete_empfänger(event=None):
            empfänger_input = empfänger_entry.get().lower()
            vorschlagsbox.delete(0, tk.END)
            if empfänger_input:
                for nutzer in lade_nutzer():
                    if nutzer.lower().startswith(empfänger_input) and nutzer != self.nutzername:
                        vorschlagsbox.insert(tk.END, nutzer)

        def set_empfänger(event):
            empfänger_entry.delete(0, tk.END)
            empfänger_entry.insert(0, vorschlagsbox.get(tk.ACTIVE))
            vorschlagsbox.delete(0, tk.END)

        def add_placeholder(entry, text):
            entry.insert(0, text)
            entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == text else None)
            entry.bind("<FocusOut>", lambda e: entry.insert(0, text) if not entry.get() else None)

        # Layout
        tk.Label(self.frame, text="📨 Nachrichten", bg="#f0f2f5", font=("Arial", 18, "bold")).pack(pady=10)

        oben = tk.Frame(self.frame, bg="#f0f2f5")
        oben.pack(fill="x", padx=10)

        tk.Label(oben, text="🔍 Suche:", bg="#f0f2f5").pack(side=tk.LEFT)
        suche_entry = tk.Entry(oben)
        suche_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        suche_entry.bind("<KeyRelease>", filter_nachrichten)

        self.nachrichtenliste = ttk.Treeview(self.frame, columns=("Datum", "Von", "Betreff"), show="headings", height=10)
        for col in ("Datum", "Von", "Betreff"):
            self.nachrichtenliste.heading(col, text=col)
        self.nachrichtenliste.pack(fill="both", expand=True, padx=10, pady=10)
        self.nachrichtenliste.bind("<<TreeviewSelect>>", zeige_nachricht)

        senden_frame = tk.LabelFrame(self.frame, text="Neue Nachricht", bg="#f0f2f5", padx=10, pady=10)
        senden_frame.pack(fill="both", expand=True, padx=10, pady=10)

        empfänger_entry = tk.Entry(senden_frame)
        add_placeholder(empfänger_entry, "Empfänger")
        empfänger_entry.pack(fill="x", pady=5)
        empfänger_entry.bind("<KeyRelease>", autocomplete_empfänger)

        vorschlagsbox = tk.Listbox(senden_frame, height=3)
        vorschlagsbox.pack(fill="x", pady=2)
        vorschlagsbox.bind("<Double-1>", set_empfänger)

        betreff_entry = tk.Entry(senden_frame)
        add_placeholder(betreff_entry, "Betreff")
        betreff_entry.pack(fill="x", pady=5)

        textfeld = tk.Text(senden_frame, height=6)
        textfeld.pack(fill="both", expand=True, pady=5)

        tk.Button(senden_frame, text="✅ Nachricht senden", command=senden, bg="#4CAF50", fg="white").pack(pady=5)

        filter_nachrichten()

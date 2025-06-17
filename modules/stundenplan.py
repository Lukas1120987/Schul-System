import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# === Hilfsfunktionen ===
def load_or_create_json(path, default_data):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(default_data, f, indent=4)
    with open(path, 'r') as f:
        return json.load(f)

# === Daten laden ===
users = load_or_create_json("data/users.json", {})
stundenplan = load_or_create_json("data/schedule.json", {})
vertretungen = load_or_create_json("data/vertretungen.json", {})
organisation = load_or_create_json("data/organisation.json", {
    "tage": [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag"
    ],
    "stunden": [
        "08:00-08:45",
        "08:55-09:40",
        "10:00-10:45",
        "10:55-11:40",
        "12:00-12:45",
        "12:55-13:40",
        "14:00-14:45",
        "14:55-15:40"
    ]
}

)

klassen = list({user["second_group"] for user in users.values() if user.get("second_group")})

# === GUI-Klasse ===
class Modul:
    def __init__(self, master, username=None, user_data=None):
        self.master = master
        self.username = username
        self.user_data = user_data

        self.frame = ttk.Frame(master)

        self.auswahl_frame = ttk.Frame(self.frame)
        self.auswahl_frame.pack(pady=10)

        self.klasse_var = tk.StringVar()
        ttk.Label(self.auswahl_frame, text="Klasse auswählen:").pack(side=tk.LEFT)
        self.klasse_combo = ttk.Combobox(self.auswahl_frame, textvariable=self.klasse_var, values=klassen, state="readonly")
        self.klasse_combo.pack(side=tk.LEFT, padx=5)
        self.klasse_combo.bind("<<ComboboxSelected>>", lambda e: self.anzeige_aktualisieren())

        self.anzeige_frame = ttk.Frame(self.frame)
        self.anzeige_frame.pack()

        self.tabelle = ttk.Treeview(self.anzeige_frame, columns=["Tag"] + organisation["stunden"], show="headings", height=6)
        for col in ["Tag"] + organisation["stunden"]:
            self.tabelle.heading(col, text=col)
            self.tabelle.column(col, width=100, anchor="center")
        self.tabelle.pack()

    def get_frame(self):
        return self.frame

    def anzeige_aktualisieren(self):
        klasse = self.klasse_var.get()
        if not klasse:
            return

        self.tabelle.delete(*self.tabelle.get_children())

        for tag in organisation["tage"]:
            zeile = [tag]
            for std_idx, _ in enumerate(organisation["stunden"]):
                stunde_info = stundenplan.get(klasse, {}).get(tag, {}).get(str(std_idx+1), {})
                vertretung_info = vertretungen.get(tag, {}).get(klasse, {}).get(str(std_idx+1), {})

                if not stunde_info:
                    zeile.append("-")
                    continue

                text = f"{stunde_info.get('fach', '')}\n{stunde_info.get('lehrer', '')}\n{stunde_info.get('raum', '')}"

                if vertretung_info:
                    if vertretung_info.get("art") == "ausfall":
                        text = "AUSFALL"
                    else:
                        text = f"{vertretung_info.get('fach', stunde_info.get('fach', ''))}\n{vertretung_info.get('lehrer', stunde_info.get('lehrer', ''))}\n{vertretung_info.get('raum', stunde_info.get('raum', ''))}"
                        text += f"\n(vertret.)"
                zeile.append(text)

            self.tabelle.insert('', 'end', values=zeile)


# === Hauptprogramm starten ===
if __name__ == "__main__":
    root = tk.Tk()
    app = Modul(root)
    root.mainloop()




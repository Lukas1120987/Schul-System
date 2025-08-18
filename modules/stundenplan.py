import customtkinter as ctk
import json
import os
from datetime import datetime
from ordner import get_data_path

# === Hilfsfunktionen ===
def load_or_create_json(filename, default_data):
    path = os.path.join(get_data_path(), filename)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)


# === Daten laden ===
users = load_or_create_json("data/users.json", {})
stundenplan = load_or_create_json("data/schedule.json", {})
vertretungen = load_or_create_json("data/vertretungen.json", {})
organisation = load_or_create_json("data/organisation.json", {
    "tage": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"],
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
})

klassen = list({user["second_group"] for user in users.values() if user.get("second_group")})


# === GUI-Klasse ===
class Modul:
    def __init__(self, master, username=None, user_data=None):
        self.master = master
        self.username = username
        self.user_data = user_data

        self.frame = ctk.CTkFrame(master, corner_radius=10)
        self.frame.pack(fill="both", expand=True)

        # Auswahl
        self.auswahl_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.auswahl_frame.pack(pady=10)

        ctk.CTkLabel(self.auswahl_frame, text="Klasse auswählen:").pack(side="left", padx=5)
        self.klasse_combo = ctk.CTkComboBox(self.auswahl_frame, values=klassen, command=lambda e=None: self.anzeige_aktualisieren())
        self.klasse_combo.pack(side="left", padx=5)

        # Tabelle (mit ScrollFrame)
        self.anzeige_frame = ctk.CTkScrollableFrame(self.frame, width=800, height=400, corner_radius=10)
        self.anzeige_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Spaltenüberschriften
        header_frame = ctk.CTkFrame(self.anzeige_frame)
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="Tag", width=100, anchor="center").pack(side="left", padx=1)
        for stunde in organisation["stunden"]:
            ctk.CTkLabel(header_frame, text=stunde, width=100, anchor="center").pack(side="left", padx=1)

        # Container für dynamische Zeilen
        self.table_rows_frame = ctk.CTkFrame(self.anzeige_frame)
        self.table_rows_frame.pack(fill="x")

    def get_frame(self):
        return self.frame

    def clear_table(self):
        for widget in self.table_rows_frame.winfo_children():
            widget.destroy()

    def anzeige_aktualisieren(self):
        klasse = self.klasse_combo.get()
        if not klasse:
            return

        self.clear_table()

        for tag in organisation["tage"]:
            row_frame = ctk.CTkFrame(self.table_rows_frame)
            row_frame.pack(fill="x", pady=1)

            # Erste Spalte: Tag
            ctk.CTkLabel(row_frame, text=tag, width=100, anchor="center").pack(side="left", padx=1)

            # Stunden-Spalten
            for std_idx, _ in enumerate(organisation["stunden"]):
                stunde_info = stundenplan.get(klasse, {}).get(tag, {}).get(str(std_idx+1), {})
                vertretung_info = vertretungen.get(tag, {}).get(klasse, {}).get(str(std_idx+1), {})

                if not stunde_info:
                    text = "-"
                else:
                    text = f"{stunde_info.get('fach', '')}\n{stunde_info.get('lehrer', '')}\n{stunde_info.get('raum', '')}"
                    if vertretung_info:
                        if vertretung_info.get("art") == "ausfall":
                            text = "❌ AUSFALL"
                        else:
                            text = f"{vertretung_info.get('fach', stunde_info.get('fach', ''))}\n{vertretung_info.get('lehrer', stunde_info.get('lehrer', ''))}\n{vertretung_info.get('raum', stunde_info.get('raum', ''))}"
                            text += "\n(vertret.)"

                ctk.CTkLabel(row_frame, text=text, width=100, anchor="center").pack(side="left", padx=1)


# === Hauptprogramm starten ===
if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # "Dark" oder "Light"
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Stundenplan & Vertretungen")
    root.geometry("1000x600")

    app = Modul(root)
    root.mainloop()

import tkinter as tk
from datetime import datetime, timedelta
import calendar
import json
import os

class Modul:
    def __init__(self, master, username, user_data):
        self.username = username
        self.group = user_data.get("second_group", "")
        self.master = master
        self.frame = tk.Frame(master, bg="white")

        self.current_monday = self.get_monday(date=datetime.today())

        self.ensure_files()
        self.load_data()
        self.build_gui()
        self.show_week()

    def get_frame(self):
        return self.frame

    def ensure_files(self):
        os.makedirs("data", exist_ok=True)
        for file in ["schedule.json", "vertretungen.json"]:
            if not os.path.exists(f"data/{file}"):
                with open(f"data/{file}", "w", encoding="utf-8") as f:
                    json.dump({} if file == "schedule.json" else [], f, indent=2)

    def load_data(self):
        with open("data/schedule.json", "r", encoding="utf-8") as f:
            self.schedule = json.load(f)
        with open("data/vertretungen.json", "r", encoding="utf-8") as f:
            self.vertretungen = json.load(f)

    def build_gui(self):
        tk.Label(self.frame, text="📅 Vertretungsplan – Wochenansicht", font=("Arial", 16), bg="white").pack(pady=10)

        nav_frame = tk.Frame(self.frame, bg="white")
        nav_frame.pack()

        tk.Button(nav_frame, text="← Vorwoche", command=self.prev_week).pack(side=tk.LEFT, padx=5)
        self.date_label = tk.Label(nav_frame, text="", font=("Arial", 12), bg="white")
        self.date_label.pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="Nächste Woche →", command=self.next_week).pack(side=tk.LEFT, padx=5)

        self.table_frame = tk.Frame(self.frame, bg="white")
        self.table_frame.pack(pady=10)

    def get_monday(self, date):
        return date - timedelta(days=date.weekday())

    def prev_week(self):
        self.current_monday -= timedelta(days=7)
        self.show_week()

    def next_week(self):
        self.current_monday += timedelta(days=7)
        self.show_week()

    def show_week(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        start_date = self.current_monday
        self.date_label.config(text=f"Woche ab {start_date.strftime('%d.%m.%Y')}")

        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

        # Kopfzeile
        tk.Label(self.table_frame, text="Stunde", font=("Arial", 10, "bold"), width=10, borderwidth=1, relief="solid").grid(row=0, column=0)
        for col, day in enumerate(days):
            datum = (start_date + timedelta(days=col)).strftime("%d.%m")
            tk.Label(self.table_frame, text=f"{day}\n({datum})", font=("Arial", 10, "bold"), width=20, borderwidth=1, relief="solid").grid(row=0, column=col+1)

        # Stundenraster
        for stunde in range(1, 9):
            tk.Label(self.table_frame, text=f"{stunde}. Std", width=10, borderwidth=1, relief="solid").grid(row=stunde, column=0)
            for col, day in enumerate(days):
                datum_obj = start_date + timedelta(days=col)
                datum_str = datum_obj.strftime("%Y-%m-%d")
                tagname = calendar.day_name[datum_obj.weekday()]
                self.draw_cell(stunde, tagname, datum_str, row=stunde, column=col+1)

    def draw_cell(self, stunde, wochentag, datum_str, row, column):
        s = str(stunde)
        plan = self.schedule.get(self.group, {}).get(wochentag, {}).get(s)
        vertretung = next((v for v in self.vertretungen if v["datum"] == datum_str and v["klasse"] == self.group and v["stunde"] == s), None)

        text = ""
        bg = "white"

        if vertretung:
            if vertretung.get("entfaellt"):
                text = "❌ entfällt"
                bg = "#ffcccc"
            else:
                fach = vertretung.get("fach") or (plan.get("fach") if plan else "")
                lehrer = vertretung.get("lehrer") or (plan.get("lehrer") if plan else "")
                raum = vertretung.get("raum") or (plan.get("raum") if plan else "")
                text = f"{fach}\n{lehrer}\nRaum {raum}"
                bg = "#fffacc"
        elif plan:
            text = f"{plan.get('fach', '')}\n{plan.get('lehrer', '')}\nRaum {plan.get('raum', '')}"
        elif not plan and vertretung:
            text = "🆕 Zusatzstunde"
            bg = "#dceeff"
        else:
            text = ""

        tk.Label(self.table_frame, text=text, width=20, height=4, bg=bg, borderwidth=1, relief="solid", wraplength=140, justify="center").grid(row=row, column=column)


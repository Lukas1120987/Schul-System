import tkinter as tk
import json

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.group = user_data["second_group"]

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="🗓️ Stundenplan", font=("Arial", 16), bg="white").pack(pady=10)

        self.table_frame = tk.Frame(self.frame, bg="white")
        self.table_frame.pack(pady=10)

        self.load_schedule()

    def get_frame(self):
        return self.frame

    def load_schedule(self):
        try:
            with open("data/schedule.json", "r", encoding="utf-8") as f:
                schedule_data = json.load(f)
        except FileNotFoundError:
            tk.Label(self.table_frame, text="Kein Stundenplan gefunden.", bg="white").pack()
            return

        user_schedule = schedule_data.get(self.group, {})

        if not user_schedule:
            tk.Label(self.table_frame, text=f"Sie sind einer Gruppe zugeordnet, die keinen Stundenplan hat.", bg="white").pack() # '{self.group}' gefunden.
            return

        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

        # Kopfzeile
        tk.Label(self.table_frame, text="Stunde", font=("Arial", 10, "bold"), width=10, borderwidth=1, relief="solid").grid(row=0, column=0)
        for col, day in enumerate(days):
            tk.Label(self.table_frame, text=day, font=("Arial", 10, "bold"), width=15, borderwidth=1, relief="solid").grid(row=0, column=col+1)

        # Inhalte
        for row in range(1, 9):  # Stunden 1-8
            tk.Label(self.table_frame, text=str(row), width=10, borderwidth=1, relief="solid").grid(row=row, column=0)
            for col, day in enumerate(days):
                subject = user_schedule.get(day, {}).get(str(row), "")
                tk.Label(self.table_frame, text=subject, width=15, borderwidth=1, relief="solid").grid(row=row, column=col+1)

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

USER_JSON_PATH = "data/users.json"
PLAN_JSON_PATH = "data/plan.json"


class Modul:
    def __init__(self, master, user_json_path="data/users.json", plan_json_path="data/plan.json"):
        self.master = master
        self.user_json_path = user_json_path
        self.plan_json_path = plan_json_path
        #...

        self.frame = tk.Frame(master, bg="white")

        tk.Label(self.frame, text="🛋 Sitzplan erstellen", font=("Arial", 16), bg="white").pack(pady=10)

        # Einstellungen
        settings_frame = tk.Frame(self.frame, bg="white")
        settings_frame.pack(pady=10)

        tk.Label(settings_frame, text="Reihen:", bg="white").grid(row=0, column=0)
        self.rows_entry = tk.Entry(settings_frame, width=5)
        self.rows_entry.insert(0, "5")
        self.rows_entry.grid(row=0, column=1)

        tk.Label(settings_frame, text="Spalten:", bg="white").grid(row=0, column=2)
        self.cols_entry = tk.Entry(settings_frame, width=5)
        self.cols_entry.insert(0, "6")
        self.cols_entry.grid(row=0, column=3)

        tk.Label(settings_frame, text="Gruppe:", bg="white").grid(row=1, column=0)
        self.group_var = tk.StringVar()
        self.group_dropdown = ttk.Combobox(settings_frame, textvariable=self.group_var, state="readonly")
        self.group_dropdown.grid(row=1, column=1, columnspan=3, sticky="ew")

        button_frame = tk.Frame(self.frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="🆕 Sitzplan generieren", command=self.generate_seating).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="💾 Sitzplan speichern", command=self.save_seating_plan).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="📂 Sitzplan laden", command=self.load_seating_plan).grid(row=0, column=2, padx=5)

        self.user_listbox = tk.Listbox(self.frame, width=30)
        self.user_listbox.pack(side=tk.LEFT, padx=10, pady=10)

        self.seat_frame = tk.Frame(self.frame, bg="white")
        self.seat_frame.pack(padx=10, pady=10)

        self.refresh_groups()

    def get_frame(self):
        return self.frame

    def refresh_groups(self):
        users = self.load_users()
        # Nur Gruppen aus tatsächlichen Nutzern, nicht aus _group_ oder Testkonten
        groups = sorted(set(user["second_group"] for name, user in users.items()
                            if not name.startswith("_group_")))
        self.group_dropdown["values"] = groups
        if groups:
            self.group_var.set(groups[0])

    def generate_seating(self):
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
        except ValueError:
            messagebox.showerror("Fehler", "Reihen und Spalten müssen Zahlen sein.")
            return

        for widget in self.seat_frame.winfo_children():
            widget.destroy()

        self.users_by_group = self.get_users_by_group(self.group_var.get())
        self.user_listbox.delete(0, tk.END)
        for user in self.users_by_group:
            self.user_listbox.insert(tk.END, user)

        self.seats = {}
        for r in range(rows):
            for c in range(cols):
                btn = tk.Button(self.seat_frame, text="Leer", width=10, height=2,
                                command=lambda pos=(r, c): self.assign_user_by_position(pos))
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.seats[(r, c)] = btn

    def assign_user_by_position(self, position):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle zuerst einen Benutzer aus der Liste.")
            return
        username = self.user_listbox.get(selection[0])
        self.seats[position]["text"] = username
        self.user_listbox.delete(selection[0])

    def save_seating_plan(self):
        if not hasattr(self, "seats"):
            messagebox.showerror("Fehler", "Kein Sitzplan generiert. Bitte zuerst Sitzplan erstellen.")
            return

        data = {
            "rows": int(self.rows_entry.get()),
            "cols": int(self.cols_entry.get()),
            "group": self.group_var.get(),
            "seats": {
                f"{r},{c}": self.seats[(r, c)]["text"]
                for (r, c) in self.seats
            }
        }
        os.makedirs(os.path.dirname(PLAN_JSON_PATH), exist_ok=True)
        with open(PLAN_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Gespeichert", "Sitzplan wurde gespeichert.")

    def load_seating_plan(self):
        if not os.path.exists(PLAN_JSON_PATH):
            messagebox.showerror("Fehler", "Kein gespeicherter Sitzplan vorhanden.")
            return

        with open(PLAN_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.rows_entry.delete(0, tk.END)
        self.rows_entry.insert(0, str(data.get("rows", 5)))
        self.cols_entry.delete(0, tk.END)
        self.cols_entry.insert(0, str(data.get("cols", 6)))
        self.group_var.set(data.get("group", ""))

        self.generate_seating()

        for key, username in data.get("seats", {}).items():
            if username != "Leer":
                r, c = map(int, key.split(","))
                if (r, c) in self.seats:
                    self.seats[(r, c)]["text"] = username
                    if username in self.user_listbox.get(0, tk.END):
                        index = self.user_listbox.get(0, tk.END).index(username)
                        self.user_listbox.delete(index)

    def get_users_by_group(self, group):
        users = self.load_users()
        return [name for name, data in users.items()
                if data.get("second_group") == group and not name.startswith("_group_")]

    def load_users(self):
        if not os.path.exists(USER_JSON_PATH):
            return {}
        with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self, users):
        os.makedirs(os.path.dirname(USER_JSON_PATH), exist_ok=True)
        with open(USER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

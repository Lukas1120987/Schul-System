import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

USER_JSON_PATH = "data/users.json"
KRANK_JSON_PATH = "data/krank.json"

class Modul:
    def __init__(self, master, users_path, krank_path):
        self.master = master
        self.user_path = users_path
        self.krank_path = krank_path
        #...

        self.frame = tk.Frame(master, bg="white")
        
        tk.Label(self.frame, text="🤒 Krankmeldungen", font=("Arial", 16), bg="white").pack(pady=10)

        # Gruppen-Auswahl
        select_frame = tk.Frame(self.frame, bg="white")
        select_frame.pack(pady=5)

        tk.Label(select_frame, text="Gruppe:", bg="white").grid(row=0, column=0)
        self.group_var = tk.StringVar()
        self.group_dropdown = ttk.Combobox(select_frame, textvariable=self.group_var, state="readonly")
        self.group_dropdown.grid(row=0, column=1)
        self.group_dropdown.bind("<<ComboboxSelected>>", self.refresh_user_list)

        # Benutzerliste
        self.user_listbox = tk.Listbox(self.frame, width=30)
        self.user_listbox.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.frame, bg="white")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Als krank melden", command=self.mark_sick).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Krankmeldung entfernen", command=self.unmark_sick).grid(row=0, column=1, padx=5)

        self.refresh_groups()

    def get_frame(self):
        return self.frame

    def refresh_groups(self):
        users = self.load_users()
        groups = sorted(set(data["group"] for username, data in users.items() if not username.startswith("_group_")))
        self.group_dropdown["values"] = groups
        if groups:
            self.group_var.set(groups[0])
            self.refresh_user_list()

    def refresh_user_list(self, event=None):
        self.user_listbox.delete(0, tk.END)
        group = self.group_var.get()
        users = self.load_users()
        krank_data = self.load_krank()

        for user, data in users.items():
            if data.get("group") == group and not user.startswith("_group_"):
                status = " (krank)" if user in krank_data else ""
                self.user_listbox.insert(tk.END, user + status)

    def mark_sick(self):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle einen Benutzer aus.")
            return
        username = self.user_listbox.get(selection[0]).replace(" (krank)", "")
        krank_data = self.load_krank()
        krank_data[username] = "krank"
        self.save_krank(krank_data)
        self.refresh_user_list()

    def unmark_sick(self):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wähle einen Benutzer aus.")
            return
        username = self.user_listbox.get(selection[0]).replace(" (krank)", "")
        krank_data = self.load_krank()
        if username in krank_data:
            del krank_data[username]
        self.save_krank(krank_data)
        self.refresh_user_list()

    def load_users(self):
        if not os.path.exists(USER_JSON_PATH):
            return {}
        with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_krank(self):
        if not os.path.exists(KRANK_JSON_PATH):
            return {}
        with open(KRANK_JSON_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_krank(self, data):
        os.makedirs(os.path.dirname(KRANK_JSON_PATH), exist_ok=True)
        with open(KRANK_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

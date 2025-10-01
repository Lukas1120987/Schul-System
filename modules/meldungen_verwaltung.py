import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class Modul:
    def __init__(self, username, user_data, master):
        self.username = username
        self.user_data = user_data
        self.master = master
        self.frame = tk.Frame()
        self.meldungen_file = "meldungen.json"
        self.load_meldungen()
        self.create_ui()

    def load_meldungen(self):
        if not os.path.exists(self.meldungen_file):
            with open(self.meldungen_file, "w") as f:
                json.dump({}, f)
        with open(self.meldungen_file, "r") as f:
            self.meldungen = json.load(f)

    def create_ui(self):
        tk.Label(self.frame, text="Meldungen verwalten", font=("Arial", 14)).pack(pady=5)

        # Filter nach Typ
        tk.Label(self.frame, text="Filter nach Typ:").pack()
        self.filter_var = tk.StringVar(value="alle")
        ttk.Combobox(self.frame, textvariable=self.filter_var, values=["alle", "nachricht", "datei", "stoerung"]).pack(pady=2)
        tk.Button(self.frame, text="Filter anwenden", command=self.refresh_tree).pack(pady=2)

        # Meldungen Treeview
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Typ", "Element", "Ersteller", "Status", "Grund", "Zeit"), show="headings")
        for col in ("ID", "Typ", "Element", "Ersteller", "Status", "Grund", "Zeit"):
            self.tree.heading(col, text=col)
        self.tree.pack(pady=5, fill="x")

        # Status ändern
        tk.Label(self.frame, text="Status ändern für ausgewählte Meldung:").pack(pady=5)
        self.status_var = tk.StringVar(value="offen")
        ttk.Combobox(self.frame, textvariable=self.status_var, values=["offen", "in Bearbeitung", "erledigt"]).pack(pady=2)
        tk.Button(self.frame, text="Status ändern", command=self.change_status).pack(pady=2)

        self.refresh_tree()

    def refresh_tree(self):
        filter_typ = self.filter_var.get()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for mid, data in self.meldungen.items():
            if filter_typ == "alle" or data["typ"] == filter_typ:
                self.tree.insert("", "end", iid=mid, values=(mid, data["typ"], data["element"], data["ersteller"], data["status"], data["grund"], data["zeit"]))

    def change_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Fehler", "Keine Meldung ausgewählt!")
            return
        new_status = self.status_var.get()
        for mid in selected:
            self.meldungen[mid]["status"] = new_status
        with open(self.meldungen_file, "w") as f:
            json.dump(self.meldungen, f, indent=2)
        self.refresh_tree()
        messagebox.showinfo("Erfolg", "Status wurde geändert!")

    def get_frame(self):
        return self.frame

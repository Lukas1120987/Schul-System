import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from ordner import get_data_path

MELDUNGEN_JSON_PATH = os.path.join(get_data_path(), "data/meldungen.json")
MELDUNGEN_JSON_PATH_GRÜNDE = os.path.join(get_data_path(), "data/stoerungsgrunde.json")

class Modul:
    def __init__(self, username, user_data, master):
        self.username = username
        self.user_data = user_data
        self.master = master
        self.frame = tk.Frame()
        self.meldungen_file = MELDUNGEN_JSON_PATH
        self.stoerungs_file = MELDUNGEN_JSON_PATH_GRÜNDE
        self.load_meldungen()
        self.load_stoerungsgrunde()
        self.create_ui()

    def load_meldungen(self):
        if not os.path.exists(self.meldungen_file):
            with open(self.meldungen_file, "w") as f:
                json.dump({}, f)
        with open(self.meldungen_file, "r") as f:
            self.meldungen = json.load(f)

    def load_stoerungsgrunde(self):
        if not os.path.exists(self.stoerungs_file):
            with open(self.stoerungs_file, "w") as f:
                json.dump({"Verwaltung": ["Server down", "Drucker defekt", "Netzwerkproblem", "Softwarefehler"]}, f)
        with open(self.stoerungs_file, "r") as f:
            self.stoerungsgrunde = json.load(f)

    def create_ui(self):
        tk.Label(self.frame, text="Neue Meldung erstellen", font=("Arial", 14)).pack(pady=5)

        # Typ Auswahl
        tk.Label(self.frame, text="Meldungstyp:").pack()
        self.typ_var = tk.StringVar(value="nachricht")
        ttk.Combobox(self.frame, textvariable=self.typ_var, values=["nachricht", "datei", "stoerung"]).pack(pady=2)

        # Elementeingabe
        tk.Label(self.frame, text="Betreff/Element:").pack()
        self.element_entry = tk.Entry(self.frame, width=30)
        self.element_entry.pack(pady=2)

        # Störungsgrund Dropdown (nur bei "stoerung")
        tk.Label(self.frame, text="Störungsgrund:").pack()
        self.grund_var = tk.StringVar()
        self.grund_combo = ttk.Combobox(self.frame, textvariable=self.grund_var, values=self.stoerungsgrunde.get("Verwaltung", []))
        self.grund_combo.pack(pady=2)

        # Meldung absenden
        tk.Button(self.frame, text="Meldung senden", command=self.add_meldung).pack(pady=5)

        # Eigene Meldungen anzeigen
        tk.Label(self.frame, text="Meine Meldungen", font=("Arial", 12)).pack(pady=10)
        self.tree = ttk.Treeview(self.frame, columns=("Typ", "Element", "Status", "Grund", "Zeit"), show="headings")
        for col in ("Typ", "Element", "Status", "Grund", "Zeit"):
            self.tree.heading(col, text=col)
        self.tree.pack(pady=5, fill="x")
        self.refresh_tree()

    def add_meldung(self):
        typ = self.typ_var.get()
        element = self.element_entry.get()
        grund = self.grund_var.get() if typ == "stoerung" else ""
        if typ != "stoerung" and element == "":
            messagebox.showwarning("Fehler", "Bitte Betreff/Element eingeben!")
            return
        new_id = str(max([int(k) for k in self.meldungen.keys()] + [0]) + 1)
        self.meldungen[new_id] = {
            "typ": typ,
            "element": element,
            "ersteller": self.username,
            "status": "offen",
            "zeit": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "grund": grund
        }
        with open(self.meldungen_file, "w") as f:
            json.dump(self.meldungen, f, indent=2)
        self.element_entry.delete(0, tk.END)
        self.refresh_tree()
        messagebox.showinfo("Erfolg", "Meldung wurde gesendet!")

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for mid, data in self.meldungen.items():
            if data["ersteller"] == self.username:
                self.tree.insert("", "end", values=(data["typ"], data["element"], data["status"], data["grund"], data["zeit"]))

    def get_frame(self):
        return self.frame

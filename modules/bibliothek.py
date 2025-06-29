import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

class Modul:
    def __init__(self, parent_frame, username=None, user_data=None):
        self.frame = tk.Frame(parent_frame)
        self.frame = tk.Frame(parent_frame)
        self.library_file = "data/library.json"
        self.buecher = self.load_buecher()
        self.create_widgets()

    def load_buecher(self):
        if not os.path.exists(self.library_file):
            return []
        with open(self.library_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_buecher(self):
        os.makedirs("data", exist_ok=True)
        with open(self.library_file, "w", encoding="utf-8") as f:
            json.dump(self.buecher, f, indent=2, ensure_ascii=False)

    def create_widgets(self):
        tk.Label(self.frame, text="Bibliothek - Bücherverwaltung", font=("Arial", 14, "bold")).pack(pady=5)

        # Liste der Bücher
        self.listbox = tk.Listbox(self.frame, width=50, height=12)
        self.listbox.pack(padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Buttons
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Buch hinzufügen", command=self.buch_hinzufuegen).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Ausleihen", command=self.buch_ausleihen).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Zurückgeben", command=self.buch_zurueckgeben).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Aktualisieren", command=self.refresh_list).grid(row=0, column=3, padx=5)

        self.status_label = tk.Label(self.frame, text="", fg="blue")
        self.status_label.pack(pady=3)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for buch in self.buecher:
            status = "verfügbar" if buch.get("verfuegbar", True) else f"ausgeliehen an {buch.get('ausgeliehen_an', '')}"
            self.listbox.insert(tk.END, f"{buch['titel']} von {buch['autor']} - {status}")
        self.status_label.config(text="")

    def on_select(self, event):
        idx = self.listbox.curselection()
        if not idx:
            self.status_label.config(text="")
            return
        buch = self.buecher[idx[0]]
        status = "verfügbar" if buch.get("verfuegbar", True) else f"ausgeliehen an {buch.get('ausgeliehen_an', '')}"
        self.status_label.config(text=f"Auswahl: {buch['titel']} ({status})")

    def buch_hinzufuegen(self):
        titel = simpledialog.askstring("Neues Buch", "Titel eingeben:", parent=self.frame)
        if not titel:
            return
        autor = simpledialog.askstring("Neues Buch", "Autor eingeben:", parent=self.frame)
        if not autor:
            return
        neues_buch = {"titel": titel.strip(), "autor": autor.strip(), "verfuegbar": True}
        self.buecher.append(neues_buch)
        self.save_buecher()
        self.refresh_list()
        messagebox.showinfo("Erfolg", "Buch hinzugefügt!")

    def buch_ausleihen(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Ausleihen", "Bitte zuerst ein Buch auswählen!")
            return
        buch = self.buecher[idx[0]]
        if not buch.get("verfuegbar", True):
            messagebox.showerror("Ausleihen", "Dieses Buch ist bereits ausgeliehen!")
            return
        name = simpledialog.askstring("Ausleihen", "Name des Ausleihers eingeben:", parent=self.frame)
        if not name:
            return
        buch["verfuegbar"] = False
        buch["ausgeliehen_an"] = name.strip()
        self.save_buecher()
        self.refresh_list()
        messagebox.showinfo("Ausleihen", f"'{buch['titel']}' wurde an {name} ausgeliehen.")

    def buch_zurueckgeben(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Zurückgeben", "Bitte zuerst ein Buch auswählen!")
            return
        buch = self.buecher[idx[0]]
        if buch.get("verfuegbar", True):
            messagebox.showinfo("Zurückgeben", "Dieses Buch ist nicht ausgeliehen.")
            return
        buch["verfuegbar"] = True
        buch.pop("ausgeliehen_an", None)
        self.save_buecher()
        self.refresh_list()
        messagebox.showinfo("Zurückgeben", f"'{buch['titel']}' wurde zurückgegeben.")

    def get_frame(self):
        return self.frame

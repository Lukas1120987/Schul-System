import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

class Modul:
    def __init__(self, parent_frame):
        self.frame = tk.Frame(parent_frame)
        self.surveys_file = "data/surveys.json"
        self.umfragen = self.load_umfragen()
        self.current_survey = None
        self.create_widgets()

    def load_umfragen(self):
        if not os.path.exists(self.surveys_file):
            return []
        with open(self.surveys_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_umfragen(self):
        os.makedirs("data", exist_ok=True)
        with open(self.surveys_file, "w", encoding="utf-8") as f:
            json.dump(self.umfragen, f, indent=2, ensure_ascii=False)

    def create_widgets(self):
        tk.Label(self.frame, text="Umfragen-Modul", font=("Arial", 14, "bold")).pack(pady=5)

        self.listbox = tk.Listbox(self.frame, width=60, height=10)
        self.listbox.pack(padx=10, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Umfrage erstellen", command=self.umfrage_erstellen).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Umfrage starten", command=self.umfrage_starten).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Umfrage stoppen", command=self.umfrage_stoppen).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Ergebnisse anzeigen", command=self.ergebnisse_anzeigen).grid(row=0, column=3, padx=5)

        self.status_label = tk.Label(self.frame, text="", fg="blue")
        self.status_label.pack(pady=3)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for umfrage in self.umfragen:
            status = "aktiv" if umfrage.get("active") else "inaktiv"
            self.listbox.insert(tk.END, f"{umfrage['title']} - {status}")
        self.status_label.config(text="")

    def on_select(self, event):
        idx = self.listbox.curselection()
        if not idx:
            self.current_survey = None
            self.status_label.config(text="")
            return
        self.current_survey = self.umfragen[idx[0]]
        status = "aktiv" if self.current_survey.get("active") else "inaktiv"
        self.status_label.config(text=f"Auswahl: {self.current_survey['title']} ({status})")

    def umfrage_erstellen(self):
        titel = simpledialog.askstring("Neue Umfrage", "Titel der Umfrage:", parent=self.frame)
        if not titel:
            return
        fragen = []
        while True:
            frage = simpledialog.askstring("Frage hinzufügen", "Frage eingeben (Abbrechen beendet):", parent=self.frame)
            if not frage:
                break
            fragen.append({"frage": frage, "antworten": [], "typ": "einfach"})  # nur Einfachauswahl hier
        if not fragen:
            messagebox.showwarning("Umfrage", "Keine Fragen hinzugefügt!")
            return
        umfrage = {
            "title": titel.strip(),
            "questions": fragen,
            "active": False,
            "results": [{} for _ in fragen],  # Liste von Dicts mit Antwortzählungen
        }
        self.umfragen.append(umfrage)
        self.save_umfragen()
        self.refresh_list()
        messagebox.showinfo("Umfrage", "Umfrage erstellt!")

    def umfrage_starten(self):
        if not self.current_survey:
            messagebox.showwarning("Starten", "Bitte erst eine Umfrage auswählen!")
            return
        self.current_survey["active"] = True
        self.save_umfragen()
        self.refresh_list()
        messagebox.showinfo("Starten", f"Umfrage '{self.current_survey['title']}' gestartet.")

    def umfrage_stoppen(self):
        if not self.current_survey:
            messagebox.showwarning("Stoppen", "Bitte erst eine Umfrage auswählen!")
            return
        self.current_survey["active"] = False
        self.save_umfragen()
        self.refresh_list()
        messagebox.showinfo("Stoppen", f"Umfrage '{self.current_survey['title']}' gestoppt.")

    def ergebnisse_anzeigen(self):
        if not self.current_survey:
            messagebox.showwarning("Ergebnisse", "Bitte erst eine Umfrage auswählen!")
            return
        ergebnisse_text = ""
        for i, frage in enumerate(self.current_survey["questions"]):
            ergebnisse_text += f"Frage {i+1}: {frage['frage']}\n"
            ergebnisse_text += "Antworten:\n"
            # Für Demo: keine Antworten, da kein Voting-UI
            ergebnisse_text += "(keine Daten, da Voting nicht implementiert)\n\n"
        messagebox.showinfo("Ergebnisse", ergebnisse_text)

    def get_frame(self):
        return self.frame

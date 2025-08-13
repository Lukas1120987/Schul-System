import tkinter as tk
from tkinter import messagebox
import json
import os
from ordner import get_data_path

WHITELIST_PATH = os.path.join(get_data_path(), "data/internet_whitelist.json")

class Modul:
    def __init__(self, parent, username, user_data=None):
        self.frame = tk.Frame(parent, bg="#f0f2f5")
        self.username = username
        self.user_data = user_data or {}

        self.baue_gui()

    def get_frame(self):
        return self.frame

    def lade_whitelist(self):
        if not os.path.exists(WHITELIST_PATH):
            return []
        try:
            with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def speichere_whitelist(self, daten):
        with open(WHITELIST_PATH, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=2, ensure_ascii=False)

    def baue_gui(self):
        tk.Label(self.frame, text="🌐 Internet-Whitelist", font=("Arial", 18, "bold"), bg="#f0f2f5").pack(pady=10)

        self.liste = tk.Listbox(self.frame, height=10)
        self.liste.pack(fill="both", expand=True, padx=10, pady=5)
        self.aktualisiere_liste()

        # Prüfen, ob Verwaltung
        if self.user_data.get("second_group") == "Verwaltung":
            eingabe_frame = tk.Frame(self.frame, bg="#f0f2f5")
            eingabe_frame.pack(fill="x", padx=10, pady=5)

            self.neue_url = tk.Entry(eingabe_frame)
            self.neue_url.pack(side="left", fill="x", expand=True, padx=(0, 5))
            tk.Button(eingabe_frame, text="➕ Hinzufügen", command=self.hinzufuegen, bg="#4CAF50", fg="white").pack(side="left")

            tk.Button(self.frame, text="❌ Entfernen", command=self.entfernen, bg="#f44336", fg="white").pack(pady=5)

    def aktualisiere_liste(self):
        self.liste.delete(0, tk.END)
        for url in self.lade_whitelist():
            self.liste.insert(tk.END, url)

    def hinzufuegen(self):
        url = self.neue_url.get().strip()
        if not url:
            messagebox.showerror("Fehler", "Bitte eine URL eingeben.")
            return
        daten = self.lade_whitelist()
        if url in daten:
            messagebox.showwarning("Hinweis", "Diese URL steht bereits auf der Whitelist.")
            return
        daten.append(url)
        self.speichere_whitelist(daten)
        self.neue_url.delete(0, tk.END)
        self.aktualisiere_liste()

    def entfernen(self):
        auswahl = self.liste.curselection()
        if not auswahl:
            messagebox.showwarning("Hinweis", "Bitte eine URL auswählen.")
            return
        daten = self.lade_whitelist()
        url = self.liste.get(auswahl[0])
        daten.remove(url)
        self.speichere_whitelist(daten)
        self.aktualisiere_liste()

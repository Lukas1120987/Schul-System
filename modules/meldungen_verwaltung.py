import tkinter as tk
from tkinter import ttk, messagebox
import json

class Modul:
    def __init__(self, root, benutzername, frame_platzhalter):
        self.root = root
        self.benutzername = benutzername
        self.frame_platzhalter = frame_platzhalter
        self.messages_file = "data/messages.json"
        self.frame = tk.Frame(self.frame_platzhalter)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Meldungen verwalten", font=("Arial", 16)).pack(pady=10)

        self.tree = ttk.Treeview(self.frame, columns=("Datum", "Absender", "Betreff", "Inhalt"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        tk.Button(self.frame, text="Löschen", command=self.loeschen).pack(pady=5)

        self.lade_meldungen()

    def lade_meldungen(self):
        try:
            with open(self.messages_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        except FileNotFoundError:
            messages = []

        self.tree.delete(*self.tree.get_children())

        for msg in messages:
            empfänger = msg.get("empfänger", "")
            if empfänger == "Verwaltung" or empfänger == self.benutzername:
                self.tree.insert("", "end", iid=msg["id"], values=(
                    msg.get("datum", ""),
                    msg.get("absender", ""),
                    msg.get("betreff", ""),
                    msg.get("inhalt", "")
                ))

    def loeschen(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Hinweis", "Bitte wähle eine Meldung aus.")
            return

        id_to_delete = selected[0]

        try:
            with open(self.messages_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        except FileNotFoundError:
            messages = []

        messages = [m for m in messages if m["id"] != id_to_delete]

        with open(self.messages_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4)

        self.tree.delete(id_to_delete)
        messagebox.showinfo("Erfolg", "Meldung gelöscht.")

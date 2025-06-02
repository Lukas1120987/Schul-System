import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import uuid

class Modul:
    def __init__(self, root, benutzername, frame_platzhalter):
        self.root = root
        self.benutzername = benutzername
        self.frame_platzhalter = frame_platzhalter

        self.messages_file = "data/messages.json"

        self.frame = tk.Frame(self.frame_platzhalter)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="Meldung erstellen", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.frame, text="Betreff:").pack()
        self.entry_betreff = tk.Entry(self.frame, width=40)
        self.entry_betreff.pack()

        tk.Label(self.frame, text="Nachricht:").pack()
        self.text_nachricht = tk.Text(self.frame, height=8, width=50)
        self.text_nachricht.pack()

        tk.Button(self.frame, text="Absenden", command=self.absenden).pack(pady=10)

    def absenden(self):
        betreff = self.entry_betreff.get()
        inhalt = self.text_nachricht.get("1.0", tk.END).strip()

        if not betreff or not inhalt:
            messagebox.showwarning("Fehler", "Bitte Betreff und Nachricht ausfüllen.")
            return

        datum = datetime.now().strftime("%Y-%m-%d %H:%M")
        meldung = {
            "id": str(uuid.uuid4()),  # Eindeutige ID
            "absender": self.benutzername,
            "datum": datum,
            "betreff": betreff,
            "inhalt": inhalt,
            "empfänger": "Verwaltung"
        }

        try:
            with open(self.messages_file, "r") as f:
                messages = json.load(f)
        except FileNotFoundError:
            messages = []

        messages.append(meldung)

        with open(self.messages_file, "w") as f:
            json.dump(messages, f, indent=4)

        messagebox.showinfo("Erfolg", "Meldung wurde erfolgreich gesendet.")
        self.entry_betreff.delete(0, tk.END)
        self.text_nachricht.delete("1.0", tk.END)

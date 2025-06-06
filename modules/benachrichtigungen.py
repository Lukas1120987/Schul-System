import tkinter as tk
import tkinter.messagebox
import json
import os
from datetime import datetime

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data

        self.frame = tk.Frame(master, bg="")
        tk.Label(self.frame, text="📣 Benachrichtigungen senden", font=("Segoe UI", 14, "bold")).pack(pady=10)

        tk.Label(self.frame, text="Empfänger (Username oder 'alle')").pack()
        self.to_entry = tk.Entry(self.frame)
        self.to_entry.pack()

        tk.Label(self.frame, text="Nachricht:").pack()
        self.msg_entry = tk.Text(self.frame, height=5)
        self.msg_entry.pack(pady=5)

        send_btn = tk.Button(self.frame, text="Senden", command=self.send_message)
        send_btn.pack(pady=10)

    def get_frame(self):
        return self.frame

    def send_message(self):
        empfaenger = self.to_entry.get().strip()
        nachricht = self.msg_entry.get("1.0", "end").strip()

        if not empfaenger or not nachricht:
            tk.messagebox.showerror("Fehler", "Bitte Empfänger und Nachricht angeben.")
            return

        # Stelle sicher, dass die Datei existiert
        if not os.path.exists("data/notifications.json"):
            with open("data/notifications.json", "w", encoding="utf-8") as f:
                json.dump({}, f)

        with open("data/notifications.json", "r", encoding="utf-8") as f:
            daten = json.load(f)

        # Wenn 'alle' gewählt wurde, alle User aus users.json laden und ansprechen
        empfaenger_liste = []
        if empfaenger.lower() == "alle":
            if not os.path.exists("data/users.json"):
                tk.messagebox.showerror("Fehler", "users.json nicht gefunden.")
                return
            with open("data/users.json", "r", encoding="utf-8") as f:
                users_data = json.load(f)
                empfaenger_liste = list(users_data.keys())
        else:
            empfaenger_liste = [empfaenger]

        # Nachricht an jeden Empfänger senden
        for emp in empfaenger_liste:
            daten.setdefault(emp, []).append({
                "text": nachricht,
                "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "gelesen": False
            })

        with open("data/notifications.json", "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=4)

        tk.messagebox.showinfo("Erfolg", f"Nachricht an {', '.join(empfaenger_liste)} gesendet.")
        self.to_entry.delete(0, "end")
        self.msg_entry.delete("1.0", "end")

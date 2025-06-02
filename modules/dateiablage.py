import os
import json
import tkinter as tk
from tkinter import messagebox

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data
        self.frame = tk.Frame(master, bg="white")

        self.upload_folder = self.ensure_folder_exists("data/upload_inbox")
        self.owners_file = "data/file_owners.json"
        self.users_file = "data/users.json"

        self.ensure_owners_file_exists()

        tk.Label(self.frame, text="📁 Dateiablage & Austausch", font=("Arial", 16), bg="white").pack(pady=10)
        tk.Label(self.frame, text="Dateien bitte manuell in 'data/upload_inbox' kopieren.",
                 bg="white", fg="gray").pack(pady=5)

        tk.Button(self.frame, text="🔄 Dateiliste aktualisieren", command=self.refresh_file_list).pack(pady=5)

        self.files_frame = tk.Frame(self.frame, bg="white")
        self.files_frame.pack(pady=10)

        self.refresh_file_list()

    def get_frame(self):
        return self.frame

    def ensure_folder_exists(self, folder):
        os.makedirs(folder, exist_ok=True)
        return folder

    def ensure_owners_file_exists(self):
        if not os.path.exists(self.owners_file):
            with open(self.owners_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def load_owners(self):
        with open(self.owners_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_owners(self, data):
        with open(self.owners_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def is_admin_or_owner(self, filename, owners_data):
        if self.username not in self.user_data:
            return False

        group = self.user_data[self.username]["group"]
        is_admin = self.user_data[self.username]["is_admin"]

        return is_admin or group == "Verwaltung" or owners_data.get(filename) == self.username

    def refresh_file_list(self):
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        files = os.listdir(self.upload_folder)
        if not files:
            tk.Label(self.files_frame, text="Keine Dateien vorhanden.", bg="white").pack()
            return

        owners_data = self.load_owners()

        # ➕ Neue Dateien automatisch dem aktuellen Benutzer zuweisen
        for file in files:
            if file not in owners_data:
                owners_data[file] = self.username
        self.save_owners(owners_data)

        for file in files:
            row = tk.Frame(self.files_frame, bg="white")
            row.pack(fill="x", padx=10, pady=2)

            is_owner = owners_data.get(file) == self.username
            user_info = self.user_data.get(self.username, {})
            group = user_info.get("group", "")
            is_admin = user_info.get("is_admin", False)

            # Status-Text setzen
            status_text = ""
            if is_owner:
                status_text = " (Eigentümer)"
            elif group == "Verwaltung" or is_admin:
                status_text = " (Verwaltung)"

            file_label = tk.Label(row, text=f"{file}{status_text}", fg="blue", cursor="hand2", bg="white")
            file_label.pack(side="left")
            file_label.bind("<Button-1>", lambda e, f=file: self.download_file(f))

            # ❌ Löschen nur bei Berechtigung
            can_delete = is_owner or group == "Verwaltung" or is_admin
            if can_delete:
                tk.Button(row, text="❌", command=lambda f=file: self.delete_file(f), bg="white", fg="red", bd=0).pack(side="right")




    def open_file(self, filename):
        filepath = os.path.abspath(os.path.join(self.upload_folder, filename))
        try:
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht geöffnet werden: {e}")

    def delete_file(self, filename):
        filepath = os.path.join(self.upload_folder, filename)
        owners_data = self.load_owners()

        file_owner = owners_data.get(filename)
        user_info = self.user_data.get(self.username, {})
        is_admin = user_info.get("is_admin", False)
        group = user_info.get("group", "")

        if self.username == file_owner or is_admin or group == "Verwaltung":
            try:
                os.remove(filepath)
                owners_data.pop(filename, None)
                self.save_owners(owners_data)
                messagebox.showinfo("Erfolg", f"Datei '{filename}' wurde gelöscht.")
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Fehler", f"Datei konnte nicht gelöscht werden: {e}")
        else:
            messagebox.showerror("Zugriff verweigert", "Du darfst diese Datei nicht löschen.")

    def download_file(self, filename):
        filepath = os.path.join(self.upload_folder, filename)
        try:
            os.startfile(filepath)  # Öffnet die Datei mit dem Standardprogramm
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht geöffnet werden: {e}")

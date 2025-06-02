import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import shutil

CLOUD_DB = "data/cloud.json"
USERS_DB = "data/users.json"
OWNERS_DB = "data/cloud-file_owners.json"

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.group = user_data["group"]
        self.upload_folder = self.ensure_upload_folder_exists()

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="☁️ Cloud-Dateien", font=("Arial", 16), bg="white").pack(pady=10)

        self.load_data()
        self.setup_ui()

    def get_frame(self):
        return self.frame

    def ensure_upload_folder_exists(self):
        os.makedirs("data/uploads", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(OWNERS_DB):
            with open(OWNERS_DB, "w") as f:
                json.dump({}, f)
        return "data/uploads"

    def load_data(self):
        try:
            with open(CLOUD_DB, "r", encoding="utf-8") as f:
                self.files = json.load(f)
        except:
            self.files = []

        try:
            with open(USERS_DB, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.userlist = [name for name in data if not name.startswith("_group_")]
                self.grouplist = list(set(user["group"] for user in data.values() if "group" in user))
        except:
            self.userlist = []
            self.grouplist = []

        try:
            with open(OWNERS_DB, "r", encoding="utf-8") as f:
                self.owners = json.load(f)
        except:
            self.owners = {}

    def setup_ui(self):
        upload_frame = tk.LabelFrame(self.frame, text="Datei hochladen & freigeben", bg="white")
        upload_frame.pack(padx=10, pady=10, fill="x")

        tk.Button(upload_frame, text="Dateipfad manuell eingeben", command=self.choose_file_dialog).pack(pady=5)
        self.path_entry = tk.Entry(upload_frame, width=50)
        self.path_entry.pack()
        self.file_label = tk.Label(upload_frame, text="Keine Datei ausgewählt", bg="white")
        self.file_label.pack()

        tk.Label(upload_frame, text="Freigeben für Gruppe:", bg="white").pack()
        self.group_select = ttk.Combobox(upload_frame, values=self.grouplist, state="readonly")
        self.group_select.pack(pady=2)

        tk.Label(upload_frame, text="...oder Nutzer:", bg="white").pack()
        self.user_select = ttk.Combobox(upload_frame, values=self.userlist, state="readonly")
        self.user_select.pack(pady=2)

        tk.Button(upload_frame, text="Hochladen", command=self.upload_file).pack(pady=5)

        self.file_table = ttk.Treeview(self.frame, columns=("file", "from", "to"), show="headings")
        self.file_table.heading("file", text="Datei")
        self.file_table.heading("from", text="Von")
        self.file_table.heading("to", text="Für")
        self.file_table.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Button(self.frame, text="Ausgewählte Datei herunterladen", command=self.download_file).pack(pady=5)
        tk.Button(self.frame, text="Ausgewählte Datei löschen", command=self.delete_file).pack(pady=5)

        self.refresh_table()

    def choose_file_dialog(self):
        path = self.path_entry.get().strip()
        if not os.path.isfile(path):
            self.file_label.config(text="❌ Ungültiger Pfad")
            return
        self.selected_path = path
        self.file_label.config(text=os.path.basename(path))

    def upload_file(self):
        if not hasattr(self, "selected_path") or not os.path.isfile(self.selected_path):
            return messagebox.showerror("Fehler", "Bitte zuerst einen gültigen Dateipfad eingeben.")

        group = self.group_select.get()
        user = self.user_select.get()

        if not group and not user:
            return messagebox.showerror("Fehler", "Bitte eine Gruppe oder einen Nutzer auswählen.")

        filename = os.path.basename(self.selected_path)
        saved_path = os.path.join(self.upload_folder, filename)

        try:
            shutil.copy(self.selected_path, saved_path)
        except Exception as e:
            return messagebox.showerror("Fehler", f"Datei konnte nicht hochgeladen werden: {e}")

        new_file = {
            "filename": filename,
            "path": saved_path,
            "from": self.username,
            "to_group": group if group else None,
            "to_user": user if user else None
        }

        self.files.append(new_file)
        with open(CLOUD_DB, "w") as f:
            json.dump(self.files, f, indent=2)

        # Datei-Eigentümer aktualisieren
        self.owners[filename] = self.username
        with open(OWNERS_DB, "w") as f:
            json.dump(self.owners, f, indent=2)

        self.selected_path = ""
        self.path_entry.delete(0, tk.END)
        self.file_label.config(text="Keine Datei ausgewählt")
        self.group_select.set("")
        self.user_select.set("")
        self.refresh_table()

    def refresh_table(self):
        for i in self.file_table.get_children():
            self.file_table.delete(i)

        for f in self.files:
            if (f["to_user"] == self.username or f["to_group"] == self.group) or f["from"] == self.username:
                freigabe = f["to_user"] if f["to_user"] else f["to_group"]
                self.file_table.insert("", "end", values=(f["filename"], f["from"], freigabe))

    def download_file(self):
        selected = self.file_table.selection()
        if not selected:
            return messagebox.showwarning("Hinweis", "Bitte eine Datei auswählen.")

        file_name = self.file_table.item(selected[0], "values")[0]
        for f in self.files:
            if f["filename"] == file_name and (
                f["to_user"] == self.username or f["to_group"] == self.group or f["from"] == self.username
            ):
                target = f"{file_name}"
                try:
                    shutil.copy(f["path"], target)
                    messagebox.showinfo("Erfolg", f"Datei gespeichert unter:\n{os.path.abspath(target)}")
                except:
                    messagebox.showerror("Fehler", "Fehler beim Kopieren der Datei.")
                return

    def delete_file(self):
        selected = self.file_table.selection()
        if not selected:
            return messagebox.showwarning("Hinweis", "Bitte eine Datei auswählen.")

        file_name = self.file_table.item(selected[0], "values")[0]

        for i, f in enumerate(self.files):
            if f["filename"] == file_name and f["from"] == self.username:
                confirm = messagebox.askyesno("Bestätigung", f"Möchtest du die Datei '{file_name}' wirklich löschen?")
                if confirm:
                    try:
                        if os.path.exists(f["path"]):
                            os.remove(f["path"])
                    except:
                        messagebox.showwarning("Warnung", "Datei konnte nicht vom Dateisystem gelöscht werden.")
                    self.files.pop(i)
                    with open(CLOUD_DB, "w") as file:
                        json.dump(self.files, file, indent=2)

                    if file_name in self.owners:
                        del self.owners[file_name]
                        with open(OWNERS_DB, "w") as f:
                            json.dump(self.owners, f, indent=2)

                    self.refresh_table()
                    messagebox.showinfo("Erfolg", "Datei erfolgreich gelöscht.")
                return

        messagebox.showerror("Fehler", "Du darfst nur Dateien löschen, die du selbst hochgeladen hast.")

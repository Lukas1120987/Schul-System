import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import json

CLOUD_DB = "data/cloud.json"
USERS_DB = "data/users.json"

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.group = user_data["group"]

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="☁️ Cloud-Dateien", font=("Arial", 16), bg="white").pack(pady=10)

        self.load_data()
        self.setup_ui()

    def get_frame(self):
        return self.frame

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



    def setup_ui(self):
        # Upload-Bereich
        upload_frame = tk.LabelFrame(self.frame, text="Datei hochladen & freigeben", bg="white")
        upload_frame.pack(padx=10, pady=10, fill="x")

        tk.Button(upload_frame, text="Datei auswählen", command=self.choose_file).pack(pady=5)
        self.file_label = tk.Label(upload_frame, text="Keine Datei ausgewählt", bg="white")
        self.file_label.pack()

        # Freigabe
        tk.Label(upload_frame, text="Freigeben für Gruppe:", bg="white").pack()
        self.group_select = ttk.Combobox(upload_frame, values=self.grouplist, state="readonly")
        self.group_select.pack(pady=2)

        tk.Label(upload_frame, text="...oder Nutzer:", bg="white").pack()
        self.user_select = ttk.Combobox(upload_frame, values=self.userlist, state="readonly")
        self.user_select.pack(pady=2)

        tk.Button(upload_frame, text="Hochladen", command=self.upload_file).pack(pady=5)

        # Dateiübersicht
        self.file_table = ttk.Treeview(self.frame, columns=("file", "from", "to"), show="headings")
        self.file_table.heading("file", text="Datei")
        self.file_table.heading("from", text="Von")
        self.file_table.heading("to", text="Für")
        self.file_table.pack(padx=10, pady=10, fill="both", expand=True)

        # Download-Button
        tk.Button(self.frame, text="Ausgewählte Datei herunterladen", command=self.download_file).pack(pady=5)


        self.refresh_table()

    def choose_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.selected_path = filepath
            self.file_label.config(text=os.path.basename(filepath))

    def download_file(self):
        selected = self.file_table.selection()
        if not selected:
            return messagebox.showwarning("Hinweis", "Bitte eine Datei auswählen.")
        
        file_name = self.file_table.item(selected[0], "values")[0]

        for f in self.files:
            if f["filename"] == file_name and (
                f["to_user"] == self.username or f["to_group"] == self.group or f["from"] == self.username
            ):
                save_path = filedialog.asksaveasfilename(initialfile=f["filename"])
                if save_path:
                    try:
                        with open(f["path"], "rb") as src, open(save_path, "wb") as dst:
                            dst.write(src.read())
                        messagebox.showinfo("Erfolg", f"Datei gespeichert unter:\n{save_path}")
                    except:
                        messagebox.showerror("Fehler", "Fehler beim Kopieren der Datei.")
                return


    def upload_file(self):
        if not hasattr(self, "selected_path"):
            return messagebox.showerror("Fehler", "Bitte zuerst eine Datei auswählen.")

        group = self.group_select.get()
        user = self.user_select.get()

        if not group and not user:
            return messagebox.showerror("Fehler", "Bitte eine Gruppe oder einen Nutzer auswählen.")

        new_file = {
            "filename": os.path.basename(self.selected_path),
            "path": self.selected_path,
            "from": self.username,
            "to_group": group if group else None,
            "to_user": user if user else None
        }
        self.files.append(new_file)

        with open(CLOUD_DB, "w", encoding="utf-8") as f:
            json.dump(self.files, f, indent=2)

        self.selected_path = ""
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

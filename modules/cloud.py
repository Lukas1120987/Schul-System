import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import json
from ordner import get_data_path

USERS_DB = os.path.join(get_data_path(), "data/users.json")
CLOUD_DB = os.path.join(get_data_path(), "data/cloud.json")

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.group = user_data["group"]

        self.frame = ctk.CTkFrame(master, corner_radius=12)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.selected_path = None

        self.load_data()
        self.setup_ui()
        self.refresh_files()

    def get_frame(self):
        return self.frame

    # ---------- Daten ----------
    def load_data(self):
        try:
            with open(CLOUD_DB, "r", encoding="utf-8") as f:
                self.files = json.load(f)
        except:
            self.files = []

        try:
            with open(USERS_DB, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.userlist = [u for u in data if not u.startswith("_group_")]
                self.grouplist = sorted(
                    {u.get("group") for u in data.values() if "group" in u}
                )
        except:
            self.userlist = []
            self.grouplist = []

    # ---------- UI ----------
    def setup_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="☁️ Cloud",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(10, 15))

        # Upload Bereich
        upload = ctk.CTkFrame(self.frame, corner_radius=10)
        upload.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            upload,
            text="Datei hochladen & freigeben",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        ctk.CTkButton(
            upload,
            text="📂 Datei auswählen",
            command=self.choose_file
        ).pack(pady=5)

        self.file_label = ctk.CTkLabel(upload, text="Keine Datei ausgewählt")
        self.file_label.pack(pady=2)

        self.group_select = ctk.CTkOptionMenu(
            upload,
            values=[""] + self.grouplist
        )
        self.group_select.set("")
        self.group_select.pack(pady=4)

        self.user_select = ctk.CTkOptionMenu(
            upload,
            values=[""] + self.userlist
        )
        self.user_select.set("")
        self.user_select.pack(pady=4)

        ctk.CTkButton(
            upload,
            text="⬆️ Hochladen",
            command=self.upload_file,
            height=38
        ).pack(pady=8)

        # Dateiübersicht
        ctk.CTkLabel(
            self.frame,
            text="Verfügbare Dateien",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 5))

        self.file_list = ctk.CTkScrollableFrame(self.frame, height=300)
        self.file_list.pack(fill="both", expand=True, padx=10, pady=5)

    # ---------- Aktionen ----------
    def choose_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.selected_path = path
            self.file_label.configure(text=os.path.basename(path))

    def upload_file(self):
        if not self.selected_path:
            messagebox.showerror("Fehler", "Bitte zuerst eine Datei auswählen.")
            return

        group = self.group_select.get()
        user = self.user_select.get()

        if not group and not user:
            messagebox.showerror("Fehler", "Bitte Gruppe oder Nutzer auswählen.")
            return

        entry = {
            "filename": os.path.basename(self.selected_path),
            "path": self.selected_path,
            "from": self.username,
            "to_group": group or None,
            "to_user": user or None
        }

        self.files.append(entry)

        with open(CLOUD_DB, "w", encoding="utf-8") as f:
            json.dump(self.files, f, indent=2, ensure_ascii=False)

        self.selected_path = None
        self.file_label.configure(text="Keine Datei ausgewählt")
        self.group_select.set("")
        self.user_select.set("")
        self.refresh_files()

    def refresh_files(self):
        for w in self.file_list.winfo_children():
            w.destroy()

        for f in self.files:
            if (
                f["from"] == self.username
                or f["to_user"] == self.username
                or f["to_group"] == self.group
            ):
                self.create_file_row(f)

    def create_file_row(self, file):
        row = ctk.CTkFrame(self.file_list, corner_radius=8)
        row.pack(fill="x", pady=4, padx=4)

        ctk.CTkLabel(
            row,
            text=file["filename"],
            anchor="w"
        ).pack(side="left", padx=10, expand=True, fill="x")

        ctk.CTkLabel(
            row,
            text=f"von {file['from']}",
            text_color="gray"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            row,
            text="⬇️ Download",
            width=100,
            command=lambda f=file: self.download_file(f)
        ).pack(side="right", padx=10)

    def download_file(self, file):
        save_path = filedialog.asksaveasfilename(
            initialfile=file["filename"]
        )
        if not save_path:
            return

        try:
            with open(file["path"], "rb") as src, open(save_path, "wb") as dst:
                dst.write(src.read())
            messagebox.showinfo("Erfolg", "Datei erfolgreich gespeichert.")
        except:
            messagebox.showerror("Fehler", "Fehler beim Speichern der Datei.")

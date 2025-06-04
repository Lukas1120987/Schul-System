import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.frame = tk.Frame(master, bg="white")

        tk.Label(self.frame, text="📁 Dateiablage & Austausch", font=("Arial", 16), bg="white").pack(pady=10)

        tk.Button(self.frame, text="Datei hochladen", command=self.upload_file).pack(pady=5)

        self.files_frame = tk.Frame(self.frame, bg="white")
        self.files_frame.pack(pady=10)

        self.refresh_file_list()

    def get_frame(self):
        return self.frame

    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            filename = os.path.basename(filepath)
            target_path = os.path.join("data", "files", filename)
            try:
                shutil.copy(filepath, target_path)
                messagebox.showinfo("Erfolg", f"Datei '{filename}' wurde hochgeladen.")
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Fehler", f"Datei konnte nicht hochgeladen werden: {e}")

    def refresh_file_list(self):
        for widget in self.files_frame.winfo_children():
            widget.destroy()

        folder = os.path.join("data", "files")
        if not os.path.exists(folder):
            os.makedirs(folder)

        files = os.listdir(folder)
        if not files:
            tk.Label(self.files_frame, text="Keine Dateien vorhanden.", bg="white").pack()
            return

        for file in files:
            tk.Button(self.files_frame, text=file, relief="flat", fg="blue",
                      command=lambda f=file: self.open_file(f)).pack(anchor="w")

    def open_file(self, filename):
        filepath = os.path.abspath(os.path.join("data", "files", filename))
        try:
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht geöffnet werden: {e}")

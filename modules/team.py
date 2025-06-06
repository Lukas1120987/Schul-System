import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys

DATA_DIR = "data"

class Redirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data
        self.console_window = None

        self.frame = tk.Frame(master, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.is_admin = self.check_if_admin()

        tk.Label(self.frame, text="🛠 Development Team Console & JSON Editor", font=("Arial", 16), bg="white").pack(pady=10)

        # --- Button: Konsole in neues Fenster ---
        self.console_button = tk.Button(self.frame, text="Konsole in neuem Fenster öffnen", command=self.open_console_window)
        self.console_button.pack(pady=5)

        # --- Konsole im Hauptfenster ---
        self.konsole_rahmen = tk.LabelFrame(self.frame, text="Konsole (Debug-Ausgabe)", bg="white")
        self.konsole_rahmen.pack(fill="both", expand=True, padx=10, pady=5)

        self.konsole_text = tk.Text(self.konsole_rahmen, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
        self.konsole_text.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0), pady=5)

        konsole_scroll = tk.Scrollbar(self.konsole_rahmen, command=self.konsole_text.yview)
        konsole_scroll.pack(side=tk.RIGHT, fill="y")
        self.konsole_text.config(yscrollcommand=konsole_scroll.set, state=tk.DISABLED)

        sys.stdout = Redirector(self.konsole_text)
        sys.stderr = Redirector(self.konsole_text)

        tk.Button(self.frame, text="Test-Log ausgeben", command=lambda: self.log("Test-Log: Modul funktioniert!")).pack(pady=5)

        # --- JSON Editor ---
        editor_frame = tk.LabelFrame(self.frame, text="JSON Datei Editor", bg="white")
        editor_frame.pack(fill="both", expand=True, padx=10, pady=5)

        top_buttons = tk.Frame(editor_frame, bg="white")
        top_buttons.pack(fill="x")

        tk.Button(top_buttons, text="JSON Datei öffnen", command=self.open_json_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_buttons, text="Speichern", command=self.save_json_file).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_buttons, text="In Datei laden (Ersetzen)", command=self.reload_json).pack(side=tk.LEFT, padx=5, pady=5)

        self.json_path_label = tk.Label(editor_frame, text="Keine Datei geladen", bg="white", fg="gray")
        self.json_path_label.pack()

        self.json_text = tk.Text(editor_frame, bg="#f0f0f0", height=15)
        self.json_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.current_file = None

    def get_frame(self):
        return self.frame

    def check_if_admin(self):
        users_datei = os.path.join(DATA_DIR, "users.json")
        if not os.path.exists(users_datei):
            return False
        with open(users_datei, "r", encoding="utf-8") as f:
            users = json.load(f)
            return users.get(self.username, {}).get("is_admin", False)

    def log(self, text: str):
        print(text)

    # --- Konsole auslagern ---
    def open_console_window(self):
        if self.console_window:
            self.console_window.lift()
            return

        self.console_window = tk.Toplevel(self.master)
        self.console_window.title("Externe Konsole")
        self.console_window.geometry("800x300")
        self.console_window.protocol("WM_DELETE_WINDOW", self.close_console_window)

        self.konsole_text.pack_forget()
        self.konsole_rahmen.pack_forget()

        # Neues Textfeld im externen Fenster
        self.konsole_text = tk.Text(self.console_window, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
        self.konsole_text.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        scroll = tk.Scrollbar(self.console_window, command=self.konsole_text.yview)
        scroll.pack(side=tk.RIGHT, fill="y")
        self.konsole_text.config(yscrollcommand=scroll.set, state=tk.DISABLED)

        sys.stdout = Redirector(self.konsole_text)
        sys.stderr = Redirector(self.konsole_text)

    def close_console_window(self):
        self.console_window.destroy()
        self.console_window = None

        # Rückkehr zur Konsole im Hauptfenster
        self.konsole_rahmen.pack(fill="both", expand=True, padx=10, pady=5)
        self.konsole_text = tk.Text(self.konsole_rahmen, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
        self.konsole_text.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0), pady=5)
        scroll = tk.Scrollbar(self.konsole_rahmen, command=self.konsole_text.yview)
        scroll.pack(side=tk.RIGHT, fill="y")
        self.konsole_text.config(yscrollcommand=scroll.set, state=tk.DISABLED)

        sys.stdout = Redirector(self.konsole_text)
        sys.stderr = Redirector(self.konsole_text)

    # --- JSON Editor ---
    def open_json_file(self):
        initial_dir = os.path.abspath(DATA_DIR)
        filepath = filedialog.askopenfilename(title="JSON Datei öffnen",
                                              initialdir=initial_dir,
                                              filetypes=[("JSON Dateien", "*.json")])
        if not filepath:
            return

        if not os.path.abspath(filepath).startswith(initial_dir):
            messagebox.showerror("Fehler", "Datei muss im data-Ordner liegen.")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)
        except Exception as e:
            messagebox.showerror("Fehler", f"JSON konnte nicht geladen werden:\n{e}")
            return

        self.current_file = filepath
        self.json_path_label.config(text=os.path.relpath(filepath, DATA_DIR))
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, json.dumps(content, indent=2, ensure_ascii=False))
        print(f"Datei geladen: {os.path.relpath(filepath, DATA_DIR)}")

    def save_json_file(self):
        if not self.current_file:
            messagebox.showwarning("Warnung", "Keine JSON-Datei geladen.")
            return

        try:
            text = self.json_text.get("1.0", tk.END).strip()
            data = json.loads(text)
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültiges JSON:\n{e}")
            return

        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Datei gespeichert: {os.path.relpath(self.current_file, DATA_DIR)}")
            messagebox.showinfo("Erfolg", "Datei erfolgreich gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht gespeichert werden:\n{e}")

    def reload_json(self):
        if not self.current_file:
            messagebox.showwarning("Warnung", "Keine JSON-Datei geladen.")
            return
        try:
            with open(self.current_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, json.dumps(content, indent=2, ensure_ascii=False))
            print(f"Datei neu geladen: {os.path.relpath(self.current_file, DATA_DIR)}")
        except Exception as e:
            messagebox.showerror("Fehler", f"JSON konnte nicht neu geladen werden:\n{e}")

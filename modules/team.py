import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sys
import datetime

DATA_DIR = "data"
LOG_BUFFER = []  # Globale Log-Speicherung für Modulwechsel
LOG_MAX_LENGTH = 5000  # Maximale Zeilen in der Konsole


class Redirector:
    def __init__(self, text_widget, stream_type="stdout"):
        self.text_widget = text_widget
        self.stream_type = stream_type
        self.auto_scroll = True

    def write(self, text):
        if not text.strip():
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}"
        LOG_BUFFER.append(line)
        LOG_BUFFER[:] = LOG_BUFFER[-LOG_MAX_LENGTH:]  # begrenzen

        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, line)
        if self.auto_scroll:
            self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

        # Fehler zusätzlich loggen
        if self.stream_type == "stderr":
            with open("error.log", "a", encoding="utf-8") as f:
                f.write(line)

    def flush(self):
        pass


class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data
        self.console_window = None
        self.filter_mode = "ALL"

        self.frame = tk.Frame(master, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.is_admin = self.check_is_admin()


        tk.Label(self.frame, text="🛠 Development Console & JSON Editor", font=("Arial", 16), bg="white").pack(pady=10)

        self.console_button = tk.Button(self.frame, text="Konsole in neuem Fenster öffnen", command=self.open_console_window)
        self.console_button.pack(pady=5)

        # Konsole intern
        self.konsole_rahmen = tk.LabelFrame(self.frame, text="Konsole (Debug-Ausgabe)", bg="white")
        self.konsole_rahmen.pack(fill="both", expand=True, padx=10, pady=5)

        self.konsole_text = self.create_console_widget(self.konsole_rahmen)

        self.stdout_redirector = Redirector(self.konsole_text, "stdout")
        self.stderr_redirector = Redirector(self.konsole_text, "stderr")
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector

        self.control_buttons()

        print("System bereit.")

    def get_frame(self):
        return self.frame


    def create_console_widget(self, parent):
        text = tk.Text(parent, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
        text.pack(side=tk.LEFT, fill="both", expand=True, padx=(5, 0), pady=5)
        scroll = tk.Scrollbar(parent, command=text.yview)
        scroll.pack(side=tk.RIGHT, fill="y")
        text.config(yscrollcommand=scroll.set, state=tk.DISABLED)
        return text

    def control_buttons(self):
        controls = tk.Frame(self.frame, bg="white")
        controls.pack()

        tk.Button(controls, text="Test-Log ausgeben", command=lambda: self.log("Test-Log: Modul funktioniert!")).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Nur Fehler anzeigen", command=lambda: self.set_filter("ERROR")).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Nur Info anzeigen", command=lambda: self.set_filter("INFO")).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Alles anzeigen", command=lambda: self.set_filter("ALL")).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Log kopieren", command=self.copy_log_to_clipboard).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Auto-Scroll an/aus", command=self.toggle_scroll).pack(side=tk.LEFT, padx=5)

    def set_filter(self, mode):
        self.filter_mode = mode
        self.refresh_console()

    def refresh_console(self):
        self.konsole_text.config(state=tk.NORMAL)
        self.konsole_text.delete("1.0", tk.END)
        for line in LOG_BUFFER:
            if self.filter_mode == "ERROR" and "Traceback" not in line and "Error" not in line:
                continue
            elif self.filter_mode == "INFO" and ("Traceback" in line or "Error" in line):
                continue
            self.konsole_text.insert(tk.END, line)
        self.konsole_text.config(state=tk.DISABLED)

    def copy_log_to_clipboard(self):
        full_log = "".join(LOG_BUFFER)
        self.master.clipboard_clear()
        self.master.clipboard_append(full_log)
        print("Log in Zwischenablage kopiert.")

    def toggle_scroll(self):
        self.stdout_redirector.auto_scroll = not self.stdout_redirector.auto_scroll
        self.stderr_redirector.auto_scroll = self.stdout_redirector.auto_scroll
        print(f"Auto-Scroll ist {'aktiviert' if self.stdout_redirector.auto_scroll else 'deaktiviert'}.")

    def log(self, text: str):
        print(text)

    def open_console_window(self):
        if self.console_window:
            self.console_window.lift()
            return

        self.console_window = tk.Toplevel(self.master)
        self.console_window.title("Externe Konsole")
        self.console_window.geometry("800x400")
        self.console_window.protocol("WM_DELETE_WINDOW", self.close_console_window)

        self.konsole_text.pack_forget()
        self.konsole_rahmen.pack_forget()

        self.konsole_text = self.create_console_widget(self.console_window)
        self.stdout_redirector.text_widget = self.konsole_text
        self.stderr_redirector.text_widget = self.konsole_text
        self.refresh_console()

    def close_console_window(self):
        self.console_window.destroy()
        self.console_window = None

        self.konsole_rahmen.pack(fill="both", expand=True, padx=10, pady=5)
        self.konsole_text = self.create_console_widget(self.konsole_rahmen)
        self.stdout_redirector.text_widget = self.konsole_text
        self.stderr_redirector.text_widget = self.konsole_text
        self.refresh_console()

    def check_is_admin(self):
        users_datei = os.path.join(DATA_DIR, "users.json")
        if not os.path.exists(users_datei):
            return False
        with open(users_datei, "r", encoding="utf-8") as f:
            users = json.load(f)
            return users.get(self.username, {}).get("is_admin", False)

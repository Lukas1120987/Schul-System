import tkinter as tk
from tkinter import ttk, messagebox
import json
from dashboard import Dashboard
import random
from tkinter import simpledialog
from updater import check_and_update
import smtplib
import ssl
import os
import customtkinter as ctk
from ordner import get_data_path  # Import der Pfadfunktion

# Farben
PRIMARY_BLUE = "#1a73e8"
WHITE = "#ffffff"
TEXT_COLOR = "#202124"

import tkinter as tk
from tkinter import ttk

PRIMARY_BLUE = "#0052cc"
WHITE = "#ffffff"
LIGHT_BLUE = "#dbe9ff"

import tkinter as tk
from tkinter import ttk
import random

PRIMARY_BLUE = "#0052cc"
WHITE = "#ffffff"
LIGHT_BLUE = "#dbe9ff"

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)  # Vollbild

        # Haupt-Frame
        self.frame = ctk.CTkFrame(self.root, fg_color=PRIMARY_BLUE, corner_radius=0)
        self.frame.pack(fill="both", expand=True)

        # Titel
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="SchulSystem",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=WHITE
        )
        self.title_label.pack(pady=(60, 15))

        # Statusanzeige
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Starte Anwendung...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=LIGHT_BLUE
        )
        self.status_label.pack()

        # Fortschrittsbalken
        self.progress = ctk.CTkProgressBar(self.frame, width=400, height=18, corner_radius=10)
        self.progress.set(0)
        self.progress.pack(pady=40)

        # Footer
        self.footer_label = ctk.CTkLabel(
            self.frame,
            text="© SchulSystem 2025\nUnter MIT License",
            font=ctk.CTkFont(size=10),
            text_color="#cccccc"
        )
        self.footer_label.pack(side="bottom", pady=15)

        # Ladephasen
        self.loading_steps = [
            "Initialisiere Datenbanken...",
            "Lade Benutzeroberflächen...",
            "Importiere Stundenpläne...",
            "Verbinde mit Updater...",
            "Lade Module...",
            "Lade Einstellungen...",
            "Überprüfe Benutzerrechte..."
        ]
        self.step_index = 0
        self.total_time = random.randint(3000, 10000)  # 3–10 Sekunden
        self.interval = 1500  # alle 1,5 Sekunden neuer Text

        # Start
        self.schedule_loading_steps()
        self.animate_progress()
        self.root.after(self.total_time, self.load_main)

    def schedule_loading_steps(self):
        if self.step_index < len(self.loading_steps):
            self.status_label.configure(text=self.loading_steps[self.step_index])
            self.step_index += 1
            self.root.after(self.interval, self.schedule_loading_steps)

    def animate_progress(self):
        """Simuliert den Ladefortschritt"""
        current = self.progress.get()
        if current < 1:
            self.progress.set(current + 0.01)
            self.root.after(30, self.animate_progress)


    def load_main(self):
        self.root.destroy()
        open_login_window()  # das Login-Fenster

class CTkPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Neues Passwort", prompt="Bitte neues Passwort eingeben:"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.grab_set()  # blockiert Hauptfenster

        # zentriert
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"+{x}+{y}")

        # Frame
        frame = ctk.CTkFrame(self, corner_radius=15, fg_color=WHITE)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Label
        label = ctk.CTkLabel(frame, text=prompt, text_color="#000", font=ctk.CTkFont(size=14))
        label.pack(pady=(20, 10))

        # Eingabefeld
        self.entry = ctk.CTkEntry(frame, placeholder_text="Neues Passwort", show="•", width=250)
        self.entry.pack(pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(20, 10))

        ok_btn = ctk.CTkButton(btn_frame, text="OK", width=100, command=self.on_ok)
        ok_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame, text="Abbrechen", fg_color="#f44336", hover_color="#e53935",
            width=100, command=self.on_cancel
        )
        cancel_btn.pack(side="left", padx=5)

        # Returnwert
        self.result = None

    def on_ok(self):
        self.result = self.entry.get().strip()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login - SchulSystem")
        self.master.geometry(f"{self.master.winfo_screenwidth()}x{self.master.winfo_screenheight()}")
        self.master.configure(bg=WHITE)

        # zentrierter Frame
        self.frame = ctk.CTkFrame(master, corner_radius=15, fg_color=WHITE)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Überschrift
        self.title_label = ctk.CTkLabel(self.frame, text="Willkommen bei SchulSystem",
                                        font=ctk.CTkFont(size=20, weight="bold"), text_color=PRIMARY_BLUE)
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # Benutzername
        self.username_label = ctk.CTkLabel(self.frame, text="Benutzername:", text_color=TEXT_COLOR)
        self.username_label.grid(row=1, column=0, sticky="e", padx=(10,5), pady=5)
        self.entry_username = ctk.CTkEntry(self.frame, width=250, placeholder_text="Benutzername")
        self.entry_username.grid(row=1, column=1, pady=5, padx=(5,10))

        # Passwort
        self.password_label = ctk.CTkLabel(self.frame, text="Passwort:", text_color=TEXT_COLOR)
        self.password_label.grid(row=2, column=0, sticky="e", padx=(10,5), pady=5)

        self.entry_password = ctk.CTkEntry(self.frame, width=250, placeholder_text="Passwort", show="•")
        self.entry_password.grid(row=2, column=1, pady=5, padx=(5,10), sticky="w")

        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_checkbox = ctk.CTkCheckBox(self.frame, text="Passwort anzeigen",
                                                      variable=self.show_password_var,
                                                      command=self.toggle_password)
        self.show_password_checkbox.grid(row=3, column=1, sticky="w", pady=(0,10), padx=(5,10))

        # Buttons
        self.login_btn = ctk.CTkButton(self.frame, text="Login", command=self.login, width=200,
                                       fg_color=PRIMARY_BLUE, hover_color="#1669c1")
        self.login_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.exit_btn = ctk.CTkButton(self.frame, text="Programm beenden", command=self.master.destroy,
                                      fg_color="#f44336", hover_color="#e53935", width=200)
        self.exit_btn.grid(row=5, column=0, columnspan=2, pady=(5, 20))

    def toggle_password(self):
        if self.show_password_var.get():
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="•")

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        user_file_path = os.path.join(get_data_path(), "data/users.json")

        try:
            with open(user_file_path, "r", encoding="utf-8") as f:
                users = json.load(f)

            if username in users:
                if users[username]["password"] == "":
                    dialog = CTkPasswordDialog(self.master)
                    self.master.wait_window(dialog)  # warten bis Fenster zu
                    new_pw = dialog.result

                    if not new_pw:
                        messagebox.showerror("Fehler", "Passwort darf nicht leer sein.")
                        return

                    users[username]["password"] = new_pw
                    with open(user_file_path, "w", encoding="utf-8") as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)

                    messagebox.showinfo("Erfolg", "Passwort gesetzt. Du bist jetzt eingeloggt.")
                    self.master.destroy()
                    root = ctk.CTk()
                    root.attributes("-fullscreen", True)
                    app = Dashboard(root, username, users[username])
                    root.mainloop()
                    return

                elif users[username]["password"] == password:
                    self.master.destroy()
                    root = ctk.CTk()
                    root.attributes("-fullscreen", True)
                    app = Dashboard(root, username, users[username])
                    root.mainloop()
                    return

            messagebox.showerror("Fehler", "Benutzername oder Passwort falsch.")
        except FileNotFoundError:
            messagebox.showerror("Fehler", "Benutzerdaten nicht gefunden.")

                
def open_login_window():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

def start():
    check_and_update()
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.mainloop()





if __name__ == "__main__":
    start()

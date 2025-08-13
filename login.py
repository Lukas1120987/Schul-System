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
        #self.root.overrideredirect(True)
        self.root.attributes("-fullscreen", True)


        self.frame = tk.Frame(self.root, bg=PRIMARY_BLUE, bd=2, relief="ridge")
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text="SchulSystem", font=("Segoe UI", 26, "bold"),
                 bg=PRIMARY_BLUE, fg=WHITE).pack(pady=(40, 10))

        self.status_label = tk.Label(self.frame, text="Starte Anwendung...", font=("Segoe UI", 12),
                                     bg=PRIMARY_BLUE, fg=LIGHT_BLUE)
        self.status_label.pack()

        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=350,
                                        mode="indeterminate")
        self.progress.pack(pady=30)
        self.progress.start(15)

        tk.Label(self.frame, text="© SchulSystem 2025 \n Unter MIT License", font=("Segoe UI", 8), #© SchulSystem 2025
                 bg=PRIMARY_BLUE, fg="#cccccc").pack(side="bottom", pady=10)

        self.loading_steps = [
            "Initialisiere Datenbanken...",
            "Lade Benutzeroberflächen...",
            "Importiere Stundenpläne...",
            "Verbinde mit Updater...",
            "Lade Module...",
            "Lade Einstellungen...",
            "Überprüfe Benutzerrechte...",
        ]

        self.step_index = 0
        self.total_time = random.randint(3000, 10000)  # 3–10 Sekunden (vorher 3000, 10000)
        self.interval = 1500  # alle 1.5 Sekunden neuer Text

        self.schedule_loading_steps()
        self.root.after(self.total_time, self.load_main)

    def schedule_loading_steps(self):
        if self.step_index < len(self.loading_steps):
            self.status_label.config(text=self.loading_steps[self.step_index])
            self.step_index += 1
            self.root.after(self.interval, self.schedule_loading_steps)

    def load_main(self):
        self.root.destroy()
        open_login_window()  # das Login-Fenster



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
                    # Erstes Passwort setzen
                    new_pw = simpledialog.askstring("Neues Passwort", "Bitte neues Passwort eingeben:", show="*")
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

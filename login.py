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
        self.master.configure(bg=WHITE)
        self.master.attributes("-fullscreen", True)

        self.frame = tk.Frame(master, bg=WHITE, padx=20, pady=20)
        self.frame.pack(expand=True)

        tk.Label(self.frame, text="Willkommen bei SchulSystem", font=("Segoe UI", 16, "bold"),
                 bg=WHITE, fg=PRIMARY_BLUE).grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # Benutzername
        tk.Label(self.frame, text="Benutzername:", bg=WHITE, fg=TEXT_COLOR, font=("Segoe UI", 10))\
            .grid(row=1, column=0, sticky="e", pady=5, padx=(0, 10))
        self.entry_username = tk.Entry(self.frame, font=("Segoe UI", 10), bg="#f1f3f4",
                                       bd=0, relief="flat", width=30)
        self.entry_username.grid(row=1, column=1, pady=5, sticky="w")

        # Passwort
        tk.Label(self.frame, text="Passwort:", bg=WHITE, fg=TEXT_COLOR, font=("Segoe UI", 10))\
            .grid(row=2, column=0, sticky="e", pady=5, padx=(0, 10))

        self.password_container = tk.Frame(self.frame, bg=WHITE)
        self.password_container.grid(row=2, column=1, pady=5, sticky="w")

        self.entry_password = tk.Entry(self.password_container, show="·", font=("Segoe UI", 10),
                                       bg="#f1f3f4", bd=0, relief="flat", width=27)
        self.entry_password.pack(side="left", ipadx=5, ipady=3)

        self.eye_button = tk.Button(self.password_container, text="👁️", bg=WHITE, bd=0,
                                    font=("Segoe UI", 10), command=self.toggle_password_visibility)
        self.eye_button.pack(side="left", padx=5)

        # Login-Button
        self.login_btn = tk.Button(self.frame, text="Login", bg=PRIMARY_BLUE, fg="white",
                                   font=("Segoe UI", 10, "bold"), activebackground="#1669c1",
                                   activeforeground="white", command=self.login,
                                   relief="flat", padx=10, pady=5)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=20)

        #self.reset_pw_btn = tk.Button(self.frame, text="Passwort zurücksetzen", bg="#f44336", fg="white",
        #                              font=("Segoe UI", 10, "bold"), command=self.reset_password,
        #                              relief="flat", padx=10, pady=5)
        #self.reset_pw_btn.grid(row=4, column=0, columnspan=2, pady=(0, 20))

    def toggle_password_visibility(self):
        if self.entry_password.cget('show') == '':
            self.entry_password.config(show='·')
            self.eye_button.config(text="👁️")
        else:
            self.entry_password.config(show='')
            self.eye_button.config(text="🚫  ")



    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            with open("data/users.json", "r") as f:
                users = json.load(f)

            if username in users:
                if users[username]["password"] == "":
                    # Erster Login – Passwort setzen
                    new_pw = tk.simpledialog.askstring("Neues Passwort", "Bitte neues Passwort eingeben:", show="*")
                    if not new_pw:
                        messagebox.showerror("Fehler", "Passwort darf nicht leer sein.")
                        return
                    users[username]["password"] = new_pw
                    with open("data/users.json", "w") as f:
                        json.dump(users, f, indent=2)
                    messagebox.showinfo("Erfolg", "Passwort gesetzt. Du bist jetzt eingeloggt.")
                    self.master.destroy()
                    root = tk.Tk()
                    root.attributes("-fullscreen", True)
                    app = Dashboard(root, username, users[username])
                    root.mainloop()

                    return
                elif users[username]["password"] == password:
                    self.master.destroy()
                    root = tk.Tk()
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

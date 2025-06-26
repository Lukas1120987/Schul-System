import tkinter as tk
from tkinter import messagebox
import json
import os

USERS_PATH = "data/users.json"
SUPPORT_PATH = "data/support.json"
FEEDBACK_PATH = "data/feedback.json"
CONFIG_PATH = "data/config.json"



class Modul:
    def __init__(self, master, nutzername, nutzerdaten):
        self.master = master
        self.nutzername = nutzername
        self.nutzerdaten = nutzerdaten
        self.frame = tk.Frame(master)

        tk.Label(self.frame, text="🔧 Einstellungen", font=("Arial", 16, "bold")).pack(pady=10)

        self.add_userinfo_display()
        self.add_username_change()
        self.add_password_change()
        self.add_update()
        self.add_support_ticket()
        self.add_feedback_form()
        self.add_email_field()
        self.add_fullscreen_toggle()
        self.add_profile_reset()
        self.add_darkmode_toggle()
        self.add_account_delete()
        



    def get_frame(self):
        return self.frame

    def add_username_change(self):
        section = tk.LabelFrame(self.frame, text="Benutzernamen ändern")
        section.pack(padx=10, pady=5, fill="x")

        new_name_entry = tk.Entry(section)
        new_name_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        def update_username():
            new_name = new_name_entry.get().strip()
            if new_name:
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                users[new_name] = users.pop(self.nutzername)
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2)
                messagebox.showinfo("Erfolg", "Benutzername geändert – bitte neu einloggen.")
            else:
                messagebox.showwarning("Fehler", "Neuer Benutzername darf nicht leer sein.")

        tk.Button(section, text="Speichern", command=update_username).pack(side="right", padx=5, pady=5)

    def add_password_change(self):
        section = tk.LabelFrame(self.frame, text="Passwort ändern")
        section.pack(padx=10, pady=5, fill="x")

        new_pw_entry = tk.Entry(section, show="*")
        new_pw_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        def update_password():
            new_pw = new_pw_entry.get().strip()
            if new_pw:
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                users[self.nutzername]["password"] = new_pw
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2)
                messagebox.showinfo("Erfolg", "Passwort aktualisiert.")
            else:
                messagebox.showwarning("Fehler", "Neues Passwort darf nicht leer sein.")

        tk.Button(section, text="Speichern", command=update_password).pack(side="right", padx=5, pady=5)

    def add_support_ticket(self):
        section = tk.LabelFrame(self.frame, text="Support-Ticket erstellen")
        section.pack(padx=10, pady=5, fill="x")

        text = tk.Text(section, height=4)
        text.pack(padx=5, pady=5, fill="x")

        def send_ticket():
            content = text.get("1.0", "end").strip()
            if content:
                if not os.path.exists(SUPPORT_PATH):
                    with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
                        json.dump([], f)
                with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                    tickets = json.load(f)
                tickets.append({"user": self.nutzername, "content": content, "status": "offen"})
                with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
                    json.dump(tickets, f, indent=2)
                messagebox.showinfo("Erfolg", "Support-Ticket gesendet.")
                text.delete("1.0", "end")
            else:
                messagebox.showwarning("Fehler", "Ticket darf nicht leer sein.")

        tk.Button(section, text="Absenden", command=send_ticket).pack(padx=5, pady=5)

    def add_update(self):
        from updater import check_and_update
        
        section = tk.LabelFrame(self.frame, text="Auf Update überprüfen")
        section.pack(padx=10, pady=5, fill="x")

        tk.Button(section, text="Auf Update prüfen", command=check_and_update, fg="red").pack(padx=5, pady=5)

        

    def add_feedback_form(self):
        section = tk.LabelFrame(self.frame, text="Feedback geben")
        section.pack(padx=10, pady=5, fill="x")

        text = tk.Text(section, height=3)
        text.pack(padx=5, pady=5, fill="x")

        def send_feedback():
            feedback = text.get("1.0", "end").strip()
            if feedback:
                if not os.path.exists(FEEDBACK_PATH):
                    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
                        json.dump([], f)
                with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
                    feedbacks = json.load(f)
                feedbacks.append({"user": self.nutzername, "feedback": feedback})
                with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
                    json.dump(feedbacks, f, indent=2)
                messagebox.showinfo("Erfolg", "Feedback gesendet.")
                text.delete("1.0", "end")
            else:
                messagebox.showwarning("Fehler", "Feedback darf nicht leer sein.")

        tk.Button(section, text="Absenden", command=send_feedback).pack(padx=5, pady=5)


    def add_email_field(self):
        section = tk.LabelFrame(self.frame, text="E-Mail-Adresse für Passwort-Zurücksetzung")
        section.pack(padx=10, pady=5, fill="x")

        email_entry = tk.Entry(section)
        email_entry.insert(0, self.nutzerdaten.get("email", ""))
        email_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        def update_email():
            email = email_entry.get().strip()
            if "@" in email and "." in email:
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                users[self.nutzername]["email"] = email
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2)
                messagebox.showinfo("Erfolg", "E-Mail-Adresse gespeichert.")
                messagebox.showwarning("Hinweis", "Dies ist eine BETA-Funktion, welche zur Zeit nicht funktioniert.")
            else:
                messagebox.showwarning("Fehler", "Bitte eine gültige E-Mail-Adresse eingeben.")

        tk.Button(section, text="Speichern", command=update_email).pack(side="right", padx=5, pady=5)

    def add_fullscreen_toggle(self):
        section = tk.LabelFrame(self.frame, text="Vollbildmodus")
        section.pack(padx=10, pady=5, fill="x")

        var = tk.BooleanVar()
        current = False

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            current = config.get(self.nutzername, {}).get("vollbild", False)

        var.set(current)

        checkbox = tk.Checkbutton(section, text="Dashboard im Vollbild starten", variable=var)
        checkbox.pack(side="left", padx=5, pady=5)

        def save_fullscreen():
            # Konfig-Datei ggf. erstellen
            if not os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump({}, f)

            # Konfiguration laden
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Nutzerbereich setzen
            if self.nutzername not in config:
                config[self.nutzername] = {}

            config[self.nutzername]["vollbild"] = var.get()

            # Speichern
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            # Hinweis
            messagebox.showinfo("Neu laden", "Die Einstellung wurde gespeichert.\nDas Dashboard wird neu geladen.")

            # Fenster schließen
            self.frame.winfo_toplevel().destroy()

            # Dashboard starten
            from login import start
            start()

        tk.Button(section, text="Speichern", command=save_fullscreen).pack(side="right", padx=5, pady=5)

    def add_profile_reset(self):
        section = tk.LabelFrame(self.frame, text="Profil zurücksetzen")
        section.pack(padx=10, pady=5, fill="x")

        def reset_profile():
            if messagebox.askyesno("Zurücksetzen", "Willst du wirklich alle Einstellungen zurücksetzen?"):
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                if self.nutzername in users:
                    users[self.nutzername]["email"] = ""
                    users[self.nutzername]["password"] = ""
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2)

                if os.path.exists(CONFIG_PATH):
                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    config[self.nutzername] = {"vollbild": False}
                    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=2)

                messagebox.showinfo("Erfolg", "Profil wurde zurückgesetzt.\nBitte erneut einloggen.")
                messagebox.showerror("Wichtig", "Dein Passwort wurde zurückgesetzt! \n Um dich anzumelden, lass das Passwort-Feld leer.")

                self.frame.winfo_toplevel().destroy()
                from login import start
                start()

        tk.Button(section, text="Zurücksetzen", command=reset_profile, fg="red").pack(padx=5, pady=5)

    def add_darkmode_toggle(self):
        section = tk.LabelFrame(self.frame, text="Dark Mode")
        section.pack(padx=10, pady=5, fill="x")

        var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(section, text="Dark Mode aktivieren (Beta)", variable=var)
        checkbox.pack(side="left", padx=5, pady=5)

        def save_darkmode():
            # Optional: hier Konfiguration speichern für späteres UI-Styling
            messagebox.showinfo("Hinweis", "Dark Mode wird beim nächsten Start aktiviert (funktioniert bald).")

        tk.Button(section, text="Speichern", command=save_darkmode).pack(side="right", padx=5, pady=5)

    def add_account_delete(self):
        section = tk.LabelFrame(self.frame, text="Konto löschen")
        section.pack(padx=10, pady=5, fill="x")

        def delete_account():
            SCHÜTZEN = ["SchulSystem", "default_user1", "default_user2", "default_user3"]

            # Adminname aus config.json laden
            try:
                with open("data/config.json", "r", encoding="utf-8") as f:
                    admin_info = json.load(f)
                    admin_name = admin_info.get("admin_name", "")
            except FileNotFoundError:
                admin_name = ""

            if self.nutzername in SCHÜTZEN or self.nutzername == admin_name:
                messagebox.showwarning("Nicht erlaubt", "Dieses Konto kann nicht gelöscht werden.")
                return

            if messagebox.askyesno("Konto löschen", "Willst du dein Konto unwiderruflich löschen?"):
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)

                if self.nutzername in users:
                    users.pop(self.nutzername)

                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2)

                messagebox.showinfo("Gelöscht", "Dein Konto wurde gelöscht.")
                self.frame.winfo_toplevel().destroy()

                from login import start
                start()


        tk.Button(section, text="Konto löschen", command=delete_account, fg="red").pack(padx=5, pady=5)

    def add_userinfo_display(self):
        info = f"👤 Angemeldet als: {self.nutzername} | Gruppe: {self.nutzerdaten.get('group')} | Sekundär/Klasse: {self.nutzerdaten.get('second_group')}"
        tk.Label(self.frame, text=info, font=("Arial", 10), fg="gray").pack(pady=(5, 0))

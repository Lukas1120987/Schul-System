import tkinter as tk
from tkinter import messagebox
import json
import os

#USERS_PATH = "data/users.json"
#SUPPORT_PATH = "data/support.json"
#FEEDBACK_PATH = "data/feedback.json"
#CONFIG_PATH = "data/config.json"
from ordner import get_data_path

CONFIG_PATH = os.path.join(get_data_path(), "data/config.json")
USERS_PATH = os.path.join(get_data_path(), "data/users.json")
SUPPORT_PATH = os.path.join(get_data_path(), "data/support.json")
FEEDBACK_PATH = os.path.join(get_data_path(), "data/feedback.json")
SYSTEM_PATH = os.path.join(get_data_path(), "data/system_info.json")



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
        self.add_version_display()
        self.add_system_info()



    def get_frame(self):
        return self.frame

    def add_username_change(self):
        section = tk.LabelFrame(self.frame, text="Benutzernamen ändern")
        section.pack(padx=10, pady=5, fill="x")

        new_name_entry = tk.Entry(section)
        new_name_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        # Platzhalter setzen
        def set_placeholder(entry, placeholder, color="grey", normal_color="black"):
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=normal_color)

            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=color)

            entry.insert(0, placeholder)
            entry.config(fg=color)
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        set_placeholder(new_name_entry, "Neuer Benutzername...")

        def update_username():
            new_name = new_name_entry.get().strip()
            if new_name and new_name != "Neuer Benutzername...":
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

        new_pw_entry = tk.Entry(section)
        new_pw_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        def set_password_placeholder(entry, placeholder, color="grey", normal_color="black"):
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=normal_color, show="*")

            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=color, show="")

            entry.insert(0, placeholder)
            entry.config(fg=color, show="")
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        # Aufruf der Funktion für das Passwortfeld
        set_password_placeholder(new_pw_entry, "Neues Passwort...")

        def update_password():
            new_pw = new_pw_entry.get().strip()
            if new_pw and new_pw != "Neues Passwort...":
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
        section = tk.LabelFrame(self.frame, text="Support-Tickets")
        section.pack(padx=10, pady=5, fill="x")

        # Neues Ticket
        tk.Label(section, text="Neues Ticket:").pack(anchor="w", padx=5)
        new_text = tk.Text(section, height=3)
        new_text.pack(padx=5, pady=(0, 5), fill="x")

        def send_ticket():
            content = new_text.get("1.0", "end").strip()
            if content:
                if not os.path.exists(SUPPORT_PATH):
                    with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
                        json.dump([], f)
                with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                    tickets = json.load(f)
                tickets.append({
                    "user": self.nutzername,
                    "content": content,
                    "status": "offen"
                })
                with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
                    json.dump(tickets, f, indent=2)
                messagebox.showinfo("Erfolg", "Support-Ticket gesendet.")
                new_text.delete("1.0", "end")
                update_ticket_list()
            else:
                messagebox.showwarning("Fehler", "Ticket darf nicht leer sein.")

        # Zentriert platzierter Button
        button_frame = tk.Frame(section)
        button_frame.pack(pady=(0, 5))
        tk.Button(button_frame, text="Absenden", command=send_ticket).pack()

        # Ticket-Verlauf (wird erst sichtbar bei vorhandenen Tickets)
        ticket_frame = tk.Frame(section)

        ticket_scrollbar = tk.Scrollbar(ticket_frame)
        ticket_listbox = tk.Listbox(ticket_frame, height=1, yscrollcommand=ticket_scrollbar.set)
        ticket_scrollbar.config(command=ticket_listbox.yview)

        ticket_text_display = tk.Text(ticket_frame, height=5, state="disabled")

        def update_ticket_list():
            if not os.path.exists(SUPPORT_PATH):
                ticket_frame.pack_forget()
                return
            with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                tickets = json.load(f)
            user_tickets = [t for t in tickets if t["user"] == self.nutzername]

            if not user_tickets:
                ticket_frame.pack_forget()
                return

            ticket_listbox.delete(0, tk.END)
            for i, ticket in enumerate(user_tickets):
                short = ticket["content"][:50].replace("\n", " ") + ("..." if len(ticket["content"]) > 50 else "")
                ticket_listbox.insert(tk.END, f"{i+1}. ({ticket['status']}) {short}")

            visible_lines = min(len(user_tickets), 7)
            ticket_listbox.config(height=visible_lines)


            # Ticketframe anzeigen, falls es Tickets gibt
            ticket_scrollbar.pack(side="right", fill="y")
            ticket_frame.pack(padx=5, pady=(0, 5), fill="x")
            


        def show_ticket_details(event):
            selection = ticket_listbox.curselection()
            if selection:
                index = selection[0]
                with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                    tickets = json.load(f)
                user_tickets = [t for t in tickets if t["user"] == self.nutzername]
                ticket = user_tickets[index]
                ticket_text_display.config(state="normal")
                ticket_text_display.delete("1.0", tk.END)
                ticket_text_display.insert("1.0", f"Inhalt:\n{ticket['content']}\n\nStatus: {ticket['status']}")
                ticket_text_display.config(state="disabled")
                ticket_text_display.pack(padx=5, pady=(5, 0), fill="x")

        # Widgets ins Ticket-Frame
        tk.Label(ticket_frame, text="Deine bisherigen Tickets:").pack(anchor="w")
        ticket_listbox.pack(fill="x", padx=0)
        ticket_listbox.bind("<<ListboxSelect>>", show_ticket_details)

        update_ticket_list()


    def add_update(self):
        # JSON-Dateipfad
        config_path = os.path.join("data", "config.json")
        
        section = tk.LabelFrame(self.frame, text="Auf Update überprüfen")
        section.pack(padx=10, pady=5, fill="x")

        def check_versions():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                local_version = config.get("local_version", "")
                latest_version = config.get("latest_github_version", "")
                
                if local_version != latest_version:
                    messagebox.showinfo("Update", "Es wird ein Update gemacht...")
                    from updater import check_and_update
                    check_and_update()
                else:
                    messagebox.showinfo("Update", f"Es gibt nichts Neues. Die aktuelle Version ist: {latest_version}.")
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Datei {config_path} nicht gefunden.")
            except json.JSONDecodeError:
                messagebox.showerror("Fehler", "Fehler beim Lesen der JSON-Datei.")

        tk.Button(section, text="Auf Update prüfen", command=check_versions, fg="black").pack(padx=5, pady=5)

        

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


    def add_version_display(self):
        import os
        import json
        import tkinter as tk
        from tkinter import messagebox

        config_path = os.path.join("data", "config.json")
        
        section = tk.LabelFrame(self.frame, text="")
        section.pack(padx=10, pady=5, fill="x")

        local_version = "Unbekannt"  # 

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                local_version = config.get("local_version", "Nicht angegeben")
        except FileNotFoundError:
            messagebox.showerror("Fehler", "Die Datei 'config.json' wurde nicht gefunden.")
        except json.JSONDecodeError:
            messagebox.showerror("Fehler", "Die Datei 'config.json' enthält ungültiges JSON.")

        version_text = f"  Version:\n    {local_version}"
        tk.Label(section, text=version_text, font=("Arial", 10), fg="gray", justify="center").pack(pady=(5, 0), anchor="center")

        
    def add_system_info(self):
        section = tk.LabelFrame(self.frame, text="")
        section.pack(padx=10, pady=5, fill="x")

        try:
            with open(SYSTEM_PATH, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        local_version = config.get("local_version", "Nicht angegeben")
        except FileNotFoundError:
                    messagebox.showerror(f"Fehler", "Die Datei {SYSTEM_PATH} wurde nicht gefunden.")
        except json.JSONDecodeError:
                    messagebox.showerror("Fehler", "Die Datei {SYSTEM_PATH} enthält ungültiges JSON.")

        version_text = f"  System-ID:\n    {local_version}"
        tk.Label(section, text=version_text, font=("Arial", 10), fg="gray", justify="center").pack(pady=(5, 0), anchor="center")


import os
import json
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from ordner import get_data_path

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(get_data_path(), "data/config.json")
USERS_PATH = os.path.join(get_data_path(), "data/users.json")
SUPPORT_PATH = os.path.join(get_data_path(), "data/support.json")
FEEDBACK_PATH = os.path.join(get_data_path(), "data/feedback.json")
SYSTEM_PATH = os.path.join(get_data_path(), "data/system_info.json")


class Modul:
    def __init__(self, master, nutzername, nutzerdaten):
        # master is expected to be a CTk root or CTkFrame
        self.master = master
        self.nutzername = nutzername
        self.nutzerdaten = nutzerdaten

        # container is a CTkFrame that will hold a scrollable tk.Canvas
        self.container = ctk.CTkFrame(master)

        # Header
        header = ctk.CTkLabel(self.container, text="🔧 Einstellungen", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(pady=10)

        # Create a scrollable area using a tk.Canvas (works well with CTk widgets inside a tk.Frame)
        self._create_scrollable_area()

        # All sections will be added to self.scrollable_frame (a tk.Frame)
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

    def _create_scrollable_area(self):
        # outer frame inside the CTk container
        outer = ctk.CTkFrame(self.container)
        outer.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Canvas + vertical scrollbar
        self.canvas = tk.Canvas(outer, bd=0, highlightthickness=0)
        self.v_scroll = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Inner frame that will contain the real widgets
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Make the inner frame resize with canvas width
        def _on_frame_configure(event):
            # update scrollregion
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        def _on_canvas_configure(event):
            # adjust inner window's width to canvas width
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)

        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        # mousewheel support (Windows/Mac/Linux)
        def _on_mousewheel(event):
            if os.name == 'nt':
                delta = -1 * int(event.delta / 120)
            else:
                delta = -1 * int(event.delta)
            self.canvas.yview_scroll(delta, "units")

        # Bindings for wheel on the canvas and its children
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def get_frame(self):
        return self.container

    # --- Sections (add widgets to self.scrollable_frame) ---
    def add_username_change(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="Benutzernamen ändern", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        new_name_entry = ctk.CTkEntry(section)
        new_name_entry.pack(side="left", padx=8, pady=8, expand=True, fill="x")

        def set_placeholder(entry, placeholder):
            entry.insert(0, placeholder)
            # CTkEntry does not have native placeholder until newer versions, so this simple approach
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        set_placeholder(new_name_entry, "Neuer Benutzername...")

        def update_username():
            new_name = new_name_entry.get().strip()
            if new_name and new_name != "Neuer Benutzername...":
                try:
                    with open(USERS_PATH, "r", encoding="utf-8") as f:
                        users = json.load(f)
                    users[new_name] = users.pop(self.nutzername)
                    with open(USERS_PATH, "w", encoding="utf-8") as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)
                    messagebox.showinfo("Erfolg", "Benutzername geändert – bitte neu einloggen.")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
            else:
                messagebox.showwarning("Fehler", "Neuer Benutzername darf nicht leer sein.")

        save_btn = ctk.CTkButton(section, text="Speichern", command=update_username)
        save_btn.pack(side="right", padx=8, pady=8)

    def add_password_change(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="Passwort ändern", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        new_pw_entry = ctk.CTkEntry(section, show="*")
        new_pw_entry.pack(side="left", padx=8, pady=8, expand=True, fill="x")

        def update_password():
            new_pw = new_pw_entry.get().strip()
            if new_pw:
                try:
                    with open(USERS_PATH, "r", encoding="utf-8") as f:
                        users = json.load(f)
                    users[self.nutzername]["password"] = new_pw
                    with open(USERS_PATH, "w", encoding="utf-8") as f:
                        json.dump(users, f, indent=2, ensure_ascii=False)
                    messagebox.showinfo("Erfolg", "Passwort aktualisiert.")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
            else:
                messagebox.showwarning("Fehler", "Neues Passwort darf nicht leer sein.")

        save_btn = ctk.CTkButton(section, text="Speichern", command=update_password)
        save_btn.pack(side="right", padx=8, pady=8)

    def add_support_ticket(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="Support-Tickets", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        tk.Label(section, text="Neues Ticket:").pack(anchor="w", padx=8)
        new_text = tk.Text(section, height=3)
        new_text.pack(padx=8, pady=(0, 5), fill="x")

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
                    json.dump(tickets, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Erfolg", "Support-Ticket gesendet.")
                new_text.delete("1.0", "end")
                update_ticket_list()
            else:
                messagebox.showwarning("Fehler", "Ticket darf nicht leer sein.")

        ctk.CTkButton(section, text="Absenden", command=send_ticket).pack(pady=(0,5))

        # Ticket-Liste mit eigenem Scrollbar (falls viele Tickets vorhanden)
        ticket_container = tk.Frame(section)
        ticket_container.pack(fill="x", padx=8, pady=(4,8))

        ticket_scrollbar = tk.Scrollbar(ticket_container, orient="vertical")
        ticket_listbox = tk.Listbox(ticket_container, height=4, yscrollcommand=ticket_scrollbar.set)
        ticket_scrollbar.config(command=ticket_listbox.yview)

        ticket_scrollbar.pack(side="right", fill="y")
        ticket_listbox.pack(side="left", fill="both", expand=True)

        ticket_text_display = tk.Text(section, height=6, state="disabled")

        def update_ticket_list():
            if not os.path.exists(SUPPORT_PATH):
                ticket_container.pack_forget()
                return
            with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                tickets = json.load(f)
            user_tickets = [t for t in tickets if t["user"] == self.nutzername]

            if not user_tickets:
                ticket_container.pack_forget()
                ticket_text_display.pack_forget()
                return

            ticket_listbox.delete(0, tk.END)
            for i, ticket in enumerate(user_tickets):
                short = ticket["content"][:50].replace("\n", " ") + ("..." if len(ticket["content"]) > 50 else "")
                ticket_listbox.insert(tk.END, f"{i+1}. ({ticket['status']}) {short}")

            visible_lines = min(len(user_tickets), 7)
            ticket_listbox.config(height=visible_lines)

            ticket_container.pack(fill="x", padx=8, pady=(4,8))

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
                ticket_text_display.pack(padx=8, pady=(4,0), fill="x")

        ticket_listbox.bind("<<ListboxSelect>>", show_ticket_details)

        # initial load
        update_ticket_list()

    def add_update(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="Auf Update überprüfen", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        def check_versions():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
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
                messagebox.showerror("Fehler", f"Datei {CONFIG_PATH} nicht gefunden.")
            except json.JSONDecodeError:
                messagebox.showerror("Fehler", "Fehler beim Lesen der JSON-Datei.")

        ctk.CTkButton(section, text="Auf Update prüfen", command=check_versions).pack(padx=8, pady=8)

    def add_feedback_form(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="Feedback geben", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        text = tk.Text(section, height=3)
        text.pack(padx=8, pady=8, fill="x")

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
                    json.dump(feedbacks, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Erfolg", "Feedback gesendet.")
                text.delete("1.0", "end")
            else:
                messagebox.showwarning("Fehler", "Feedback darf nicht leer sein.")

        ctk.CTkButton(section, text="Absenden", command=send_feedback).pack(padx=8, pady=(0,8))

    def add_email_field(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="E-Mail-Adresse für Passwort-Zurücksetzung", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        email_entry = ctk.CTkEntry(section)
        email_entry.insert(0, self.nutzerdaten.get("email", ""))
        email_entry.pack(side="left", padx=8, pady=8, expand=True, fill="x")

        def update_email():
            email = email_entry.get().strip()
            if "@" in email and "." in email:
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                users[self.nutzername]["email"] = email
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Erfolg", "E-Mail-Adresse gespeichert.")
                messagebox.showwarning("Hinweis", "Dies ist eine BETA-Funktion, welche zur Zeit nicht funktioniert.")
            else:
                messagebox.showwarning("Fehler", "Bitte eine gültige E-Mail-Adresse eingeben.")

        ctk.CTkButton(section, text="Speichern", command=update_email).pack(side="right", padx=8, pady=8)

    def add_fullscreen_toggle(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        label = ctk.CTkLabel(section, text="Vollbildmodus", anchor="w")
        label.pack(padx=8, pady=(8,4), anchor="w")

        var = tk.BooleanVar()
        current = False

        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            current = config.get(self.nutzername, {}).get("vollbild", False)

        var.set(current)

        checkbox = ctk.CTkCheckBox(section, text="Dashboard im Vollbild starten", variable=var)
        checkbox.pack(side="left", padx=8, pady=8)

        def save_fullscreen():
            if not os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump({}, f)
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            if self.nutzername not in config:
                config[self.nutzername] = {}
            config[self.nutzername]["vollbild"] = var.get()
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Neu laden", "Die Einstellung wurde gespeichert.\nDas Dashboard wird neu geladen.")
            self.container.winfo_toplevel().destroy()
            from login import start
            start()

        ctk.CTkButton(section, text="Speichern", command=save_fullscreen).pack(side="right", padx=8, pady=8)

    def add_profile_reset(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        def reset_profile():
            if messagebox.askyesno("Zurücksetzen", "Willst du wirklich alle Einstellungen zurücksetzen?"):
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                if self.nutzername in users:
                    users[self.nutzername]["email"] = ""
                    users[self.nutzername]["password"] = ""
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2, ensure_ascii=False)

                if os.path.exists(CONFIG_PATH):
                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    config[self.nutzername] = {"vollbild": False}
                    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Erfolg", "Profil wurde zurückgesetzt.\nBitte erneut einloggen.")
                messagebox.showerror("Wichtig", "Dein Passwort wurde zurückgesetzt! \n Um dich anzumelden, lass das Passwort-Feld leer.")
                self.container.winfo_toplevel().destroy()
                from login import start
                start()

        ctk.CTkButton(section, text="Zurücksetzen", fg_color="#b30000", hover_color="#cc0000", command=reset_profile).pack(padx=8, pady=8)

    def add_darkmode_toggle(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        var = tk.BooleanVar(value=(ctk.get_appearance_mode() == "Dark"))
        checkbox = ctk.CTkCheckBox(section, text="Dark Mode aktivieren (Beta)", variable=var)
        checkbox.pack(side="left", padx=8, pady=8)

        def save_darkmode():
            ctk.set_appearance_mode("Dark" if var.get() else "Light")
            messagebox.showinfo("Hinweis", "Dark Mode wurde gewechselt (temporär).")

        ctk.CTkButton(section, text="Speichern", command=save_darkmode).pack(side="right", padx=8, pady=8)

    def add_account_delete(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        def delete_account():
            SCHUETZEN = ["SchulSystem", "default_user1", "default_user2", "default_user3"]
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    admin_info = json.load(f)
                    admin_name = admin_info.get("admin_name", "")
            except Exception:
                admin_name = ""

            if self.nutzername in SCHUETZEN or self.nutzername == admin_name:
                messagebox.showwarning("Nicht erlaubt", "Dieses Konto kann nicht gelöscht werden.")
                return

            if messagebox.askyesno("Konto löschen", "Willst du dein Konto unwiderruflich löschen?"):
                with open(USERS_PATH, "r", encoding="utf-8") as f:
                    users = json.load(f)
                if self.nutzername in users:
                    users.pop(self.nutzername)
                with open(USERS_PATH, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Gelöscht", "Dein Konto wurde gelöscht.")
                self.container.winfo_toplevel().destroy()
                from login import start
                start()

        ctk.CTkButton(section, text="Konto löschen", fg_color="#b30000", hover_color="#cc0000", command=delete_account).pack(padx=8, pady=8)

    def add_userinfo_display(self):
        info = f"👤 Angemeldet als: {self.nutzername} | Gruppe: {self.nutzerdaten.get('group')} | Sekundär/Klasse: {self.nutzerdaten.get('second_group')}"
        ctk.CTkLabel(self.scrollable_frame, text=info, text_color="#6b6b6b").pack(pady=(0,6), padx=10)

    def add_version_display(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        local_version = "Unbekannt"
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                local_version = config.get("local_version", "Nicht angegeben")
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass

        version_text = f"Version:\n{local_version}"
        ctk.CTkLabel(section, text=version_text, anchor="center").pack(pady=8)

    def add_system_info(self):
        section = ctk.CTkFrame(self.scrollable_frame, corner_radius=6)
        section.pack(padx=10, pady=8, fill="x")

        ctk.CTkLabel(section, text="System-Infos:", anchor="w").pack(padx=8, pady=(6,2), anchor="w")

        try:
            with open(SYSTEM_PATH, "r", encoding="utf-8") as f:
                system_data = json.load(f)
        except Exception:
            system_data = {}

        info_text = json.dumps(system_data, indent=2, ensure_ascii=False)
        text_display = tk.Text(section, height=6, wrap="none")
        text_display.insert("1.0", info_text)
        text_display.config(state="disabled")
        text_display.pack(fill="x", padx=8, pady=(0,6))

        def copy_system_info():
            self.container.clipboard_clear()
            self.container.clipboard_append(info_text)
            messagebox.showinfo("Kopiert", "System-Infos wurden in die Zwischenablage kopiert.")

        ctk.CTkButton(section, text="In Zwischenablage kopieren", command=copy_system_info).pack(padx=8, pady=(0,8))


# --- Kurzes Test-Layout (nur ausführen, wenn Datei direkt gestarted wird) ---
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("700x700")
    # Dummy paths for testing if ordner.get_data_path not present
    try:
        test_user = "default_user1"
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            users = json.load(f)
        data = users.get(test_user, {"group": "Lehrer", "second_group": "Musterklasse"})
    except Exception:
        data = {"group": "Lehrer", "second_group": "Musterklasse"}
    modul = Modul(root, test_user, data)
    modul.get_frame().pack(fill="both", expand=True)
    root.mainloop()

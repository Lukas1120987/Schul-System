import tkinter as tk
from tkinter import messagebox
import json
import os

#STANDARDGRUPPEN = ["Schüler", "Lehrer", "Verwaltung"]
STANDARDGRUPPEN = ["Schüler", "Lehrer", "Verwaltung", "SchulSystem-Team"]
USER_JSON_PATH = "data/users.json"


class Modul:
    def __init__(self, master, username, user_data):
        self.master = master
        self.frame = tk.Frame(master, bg="white")

        #self.ensure_default_groups()

        tk.Label(self.frame, text="⚙️ Adminbereich", font=("Arial", 16), bg="white").pack(pady=10)

        tk.Button(self.frame, text="📋 Schnell Benutzer erstellen", bg="#e0e0e0", command=self.open_quick_create_window).pack(pady=(0, 10))

        tk.Button(self.frame, text="👥 Alle Nutzer anzeigen", bg="#e0e0e0", command=self.open_user_list_window).pack(pady=(0, 10))

        tk.Label(self.frame, text="👤 Neuen Benutzer anlegen", font=("Arial", 12, "bold"), bg="white").pack(pady=5)
        tk.Label(self.frame, text="Benutzername", bg="white").pack()
        self.user_entry = tk.Entry(self.frame)
        self.user_entry.pack()

        tk.Label(self.frame, text="Passwort", bg="white").pack()
        self.pass_entry = tk.Entry(self.frame, show="*")
        self.pass_entry.pack()

        tk.Label(self.frame, text="Gruppe auswählen", bg="white").pack()
        self.group_var = tk.StringVar()
        self.group_dropdown = tk.OptionMenu(self.frame, self.group_var, "")
        self.group_dropdown.config(width=20)
        self.group_dropdown.pack()

        tk.Label(self.frame, text="Zweite Gruppe (Klasse)", bg="white").pack()
        self.group2_var = tk.StringVar()
        self.group2_dropdown = tk.OptionMenu(self.frame, self.group2_var, "")
        self.group2_dropdown.config(width=20)
        self.group2_dropdown.pack()


        tk.Button(self.frame, text="Benutzer erstellen", command=self.create_user).pack(pady=5)

        tk.Label(self.frame, text="🔐 Passwort eines Benutzers ändern", font=("Arial", 12, "bold"), bg="white").pack(pady=10)
        tk.Label(self.frame, text="Benutzername", bg="white").pack()
        self.user_change = tk.Entry(self.frame)
        self.user_change.pack()

        tk.Label(self.frame, text="Neues Passwort", bg="white").pack()
        self.pass_change = tk.Entry(self.frame, show="*")
        self.pass_change.pack()

        tk.Button(self.frame, text="Passwort ändern", command=self.change_password).pack(pady=5)

        tk.Label(self.frame, text="🏫 Gruppen verwalten", font=("Arial", 12, "bold"), bg="white").pack(pady=10)

        group_list_frame = tk.Frame(self.frame, bg="white")
        group_list_frame.pack()

        self.group_list = tk.Listbox(group_list_frame, width=30, height=5)
        self.group_list.pack(side=tk.LEFT)

        scrollbar = tk.Scrollbar(group_list_frame, command=self.group_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_list.config(yscrollcommand=scrollbar.set)

        tk.Button(self.frame, text="Gruppe löschen", command=self.delete_group).pack(pady=5)

        tk.Label(self.frame, text="Neue Gruppe erstellen:", bg="white").pack()
        self.new_group_entry = tk.Entry(self.frame)
        self.new_group_entry.pack()
        tk.Button(self.frame, text="Gruppe hinzufügen", command=self.create_group).pack(pady=5)

        self.refresh_group_list()

    def get_frame(self):
        return self.frame

    def ensure_default_groups(self):
        users = self.load_users()
        changed = False
        for group in STANDARDGRUPPEN:
            dummy_name = f"{group}"
            if dummy_name not in users:
                users[dummy_name] = {"password": "", "group": group, "is_admin": False}
                changed = True
        if changed:
            self.save_users(users)

    def create_user(self):
        user = self.user_entry.get().strip()
        pw = self.pass_entry.get().strip()
        group = self.group_var.get().strip()
        group2 = self.group2_var.get().strip()

        if not user or not pw or not group:
            messagebox.showerror("Fehler", "Benutzername, Passwort und Gruppe müssen angegeben werden.")
            return

        users = self.load_users()

        if user in users:
            messagebox.showerror("Fehler", "Benutzer existiert bereits.")
            return

        users[user] = {
            "password": pw,
            "group": group,
            "second_group": group2 if group2 else None,
            "is_admin": False
        }
        self.save_users(users)

        messagebox.showinfo("Erfolg", f"Benutzer '{user}' wurde angelegt.")
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.group_var.set("")
        self.group2_var.set("")
        self.refresh_group_list()
        self.user_entry.focus_set()


    def change_password(self):
        user = self.user_change.get().strip()
        new_pw = self.pass_change.get().strip()

        if not user or not new_pw:
            messagebox.showerror("Fehler", "Benutzer und Passwort eingeben.")
            return

        users = self.load_users()

        if user not in users:
            messagebox.showerror("Fehler", "Benutzer nicht gefunden.")
            return

        users[user]["password"] = new_pw
        self.save_users(users)

        messagebox.showinfo("Erfolg", f"Passwort für '{user}' geändert.")
        self.user_change.delete(0, tk.END)
        self.pass_change.delete(0, tk.END)

    def create_group(self):
        new_group = self.new_group_entry.get().strip()
        if not new_group:
            messagebox.showerror("Fehler", "Gruppenname darf nicht leer sein.")
            return

        users = self.load_users()
        dummy_name = f"_group_{new_group}"
        if dummy_name in users:
            messagebox.showerror("Fehler", "Gruppe existiert bereits.")
            return

        users[dummy_name] = {"password": "", "group": new_group, "is_admin": False}
        self.save_users(users)

        messagebox.showinfo("Erfolg", f"Gruppe '{new_group}' wurde erstellt.")
        self.new_group_entry.delete(0, tk.END)
        self.refresh_group_list()

    def delete_group(self):
        selected = self.group_list.curselection()
        if not selected:
            messagebox.showerror("Fehler", "Bitte eine Gruppe auswählen.")
            return

        group_to_delete = self.group_list.get(selected[0])

        if group_to_delete in STANDARDGRUPPEN:
            messagebox.showwarning("Nicht erlaubt", f"Die Gruppe '{group_to_delete}' ist geschützt und kann nicht gelöscht werden.")
            return

        confirm = messagebox.askyesno("Bestätigung", f"Möchtest du die Gruppe '{group_to_delete}' wirklich löschen?\nAlle zugehörigen Benutzer werden entfernt?")
        if not confirm:
            return

        users = self.load_users()
        users = {user: data for user, data in users.items() if data["group"] != group_to_delete}
        self.save_users(users)

        messagebox.showinfo("Erfolg", f"Gruppe '{group_to_delete}' und alle zugehörigen Benutzer wurden gelöscht.")
        self.refresh_group_list()

    def refresh_group_list(self):
        self.group_list.delete(0, tk.END)
        users = self.load_users()

        groups = sorted(set(u["group"] for u in users.values()))
        for group in groups:
            self.group_list.insert(tk.END, group)

        menu = self.group_dropdown["menu"]
        menu.delete(0, "end")
        for group in groups:
            menu.add_command(label=group, command=lambda g=group: self.group_var.set(g))
        if groups:
            self.group_var.set(groups[0])
        else:
            self.group_var.set("")

        menu2 = self.group2_dropdown["menu"]
        menu2.delete(0, "end")
        for group in groups:
            menu2.add_command(label=group, command=lambda g=group: self.group2_var.set(g))
        self.group2_var.set("")


    def load_users(self):
        if not os.path.exists(USER_JSON_PATH):
            return {}
        with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self, users):
        os.makedirs(os.path.dirname(USER_JSON_PATH), exist_ok=True)
        with open(USER_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

    def open_quick_create_window(self):
        win = tk.Toplevel(self.master)
        win.title("Schnell Benutzer erstellen")
        win.geometry("300x350")
        win.configure(bg="white")

        tk.Label(win, text="Benutzername", bg="white").pack(pady=(10, 0))
        user_entry = tk.Entry(win)
        user_entry.pack()

        tk.Label(win, text="Gruppe", bg="white").pack()
        group_var = tk.StringVar()
        group_dropdown = tk.OptionMenu(win, group_var, *self.get_all_groups())
        group_dropdown.pack()

        tk.Label(win, text="Zweite Gruppe (optional)", bg="white").pack()
        group2_var = tk.StringVar()
        group2_dropdown = tk.OptionMenu(win, group2_var, *self.get_all_groups())
        group2_dropdown.pack()

        def create():
            user = user_entry.get().strip()
            group = group_var.get().strip()
            group2 = group2_var.get().strip()

            if not user or not group:
                messagebox.showerror("Fehler", "Benutzername und Gruppe erforderlich.", parent=win)
                return

            users = self.load_users()
            if user in users:
                messagebox.showerror("Fehler", "Benutzer existiert bereits.", parent=win)
                return

            users[user] = {
                "password": "", 
                "group": group, 
                "second_group": group2 if group2 else None, 
                "is_admin": False
            }
            self.save_users(users)

            messagebox.showinfo("Erfolg", f"Benutzer '{user}' erstellt. Passwort wird beim ersten Login gesetzt.", parent=win)
            user_entry.delete(0, tk.END)
            user_entry.focus_set()

        tk.Button(win, text="Erstellen", command=create).pack(pady=10)


    def get_all_groups(self):
        users = self.load_users()
        return sorted(set(u["group"] for u in users.values()))

    def open_user_list_window(self):
        users = self.load_users()
        user_list = [user for user in users.keys() if not user.startswith("_group_")]

        win = tk.Toplevel(self.master)
        win.title("Alle Nutzer")
        win.geometry("400x300")
        win.configure(bg="white")

        tk.Label(win, text="👥 Nutzerübersicht", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        listbox = tk.Listbox(win, width=40)
        listbox.pack(pady=5, expand=True, fill=tk.BOTH)

        user_map = {}

        for user in user_list:
            info = users[user]
            display_text = f"{user} — {info.get('group', '')} | {info.get('second_group', '')}"
            listbox.insert(tk.END, display_text)
            user_map[display_text] = user

        def on_select(event):
            selection = listbox.curselection()
            if not selection:
                return
            display = listbox.get(selection[0])
            username = user_map[display]
            self.edit_user_window(username)

        listbox.bind("<<ListboxSelect>>", on_select)

    def edit_user_window(self, username):
        users = self.load_users()
        user_data = users.get(username)
        if not user_data:
            messagebox.showerror("Fehler", "Benutzer nicht gefunden.")
            return

        win = tk.Toplevel(self.master)
        win.title(f"Benutzer bearbeiten: {username}")
        win.geometry("300x250")
        win.configure(bg="white")

        tk.Label(win, text=f"Benutzer: {username}", font=("Arial", 12, "bold"), bg="white").pack(pady=10)

        tk.Label(win, text="Gruppe", bg="white").pack()
        group_var = tk.StringVar(value=user_data.get("group", ""))
        group_dropdown = tk.OptionMenu(win, group_var, *self.get_all_groups())
        group_dropdown.pack()

        tk.Label(win, text="Zweite Gruppe", bg="white").pack()
        group2_var = tk.StringVar(value=user_data.get("second_group", ""))
        group2_dropdown = tk.OptionMenu(win, group2_var, *self.get_all_groups())
        group2_dropdown.pack()

        def save_changes():
            users[username]["group"] = group_var.get().strip()
            users[username]["second_group"] = group2_var.get().strip()
            self.save_users(users)
            messagebox.showinfo("Erfolg", "Änderungen gespeichert.", parent=win)
            win.destroy()

        tk.Button(win, text="Speichern", command=save_changes).pack(pady=10)

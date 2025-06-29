import tkinter as tk

from tkinter import messagebox

from tkinter import ttk
import importlib
import os
import json
from PIL import Image, ImageTk

CONFIG_PATH = "data/config.json"

class Dashboard:
    def __init__(self, master, username, user_data):
        self.master = master
        self.username = username
        self.user_data = user_data

        # --- Konfigurationsdatei laden oder erstellen ---
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f)

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        user_config = config.get(self.username, {})

        # --- Fenstergröße anpassen je nach Einstellung ---
        if user_config.get("vollbild", False):
            self.master.attributes('-fullscreen', True)
        else:
            self.master.geometry(f"{self.master.winfo_screenwidth()}x{self.master.winfo_screenheight()}")
            self.master.attributes('-fullscreen', False)

        self.master.title("SchulSystem – Dashboard")
        self.master.minsize(800, 500)

        self.username = username
        self.user_data = user_data

        self.sidebar_bg = "#1e272e"           # Dunkles Grau-Blau
        self.sidebar_hover = "#485460"        # Etwas heller bei Hover
        self.button_fg = "#ecf0f1"            # Helles Grau
        self.content_bg = "#f8f9fa"           # Sanft helles Hauptfeld

        self.button_hover_bg = "#3498db"
        self.content_bg = "#ecf0f1"

        # --- Sidebar mit Scrollfunktion ---
        self.sidebar_canvas = tk.Canvas(master, bg=self.sidebar_bg, width=220, highlightthickness=0)
        self.sidebar_canvas.pack(side="left", fill="y")

        self.sidebar_scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar_scrollbar.place(x=220, rely=0, relheight=1)  # scrollbar rechts neben canvas

        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)

        # Inhalt der Sidebar als Frame im Canvas
        self.sidebar_frame = tk.Frame(self.sidebar_canvas, bg=self.sidebar_bg)
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar_frame, anchor="nw")

        # Automatisches Scrollregion-Update
        def update_scroll_region(event=None):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

        self.sidebar_frame.bind("<Configure>", update_scroll_region)

        # Mausrad-Unterstützung
        def on_mousewheel(event):
            self.sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.sidebar_canvas.bind_all("<MouseWheel>", on_mousewheel)  # für Windows
        self.sidebar_canvas.bind_all("<Button-4>", lambda e: self.sidebar_canvas.yview_scroll(-1, "units"))  # Linux scroll up
        self.sidebar_canvas.bind_all("<Button-5>", lambda e: self.sidebar_canvas.yview_scroll(1, "units"))   # Linux scroll down

        # Endgültige Zuweisung für weitere Widgets
        self.sidebar = self.sidebar_frame  # damit add_user_info etc. weiter funktionieren

        self.content = tk.Frame(master, bg=self.content_bg)
        self.content.pack(side="right", fill="both", expand=True)

        self.current_frame = None

        self.check_unread_notifications()
        self.add_notification_button()


        self.add_user_info()
        self.module_config = self.load_module_config()
        self.add_module_buttons()
        self.add_logout_button()
        self.add_help_button()

        self.icon_cache = {}  # damit Bilder nicht vom Garbage Collector gelöscht werden


    def load_module_config(self):
        standard_module_config = {
            "stundenplan": {"aktiv": True, "beschreibung": "Zeigt den persönlichen Stundenplan an"},
            "nachrichten": {"aktiv": True, "beschreibung": "Senden und Empfangen von Mitteilungen"},
            "dateiablage": {"aktiv": True, "beschreibung": "Austausch von Dateien mit Gruppen"},
            "einstellungen": {"aktiv": True, "beschreibung": "Persönliche Einstellungen ändern"},
            "cloud": {"aktiv": True, "beschreibung": "Dateien freigeben und abrufen"},
            "kalender": {"aktiv": True, "beschreibung": "Zeigt Termine und Veranstaltungen"},
            "ToDo": {"aktiv": True, "beschreibung": "Aufgabenverwaltung und Hausaufgaben"},
            "e_learning": {"aktiv": True, "beschreibung": "Lernmodule und Tests absolvieren"},
            "adminbereich": {"aktiv": True, "beschreibung": "Zugang zu Administratorfunktionen"},
            "supportverwaltung": {"aktiv": True, "beschreibung": "Supporttickets verwalten (Admin)"},
            "stundenplan_verwaltung": {"aktiv": True, "beschreibung": "Stundenpläne verwalten (Verwaltung)"},
            "modulverwaltung": {"aktiv": True, "beschreibung": "Aktive Module verwalten (Admin)"},
            "sitzplan" : {"aktiv" : True, "beschreibung" : "Verwalten von Sitzplänen für Klassen/Gruppen (Lehrer)"},
            "krankmeldungen" : {"aktiv" : True, "beschreibung" : "Eintragen und Melden von Krankheitsfällen"},
            "benachrichtigungen" : {"aktiv": True, "beschreibung": "Benachrichtigungen an alle senden (Admin)"},
            "sprechstunden" : {"aktiv": True, "beschreibung": "Buchen von Sprechstunden"},
            "ausleihe" : {"aktiv": True, "beschreibung": "Ausleihen von Geräten und Unterrichtsmaterialien"},
            "meldungen": {"aktiv": False, "beschreibung": "Melden von Nutzern "},
            "meldungen_verwaltung": {"aktiv": False, "beschreibung": "Meldungen von Nutzern verwalten (Admin)"},
            "team": {"aktiv": True, "beschreibung": "Development-Bereich zum beheben von Fehlern"},
            "umfragen": {"aktiv": False, "beschreibung": "Durchführen und Auswerten von Umfragen."},
            "bibliothek": {"aktiv": True, "beschreibung": "Bchereisystem mit: Bücher hinzufügen, anzeigen, ausleihen und zurückgeben."},
            "statistiken": {"aktiv": True, "beschreibung": "Anzeigen von Statistiken"}
        }

        if not os.path.exists("data/modules.json"):
            with open("data/modules.json", "w") as f:
                json.dump(standard_module_config, f, indent=4)
            print("modules.json wurde automatisch erstellt.")

        with open("data/modules.json", "r") as f:
            return json.load(f)


    def add_user_info(self):
        name_label = tk.Label(
            self.sidebar,
            text=f"👤 {self.username}",
            bg=self.sidebar_bg,
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            anchor="center"
        )
        name_label.pack(pady=(20, 10), fill="x")

    
    def check_unread_notifications(self):
        def update_notifications():
            notifications_found = False

            # --- notifications.json (strukturierter nach Benutzernamen) ---
            notif_file = "data/notifications.json"
            if os.path.exists(notif_file):
                try:
                    with open(notif_file, "r", encoding="utf-8") as f:
                        notif_data = json.load(f)
                    user_notifs = notif_data.get(self.username, [])
                    unread_notifs = [n for n in user_notifs if not n.get("gelesen")]
                    if unread_notifs:
                        message = unread_notifs[0]["text"]
                        command_line = None
                        lines = message.splitlines()

                        for line in lines:
                            if line.startswith("#COMMAND:DELETE_FILE:"):
                                command_line = line
                                break

                        if command_line:
                            filename_to_delete = command_line[len("#COMMAND:DELETE_FILE:"):].strip()
                            # Nachricht ohne die Befehlszeile
                            message = "\n".join(line for line in lines if not line.startswith("#COMMAND:DELETE_FILE:"))

                            # Popup mit Button anzeigen (funktion unten)
                            self.show_dashboard_popup_with_button(message, filename_to_delete)

                        else:
                            self.show_dashboard_popup(message)

                        # Als gelesen markieren
                        unread_notifs[0]["gelesen"] = True
                        with open(notif_file, "w", encoding="utf-8") as f:
                            json.dump(notif_data, f, indent=4, ensure_ascii=False)

                        notifications_found = True
                except Exception as e:
                    print("Fehler beim Laden von notifications.json:", e)

            # --- message_notifications.json (Liste aller Nachrichten) ---
            if not notifications_found:
                msg_file = "data/message_notifications.json"
                if os.path.exists(msg_file):
                    try:
                        with open(msg_file, "r", encoding="utf-8") as f:
                            msg_data = json.load(f)
                        for msg in msg_data:
                            if msg.get("empfänger") == self.username and not msg.get("gelesen"):
                                message = msg.get("titel", "") + "\n" + msg.get("text", "")
                                self.show_dashboard_popup(message)
                                # Als gelesen markieren
                                msg["gelesen"] = True
                                with open(msg_file, "w") as f:
                                    json.dump(msg_data, f, indent=4)
                                break
                    except Exception as e:
                        print("Fehler beim Laden von message_notifications.json:", e)

            self.master.after(2000, update_notifications)

        self.master.after(2000, update_notifications)




    def add_notification_button(self):
        btn = tk.Button(
            self.master,
            text="🔔",
            font=("Segoe UI", 12),
            bg="#e67e22",     # Hintergrundfarbe des Master-Widgets
            fg="#1e272e",
            activebackground="#e67e22",
            activeforeground="#1e272e",
            borderwidth=0,
            relief="flat",
            cursor="hand2",
            command=self.show_all_notifications
        )
        btn.place(x=230, y=10, width=40, height=40)

    def show_dashboard_popup_with_button(self, message, filename_to_delete):
        # Gleicher Aufbau wie show_dashboard_popup, mit Popup, Scrollbar, Close-Button
        shadow = tk.Label(self.content, bg="#aaa", width=43, height=7)
        shadow.place(relx=1.0, rely=1.0, anchor="se", x=-22, y=-22)

        popup_frame = tk.Frame(self.content, bg="#fef9e7", bd=1, relief="solid", width=300, height=140)
        popup_frame.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        canvas = tk.Canvas(popup_frame, bg="#fef9e7", bd=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(popup_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        content_frame = tk.Frame(canvas, bg="#fef9e7")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Close-Button
        close_btn = tk.Button(
            content_frame,
            text="✖",
            bg="#fef9e7",
            fg="black",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            command=lambda: (popup_frame.destroy(), shadow.destroy()),
            cursor="hand2",
            activebackground="#fef9e7",
            activeforeground="red"
        )
        close_btn.pack(anchor="ne", padx=5, pady=3)

        # Nachrichtentext
        message_label = tk.Label(
            content_frame,
            text=message,
            wraplength=270,
            justify="left",
            bg="#fef9e7",
            font=("Segoe UI", 10),
            anchor="nw"
        )
        message_label.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        # Button zum Löschen der Datei
        def delete_file():
            filepath = os.path.join("data", filename_to_delete)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    messagebox.showinfo("Erfolg", f"Datei '{filename_to_delete}' wurde gelöscht.")
                else:
                    messagebox.showwarning("Warnung", f"Datei '{filename_to_delete}' existiert nicht.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen der Datei:\n{e}")

        btn = tk.Button(
            content_frame,
            text=f"Datei {filename_to_delete} löschen",
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            command=delete_file
        )
        btn.pack(pady=(0, 10))

        # Scrollbereich aktualisieren
        def update_scroll():
            canvas.configure(scrollregion=canvas.bbox("all"))
            if canvas.bbox("all")[3] > canvas.winfo_height():
                scrollbar.pack(side="right", fill="y")
            else:
                scrollbar.pack_forget()

        content_frame.bind("<Configure>", lambda e: update_scroll())
        canvas.bind("<Configure>", lambda e: update_scroll())



    def show_dashboard_popup(self, message):
        # Schatten für Popup
        shadow = tk.Label(self.content, bg="#aaa", width=43, height=7)
        shadow.place(relx=1.0, rely=1.0, anchor="se", x=-22, y=-22)

        # Haupt-Popup
        popup_frame = tk.Frame(self.content, bg="#fef9e7", bd=1, relief="solid", width=300, height=110)
        popup_frame.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        # Canvas
        canvas = tk.Canvas(popup_frame, bg="#fef9e7", bd=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(popup_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Content-Frame im Canvas
        content_frame = tk.Frame(canvas, bg="#fef9e7")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # „X“-Schließen-Button
        close_btn = tk.Button(
            content_frame,
            text="✖",
            bg="#fef9e7",
            fg="black",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            command=lambda: (popup_frame.destroy(), shadow.destroy()),
            cursor="hand2",
            activebackground="#fef9e7",
            activeforeground="red"
        )
        close_btn.pack(anchor="ne", padx=5, pady=3)

        # Nachrichtentext
        message_label = tk.Label(
            content_frame,
            text=message,
            wraplength=270,
            justify="left",
            bg="#fef9e7",
            font=("Segoe UI", 10),
            anchor="nw"
        )
        message_label.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        # Scrollbereich aktualisieren
        def update_scroll():
            canvas.configure(scrollregion=canvas.bbox("all"))
            if canvas.bbox("all")[3] > canvas.winfo_height():
                scrollbar.pack(side="right", fill="y")
            else:
                scrollbar.pack_forget()

        content_frame.bind("<Configure>", lambda e: update_scroll())
        canvas.bind("<Configure>", lambda e: update_scroll())



    def show_all_notifications(self):
        win = tk.Toplevel(self.master)
        win.title("Alle Benachrichtigungen")
        win.geometry("400x400")

        try:
            with open("data/notifications.json", "r", encoding="utf-8") as f:
                all_data = json.load(f)
            user_msgs = all_data.get(self.username, [])
        except:
            user_msgs = []

        if not user_msgs:
            tk.Label(win, text="Keine Benachrichtigungen vorhanden.").pack(pady=20)
            return

        for msg in reversed(user_msgs):
            status = "❎" if not msg.get("gelesen") else "✅"
            text = f"{status} {msg['datum']} – {msg['text']}"
            tk.Label(win, text=text, wraplength=380, anchor="w", justify="left").pack(fill="x", padx=10, pady=5)


    def add_module_buttons(self):
        self.button_images = {}

        for modulname, einstellungen in self.module_config.items():
            if not einstellungen.get("aktiv", False):
                continue

            # Zugriffsregeln
            if modulname == "adminbereich" and not self.user_data.get("is_admin"):
                continue
            if modulname == "krankmeldungen" and self.user_data.get("group") != "Lehrer":
                continue
            if modulname == "ausleihe" and self.user_data.get("group") != "Lehrer":
                continue
            if modulname == "supportverwaltung" and not self.user_data.get("is_admin"):
                continue
            if modulname == "meldungen_verwaltung" and not self.user_data.get("is_admin"):
                continue
            if modulname == "benachrichtigungen" and not self.user_data.get("is_admin"):
                continue
            if modulname == "stundenplan_verwaltung" and self.user_data.get("group") != "Verwaltung":
                continue
            if modulname == "modulverwaltung" and self.user_data.get("group") != "Verwaltung":
                continue
            if modulname == "team" and self.user_data.get("group") != "SchulSystem-Team":
                print("Debug")
                continue
            if modulname == "sitzplan" and self.user_data.get("group") != "Lehrer":
                continue

            # Icon laden
            icon = self.get_icon(modulname)
            if not icon:
                icon = self.get_icon("leer")

            # Button mit Icon und Text
            btn = tk.Label(
                self.sidebar,
                image=icon,
                text=f"  {modulname.replace('_', ' ').title()}",
                compound="left",
                bg=self.sidebar_bg,
                fg=self.button_fg,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                padx=10,
                pady=10,
                cursor="hand2"
            )
            btn.image = icon  # Referenz speichern
            btn.pack(fill="x", pady=2)

            # Hover-Effekt
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.sidebar_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.sidebar_bg))
            btn.bind("<Button-1>", lambda e, m=modulname: self.load_module(m))





    # from PIL import Image, ImageTk -> In die requirements.txt!!!

    def get_icon(self, modulname, size=(20, 20)):
        try:
            path = os.path.join("icons", f"{modulname}.png")
            image = Image.open(path).resize(size, Image.Resampling.LANCZOS)
            print(f"Prüfe Modul: {modulname}")  # Debug
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Kein Icon für {modulname}: {e}")
            try:
                leer_icon = os.path.join("icons", "leer.png")
                image = Image.open(leer_icon).resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception as e2:
                print(f"Kein Fallback-Icon verfügbar: {e2}")
                return None



    def load_module(self, modulname):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

        for widget in self.content.winfo_children():
            widget.destroy()

        loading_label = tk.Label(
            self.content, text="⏳ Modul wird geladen...", font=("Segoe UI", 14),
            bg=self.content_bg, fg="#555"
        )
        loading_label.pack(expand=True)
        self.content.update_idletasks()

        def do_import():
            try:
                modul = importlib.import_module(f"modules.{modulname}")
                modul_class = getattr(modul, "Modul", None)
                if not modul_class:
                    raise ImportError(f"Klasse 'Modul' in Modul '{modulname}' nicht gefunden.")
                frame = modul_class(self.content, self.username, self.user_data).get_frame()
                loading_label.destroy()
                frame.pack(fill="both", expand=True)
                self.current_frame = frame
            except Exception as e:
                loading_label.destroy()
                self.show_error(modulname, str(e))

        self.master.after(100, do_import)



    def show_error(self, modulname, error_text):
        # Fehleranzeige
        USER_INFO_PATH = "data/users.json"
        error_frame = tk.Frame(self.content, bg="#f8d7da")
        error_frame.pack(expand=True, fill="both")

        error_label = tk.Label(
            error_frame,
            text=f"❌ Modul '{modulname}' konnte nicht geladen werden.\n\nFehlermeldung:\n{error_text}\nBitte melde den Fehler in einem Issue-Report bei GitHub.",
            bg="#f8d7da",
            fg="#721c24",
            font=("Segoe UI", 12),
            justify="left",
            padx=20,
            pady=20
        )
        error_label.pack(expand=True, fill="both")

        def copy_error():
            # Nutzerdaten laden
            try:
                if os.path.exists(USER_INFO_PATH):
                    with open(USER_INFO_PATH, "r",  encoding="utf-8") as f:
                        users_data = json.load(f)
                else:
                    users_data = {"Fehler": "users.json nicht gefunden."}
            except Exception as e:
                users_data = {"Fehler beim Laden": str(e)}

            # Kopierbarer Text
            full_error = (
                f"❌ Fehler beim Laden des Moduls:\n"
                f"Modulname: {modulname}\n "
                f"GitHub-Adresse: https://github.com/Lukas1120987/Schul-System/issues \n"
                f"Fehlermeldung: {error_text}\n\n"
                f"🔐 Nutzerdaten:\n{json.dumps(self.user_data, indent=2)}"
            )

            from tkinter import messagebox

            # In Zwischenablage kopieren
            self.master.clipboard_clear()
            self.master.clipboard_append(full_error)
            self.master.update()
            messagebox.showinfo("Kopiert", "Fehlerdetails wurden in die Zwischenablage kopiert.")

        # Kopier-Button mit Emoji
        copy_btn = tk.Button(
            error_frame,
            text="📋 Kopieren",
            bg="#f5c6cb",
            fg="#721c24",
            font=("Segoe UI", 10, "bold"),
            command=copy_error
        )
        copy_btn.pack(pady=(0, 20))


    def logout(self):
        from login import open_login_window
        self.master.destroy()
        open_login_window()

    def add_logout_button(self):
        logout_frame = tk.Frame(self.sidebar, bg="#1e272e")
        logout_frame.pack(side="bottom", fill="x", pady=10)

        logout_btn = tk.Button(
            logout_frame,
            text="🚪 Logout",
            font=("Arial", 10, "bold"),
            bg="#d9534f",
            fg="white",
            activebackground="#c9302c",
            relief="flat",
            command=self.logout
        )
        logout_btn.pack(padx=10, pady=5, fill="x")

    def add_help_button(self):
        help_btn = tk.Button(
            self.master,
            text="ℹ️ Hilfe",
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            relief="flat",
            command=self.show_help_window
        )
        help_btn.place(relx=1.0, x=-10, y=10, anchor="ne")  # Oben rechts im Fenster


    def show_help_window(self):
        try:
            with open("data/help.json", "r", encoding="utf-8") as f:
                all_entries = json.load(f)
        except FileNotFoundError:
            tk.messagebox.showerror("Fehler", "Die Hilfedatei wurde nicht gefunden.")
            return

        help_window = tk.Toplevel(self.master)
        help_window.title("Hilfecenter")
        help_window.geometry("700x550")

        # Suchen-Bereich
        search_frame = tk.Frame(help_window)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Suche:", font=("Segoe UI", 10)).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=(5, 10))

        filter_var = tk.StringVar(value="Alle")
        filter_options = ["Alle", "Kategorie", "Titel", "Inhalt"]
        filter_dropdown = ttk.Combobox(search_frame, textvariable=filter_var, values=filter_options, width=12, state="readonly")
        filter_dropdown.pack(side="left")

        # Scrollbarer Bereich
        canvas = tk.Canvas(help_window, borderwidth=0)
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def display_entries(entries):
            for widget in scroll_frame.winfo_children():
                widget.destroy()

            if not entries:
                tk.Label(scroll_frame, text="Keine passenden Einträge gefunden.", font=("Segoe UI", 10, "italic")).pack(pady=10)
                return

            categories = {}
            for entry in entries:
                categories.setdefault(entry["category"], []).append(entry)

            for category, items in sorted(categories.items()):
                cat_label = tk.Label(scroll_frame, text=category, font=("Segoe UI", 12, "bold"), anchor="w", pady=8)
                cat_label.pack(fill="x", padx=10)

                for item in items:
                    title = tk.Label(scroll_frame, text="• " + item["title"], font=("Segoe UI", 10, "bold"), anchor="w")
                    content = tk.Label(scroll_frame, text=item["content"], font=("Segoe UI", 10), anchor="w", wraplength=640, justify="left")
                    title.pack(fill="x", padx=20)
                    content.pack(fill="x", padx=30, pady=(0, 8))

        def on_search_change(*args):
            query = search_var.get().strip().lower()
            mode = filter_var.get()
            if not query:
                display_entries(all_entries)
                return

            filtered = []
            for entry in all_entries:
                if mode == "Alle":
                    if (query in entry["category"].lower() or
                        query in entry["title"].lower() or
                        query in entry["content"].lower()):
                        filtered.append(entry)
                elif mode == "Kategorie" and query in entry["category"].lower():
                    filtered.append(entry)
                elif mode == "Titel" and query in entry["title"].lower():
                    filtered.append(entry)
                elif mode == "Inhalt" and query in entry["content"].lower():
                    filtered.append(entry)

            display_entries(filtered)

        search_var.trace_add("write", on_search_change)
        filter_dropdown.bind("<<ComboboxSelected>>", lambda e: on_search_change())

        display_entries(all_entries)


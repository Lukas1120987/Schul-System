# main.py – Hauptkonfiguration vom SchulSystem
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import random
from login import SplashScreen, open_login_window, start
from first_splash import InstallAssistantSplash
from datetime import datetime
from ordner import get_data_path
import platform
import sys
import psutil
import socket

# Farbdefinitionen 
PRIMARY_BLUE = "#2a4d8f"
WHITE = "#ffffff"
LIGHT_BLUE = "#aaccff"

DATA_PATH = os.path.join(get_data_path(), "data/users.json")

def load_data_path():
    """Lädt den Speicherort aus setup.json"""
    with open("setup.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("data_path", ".")

def create_file_if_missing(filename, content):
    """Erstellt Datei im in setup.json angegebenen Ordner, falls sie nicht existiert."""
    data_path = load_data_path()
    full_path = os.path.join(data_path, filename)

    if not os.path.exists(full_path):
        print(f"Erstelle {filename} im Pfad {data_path}...")
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4, ensure_ascii=False)


def setup_databases(admin_name, admin_password):
    """Initialisiert alle notwendigen Datenbanken und Beispielinhalte."""
    os.makedirs("data", exist_ok=True)

    create_file_if_missing(
        "data/users.json",
        {
            admin_name: {
                "password": admin_password,
                "group": "Verwaltung",
                "second_group": "Musterklasse",
                "is_admin": True,
                "kontaktierbar": True,
                "geschützt": True,
            },
            "default_user1": {
                "password": admin_password,
                "group": "Lehrer",
                "second_group": "Musterklasse",
                "is_admin": False,
                "kontaktierbar": False,
                "geschützt": True,
            },
            "default_user2": {
                "password": admin_password,
                "group": "Schüler",
                "second_group": "Musterklasse",
                "is_admin": False,
                "kontaktierbar": False,
                "geschützt": True,

            },
            "SchulSystem": {
                "password": admin_password,
                "group": "SchulSystem-Team",
                "second_group": "Verwaltung",
                "is_admin": True,
                "kontaktierbar": False,
                "geschützt": True,

            },
            "default_user3": {
                "password": admin_password,
                "group": "Verwaltung",
                "second_group": "Musterklasse",
                "is_admin": True,
                "kontaktierbar": False,
                "geschützt": True,

            }
        }
    )

    create_file_if_missing(
        "data/messages.json",
        [
            {
                "absender": "System",
                "empfänger": admin_name,
                "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "betreff": "Willkommen",
                "inhalt": (
                    f"Hallo {admin_name}, willkommen im SchulSystem! \n"
                    "Schau im Hilfe-Bereich nach, wenn du Fragen hast."
                ),
            }
        ],
    )

    create_file_if_missing(
        "data/support.json",
        [
            {
                "user": "System",
                "content": "Dies ist eine, automatisch zur Konfiguration, erstellte Nachricht",
                "status": "erledigt",
            }
        ],
    )

    create_file_if_missing(
        "data/feedback.json",
        [
            {
                "user": "System",
                "feedback": "Dies ist eine, automatisch zur Konfiguration, erstellte Nachricht",
            }
        ],
    )

    create_file_if_missing(
        "data/help.json",
        [
            {
                "title": "Wie funktioniert der Stundenplan?",
                "category": "Stundenplan",
                "content": (
                    "Im Modul 'Stundenplan' findest du deinen aktuellen Stundenplan "
                    "basierend auf deiner Gruppen- oder Klassenzugehörigkeit."
                ),
            },
            {
                "title": "Wie schreibe ich eine Nachricht?",
                "category": "Nachrichten",
                "content": (
                    "Öffne das Nachrichten-Modul und klicke auf 'Neue Nachricht'. "
                    "Gib Empfänger, Betreff und Nachricht ein."
                ),
            },
            {
                "title": "Wie finde ich eine alte Nachricht?",
                "category": "Nachrichten",
                "content": (
                    "Im Nachrichten-Modul kannst du über das Suchfeld nach Stichwörtern "
                    "oder Empfängern suchen."
                ),
            },
            {
                "title": "Wie funktioniert die Dateiablage?",
                "category": "Dateiablage",
                "content": (
                    "Im Modul 'Dateiablage' kannst du Dateien hoch- und herunterladen "
                    "und mit Gruppen teilen."
                ),
            },
            {
                "title": "Wie ändere ich meinen Benutzernamen?",
                "category": "Einstellungen",
                "content": "Im Modul 'Einstellungen' unter 'Benutzernamen ändern'.",
            },
            {
                "title": "Wie ändere ich mein Passwort?",
                "category": "Einstellungen",
                "content": "Im Modul 'Einstellungen' unter 'Passwort ändern'.",
            },
            {
                "title": "Wie kann ich ein Supportticket erstellen?",
                "category": "Einstellungen",
                "content": "Unter 'Einstellungen' → 'Support' kannst du neue Tickets erstellen.",
            },
            {
                "title": "Wie gebe ich Feedback?",
                "category": "Einstellungen",
                "content": "Gehe zu 'Einstellungen' → 'Feedback senden'.",
            },
            {
                "title": "Was ist die Support-Verwaltung?",
                "category": "Support-Verwaltung",
                "content": "Admins können dort Tickets sehen, beantworten und verwalten.",
            },
            {
                "title": "Was ist der Adminbereich?",
                "category": "Adminbereich",
                "content": (
                    "Im Adminbereich verwalten Administratoren Gruppen, Accounts "
                    "und Passwörter."
                ),
            },
            {
                "title": "Wie kann ich Benutzer schnell erstellen?",
                "category": "Adminbereich",
                "content": (
                    "Im Schnell-Erstellungs-Dialog im Adminbereich kannst du schnell Benutzer anlegen "
                    "und diesen Gruppen zuweisen."
                ),
            },
            {
                "title": "Wie nutze ich das Hilfecenter?",
                "category": "Hilfe",
                "content": "Klicke auf 'ℹ️ Hilfe', um das Hilfecenter zu öffnen.",
            },
            {
                "title": "Wie nutze ich die Modulverwaltung?",
                "category": "Modulverwaltung",
                "content": (
                    "Klicke auf 'Modulverwaltung', um das Verwaltungstool zu öffnen. \n"
                    "Dort kannst du die Module auswählen, die für die Schule aktiviert "
                    "sein sollen. \nWenn du deine Eingabe speicherst, musst du das Programm "
                    "einmal neu starten."
                ),
            },
            {
                "title": "Wie funktioniert das Krankmeldungsmodul?",
                "category": "Krankmeldung",
                "content": (
                    "Im Modul 'Krankmeldung' können Benutzer sich krank melden. "
                    "Die Daten werden gespeichert und sind für die Verwaltung sichtbar."
                ),
            },
            {
                "title": "Wie nutze ich das Sitzplan-Modul?",
                "category": "Sitzplan",
                "content": (
                    "Im Sitzplan-Modul kannst du Sitzplätze für eine Gruppe festlegen. "
                    "Die Plätze werden per Drag & Drop vergeben und gespeichert."
                ),
            },
            {
                "title": "Wie funktioniert das Benachrichtigungssystem?",
                "category": "Benachrichtigungen",
                "content": (
                    "Admins können Benachrichtigungen an Benutzer senden. "
                    "Diese erscheinen als Pop-up im Dashboard und können oben links eingesehen werden."
                ),
            },
            {
                "title": "Was passiert beim ersten Start?",
                "category": "Allgemein",
                "content": (
                    "Beim ersten Start legst du einen Admin-Benutzer an. Danach wirst du automatisch zum Login weitergeleitet."
                ),
            },
            {
                "title": "Was ist der Unterschied zwischen Dateiablage und Cloud?",
                "category": "Allgemein",
                "content": (
                    "Wenn eine Datei in 'Dateiablage' hochgeladen wird, ist diese für alle Nutzer verfügbar. In der Cloud müssen Nutzer oder Gruppen der Datei zugeordnet werden."
                ),
            },
            {
                "title": "Was macht der Ladebildschirm?",
                "category": "Allgemein",
                "content": (
                    "Der Ladebildschirm zeigt dir den Fortschritt beim Start der Anwendung. "
                    "Währenddessen werden Module geladen und Systeme initialisiert."
                ),
            },
        ]
    )




def show_admin_creation_dialog():
    def choose_directory():
        path = filedialog.askdirectory(parent=dialog, title="Speicherort wählen")
        if path:
            path_var.set(path)

    def submit():
        name = name_entry.get().strip()
        pw = pw_entry.get().strip()
        path = path_var.get().strip()

        if not name or not pw or not path:
            messagebox.showerror("Fehler", "Bitte fülle alle Felder aus.")
            return

        # Speichere setup.json
        with open("setup.json", "w", encoding="utf-8") as f:
            json.dump({"data_path": path}, f, indent=4)

        result["name"] = name
        result["password"] = pw
        dialog.destroy()

    result = {"name": None, "password": None}

    parent = tk.Tk()
    parent.withdraw()

    dialog = tk.Toplevel(parent)
    dialog.title("Admin-Setup")
    dialog.configure(bg=PRIMARY_BLUE)
    dialog.overrideredirect(True)

    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    dialog.geometry(f"{screen_width}x{screen_height}+0+0")
    dialog.grab_set()

    frame = tk.Frame(dialog, bg=PRIMARY_BLUE)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    title = tk.Label(frame, text="Admin-Konto erstellen", font=("Segoe UI", 28, "bold"),
                     bg=PRIMARY_BLUE, fg=WHITE)
    title.pack(pady=(0, 40))

    # Benutzername
    tk.Label(frame, text="Benutzername:", bg=PRIMARY_BLUE, fg=WHITE, font=("Segoe UI", 14)).pack(fill="x")
    name_entry = tk.Entry(frame, font=("Segoe UI", 14))
    name_entry.pack(fill="x", pady=(0, 20))

    # Passwort
    tk.Label(frame, text="Passwort:", bg=PRIMARY_BLUE, fg=WHITE, font=("Segoe UI", 14)).pack(fill="x")
    pw_entry = tk.Entry(frame, show="*", font=("Segoe UI", 14))
    pw_entry.pack(fill="x", pady=(0, 20))

    # Speicherort
    tk.Label(frame, text="Datei-Speicherort:", bg=PRIMARY_BLUE, fg=WHITE, font=("Segoe UI", 14)).pack(fill="x")

    path_frame = tk.Frame(frame, bg=PRIMARY_BLUE)
    path_frame.pack(fill="x", pady=(0, 30))

    path_var = tk.StringVar()
    path_entry = tk.Entry(path_frame, textvariable=path_var, font=("Segoe UI", 14))
    path_entry.pack(side="left", fill="x", expand=True)
    browse_btn = tk.Button(path_frame, text="...", command=choose_directory, bg=LIGHT_BLUE)
    browse_btn.pack(side="right")

    submit_btn = tk.Button(frame, text="Erstellen", command=submit,
                           bg=LIGHT_BLUE, fg="black", font=("Segoe UI", 14))
    submit_btn.pack()

    dialog.bind("<Escape>", lambda e: dialog.destroy())

    parent.wait_window(dialog)
    parent.destroy()

    return result["name"], result["password"]




def show_tutorial(admin_name):
    """Zeigt das Tutorial-Fenster beim Erststart an."""
    root = tk.Tk()
    root.title("SchulSystem Setup")

    tutorial_text = f"""
Willkommen im SchulSystem, {admin_name}!

Dies ist dein erstes Setup. Hier werden die wichtigsten Features erklärt:

✔ Dein Admin-Account wurde erstellt.
✔ Der Beispiel-Stundenplan ist aktiv.
✔ Du hast eine Begrüßungsnachricht erhalten.

Bitte aktiviere im Verwaltungstool alle gewünschten Module.
Diese kannst du jederzeit anpassen.

Klicke auf „Weiter“, um SchulSystem zu starten.
"""

    label = tk.Label(root, text=tutorial_text, padx=20, pady=20, justify="left")
    label.pack()

    def continue_to_login():
        root.destroy()
        from updater import check_and_update
        check_and_update()
        
        open_login_window()

    button = tk.Button(root, text="Weiter", command=continue_to_login)
    button.pack(pady=20)

    root.mainloop()


def main():
    os.makedirs("data", exist_ok=True)

    

    if os.path.exists(DATA_PATH):
        # Normales Starten mit klassischem SplashScreen (nicht InstallAssistantSplash!)
        start()
        return

    from ordner import get_data_path
    import uuid
    SYSTEM_INFO_FILE = os.path.join(get_data_path(), "data/system_info.json")


    def _init_system_info():
        """Erstellt oder aktualisiert die Systeminformationen inklusive Hardware, OS, Python, Netzwerk usw."""

        def get_current_version():
            """Liest die Version aus version.txt"""
            try:
                with open("version.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
            except FileNotFoundError:
                return "unbekannt"

        current_version = get_current_version()

        # Falls Datei existiert, laden, sonst neu erstellen
        info = {}
        if os.path.exists(SYSTEM_INFO_FILE):
            try:
                with open(SYSTEM_INFO_FILE, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                info = {}

        # System-ID erstellen falls nicht vorhanden
        if "system_id" not in info:
            info["system_id"] = str(uuid.uuid4())

        # Versionsinformationen
        info["version"] = current_version
        info["created"] = info.get("created", datetime.now().isoformat(timespec="seconds"))
        info["last_update"] = datetime.now().isoformat(timespec="seconds")

        # --- 1. Betriebssystem & Hardware ---
        info["os"] = platform.system()
        info["os_release"] = platform.release()
        info["os_version"] = platform.version()
        info["architecture"] = platform.architecture()[0]
        info["machine"] = platform.machine()
        info["processor"] = platform.processor()
        info["cpu_count"] = os.cpu_count()
        try:
            ram = psutil.virtual_memory()
            info["ram_total_gb"] = round(ram.total / (1024 ** 3), 2)
        except Exception:
            info["ram_total_gb"] = None

        try:
            disk = psutil.disk_usage("/")
            info["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
            info["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)
        except Exception:
            info["disk_total_gb"] = None
            info["disk_free_gb"] = None

        try:
            info["hostname"] = socket.gethostname()
            info["ip_address"] = socket.gethostbyname(info["hostname"])
        except Exception:
            info["hostname"] = None
            info["ip_address"] = None

        # --- 2. Python & Laufzeit ---
        info["python_version"] = sys.version
        info["python_executable"] = sys.executable
        info["python_platform"] = sys.platform
        info["sys_path"] = sys.path

        # --- 3. Systemstart & Logging ---
        info["uuid"] = str(uuid.uuid4())
        info["timestamp"] = datetime.now().isoformat(timespec="seconds")

        # --- 4. Optional / Debugging (falls relevant) ---
        # info["environment_variables"] = dict(os.environ)

        # Datei speichern
        os.makedirs(os.path.dirname(SYSTEM_INFO_FILE), exist_ok=True)
        with open(SYSTEM_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)

        print(f"[INFO] Systeminformationen gespeichert: {SYSTEM_INFO_FILE}")
        return info

    def get_system_info():
        """Liest Systeminformationen aus."""
        with open(SYSTEM_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)



    # Erststart: InstallAssistantSplash + Admin-Einrichtung
    splash_root = tk.Tk()
    

    def start_setup_wrapper():
        admin_name, admin_password = show_admin_creation_dialog()
        if not admin_name or not admin_password:
            splash_root.destroy()
            return
        setup_databases(admin_name, admin_password)
        # setup_databases.py oder direkt in main()
        with open("data/config.json", "w", encoding="utf-8") as f:
            json.dump({"admin_name": admin_name}, f, indent=2)
        _init_system_info()
        splash_root.destroy()  # Splash schließen
        show_tutorial(admin_name)
        
        open_login_window()

    # Jetzt korrekt: InstallAssistantSplash für Erststart
    splash = InstallAssistantSplash(splash_root, start_setup_wrapper)
    splash_root.mainloop()




    


if __name__ == "__main__":
    main()
    




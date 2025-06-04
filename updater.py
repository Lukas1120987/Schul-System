import os
import urllib.request
import zipfile
import shutil
import sys
import signal
import subprocess
import tkinter as tk
from tkinter import ttk
import random
import time
import threading

# === Konfiguration ===
GITHUB_ZIP_URL = "https://github.com/Lukas1120987/SchulSystem/archive/refs/heads/main.zip"
UPDATE_DIR = "update_temp"
EXCLUDE_DIRS = ["data", "__pycache__"]
EXCLUDE_FILES = ["main.exe"]

# === Ladebildschirm-Klasse ===
class InstallAssistantSplash:
    def __init__(self, root, on_continue_callback):
        self.root = root
        self.on_continue_callback = on_continue_callback
        self.progress_value = 0
        self.progress_max = 100
        self.dot_count = 0
        self.start_time = time.time()
        self.min_duration = 1
        self.max_duration = 500

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.overrideredirect(True)
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        root.configure(bg="#1e2a45")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("blue.Horizontal.TProgressbar", troughcolor='#32415e',
                        background='#6fa8dc', thickness=20, bordercolor='#1e2a45')

        self.container = tk.Frame(root, bg="#1e2a45")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        try:
            self.logo_photo = tk.PhotoImage(file="logo.png")
            self.logo_photo = self.logo_photo.subsample(2, 2)
            self.logo_label = tk.Label(self.container, image=self.logo_photo, bg="#1e2a45")
            self.logo_label.pack(pady=(0, 30))
        except Exception as e:
            print("Logo konnte nicht geladen werden:", e)

        self.title_label = tk.Label(self.container, text="SchulSystem \n Update",
                                    font=("Segoe UI", 44, "bold"), fg="white", bg="#1e2a45")
        self.title_label.pack(pady=(0, 30))

        self.instructions = tk.Label(self.container,
                                     text="Update-Assistent für SchulSystem\n",
                                     font=("Segoe UI", 18), fg="lightgray", bg="#1e2a45", justify="center")
        self.instructions.pack(pady=(0, 20))

        self.loading_label = tk.Label(self.container, text="Suche nach Updates", font=("Segoe UI", 16),
                                      fg="lightgray", bg="#1e2a45")
        self.loading_label.pack(pady=10)

        self.progress_frame = tk.Frame(self.container, bg="#1e2a45")
        self.progress_frame.pack(pady=20)

        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=400,
                                        mode="determinate", style="blue.Horizontal.TProgressbar")
        self.progress.pack(side="left")

        self.percent_label = tk.Label(self.progress_frame, text="0%", font=("Segoe UI", 14),
                                      fg="lightgray", bg="#1e2a45")
        self.percent_label.pack(side="left", padx=(10, 0))

        self.progress["maximum"] = self.progress_max
        self.progress["value"] = 0

        self.root.bind("<h>", lambda e: self.continue_now())
        self.load_progress()

    def load_progress(self):
        if self.progress_value < self.progress_max:
            step = random.randint(1, 2)
            self.progress_value = min(self.progress_value + step, self.progress_max)
            self.progress["value"] = self.progress_value
            self.percent_label.config(text=f"{self.progress_value}%")
            self.animate_loading_text()
            delay = random.randint(10, 130)
            self.root.after(delay, self.load_progress)
        else:
            self.continue_now()

    def animate_loading_text(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.loading_label.config(text="Suche nach Updates" + "." * self.dot_count)

    def continue_now(self):
        self.root.unbind("<h>")
        elapsed = time.time() - self.start_time
        if elapsed < self.min_duration:
            remaining = int((self.min_duration - elapsed) * 1000)
            self.root.after(remaining, self.on_continue_callback)
        else:
            self.on_continue_callback()

# === Versionsverwaltung ===
def get_local_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_remote_version():
    try:
        with urllib.request.urlopen("https://raw.githubusercontent.com/Lukas1120987/SchulSystem/main/version.txt") as response:
            return response.read().decode('utf-8').strip()
    except:
        return None

def is_newer_version(local, remote):
    return local != remote

def copy_files(source_dir, target_dir):
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        if rel_path == ".":
            rel_path = ""
        if any(part in EXCLUDE_DIRS for part in rel_path.split(os.sep)):
            continue
        for file in files:
            if file in EXCLUDE_FILES:
                print(f"[Updater] Datei übersprungen (ausgeschlossen): {file}")
                continue
            src_file = os.path.join(root, file)
            dest_file = os.path.join(target_dir, rel_path, file)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            try:
                shutil.copy2(src_file, dest_file)
                print(f"[Updater] Datei überschrieben: {dest_file}")
            except Exception as e:
                print(f"[Updater] Fehler beim Kopieren: {dest_file} → {e}")

def force_exit_all_windows():
    print("[Updater] Beende Anwendung...")
    os.kill(os.getpid(), signal.SIGTERM)

def download_and_extract_update():
    print("[Updater] Lade neue Version herunter...")
    os.makedirs(UPDATE_DIR, exist_ok=True)
    zip_path = os.path.join(UPDATE_DIR, "update.zip")
    try:
        urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
    except Exception as e:
        print(f"[Updater] Fehler beim Download: {e}")
        return
    print("[Updater] Entpacke Archiv...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(UPDATE_DIR)
    except Exception as e:
        print(f"[Updater] Fehler beim Entpacken: {e}")
        return
    entries = [entry for entry in os.listdir(UPDATE_DIR) if os.path.isdir(os.path.join(UPDATE_DIR, entry))]
    if not entries:
        print("[Updater] Keine gültigen Dateien gefunden.")
        return
    extracted_path = os.path.join(UPDATE_DIR, entries[0])
    print(f"[Updater] Entpackt nach: {extracted_path}")
    copy_files(extracted_path, ".")
    shutil.rmtree(UPDATE_DIR, ignore_errors=True)

def check_and_update():
    local = get_local_version()
    remote = get_remote_version()
    if not remote:
        print("[Updater] Keine Verbindung zum Server.")
        return
    if is_newer_version(local, remote):
        print(f"[Updater] Neue Version verfügbar: {remote} (aktuell: {local})")
        download_and_extract_update()
        with open("version.txt", "w") as f:
            f.write(remote)
        print("[Updater] Update abgeschlossen. Starte Anwendung neu...")
        APP_TO_START = "main.exe" if os.path.exists("main.exe") else "main.py"
        subprocess.Popen([sys.executable, APP_TO_START] if APP_TO_START.endswith(".py") else [APP_TO_START])
        force_exit_all_windows()
    else:
        print("[Updater] Version ist aktuell: " + local)

# === Hauptprogrammstart mit Splashscreen ===
def start_update():
    threading.Thread(target=check_and_update).start()

if __name__ == "__main__":
    root = tk.Tk()
    splash = InstallAssistantSplash(root, on_continue_callback=lambda: [root.destroy(), start_update()])
    root.mainloop()

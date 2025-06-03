import os
import urllib.request
import zipfile
import shutil
import sys
import signal
import subprocess

# === Konfiguration ===
GITHUB_ZIP_URL = "https://github.com/Lukas1120987/SchulSystem/archive/refs/heads/main.zip"
UPDATE_DIR = "update_temp"
EXCLUDE_DIRS = ["data", "__pycache__"]
EXCLUDE_FILES = ["main.exe"]

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

# === Dateiüberschreibung ohne Löschen ===
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

# === Fenster schließen ===
def force_exit_all_windows():
    print("[Updater] Beende Anwendung...")
    os.kill(os.getpid(), signal.SIGTERM)

# === Download + Entpacken ===
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

    # Finde entpacktes Hauptverzeichnis
    entries = [entry for entry in os.listdir(UPDATE_DIR) if os.path.isdir(os.path.join(UPDATE_DIR, entry))]
    if not entries:
        print("[Updater] Keine gültigen Dateien gefunden.")
        return
    extracted_path = os.path.join(UPDATE_DIR, entries[0])
    print(f"[Updater] Entpackt nach: {extracted_path}")

    # Dateien kopieren
    copy_files(extracted_path, ".")

    # Aufräumen
    shutil.rmtree(UPDATE_DIR, ignore_errors=True)

# === Updateprozess ===
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

        # Anwendung neu starten
        APP_TO_START = "main.exe" if os.path.exists("main.exe") else "main.py"
        subprocess.Popen([sys.executable, APP_TO_START] if APP_TO_START.endswith(".py") else [APP_TO_START])


        # Beenden
        force_exit_all_windows()
    else:
        print("[Updater] Version ist aktuell: " + local)

# === Direktstart ===
if __name__ == "__main__":
    check_and_update()

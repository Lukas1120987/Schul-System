
# 📚 SchulSystem – Das digitale Schulverwaltungssystem


![Version](https://img.shields.io/badge/Version-1.5.0-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-BETA-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white&style=flat-square)

**SchulSystem** ist ein modulares Schulverwaltungssystem in Python, das IServ, WebUntis und weitere Tools kombiniert – mit Fokus auf einfache Bedienung, modulare Erweiterung und lokale Datenhaltung.

---

## 🔧 Voraussetzungen

Bevor du `main.py` startest:

1. 📦 **ZIP-Datei entpacken**
2. 📂 Verzeichnisstruktur beibehalten
3. 🔁 Pakete aus `requirements.txt` installieren  
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧩 Enthaltene Module

| Modul | Beschreibung |
|-------|--------------|
| 💬 **Nachrichten** | Schulinterne Nachrichten mit Suchfunktion |
| ☁️ **Cloud** | Dateien mit Gruppen oder Personen teilen |
| 🗂️ **Dateiablage** | Öffentlicher Dateiupload für alle |
| 🪑 **Sitzplan** | Drag-and-Drop Sitzplaneditor |
| 🧪 **E-Learning** | Digitale Tests mit Ergebnisauswertung |
| 📅 **Stundenplan** | Individuelle Anzeige nach Gruppe |
| 🛠️ **Stundenplanverwaltung** | Verwaltung und Bearbeitung zentral |
| 📢 **Meldungen** | Kurzmeldungen für Info & Datei-Uploads |
| 📝 **Meldungsverwaltung** | Bestehende Meldungen bearbeiten |
| 🧑‍🏫 **Sprechstunden** | Zeiten setzen und Termine buchen |
| 📚 **Ausleihe** | Verwaltung von Schulmaterialien |
| 🧑‍💼 **Adminbereich** | Benutzer- und Gruppenverwaltung |
| 🤧 **Krankmeldungen** | Abwesenheiten mit Gruppenansicht |
| ✅ **ToDo’s** | Persönliche Aufgabenverwaltung |
| 📆 **Kalender** | Monats- & Wochenübersicht für alle Termine |
| 🆘 **Support** | Ticketsystem für Hilfe & Feedback |
| ⚙️ **Einstellungen** | Nutzerprofil anpassen & Rückmeldung geben |

---

## 🚀 Schnellstart

```bash
git clone https://github.com/Lukas1120987/Schul-System.git
cd SchulSystem
pip install -r requirements.txt
python main.py
```

---

## 📌 Versionsübersicht

| Version        | Features         | Status |
|----------------|------------------|--------|
| **v2.1**       | Viele neue Module, Rework        | ![Beta](https://img.shields.io/badge/BETA-red) |
| **< 2.0**       | Erste stabile Hauptversion       | ![Published](https://img.shields.io/badge/Published-green) |
| **v1.3**        | Basismodul mit Login und Nachrichtensystem | ![Published](https://img.shields.io/badge/Published-green) |

---

## 🏗️ Projektstruktur

```plaintext
SchulSystem/
├── main.py                 # Hauptstartdatei
├── login.py                # Loginfenster
├── dashboard.py            # Zentrale Oberfläche
├── updater.py              # Auto-Updater
├── modules/                # Alle Funktionsmodule
│   ├── stundenplan.py
│   ├── nachrichten.py
│   └── ...
├── data/                   # Lokale JSON-Daten
│   ├── users.json
│   ├── messages.json
│   └── ...
```

---

## 💬 Kontakt

📨 **Discord-Server**: [Beitreten](https://discord.gg/NHgr4FKXE3)  
✉️ **Fragen / Ideen / Bugreports**? – Immer gern auf Discord oder als Git-Issue.

---

## 📃 Lizenz

Dieses Projekt steht unter der [MIT License](https://opensource.org/licenses/MIT).

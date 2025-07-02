
# 📚 SchulSystem – Das digitale Schulverwaltungssystem


![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-BETA-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white&style=flat-square)

**SchulSystem** ist ein modulares Schulverwaltungssystem in Python. Es werden verschiedene Tools kombiniert, mit Fokus auf einfache Bedienung, modulare Erweiterung und lokale Datenhaltung.

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

| Modul | Funktion |
|-------|-------|
| 💬 **Nachrichten** | ![Nachrichten](https://img.shields.io/badge/Schulinterne%20Nachrichten%20mit%20Suchfunktion-lightgrey) |
| ☁️ **Cloud** | ![Cloud](https://img.shields.io/badge/Dateien%20mit%20Gruppen%20oder%20Personen%20teilen-lightgrey) |
| 🗂️ **Dateiablage** | ![Dateiablage](https://img.shields.io/badge/%C3%96ffentlicher%20Dateiupload%20f%C3%BCr%20alle-lightgrey) |
| 🪑 **Sitzplan** | ![Sitzplan](https://img.shields.io/badge/Drag--and--Drop%20Sitzplaneditor-lightgrey) |
| 🧪 **E-Learning** | ![E-Learning](https://img.shields.io/badge/Digitale%20Tests%20mit%20Ergebnisauswertung-lightgrey) |
| 📅 **Stundenplan** | ![Stundenplan](https://img.shields.io/badge/Individuelle%20Anzeige%20nach%20Gruppe-lightgrey) |
| 🛠️ **Stundenplanverwaltung** | ![Stundenplanverwaltung](https://img.shields.io/badge/Verwaltung%20und%20Bearbeitung%20zentral-lightgrey) |
| 📢 **Meldungen** | ![Meldungen](https://img.shields.io/badge/Kurzmeldungen%20f%C3%BCr%20Info%20%26%20Datei--Uploads-lightgrey) |
| 📝 **Meldungsverwaltung** | ![Meldungsverwaltung](https://img.shields.io/badge/Bestehende%20Meldungen%20bearbeiten-lightgrey) |
| 🧑‍🏫 **Sprechstunden** | ![Sprechstunden](https://img.shields.io/badge/Zeiten%20setzen%20und%20Termine%20buchen-lightgrey) |
| 📚 **Ausleihe** | ![Ausleihe](https://img.shields.io/badge/Verwaltung%20von%20Schulmaterialien-lightgrey) |
| 🧑‍💼 **Adminbereich** | ![Adminbereich](https://img.shields.io/badge/Benutzer--%20und%20Gruppenverwaltung-lightgrey) |
| 🤧 **Krankmeldungen** | ![Krankmeldungen](https://img.shields.io/badge/Abwesenheiten%20mit%20Gruppenansicht-lightgrey) |
| ✅ **ToDo’s** | ![ToDo's](https://img.shields.io/badge/Pers%C3%B6nliche%20Aufgabenverwaltung-lightgrey) |
| 📆 **Kalender** | ![Kalender](https://img.shields.io/badge/Monats--%20%26%20Wochen%C3%BCbersicht%20f%C3%BCr%20alle%20Termine-lightgrey) |
| 🆘 **Support** | ![Support](https://img.shields.io/badge/Ticketsystem%20f%C3%BCr%20Hilfe%20%26%20Feedback-lightgrey) |
| ⚙️ **Einstellungen** | ![Einstellungen](https://img.shields.io/badge/Nutzerprofil%20anpassen%20%26%20R%C3%BCckmeldung%20geben-lightgrey) |


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

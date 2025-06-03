# 📚 SchulSystem – Das digitale Schulverwaltungssystem

**SchulSystem** ist ein modulares Schulverwaltungssystem in Python, das IServ, WebUntis und andere Tools kombiniert – mit Fokus auf einfache Bedienung, erweiterbare Module und lokale Datenhaltung.

---

## ✨ Features

- 🔐 **Login-System** mit Benutzergruppen und Adminrechten  
- 🗓️ **Stundenplan- und Vertretungsplananzeige** mit Wochenansicht  
- 💬 **Nachrichtensystem** mit Gruppen- und Einzelnachrichten  
- 📂 **Dateiablage** mit Upload-/Download-Funktion  
- 👥 **Cloud-Modul** zum Freigeben von Dateien an Nutzer und Gruppen  
- 🧪 **E-Learning-Modul** für Tests und Ergebnisauswertung  
- 📒 **Klassenbuch** mit Hausaufgaben, Anwesenheit und Lehrstoff  
- 📌 **Kalender und Newsfeed** für Termine und schulweite Ankündigungen  
- ⚙️ **Adminbereich** zur Verwaltung von Nutzern, Gruppen und Einstellungen  
- 🔄 **Auto-Updater** via GitHub (optional)  

## Nutzung
git clone https://github.com/Lukas1120987/SchulSystem.git


## 🏗️ Aufbau

```plaintext
EduClass/
├── main.py                 # Hauptstartdatei
├── login.py                # Loginfenster
├── dashboard.py            # Zentrale Oberfläche
├── update_manager.py       # Automatisches Update-System
├── modules/                # Alle Funktionsmodule
│   ├── stundenplan.py
│   ├── nachrichten.py
│   └── ...
├── data/                   # JSON-Dateien zur Datenspeicherung (lokal)
│   ├── users.json
│   ├── messages.json
│   └── ...


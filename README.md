# 📚 SchulSystem – Das digitale Schulverwaltungssystem

![Alternativtext](https://cdn.discordapp.com/attachments/1380542231135653980/1380571204146167980/IMG_1509.jpeg?ex=68445ca0&is=68430b20&hm=5a68ff33fab0c76685586cc88a0778e9b98da0728d1716287372605e6ac7fdf3&)


**SchulSystem** ist ein modulares Schulverwaltungssystem in Python, das IServ, WebUntis und andere Tools kombiniert – mit Fokus auf einfache Bedienung, erweiterbare Module und lokale Datenhaltung.

---
## Wichtiges
Bevor du main.py startest, achte bitte darauf, dass du die `ZIP` entpackt hast.

---
## Enthaltene Module:

💬 Nachrichten
Versende und empfange schulinterne Nachrichten – mit Suchfunktion.

☁️ Cloud
Teile Dateien direkt mit Gruppen oder Einzelpersonen. Verwalte Freigaben und Zugriffsrechte komfortabel über eine übersichtliche Oberfläche.

🗂️ Dateiablage
Lade Dateien für alle hoch, speichere sie  ab und greife jederzeit lokal darauf zu.

🪑 Sitzplan
Erstelle Sitzpläne für Klassen mit Drag-and-Drop-Funktion – ideal zur Visualisierung und Organisation im Unterricht.

 🧪 E-Learning
Erstelle Tests, ordne sie Gruppen zu und werte Ergebnisse aus. Für digitales Lernen im Schulalltag.

 📅 Stundenplan
Zeigt deinen persönlichen Stundenplan (Wochenansicht), angepasst an deine Gruppenzugehörigkeit.

 🛠️ Stundenplanverwaltung
Erstelle, bearbeite und verwalte den Stundenplan zentral.

 📢 Meldungen
Erstelle neue Meldungen für Nachrichten oder Dateien.

 📝 Meldungenverwaltung
Anzeigen und bearbeiten von Meldungen.

 🧑‍🏫 Sprechstunden
Lehrkräfte können hier Sprechzeiten festlegen, Schüler buchen Termine.

📚 Ausleihe
Verwalte schulinterne Ausleihsysteme (z. B. Laptops, Bücher, Geräte) mit Ausleihe und Rückgabe.

🧑‍💼 Adminbereich
Zentraler Zugang für Administratoren zur Benutzerverwaltung und Gruppenzuweisung.

 🤧 Krankmeldungen
Ermöglicht einfache Abwesenheits- und Krankmeldungen mit Gruppenübersicht.

 ✅ ToDo‘s
Persönliche Aufgabenverwaltung für Schüler, Lehrer und Verwaltung – mit Status und Gruppenbindung.

 📆 Kalender
Zeigt alle schulischen Termine, Veranstaltungen, Prüfungen und individuelle Einträge in einer Monats- oder Wochenübersicht des Nutzers.

 🆘 Support
Erstelle Supporttickets, verfolge Bearbeitungsstatus und gib Rückmeldung – direkt an das Admin-Team.

 ⚙️ Einstellungen
Hier kannst du deinen Benutzernamen ändern, dein Passwort anpassen, Feedback geben oder das System personalisieren.

---
## 🚀 Nutzung

1. 🔽 **Download oder Clone** des Repositories:
   
bash
   git clone https://github.com/Lukas1120987/SchulSystem

2. 📂 **Extrahieren** der `ZIP`-Datei

---
## Kontakt
per Discord: https://discord.gg/NHgr4FKXE3

---

## 🏗️ Aufbau

```plaintext
SchulSystem/
├── main.py                 # Hauptstartdatei
├── login.py                # Loginfenster
├── dashboard.py            # Zentrale Oberfläche
├── updater.py       # Automatisches Update-System
├── modules/                # Alle Funktionsmodule
│   ├── stundenplan.py
│   ├── nachrichten.py
│   └── ...
├── data/                   # JSON-Dateien zur Datenspeicherung (lokal)
│   ├── users.json
│   ├── messages.json
│   └── ...


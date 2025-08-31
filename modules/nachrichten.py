import os
import json
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from ordner import get_data_path

# Pfade
USER_JSON_PATH = os.path.join(get_data_path(), "data/users.json")
NOTI_JSON_PATH = os.path.join(get_data_path(), "data/notifications.json")
MESS_JSON_PATH = os.path.join(get_data_path(), "data/messages.json")

# CTK Appearance (optional anpassbar)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class Modul:
    def __init__(self, parent, nutzername, user_data=None):
        # Hauptframe als CTkFrame
        self.frame = ctk.CTkFrame(parent)
        self.nutzername = nutzername
        self.user_data = user_data or {}

        # mapping der aktuell angezeigten nachrichten: iids -> globaler index
        self.anzeigen_indices = []

        self.baue_gui()

    def get_frame(self):
        return self.frame

    # --- Hilfsfunktionen ---
    def lade_nutzer(self):
        try:
            with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
                nutzer_daten = json.load(f)
            return list(nutzer_daten.keys())
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def lade_nachrichten_roh(self):
        try:
            with open(MESS_JSON_PATH, "r", encoding="utf-8") as f:
                nachrichten = json.load(f)
            # Sicherstellen, dass alle Nachrichten ein 'gelesen' feld haben
            changed = False
            for n in nachrichten:
                if "gelesen" not in n:
                    n["gelesen"] = False
                    changed = True
            if changed:
                with open(MESS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(nachrichten, f, indent=2, ensure_ascii=False)
            return nachrichten
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def schreibe_nachrichten_roh(self, nachrichten):
        with open(MESS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(nachrichten, f, indent=2, ensure_ascii=False)

    def lade_benachrichtigungen(self):
        try:
            with open(NOTI_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def schreibe_benachrichtigungen(self, benachrichtigungen):
        with open(NOTI_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(benachrichtigungen, f, indent=2, ensure_ascii=False)

    # --- GUI Aufbau ---
    def baue_gui(self):
        # Überschrift
        header = ctk.CTkLabel(self.frame, text="📨 Nachrichten", font=ctk.CTkFont(size=18, weight="bold"))
        header.pack(pady=(12,6), padx=10, anchor="w")

        # Obere Suchleiste
        oben = ctk.CTkFrame(self.frame)
        oben.pack(fill="x", padx=10)
        ctk.CTkLabel(oben, text="🔍 Suche:").pack(side="left", padx=(6,4))
        self.suche_entry = ctk.CTkEntry(oben)
        self.suche_entry.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.suche_entry.bind("<KeyRelease>", lambda e: self.filter_nachrichten())

        # Treeview Bereich (ttk innerhalb CTkFrame)
        tree_frame = ctk.CTkFrame(self.frame)
        tree_frame.pack(fill="both", expand=False, padx=10, pady=(8,6))

        # Scrollbar + Treeview
        self.tree_vscroll = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree_hscroll = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ("Neu", "Datum", "Von", "Betreff", "Aktion")
        self.nachrichtenliste = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=10,
            yscrollcommand=self.tree_vscroll.set,
            xscrollcommand=self.tree_hscroll.set
        )

        # Scrollbars konfigurieren
        self.tree_vscroll.config(command=self.nachrichtenliste.yview)
        self.tree_hscroll.config(command=self.nachrichtenliste.xview)

        # Kopfzeilen
        self.nachrichtenliste.heading("Neu", text="")
        self.nachrichtenliste.heading("Datum", text="Datum")
        self.nachrichtenliste.heading("Von", text="Von")
        self.nachrichtenliste.heading("Betreff", text="Betreff")
        self.nachrichtenliste.heading("Aktion", text="")

        # Spaltenbreiten
        self.nachrichtenliste.column("Neu", width=30, anchor="center", stretch=False)
        self.nachrichtenliste.column("Datum", width=140, anchor="w")
        self.nachrichtenliste.column("Von", width=120, anchor="w")
        self.nachrichtenliste.column("Betreff", width=420, anchor="w")
        self.nachrichtenliste.column("Aktion", width=40, anchor="center", stretch=False)

        # Pack Treeview + Scrollbars
        self.nachrichtenliste.grid(row=0, column=0, sticky="nsew")
        self.tree_vscroll.grid(row=0, column=1, sticky="ns")
        self.tree_hscroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Events
        self.nachrichtenliste.bind("<Double-1>", self._on_doubleclick_open)
        self.nachrichtenliste.bind("<Button-1>", self._on_click_tree)
        self.nachrichtenliste.bind("<Button-3>", self._on_right_click)  # Rechtsklick (Kontextmenü)

        # Kontextmenü
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Öffnen", command=self._context_open)
        self.context_menu.add_command(label="Löschen", command=self._context_delete)

        # Sende-Frame (Neue Nachricht)
        senden_frame = ctk.CTkFrame(self.frame)
        senden_frame.pack(fill="both", expand=False, padx=10, pady=(6,12))

        # Empfänger + Autocomplete (einfach)
        self.empfänger_entry = ctk.CTkEntry(senden_frame, placeholder_text="Empfänger eingeben...")
        self.empfänger_entry.pack(fill="x", pady=(6,4))
        self.empfänger_entry.bind("<KeyRelease>", lambda e: self.autocomplete_empfänger())

        # Vorschlags-Liste als Listbox (tk) eingebettet
        self.vorschlagsbox = tk.Listbox(senden_frame, height=3)
        self.vorschlagsbox.pack(fill="x", pady=(0,6))
        self.vorschlagsbox.bind("<Double-1>", lambda e: self._set_empfänger_from_listbox())

        self.betreff_entry = ctk.CTkEntry(senden_frame, placeholder_text="Betreff eingeben...")
        self.betreff_entry.pack(fill="x", pady=4)

        # Textfeld: CTk hat je nach version CTkTextbox, aber für Sicherheit nutzen wir tk.Text in einem Frame
        text_container = ctk.CTkFrame(senden_frame)
        text_container.pack(fill="both", expand=True, pady=(4,6))
        self.textfeld = tk.Text(text_container, height=6, wrap="word")
        self.textfeld.pack(side="left", fill="both", expand=True)
        self.text_scroll = ttk.Scrollbar(text_container, command=self.textfeld.yview)
        self.text_scroll.pack(side="right", fill="y")
        self.textfeld.config(yscrollcommand=self.text_scroll.set)

        # Senden-Button
        senden_btn = ctk.CTkButton(senden_frame, text="✅ Nachricht senden", command=self.senden)
        senden_btn.pack(pady=(6,8))

        # initial laden
        self.filter_nachrichten()

    # --- Nachrichten filtern und anzeigen ---
    def filter_nachrichten(self):
        suchbegriff = self.suche_entry.get().lower() if hasattr(self, "suche_entry") else ""
        self.nachrichtenliste.delete(*self.nachrichtenliste.get_children())
        self.anzeigen_indices = []

        nachrichten = self.lade_nachrichten_roh()

        # Nur empfänger = aktueller nutzer, sortiert nach datum desc
        def parse_datum(n):
            try:
                return datetime.strptime(n.get("datum", ""), "%d.%m.%Y %H:%M")
            except Exception:
                return datetime.min

        # Enumerate so wir globale indexe erhalten
        for idx, nachricht in sorted(enumerate(nachrichten), key=lambda iv: parse_datum(iv[1]), reverse=True):
            if nachricht.get("empfänger") != self.nutzername:
                continue
            betreff = nachricht.get("betreff", "").lower()
            inhalt = nachricht.get("inhalt", "").lower()
            if suchbegriff and (suchbegriff not in betreff and suchbegriff not in inhalt):
                continue

            # Visual für ungelesen
            neu_symbol = "●" if not nachricht.get("gelesen", False) else ""

            # Delete-Icon in Aktion-Spalte
            aktion_icon = "🗑️"

            # Insert mit iid = globaler index (so können wir später einfach darauf zugreifen)
            self.nachrichtenliste.insert("", "end", iid=str(idx), values=(
                neu_symbol,
                nachricht.get("datum", ""),
                nachricht.get("absender", ""),
                nachricht.get("betreff", ""),
                aktion_icon
            ))
            self.anzeigen_indices.append(idx)

    # --- Klick-Handler: erkennen ob Lösch-Spalte geklickt wurde ---
    def _on_click_tree(self, event):
        region = self.nachrichtenliste.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = self.nachrichtenliste.identify_column(event.x)  # z.B. "#5"
        row = self.nachrichtenliste.identify_row(event.y)
        if not row:
            return

        # Wenn Aktion-Spalte (letzte Spalte) -> löschen prompt
        # Spalten beginnen mit #1; wir haben 5 Spalten -> Aktion ist "#5"
        if col == "#5":
            global_index = int(row)
            if messagebox.askyesno("Löschen", "Möchten Sie diese Nachricht wirklich löschen?"):
                nachrichten = self.lade_nachrichten_roh()
                if 0 <= global_index < len(nachrichten):
                    del nachrichten[global_index]
                    self.schreibe_nachrichten_roh(nachrichten)
                    self.filter_nachrichten()
            return
        # ansonsten normale Auswahl (doppelklick öffnet)
        # wir lassen hier nichts weiter zu

    def _on_doubleclick_open(self, event):
        row = self.nachrichtenliste.identify_row(event.y)
        if not row:
            return
        self._open_message_by_iid(row)

    # --- Rechtsklick Kontextmenü ---
    def _on_right_click(self, event):
        rowid = self.nachrichtenliste.identify_row(event.y)
        if rowid:
            # selektieren und menu öffnen
            self.nachrichtenliste.selection_set(rowid)
            self.context_menu.tk_popup(event.x_root, event.y_root)
        else:
            # nichts selektiert
            pass

    def _context_open(self):
        sel = self.nachrichtenliste.selection()
        if sel:
            self._open_message_by_iid(sel[0])

    def _context_delete(self):
        sel = self.nachrichtenliste.selection()
        if not sel:
            return
        iid = sel[0]
        if messagebox.askyesno("Löschen", "Möchten Sie diese Nachricht wirklich löschen?"):
            global_index = int(iid)
            nachrichten = self.lade_nachrichten_roh()
            if 0 <= global_index < len(nachrichten):
                del nachrichten[global_index]
                self.schreibe_nachrichten_roh(nachrichten)
                self.filter_nachrichten()

    # --- Nachricht öffnen nach iid (globaler index) ---
    def _open_message_by_iid(self, iid):
        try:
            idx = int(iid)
        except ValueError:
            return
        nachrichten = self.lade_nachrichten_roh()
        if not (0 <= idx < len(nachrichten)):
            return
        nachricht = nachrichten[idx]

        # Markiere als gelesen wenn noch ungelesen
        if not nachricht.get("gelesen", False):
            nachricht["gelesen"] = True
            self.schreibe_nachrichten_roh(nachrichten)
            # Update Anzeige
            self.filter_nachrichten()

        # Neues Fenster (CTk) - inhalt via tk.Text weil einfacher
        fenster = ctk.CTkToplevel(self.frame)
        fenster.title(f"Nachricht von {nachricht.get('absender','')}")
        fenster.geometry("800x500")

        ctk.CTkLabel(fenster, text=f"Betreff: {nachricht.get('betreff','')}", anchor="w",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(fill="x", padx=10, pady=(10,5))
        ctk.CTkLabel(fenster, text=f"Datum: {nachricht.get('datum','')}  |  Von: {nachricht.get('absender','')}", anchor="w").pack(fill="x", padx=10, pady=(0,8))

        inhalt_frame = ctk.CTkFrame(fenster)
        inhalt_frame.pack(fill="both", expand=True, padx=10, pady=6)

        text_widget = tk.Text(inhalt_frame, wrap="word", state="normal")
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.insert("1.0", nachricht.get("inhalt",""))
        text_widget.config(state="disabled")

        scrollbar = ttk.Scrollbar(inhalt_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)

        ctk.CTkButton(fenster, text="Schließen", command=fenster.destroy).pack(pady=6)

    # --- Senden ---
    def senden(self):
        empfänger = self.empfänger_entry.get().strip()
        betreff = self.betreff_entry.get().strip()
        inhalt = self.textfeld.get("1.0", tk.END).strip()

        if not empfänger or not betreff or not inhalt:
            messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllt werden.")
            return

        try:
            with open(USER_JSON_PATH, "r", encoding="utf-8") as f:
                nutzer_daten = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Fehler", "Benutzerdaten konnten nicht geladen werden.")
            return

        if empfänger not in nutzer_daten:
            messagebox.showerror("Fehler", f"Der Nutzer '{empfänger}' existiert nicht.")
            return

        if nutzer_daten[empfänger].get("kontaktierbar") is False:
            messagebox.showwarning("Nicht möglich", f"Der Nutzer '{empfänger}' kann nicht kontaktiert werden.")
            return

        neue_nachricht = {
            "absender": self.nutzername,
            "empfänger": empfänger,
            "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "betreff": betreff,
            "inhalt": inhalt,
            "gelesen": False
        }

        nachrichten = self.lade_nachrichten_roh()
        nachrichten.append(neue_nachricht)
        self.schreibe_nachrichten_roh(nachrichten)

        # Benachrichtigungen
        benachrichtigungen = self.lade_benachrichtigungen()
        if empfänger not in benachrichtigungen:
            benachrichtigungen[empfänger] = []
        benachrichtigungen[empfänger].append({
            "text": f"Neue Nachricht von {self.nutzername} \n Betreff: {betreff} \n {inhalt}",
            "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "gelesen": False
        })
        self.schreibe_benachrichtigungen(benachrichtigungen)

        messagebox.showinfo("Erfolg", "Nachricht erfolgreich gesendet.")
        self.empfänger_entry.delete(0, tk.END)
        self.betreff_entry.delete(0, tk.END)
        self.textfeld.delete("1.0", tk.END)
        self.filter_nachrichten()

    # --- Autocomplete für Empfänger ---
    def autocomplete_empfänger(self):
        empfänger_input = self.empfänger_entry.get().lower()
        self.vorschlagsbox.delete(0, tk.END)
        if empfänger_input:
            for nutzer in self.lade_nutzer():
                if nutzer.lower().startswith(empfänger_input) and nutzer != self.nutzername:
                    self.vorschlagsbox.insert(tk.END, nutzer)

    def _set_empfänger_from_listbox(self):
        sel = self.vorschlagsbox.curselection()
        if sel:
            val = self.vorschlagsbox.get(sel[0])
            self.empfänger_entry.delete(0, tk.END)
            self.empfänger_entry.insert(0, val)
            self.vorschlagsbox.delete(0, tk.END)


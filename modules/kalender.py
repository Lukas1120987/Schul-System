import customtkinter as ctk
import json
import os
from tkcalendar import Calendar
from tkinter import messagebox
from ordner import get_data_path

USER_JSON_PATH = os.path.join(get_data_path(), "data/users.json")
KAL_JSON_PATH = os.path.join(get_data_path(), "data/kalender.json")

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


CATEGORY_COLORS = {
    "klausur": "#e74c3c",
    "test": "#f39c12",
    "event": "#3498db",
    "sonstiges": "#9b59b6"
}


class Modul:
    def __init__(self, parent, username, user_data):
        self.parent = parent
        self.username = username
        self.user_data = user_data

        self.group = user_data.get("group", "all").lower()
        self.second_group = user_data.get("second_group", "").lower()
        self.is_admin = user_data.get("is_admin", False)

        self.data_file = KAL_JSON_PATH
        self.users_file = USER_JSON_PATH
        self.selected_entry = None

        self.frame = ctk.CTkFrame(parent, corner_radius=12)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.load_dates()
        self.create_widgets()
        self.update_display()

    def get_frame(self):
        return self.frame

    # ---------- UI ----------
    def create_widgets(self):
        ctk.CTkLabel(
            self.frame,
            text="Kalender",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=10)

        self.calendar = Calendar(self.frame, date_pattern="dd.mm.yyyy")
        self.calendar.pack(pady=5)

        # Suche
        self.search_entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="🔍 Termine durchsuchen..."
        )
        self.search_entry.pack(fill="x", padx=20, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_display())

        self.display = ctk.CTkTextbox(self.frame, height=220)
        self.display.pack(fill="both", expand=True, padx=20, pady=10)
        self.display.configure(state="disabled")

        if self.is_admin:
            self.create_admin_section()

    def create_admin_section(self):
        admin = ctk.CTkFrame(self.frame)
        admin.pack(fill="x", padx=20, pady=10)

        self.entry_title = ctk.CTkEntry(admin, placeholder_text="Titel")
        self.entry_title.pack(fill="x", pady=4)

        self.entry_desc = ctk.CTkEntry(admin, placeholder_text="Beschreibung")
        self.entry_desc.pack(fill="x", pady=4)

        self.entry_category = ctk.CTkEntry(admin, placeholder_text="Kategorie (z.B. Klausur)")
        self.entry_category.pack(fill="x", pady=4)

        self.entry_target = ctk.CTkEntry(
            admin,
            placeholder_text="Zielgruppen (z.B. 10A, 10B, alle)"
        )
        self.entry_target.pack(fill="x", pady=4)

        ctk.CTkButton(
            admin,
            text="💾 Speichern / Aktualisieren",
            command=self.save_entry
        ).pack(pady=5)

        ctk.CTkButton(
            admin,
            text="🗑 Termin löschen",
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self.delete_entry
        ).pack(pady=3)

    # ---------- Daten ----------
    def load_dates(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.dates = json.load(f)
        except:
            self.dates = {}

    def save_dates(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.dates, f, indent=2, ensure_ascii=False)

    # ---------- Anzeige ----------
    def update_display(self):
        key = self.calendar.get_date()
        query = self.search_entry.get().lower()

        self.display.configure(state="normal")
        self.display.delete("1.0", "end")

        self.visible_entries = []

        for entry in self.dates.get(key, []):
            targets = [t.strip().lower() for t in entry["target"].split(",")]

            if not any(t in targets for t in [self.group, self.second_group, "alle"]):
                continue

            text = f"{entry['title']} {entry['desc']} {entry['category']}".lower()
            if query and query not in text:
                continue

            self.visible_entries.append(entry)

            color = CATEGORY_COLORS.get(entry["category"].lower(), "#7f8c8d")

            self.display.insert(
                "end",
                f"● {entry['title']} ({entry['category']})\n",
                entry["title"]
            )
            self.display.insert("end", f"  {entry['desc']}\n\n")

            self.display.tag_config(entry["title"], foreground=color)

        self.display.configure(state="disabled")

        self.display.bind("<Button-1>", self.on_click_entry)

    # ---------- Bearbeiten ----------
    def on_click_entry(self, event):
        index = self.display.index("@%s,%s" % (event.x, event.y))
        line = int(index.split(".")[0]) - 1

        if line < len(self.visible_entries):
            self.selected_entry = self.visible_entries[line]
            self.load_entry_to_form()

    def load_entry_to_form(self):
        e = self.selected_entry
        self.entry_title.delete(0, "end")
        self.entry_desc.delete(0, "end")
        self.entry_category.delete(0, "end")
        self.entry_target.delete(0, "end")

        self.entry_title.insert(0, e["title"])
        self.entry_desc.insert(0, e["desc"])
        self.entry_category.insert(0, e["category"])
        self.entry_target.insert(0, e["target"])

    def save_entry(self):
        key = self.calendar.get_date()

        entry = {
            "title": self.entry_title.get().strip(),
            "desc": self.entry_desc.get().strip(),
            "category": self.entry_category.get().strip(),
            "target": self.entry_target.get().strip(),
        }

        if not all(entry.values()):
            messagebox.showerror("Fehler", "Alle Felder ausfüllen.")
            return

        if self.selected_entry:
            self.dates[key].remove(self.selected_entry)

        self.dates.setdefault(key, []).append(entry)
        self.selected_entry = None
        self.save_dates()
        self.update_display()

        messagebox.showinfo("Gespeichert", "Termin gespeichert.")

    def delete_entry(self):
        if not self.selected_entry:
            messagebox.showwarning("Hinweis", "Kein Termin ausgewählt.")
            return

        if not messagebox.askyesno("Löschen", "Termin wirklich löschen?"):
            return

        key = self.calendar.get_date()
        self.dates[key].remove(self.selected_entry)
        self.selected_entry = None
        self.save_dates()
        self.update_display()

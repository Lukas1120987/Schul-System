import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class Modul:
    def __init__(self, parent, username, user_data):
        self.parent = parent
        self.username = username
        self.group = user_data.get("group", "alle")
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(parent, bg="white")

        self.user_tasks_file = "data/aufgaben_user.json"
        self.group_tasks_file = "data/aufgaben_gruppen.json"

        self.load_tasks()
        self.create_widgets()

    def get_frame(self):
        return self.frame

    def load_tasks(self):
        try:
            with open(self.user_tasks_file, "r", encoding="utf-8") as f:
                self.user_tasks = json.load(f)
        except:
            self.user_tasks = {}

        try:
            with open(self.group_tasks_file, "r", encoding="utf-8") as f:
                self.group_tasks = json.load(f)
        except:
            self.group_tasks = {}

    def save_tasks(self):
        with open(self.user_tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.user_tasks, f, indent=2)
        with open(self.group_tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.group_tasks, f, indent=2)

    def create_widgets(self):
        title = tk.Label(self.frame, text="Aufgaben & ToDos", font=("Segoe UI", 18), bg="white")
        title.pack(pady=10)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.personal_tab = tk.Frame(self.notebook, bg="white")
        self.group_tab = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.personal_tab, text="Aufgaben")
        self.notebook.add(self.group_tab, text="Gruppenaufgaben")

        self.build_personal_tab()
        self.build_group_tab()

    def build_personal_tab(self):
        self.personal_tasks_box = tk.Listbox(self.personal_tab, width=80, height=10)
        self.personal_tasks_box.pack(pady=5)

        self.refresh_personal_tasks()

        entry_frame = tk.Frame(self.personal_tab, bg="white")
        entry_frame.pack(pady=5)

        self.personal_entry = tk.Entry(entry_frame, width=50)
        self.personal_entry.pack(side="left", padx=5)
        tk.Button(entry_frame, text="Hinzufügen", command=self.add_personal_task).pack(side="left")

        btn_frame = tk.Frame(self.personal_tab, bg="white")
        btn_frame.pack()

        tk.Button(btn_frame, text="Erledigt", command=self.mark_personal_done).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Löschen", command=self.delete_personal_task).pack(side="left", padx=5)

    def build_group_tab(self):
        self.group_tasks_box = tk.Listbox(self.group_tab, width=80, height=10)
        self.group_tasks_box.pack(pady=5)

        self.refresh_group_tasks()

        if self.is_admin:
            separator = ttk.Separator(self.group_tab, orient="horizontal")
            separator.pack(fill="x", pady=10)

            form_frame = tk.LabelFrame(self.group_tab, text="Neue Gruppenaufgabe", bg="white")
            form_frame.pack(fill="x", padx=10, pady=5)

            self.group_title_entry = tk.Entry(form_frame, width=40)
            self.group_title_entry.insert(0, "Titel der Aufgabe")
            self.group_title_entry.pack(pady=2)

            self.group_target_entry = tk.Entry(form_frame, width=30)
            self.group_target_entry.insert(0, "Zielgruppe (z. B. 10A oder alle)")
            self.group_target_entry.pack(pady=2)

            tk.Button(form_frame, text="Veröffentlichen", command=self.add_group_task).pack(pady=5)

    def refresh_personal_tasks(self):
        self.personal_tasks_box.delete(0, "end")
        for task in self.user_tasks.get(self.username, []):
            status = "[✓]" if task.get("done") else "[  ]"
            self.personal_tasks_box.insert("end", f"{status} {task['text']}")

    def refresh_group_tasks(self):
        self.group_tasks_box.delete(0, "end")
        for task in self.group_tasks.get(self.group, []) + self.group_tasks.get("alle", []):
            date = task.get("date", "")
            self.group_tasks_box.insert("end", f"- {task['title']} ({date})")

    def add_personal_task(self):
        text = self.personal_entry.get().strip()
        if not text:
            return
        self.user_tasks.setdefault(self.username, []).append({"text": text, "done": False})
        self.save_tasks()
        self.refresh_personal_tasks()
        self.personal_entry.delete(0, "end")

    def mark_personal_done(self):
        idx = self.personal_tasks_box.curselection()
        if not idx:
            return
        index = idx[0]
        self.user_tasks[self.username][index]["done"] = True
        self.save_tasks()
        self.refresh_personal_tasks()

    def delete_personal_task(self):
        idx = self.personal_tasks_box.curselection()
        if not idx:
            return
        index = idx[0]
        del self.user_tasks[self.username][index]
        self.save_tasks()
        self.refresh_personal_tasks()

    def add_group_task(self):
        title = self.group_title_entry.get().strip()
        target = self.group_target_entry.get().strip().lower()
        if not title or not target:
            messagebox.showerror("Fehler", "Bitte Titel und Zielgruppe angeben.")
            return
        task = {"title": title, "date": datetime.now().strftime("%d.%m.%Y")}
        self.group_tasks.setdefault(target, []).append(task)
        self.save_tasks()
        self.refresh_group_tasks()
        messagebox.showinfo("Gespeichert", "Aufgabe wurde veröffentlicht.")

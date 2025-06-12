import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

DATA_DIR = "data"
FILES = {
    "subjects": "data/subjects.json",
    "rooms": "data/rooms.json",
    "timeslots": "data/timeslots.json",
    "teachers": "data/teachers.json",
    "schedule": "data/schedule.json",
    "users": "data/users.json",
    "vertretungen": "data/vertretungen.json",
    "organisation": "data/organisation.json"
}


def load_json(name):
    try:
        with open(os.path.join(DATA_DIR, FILES[name]), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(name, data):
    with open(os.path.join(DATA_DIR, FILES[name]), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class Modul:
    def __init__(self, master, username=None, user_data=None):
        self.master = master
        self.username = username
        self.user_data = user_data

        self.frame = tk.Frame(master, bg="white")  # Hauptcontainer
        self.frame.place(x=0, y=50, relwidth=1, relheight=1) 

        self.tabs = ttk.Notebook(self.frame)
        self.tabs.place(x=0, y=55, relwidth=1, relheight=1, height=-50)


        self.setup_stammdaten_tab()
        self.setup_lehrer_tab()
        self.setup_stundenplan_tab()

    def get_frame(self):
        return self.frame

    # --- Stammdaten ---
    def setup_stammdaten_tab(self):
        tab = tk.Frame(self.tabs)
        self.tabs.add(tab, text="📚 Stammdaten")

        # Fächer
        self.subjects = load_json("subjects")
        tk.Label(tab, text="Fächer").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.subject_entry = tk.Entry(tab)
        self.subject_entry.grid(row=1, column=0, padx=10)
        tk.Button(tab, text="➕ Hinzufügen", command=self.add_subject).grid(row=1, column=1)
        self.subject_list = tk.Listbox(tab, height=5)
        self.subject_list.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        for s in self.subjects:
            self.subject_list.insert(tk.END, s)

        # Räume
        self.rooms = load_json("rooms")
        tk.Label(tab, text="Räume").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.room_entry = tk.Entry(tab)
        self.room_entry.grid(row=4, column=0, padx=10)
        tk.Button(tab, text="➕ Hinzufügen", command=self.add_room).grid(row=4, column=1)
        self.room_list = tk.Listbox(tab, height=5)
        self.room_list.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        for r in self.rooms:
            self.room_list.insert(tk.END, r)

        # Zeiten
        self.times = load_json("timeslots")
        tk.Label(tab, text="Unterrichtszeiten (z.B. 08:00-08:45)").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.timeslots_entries = []
        for i in range(8):
            e = tk.Entry(tab)
            e.insert(0, self.times.get(str(i+1), ""))
            e.grid(row=7+i, column=0, padx=10)
            self.timeslots_entries.append(e)

        tk.Button(tab, text="💾 Zeiten speichern", command=self.save_times).grid(row=15, column=0, pady=10)

    def add_subject(self):
        s = self.subject_entry.get().strip()
        if s and s not in self.subjects:
            self.subjects.append(s)
            self.subject_list.insert(tk.END, s)
            save_json("subjects", self.subjects)
            self.subject_entry.delete(0, tk.END)

    def add_room(self):
        r = self.room_entry.get().strip()
        if r and r not in self.rooms:
            self.rooms.append(r)
            self.room_list.insert(tk.END, r)
            save_json("rooms", self.rooms)
            self.room_entry.delete(0, tk.END)

    def save_times(self):
        new_times = {str(i+1): e.get().strip() for i, e in enumerate(self.timeslots_entries)}
        save_json("timeslots", new_times)
        messagebox.showinfo("Gespeichert", "Zeiten gespeichert.")

    # --- Lehrkräfte ---
    def setup_lehrer_tab(self):
        tab = tk.Frame(self.tabs)
        self.tabs.add(tab, text="👨‍🏫 Lehrer")

        self.users = load_json("users")
        self.subjects = load_json("subjects")
        self.teachers_data = load_json("teachers")

        self.lehrer_liste = [u for u, d in self.users.items() if d.get("group") == "Lehrer"]

        tk.Label(tab, text="Lehrkraft auswählen:").grid(row=0, column=0, padx=10, pady=5)
        self.selected_teacher = tk.StringVar()
        self.teacher_menu = ttk.Combobox(tab, textvariable=self.selected_teacher, values=self.lehrer_liste)
        self.teacher_menu.grid(row=0, column=1, padx=10)
        self.teacher_menu.bind("<<ComboboxSelected>>", self.load_teacher_data)

        self.fach_vars = {}
        tk.Label(tab, text="Fächer:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        for i, subject in enumerate(self.subjects):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(tab, text=subject, variable=var)
            cb.grid(row=2+i//5, column=i%5, padx=5, sticky="w")
            self.fach_vars[subject] = var

        self.nicht_verfuegbar = {}
        tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        tk.Label(tab, text="Nicht verfügbar:").grid(row=7, column=0, sticky="w", padx=10)
        for i, tag in enumerate(tage):
            self.nicht_verfuegbar[tag] = []
            for h in range(1, 9):
                var = tk.BooleanVar()
                cb = tk.Checkbutton(tab, text=f"{tag[:2]} {h}", variable=var)
                cb.grid(row=8+i, column=h, sticky="w")
                self.nicht_verfuegbar[tag].append(var)

        tk.Button(tab, text="💾 Speichern", command=self.save_teacher_data).grid(row=14, column=0, pady=10)

    def load_teacher_data(self, event=None):
        name = self.selected_teacher.get()
        data = self.teachers_data.get(name, {})
        faecher = data.get("faecher", [])
        for f in self.fach_vars:
            self.fach_vars[f].set(f in faecher)

        for tag in self.nicht_verfuegbar:
            for i in range(8):
                try:
                    self.nicht_verfuegbar[tag][i].set(str(i+1) in data.get("nicht_verfuegbar", {}).get(tag, []))
                except:
                    self.nicht_verfuegbar[tag][i].set(False)

    def save_teacher_data(self):
        name = self.selected_teacher.get()
        faecher = [f for f, v in self.fach_vars.items() if v.get()]
        nicht = {}
        for tag in self.nicht_verfuegbar:
            nicht[tag] = [str(i+1) for i, var in enumerate(self.nicht_verfuegbar[tag]) if var.get()]
        self.teachers_data[name] = {"faecher": faecher, "nicht_verfuegbar": nicht}
        save_json("teachers", self.teachers_data)
        messagebox.showinfo("Gespeichert", f"Lehrkraft {name} gespeichert.")

    # --- Stundenplan ---
    def setup_stundenplan_tab(self):
        tab = tk.Frame(self.tabs)
        self.tabs.add(tab, text="📅 Stundenplan")

        self.schedule_data = load_json("schedule")
        self.subjects = load_json("subjects")
        self.rooms = load_json("rooms")
        self.teachers_data = load_json("teachers")

        self.classes = sorted({d.get("second_group") for d in load_json("users").values() if "second_group" in d})
        self.selected_class = tk.StringVar()
        ttk.Combobox(tab, textvariable=self.selected_class, values=self.classes).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(tab, text="🗓️ Laden", command=lambda: self.load_schedule_editor(tab)).grid(row=0, column=1)

        self.schedule_widgets = {}

    def load_schedule_editor(self, parent):
        for widget in parent.winfo_children()[1:]:
            widget.destroy()

        group = self.selected_class.get()
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

        for col, day in enumerate(["Stunde"] + days):
            tk.Label(parent, text=day, relief="solid", width=18).grid(row=1, column=col)

        self.schedule_widgets = {}

        for hour in range(1, 9):
            tk.Label(parent, text=str(hour), relief="solid", width=8).grid(row=1+hour, column=0)

            for col, day in enumerate(days):
                frame = tk.Frame(parent)
                frame.grid(row=1+hour, column=1+col)

                subject_cb = ttk.Combobox(frame, values=[""] + self.subjects + ["Pause", "Frei"], width=12)
                teacher_cb = ttk.Combobox(frame, values=list(self.teachers_data.keys()), width=12)
                room_cb = ttk.Combobox(frame, values=self.rooms, width=8)

                subject_cb.pack()
                teacher_cb.pack()
                room_cb.pack()

                self.schedule_widgets[(day, str(hour))] = (subject_cb, teacher_cb, room_cb)

        tk.Button(parent, text="💾 Speichern", command=self.save_schedule).grid(row=11, column=0, pady=10)

    def save_schedule(self):
        group = self.selected_class.get()
        self.schedule_data[group] = {}
        for (day, hour), (subject_cb, teacher_cb, room_cb) in self.schedule_widgets.items():
            fach = subject_cb.get().strip()
            lehrer = teacher_cb.get().strip()
            raum = room_cb.get().strip()

            if fach or lehrer or raum:
                self.schedule_data[group].setdefault(day, {})[hour] = {
                    "fach": fach,
                    "lehrer": lehrer,
                    "raum": raum
                }

        save_json("schedule", self.schedule_data)
        messagebox.showinfo("Gespeichert", f"Stundenplan für {group} gespeichert.")

# Start der Anwendung
if __name__ == "__main__":
    root = tk.Tk()
    app = Modul(root)
    root.mainloop()

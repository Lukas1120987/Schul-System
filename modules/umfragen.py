import tkinter as tk
from tkinter import messagebox
import json, os

class Modul:
    def __init__(self, parent, username=None, user_data=None):
        self.username = username
        self.user_data = user_data
        self.frame = tk.Frame(parent)
        self.surveys_file = "data/surveys.json"
        self.groups_file = "data/groups.json"
        self.umfragen = self.load(self.surveys_file)  # direkt load() nutzen
        self.groups = self.load(self.groups_file)
        self.current = None
        self.mode = None  # None, "edit", "answer", "results"
        self.message_text = tk.StringVar()
        self.build_ui()
        self.refresh()

    def load(self, path):
        if os.path.exists(path):
            return json.load(open(path, "r", encoding="utf-8"))
        return {} if path.endswith(".json") else []

    def get_frame(self):
            if self.frame:
                self.frame.destroy()
            self.frame = tk.Frame(self.parent)

    def save(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    def in_verwaltung(self):
        if not self.user_data:
            return False
        return "Verwaltung" in (self.user_data.get("group", ""), self.user_data.get("second_group", ""))

    def build_ui(self):
        top = tk.Frame(self.frame)
        top.pack(fill="x", pady=5)
        tk.Label(top, text="Umfragen‑Modul", font=('',14,'bold')).pack(side="left", padx=5)
        btns = tk.Frame(self.frame)
        btns.pack(fill="x", pady=5)
        self.btn_new = tk.Button(btns, text="Neu", command=self.neu)
        self.btn_start = tk.Button(btns, text="Start", command=self.start)
        self.btn_stop = tk.Button(btns, text="Stop", command=self.stop)
        self.btn_answer = tk.Button(btns, text="Beantworten", command=self.beantworten)
        self.btn_results = tk.Button(btns, text="Ergebnisse", command=self.results)
        for b in (self.btn_new, self.btn_start, self.btn_stop, self.btn_answer, self.btn_results):
            b.pack(side="left", padx=3)

        mid = tk.Frame(self.frame)
        mid.pack(fill="both", expand=True)
        # Linke Seite: Liste der Umfragen
        self.lb = tk.Listbox(mid, height=10)
        self.lb.pack(side="left", padx=5, pady=5, fill="y")
        self.lb.bind("<<ListboxSelect>>", self.on_select)

        # Rechte Seite: Canvas für Details / Editor / Antwort / Ergebnisse
        self.canvas = tk.Frame(mid)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Message / Statusleiste unten
        self.status = tk.Label(self.frame, textvariable=self.message_text, fg="blue", anchor="w")
        self.status.pack(fill="x", padx=5, pady=3)

    def refresh(self):
        self.message_text.set("")
        self.lb.delete(0, "end")
        for idx, u in enumerate(self.umfragen):
            st = "aktiv" if u.get("active") else "inaktiv"
            title = u.get("title", "(kein Titel)")
            # Aktive Umfragen farblich hervorheben:
            display_text = f"{title} – {st}"
            self.lb.insert("end", display_text)
            if u.get("active"):
                self.lb.itemconfig(idx, fg="green")
            else:
                self.lb.itemconfig(idx, fg="black")
        self.update_buttons()
        self.render_canvas()

    def update_buttons(self):
        admin = self.in_verwaltung()
        self.btn_new["state"] = "normal" if admin else "disabled"
        self.btn_start["state"] = self.btn_stop["state"] = self.btn_results["state"] = "normal" if admin else "disabled"
        self.btn_answer["state"] = "normal"
        # Wenn keine Auswahl, disable start/stop/results
        if not self.current:
            self.btn_start["state"] = "disabled"
            self.btn_stop["state"] = "disabled"
            self.btn_results["state"] = "disabled"

    def on_select(self, evt):
        sel = self.lb.curselection()
        if not sel:
            self.current = None
            self.message_text.set("Keine Umfrage ausgewählt.")
            self.update_buttons()
            self.render_canvas()
            return
        i = sel[0]
        self.current = self.umfragen[i]
        self.message_text.set(f"Auswahl: {self.current.get('title', '')} ({'aktiv' if self.current.get('active') else 'inaktiv'})")
        self.update_buttons()
        self.render_canvas()

    def neu(self):
        if not self.in_verwaltung():
            self.message_text.set("Du hast keine Berechtigung, eine Umfrage zu erstellen.")
            return
        self.mode = "edit"
        self.current = {"title":"Neue Umfrage", "active":False, "questions":[], "results":[], "users_voted":[]}
        self.render_canvas()

    def start(self):
        if not self.current or not self.in_verwaltung():
            self.message_text.set("Starten nicht möglich.")
            return
        self.current["active"] = True
        self.save(self.surveys_file, self.umfragen)
        self.message_text.set(f"Umfrage '{self.current['title']}' gestartet.")
        self.refresh()

    def stop(self):
        if not self.current or not self.in_verwaltung():
            self.message_text.set("Stoppen nicht möglich.")
            return
        self.current["active"] = False
        self.save(self.surveys_file, self.umfragen)
        self.message_text.set(f"Umfrage '{self.current['title']}' gestoppt.")
        self.refresh()

    def render_canvas(self):
        # Canvas leeren
        for w in self.canvas.winfo_children():
            w.destroy()
        self.message_text.set("")

        if self.mode == "edit":
            self.edit_ui()
        elif self.mode == "answer":
            if self.current and self.current.get("active"):
                self.answer_ui()
            else:
                tk.Label(self.canvas, text="Keine Umfrage aktiv", fg="gray").pack(pady=20)
        elif self.mode == "results":
            self.results_ui()
        else:
            # Normalansicht - Details der Umfrage und Fragenliste wenn ausgewählt
            if self.current:
                self.view_ui()
            else:
                tk.Label(self.canvas, text="Keine Umfrage ausgewählt.", fg="gray").pack(pady=20)

    ##########################
    # View-Modus (Details & Fragen anzeigen)
    ##########################
    def view_ui(self):
        # Titel
        tk.Label(self.canvas, text=f"Titel: {self.current.get('title','')}", font=('',12,'bold')).pack(anchor="w", padx=5, pady=5)

        # Fragen mit Antworten und ggf. löschen/bearbeiten (für Admin)
        qframe = tk.Frame(self.canvas)
        qframe.pack(fill="both", expand=True, padx=5, pady=5)

        # Überschrift und ggf. Button "Frage hinzufügen"
        top = tk.Frame(qframe)
        top.pack(fill="x")
        tk.Label(top, text="Fragen:", font=('',11,'underline')).pack(side="left")
        if self.in_verwaltung():
            tk.Button(top, text="Frage hinzufügen", command=self.open_add_question).pack(side="right")

        # Liste der Fragen
        for i, q in enumerate(self.current.get("questions", [])):
            frm = tk.LabelFrame(qframe, text=f"Frage {i+1}: {q.get('frage','')}")
            frm.pack(fill="x", pady=3)
            # Antwortmöglichkeiten anzeigen
            opts_text = ", ".join(q.get("options", []))
            tk.Label(frm, text=f"Typ: {q.get('typ','')} — Optionen: {opts_text}").pack(anchor="w")

            if self.in_verwaltung():
                btns = tk.Frame(frm)
                btns.pack(anchor="e")
                tk.Button(btns, text="Bearbeiten", command=lambda i=i: self.open_edit_question(i)).pack(side="left", padx=3)
                tk.Button(btns, text="Löschen", command=lambda i=i: self.delete_question(i)).pack(side="left", padx=3)

    ##########################
    # Frage hinzufügen / bearbeiten als UI unterhalb (kein Popup!)
    ##########################
    def open_add_question(self):
        self.message_text.set("")
        self.edit_question_ui(new=True)

    def open_edit_question(self, index):
        self.message_text.set("")
        self.edit_question_ui(new=False, index=index)

    def edit_question_ui(self, new=True, index=None):
        # Canvas komplett leeren und UI für Frage bearbeiten anzeigen
        for w in self.canvas.winfo_children():
            w.destroy()
        frame = self.canvas

        # Variablen für Eingaben
        frage_var = tk.StringVar()
        typ_var = tk.StringVar(value="single")
        opts_var = tk.StringVar()

        if not new and index is not None:
            q = self.current["questions"][index]
            frage_var.set(q.get("frage",""))
            typ_var.set(q.get("typ","single"))
            opts_var.set(", ".join(q.get("options", [])))

        tk.Label(frame, text="Frage bearbeiten" if not new else "Neue Frage", font=('',13,'bold')).pack(anchor="w", padx=5, pady=5)

        # Frage-Text
        tk.Label(frame, text="Fragetext:").pack(anchor="w", padx=5)
        frage_entry = tk.Entry(frame, textvariable=frage_var, width=50)
        frage_entry.pack(fill="x", padx=5, pady=2)

        # Fragetyp
        tk.Label(frame, text="Typ:").pack(anchor="w", padx=5)
        typ_frame = tk.Frame(frame)
        typ_frame.pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(typ_frame, text="Single Choice", variable=typ_var, value="single").pack(side="left", padx=5)
        tk.Radiobutton(typ_frame, text="Multiple Choice", variable=typ_var, value="multi").pack(side="left", padx=5)

        # Optionen (mit Komma getrennt)
        tk.Label(frame, text="Antwortoptionen (Komma getrennt):").pack(anchor="w", padx=5)
        opts_entry = tk.Entry(frame, textvariable=opts_var, width=50)
        opts_entry.pack(fill="x", padx=5, pady=2)

        # Fehlermeldung
        err_msg = tk.StringVar()
        err_lbl = tk.Label(frame, textvariable=err_msg, fg="red")
        err_lbl.pack(anchor="w", padx=5, pady=3)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)

        def save_question():
            frage = frage_var.get().strip()
            typ = typ_var.get()
            options = [o.strip() for o in opts_var.get().split(",") if o.strip()]
            if not frage:
                err_msg.set("Die Frage darf nicht leer sein.")
                return
            if not options:
                err_msg.set("Bitte mindestens eine Antwortoption angeben.")
                return
            # Speichern
            qdata = {"frage": frage, "typ": typ, "options": options}
            if new:
                self.current["questions"].append(qdata)
            else:
                self.current["questions"][index] = qdata
            self.save(self.surveys_file, self.umfragen)
            self.mode = None
            self.message_text.set("Frage gespeichert.")
            self.refresh()

        def cancel():
            self.mode = None
            self.message_text.set("Bearbeitung abgebrochen.")
            self.refresh()

        tk.Button(btn_frame, text="Speichern", command=save_question).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Abbrechen", command=cancel).pack(side="left", padx=10)

    ##########################
    # Frage löschen
    ##########################
    def delete_question(self, index):
        if not self.in_verwaltung():
            self.message_text.set("Keine Berechtigung zum Löschen.")
            return
        del self.current["questions"][index]
        self.save(self.surveys_file, self.umfragen)
        self.message_text.set("Frage gelöscht.")
        self.refresh()

    ##########################
    # Antwort-Modus UI
    ##########################
    def beantworten(self):
        if not self.current:
            self.message_text.set("Keine Umfrage ausgewählt.")
            return
        if not self.current.get("active"):
            self.message_text.set("Diese Umfrage ist nicht aktiv.")
            return
        if self.username in self.current.get("users_voted", []):
            self.message_text.set("Du hast diese Umfrage bereits beantwortet.")
            return
        self.mode = "answer"
        self.render_canvas()

    def answer_ui(self):
        frame = self.canvas
        tk.Label(frame, text=f"Umfrage: {self.current.get('title','')}", font=('',13,'bold')).pack(anchor="w", padx=5, pady=5)
        questions = self.current.get("questions", [])
        if not questions:
            tk.Label(frame, text="Keine Fragen vorhanden.", fg="gray").pack(pady=20)
            return
        self.answers = []

        self.answer_vars = []  # Liste für Antwort-Variablen (StringVar oder Liste von BooleanVar)

        canvas_scroll = tk.Canvas(frame)
        scroll_frame = tk.Frame(canvas_scroll)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas_scroll.yview)
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        canvas_scroll.create_window((0, 0), window=scroll_frame, anchor="nw")

        for idx, q in enumerate(questions):
            qframe = tk.LabelFrame(scroll_frame, text=f"Frage {idx+1}: {q.get('frage','')}", padx=5, pady=5)
            qframe.pack(fill="x", pady=3)
            if q.get("typ") == "single":
                var = tk.StringVar()
                self.answer_vars.append(var)
                for opt in q.get("options", []):
                    rb = tk.Radiobutton(qframe, text=opt, variable=var, value=opt)
                    rb.pack(anchor="w")
            else:
                # multiple choice -> Liste von BooleanVars
                vars_multi = []
                self.answer_vars.append(vars_multi)
                for opt in q.get("options", []):
                    bvar = tk.BooleanVar()
                    cb = tk.Checkbutton(qframe, text=opt, variable=bvar)
                    cb.pack(anchor="w")
                    vars_multi.append((opt, bvar))

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=5)
        self.answer_err_msg = tk.StringVar()
        err_lbl = tk.Label(btn_frame, textvariable=self.answer_err_msg, fg="red")
        err_lbl.pack(anchor="w", padx=5)

        def submit_answers():
            # Prüfen, ob alle Fragen beantwortet wurden
            for idx, q in enumerate(questions):
                if q.get("typ") == "single":
                    if not self.answer_vars[idx].get():
                        self.answer_err_msg.set(f"Bitte Frage {idx+1} beantworten.")
                        return
                else:
                    if not any(bvar.get() for _, bvar in self.answer_vars[idx]):
                        self.answer_err_msg.set(f"Bitte Frage {idx+1} beantworten.")
                        return
            self.answer_err_msg.set("")
            # Ergebnisse speichern
            result_entry = []
            for idx, q in enumerate(questions):
                if q.get("typ") == "single":
                    result_entry.append(self.answer_vars[idx].get())
                else:
                    # Liste der gewählten Optionen
                    chosen = [opt for opt, bvar in self.answer_vars[idx] if bvar.get()]
                    result_entry.append(chosen)
            self.current.setdefault("results", []).append(result_entry)
            self.current.setdefault("users_voted", []).append(self.username)
            self.save(self.surveys_file, self.umfragen)
            self.message_text.set("Antworten gespeichert. Danke für die Teilnahme!")
            self.mode = None
            self.refresh()

        tk.Button(btn_frame, text="Antworten abschicken", command=submit_answers).pack(side="right", padx=10)
        tk.Button(btn_frame, text="Abbrechen", command=lambda: [setattr(self, 'mode', None), self.refresh()]).pack(side="right", padx=10)

    ##########################
    # Ergebnisse anzeigen
    ##########################
    def results(self):
        if not self.current:
            self.message_text.set("Keine Umfrage ausgewählt.")
            return
        if not self.in_verwaltung():
            self.message_text.set("Keine Berechtigung, Ergebnisse einzusehen.")
            return
        self.mode = "results"
        self.render_canvas()

    def results_ui(self):
        frame = self.canvas
        tk.Label(frame, text=f"Ergebnisse Umfrage: {self.current.get('title','')}", font=('',13,'bold')).pack(anchor="w", padx=5, pady=5)
        results = self.current.get("results", [])
        questions = self.current.get("questions", [])

        if not results:
            tk.Label(frame, text="Noch keine Ergebnisse vorhanden.", fg="gray").pack(pady=20)
            return

        # Ergebnisse auswerten: für jede Frage Optionenzählung
        auswertung = []
        for qidx, q in enumerate(questions):
            counts = {}
            for opt in q.get("options", []):
                counts[opt] = 0
            for res in results:
                antwort = res[qidx]
                if q.get("typ") == "single":
                    if antwort in counts:
                        counts[antwort] += 1
                else:
                    for wahl in antwort:
                        if wahl in counts:
                            counts[wahl] += 1
            auswertung.append(counts)

        for idx, q in enumerate(questions):
            qframe = tk.LabelFrame(frame, text=f"Frage {idx+1}: {q.get('frage','')}", padx=5, pady=5)
            qframe.pack(fill="x", pady=3)
            counts = auswertung[idx]
            gesamt = sum(counts.values())
            if gesamt == 0:
                tk.Label(qframe, text="Keine Antworten").pack(anchor="w")
            else:
                for opt, anz in counts.items():
                    prozent = (anz / gesamt) * 100 if gesamt else 0
                    tk.Label(qframe, text=f"{opt}: {anz} ({prozent:.1f}%)").pack(anchor="w")


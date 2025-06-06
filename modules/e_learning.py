import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DB = "data/elearning.json"
USERS_DB = "data/users.json"

class Modul:
    def __init__(self, master, username, user_data,):
        self.master = master
        self.username = username
        self.group = user_data["group"]
        self.is_admin = user_data.get("is_admin", False)

        self.frame = tk.Frame(master, bg="white")
        tk.Label(self.frame, text="📚 E-Learning", font=("Arial", 16), bg="white").pack(pady=10)

        self.ensure_db_exists()
        self.load_data()
        self.setup_ui()

    def get_frame(self):
        return self.frame

    def ensure_db_exists(self):
        os.makedirs(os.path.dirname(DB), exist_ok=True)
        if not os.path.exists(DB):
            with open(DB, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_data(self):
        # Nutzergruppen laden
        try:
            with open(USERS_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
                self.groups = list(set(user["group"] for user in users.values()))
        except:
            self.groups = []

        # Tests laden
        try:
            with open(DB, "r", encoding="utf-8") as f:
                self.tests = json.load(f)
        except:
            self.tests = []


    def setup_ui(self):
        if self.is_admin or self.group == "Lehrer":
            admin_frame = tk.LabelFrame(self.frame, text="Test erstellen", bg="white")
            admin_frame.pack(padx=10, pady=10, fill="x")

            tk.Label(admin_frame, text="Titel:", bg="white").pack()
            self.test_title = tk.Entry(admin_frame)
            self.test_title.pack(pady=2)

            self.questions = []

            tk.Label(admin_frame, text="Frage:", bg="white").pack()
            self.question_entry = tk.Entry(admin_frame)
            self.question_entry.pack(pady=2)

            tk.Label(admin_frame, text="Lösung:", bg="white").pack()
            self.answer_entry = tk.Entry(admin_frame)
            self.answer_entry.pack(pady=2)

            tk.Button(admin_frame, text="Frage hinzufügen", command=self.add_question).pack(pady=2)

            tk.Label(admin_frame, text="Gruppe:", bg="white").pack()
            self.group_select = ttk.Combobox(admin_frame, values=self.groups, state="readonly")
            self.group_select.pack(pady=2)

            tk.Button(admin_frame, text="Test speichern", command=self.save_test).pack(pady=5)

        self.test_list = tk.LabelFrame(self.frame, text="Verfügbare Tests", bg="white")
        self.test_list.pack(padx=10, pady=10, fill="both", expand=True)

        self.display_tests()

    def add_question(self):
        q = self.question_entry.get().strip()
        a = self.answer_entry.get().strip()
        if q and a:
            self.questions.append({"question": q, "answer": a})
            self.question_entry.delete(0, "end")
            self.answer_entry.delete(0, "end")
            messagebox.showinfo("Hinzugefügt", f"Frage hinzugefügt. ({len(self.questions)} insgesamt)")
        else:
            messagebox.showwarning("Fehler", "Bitte Frage und Antwort eingeben.")

    def save_test(self):
        if not self.questions:
            messagebox.showwarning("Keine Fragen", "Bitte mindestens eine Frage hinzufügen.")
            return
        test = {
            "title": self.test_title.get(),
            "questions": self.questions,
            "group": self.group_select.get(),
            "results": {}
        }

        self.tests.append(test)
        with open(DB, "w", encoding="utf-8") as f:
            json.dump(self.tests, f, indent=2)

        self.test_title.delete(0, "end")
        self.group_select.set("") 
        self.questions = []
        self.display_tests()

    def display_tests(self):
        for widget in self.test_list.winfo_children():
            widget.destroy()

        for i, test in enumerate(self.tests):
            if test["group"] == self.group or self.is_admin:
                frame = tk.Frame(self.test_list, bg="white", bd=1, relief="solid")
                frame.pack(fill="x", pady=2)

                tk.Label(frame, text=f"📘 {test['title']}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=5)

                user_answers = test.get("results", {}).get(self.username, {})

                for q_index, q in enumerate(test["questions"]):
                    subframe = tk.Frame(frame, bg="white")
                    subframe.pack(anchor="w", fill="x", padx=10)

                    tk.Label(subframe, text=f"• {q['question']}", bg="white").pack(side="left", padx=5)

                    if str(q_index) not in user_answers:
                        entry = tk.Entry(subframe)
                        entry.pack(side="left", padx=5)
                        btn = tk.Button(subframe, text="Antwort", command=lambda i=i, q_index=q_index, e=entry: self.submit_answer(i, q_index, e))
                        btn.pack(side="left", padx=5)
                    else:
                        res = user_answers[str(q_index)]
                        correct = q["answer"]
                        status = "✅ Richtig" if res == correct else "❌ Falsch"
                        tk.Label(subframe, text=f"Deine Antwort: {res} – {status}", bg="white", fg="green" if res == correct else "red").pack(side="left", padx=5)

    def submit_answer(self, test_index, question_index, entry):
        answer = entry.get().strip()
        if not answer:
            return
        if "results" not in self.tests[test_index]:
            self.tests[test_index]["results"] = {}
        if self.username not in self.tests[test_index]["results"]:
            self.tests[test_index]["results"][self.username] = {}
        self.tests[test_index]["results"][self.username][str(question_index)] = answer

        with open(DB, "w") as f:
            json.dump(self.tests, f, indent=2)

        self.display_tests()

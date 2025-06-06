import tkinter as tk
from tkinter import messagebox
import json
import os

SUPPORT_PATH = "data/support.json"
FEEDBACK_PATH = "data/feedback.json"

class Modul:
    def __init__(self, master, nutzername, nutzerdaten):
        self.master = master
        self.nutzername = nutzername
        self.nutzerdaten = nutzerdaten
        self.frame = tk.Frame(master)

        if not nutzerdaten.get("is_admin"):
            tk.Label(self.frame, text="Zugriff verweigert.", font=("Arial", 14)).pack(pady=20)
            return

        tk.Label(self.frame, text="🛠️ Support-Verwaltung", font=("Arial", 16, "bold")).pack(pady=10)

        self.notebook = tk.ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)

        self.create_ticket_tab()
        self.create_feedback_tab()

    def get_frame(self):
        return self.frame

    def create_ticket_tab(self):
        ticket_tab = tk.Frame(self.notebook)
        self.notebook.add(ticket_tab, text="Support-Tickets")

        self.ticket_listbox = tk.Listbox(ticket_tab)
        self.ticket_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.ticket_details = tk.Text(ticket_tab, height=10)
        self.ticket_details.pack(fill="both", padx=5, pady=5)

        status_frame = tk.Frame(ticket_tab)
        status_frame.pack(pady=5)

        self.status_var = tk.StringVar()
        status_menu = tk.OptionMenu(status_frame, self.status_var, "offen", "in Bearbeitung", "erledigt")
        status_menu.pack(side="left", padx=5)

        tk.Button(status_frame, text="Status speichern", command=self.update_ticket_status).pack(side="left", padx=5)

        self.load_tickets()
        self.ticket_listbox.bind("<<ListboxSelect>>", self.display_ticket)

    def create_feedback_tab(self):
        feedback_tab = tk.Frame(self.notebook)
        self.notebook.add(feedback_tab, text="Feedback")

        self.feedback_text = tk.Text(feedback_tab, state="disabled")
        self.feedback_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_feedback()

    def load_tickets(self):
        self.tickets = []
        self.ticket_listbox.delete(0, tk.END)

        if os.path.exists(SUPPORT_PATH):
            with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                self.tickets = json.load(f)

        for i, ticket in enumerate(self.tickets):
            summary = f"{i + 1}. {ticket['user']} – {ticket['status']}"
            self.ticket_listbox.insert(tk.END, summary)
            
    def display_ticket(self, event):
        index = self.ticket_listbox.curselection()
        if not index:
            return
        ticket = self.tickets[index[0]]
        self.ticket_details.delete("1.0", tk.END)
        self.ticket_details.insert("1.0", f"Von: {ticket['user']}\n\n{ticket['content']}")
        self.status_var.set(ticket["status"])

    def update_ticket_status(self):
        index = self.ticket_listbox.curselection()
        if not index:
            return
        new_status = self.status_var.get()
        self.tickets[index[0]]["status"] = new_status
        with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.tickets, f, indent=2)
        self.load_tickets()
        messagebox.showinfo("Erfolg", "Ticketstatus aktualisiert.")

    def load_feedback(self):
        feedbacks = []
        if os.path.exists(FEEDBACK_PATH):
            with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)

        self.feedback_text.config(state="normal")
        self.feedback_text.delete("1.0", tk.END)
        for f in feedbacks:
            self.feedback_text.insert(tk.END, f"Von: {f['user']}\n{f['feedback']}\n\n")
        self.feedback_text.config(state="disabled")

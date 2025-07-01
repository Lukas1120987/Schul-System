import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

from ordner import get_data_path

SUPPORT_PATH = os.path.join(get_data_path(), "data/support.json")
FEEDBACK_PATH = os.path.join(get_data_path(), "data/feedback.json")


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

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)

        self.create_ticket_tab()
        self.create_feedback_tab()

    def get_frame(self):
        return self.frame

    def create_ticket_tab(self):
        ticket_tab = tk.Frame(self.notebook)
        self.notebook.add(ticket_tab, text="Support-Tickets")

        top_frame = tk.Frame(ticket_tab)
        top_frame.pack(fill="x", pady=5)

        tk.Label(top_frame, text="Suche:").pack(side="left", padx=5)
        self.search_entry = tk.Entry(top_frame)
        self.search_entry.pack(side="left", padx=5)
        tk.Button(top_frame, text="🔍", command=self.search_tickets).pack(side="left", padx=2)

        tk.Label(top_frame, text="Status-Filter:").pack(side="left", padx=10)
        self.filter_var = tk.StringVar(value="Alle")
        filter_menu = ttk.Combobox(top_frame, textvariable=self.filter_var, values=["Alle", "offen", "in Bearbeitung", "erledigt"], state="readonly", width=15)
        filter_menu.pack(side="left", padx=2)
        tk.Button(top_frame, text="Filter anwenden", command=self.load_tickets).pack(side="left", padx=5)

        main_frame = tk.Frame(ticket_tab)
        main_frame.pack(fill="both", expand=True)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.ticket_listbox = tk.Listbox(left_frame, width=40)
        self.ticket_listbox.pack(fill="y", expand=True)
        self.ticket_listbox.bind("<<ListboxSelect>>", self.display_ticket)

        self.ticket_details = tk.Text(right_frame, height=10, wrap="word")
        self.ticket_details.pack(fill="both", expand=True)

        status_frame = tk.Frame(right_frame)
        status_frame.pack(pady=5)

        self.status_var = tk.StringVar(value="offen")
        status_menu = tk.OptionMenu(status_frame, self.status_var, "offen", "in Bearbeitung", "erledigt")
        status_menu.pack(side="left", padx=5)

        tk.Button(status_frame, text="Status speichern", command=self.update_ticket_status).pack(side="left", padx=5)
        tk.Button(status_frame, text="🗑️ Ticket löschen", command=self.delete_ticket).pack(side="left", padx=5)

        self.load_tickets()

    def create_feedback_tab(self):
        feedback_tab = tk.Frame(self.notebook)
        self.notebook.add(feedback_tab, text="Feedback")

        self.feedback_text = tk.Text(feedback_tab, state="disabled", wrap="word")
        self.feedback_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_feedback()

    def load_tickets(self):
        self.tickets = []
        self.ticket_listbox.delete(0, tk.END)

        if os.path.exists(SUPPORT_PATH):
            try:
                with open(SUPPORT_PATH, "r", encoding="utf-8") as f:
                    self.tickets = json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Fehler", "Supportdaten konnten nicht geladen werden.")
                return

        suchtext = self.search_entry.get().lower()
        filter_status = self.filter_var.get()

        for i, ticket in enumerate(self.tickets):
            user = ticket.get("user", "Unbekannt")
            content = ticket.get("content", "")
            status = ticket.get("status", "offen")

            if (filter_status != "Alle" and status != filter_status):
                continue
            if suchtext and suchtext not in user.lower() and suchtext not in content.lower():
                continue

            display_text = f"{i + 1}. {user} – {status}"
            self.ticket_listbox.insert(tk.END, display_text)

    def display_ticket(self, event):
        index = self.ticket_listbox.curselection()
        if not index:
            return
        visible_index = index[0]

        suchtext = self.search_entry.get().lower()
        filter_status = self.filter_var.get()
        filtered_tickets = [
            ticket for ticket in self.tickets
            if (filter_status == "Alle" or ticket.get("status") == filter_status) and
               (not suchtext or suchtext in ticket.get("user", "").lower() or suchtext in ticket.get("content", "").lower())
        ]

        if visible_index >= len(filtered_tickets):
            return

        self.current_ticket_index = self.tickets.index(filtered_tickets[visible_index])
        ticket = self.tickets[self.current_ticket_index]

        self.ticket_details.delete("1.0", tk.END)
        self.ticket_details.insert("1.0", f"Von: {ticket.get('user', 'Unbekannt')}\n\n{ticket.get('content', '')}")
        self.status_var.set(ticket.get("status", "offen"))

    def update_ticket_status(self):
        if getattr(self, 'current_ticket_index', None) is None:
            messagebox.showwarning("Hinweis", "Bitte ein Ticket auswählen.")
            return

        self.tickets[self.current_ticket_index]["status"] = self.status_var.get()

        try:
            with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
                json.dump(self.tickets, f, indent=2, ensure_ascii=False)
            self.load_tickets()
            messagebox.showinfo("Erfolg", "Ticketstatus aktualisiert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{str(e)}")

    def delete_ticket(self):
        if getattr(self, 'current_ticket_index', None) is None:
            messagebox.showwarning("Hinweis", "Bitte ein Ticket auswählen.")
            return

        if messagebox.askyesno("Bestätigung", "Soll dieses Ticket wirklich gelöscht werden?"):
            try:
                self.tickets.pop(self.current_ticket_index)
                with open(SUPPORT_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.tickets, f, indent=2, ensure_ascii=False)
                self.ticket_details.delete("1.0", tk.END)
                self.load_tickets()
                messagebox.showinfo("Erfolg", "Ticket gelöscht.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen:\n{str(e)}")

    def search_tickets(self):
        self.load_tickets()

    def load_feedback(self):
        feedbacks = []
        if os.path.exists(FEEDBACK_PATH):
            try:
                with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
                    feedbacks = json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Fehler", "Feedbackdaten konnten nicht geladen werden.")

        self.feedback_text.config(state="normal")
        self.feedback_text.delete("1.0", tk.END)

        for f in feedbacks:
            self.feedback_text.insert(
                tk.END,
                f"Von: {f.get('user', 'Unbekannt')}\n{f.get('feedback', '')}\n\n"
            )

        self.feedback_text.config(state="disabled")

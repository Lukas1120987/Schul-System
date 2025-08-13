import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from urllib.parse import urlparse
import webbrowser
import threading
import webview  # pip install pywebview
from ordner import get_data_path

WHITELIST_PATH = os.path.join(get_data_path(), "data/internet_whitelist.json")


class Modul:
    def __init__(self, parent, username, user_data=None):
        self.frame = tk.Frame(parent, bg="#f0f2f5")
        self.username = username
        self.user_data = user_data or {}

        # State
        self.history = []
        self.history_index = -1
        self.webview_window = None
        self.webview_thread = None

        self._build_ui()
        self._load_whitelist()
        self._refresh_whitelist_listbox()
        self._update_nav_buttons()

    def get_frame(self):
        return self.frame

    # ---------- Daten ----------

    def _load_whitelist(self):
        if not os.path.exists(WHITELIST_PATH):
            self.whitelist = []
            self._save_whitelist()
            return
        try:
            with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            cleaned = []
            for item in data:
                if not isinstance(item, str):
                    continue
                item = item.strip()
                if item:
                    cleaned.append(item)
            self.whitelist = sorted(list(dict.fromkeys(cleaned)))
        except Exception:
            self.whitelist = []

    def _save_whitelist(self):
        os.makedirs(os.path.dirname(WHITELIST_PATH), exist_ok=True)
        with open(WHITELIST_PATH, "w", encoding="utf-8") as f:
            json.dump(self.whitelist, f, indent=2, ensure_ascii=False)

    # ---------- URL/Whitelist-Logik ----------

    def _ensure_scheme(self, url: str) -> str:
        url = url.strip()
        if not url:
            return url
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", url):
            url = "https://" + url
        return url

    def _is_allowed(self, url: str) -> bool:
        try:
            target = urlparse(self._ensure_scheme(url))
        except Exception:
            return False

        t_netloc = target.netloc.lower()

        for entry in self.whitelist:
            e = entry.strip()
            if not e:
                continue

            if re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", e):
                try:
                    pe = urlparse(e)
                except Exception:
                    continue
                if target.scheme == pe.scheme and t_netloc == pe.netloc.lower():
                    if target.path.startswith(pe.path):
                        return True
            else:
                domain = e.lower()
                if t_netloc == domain or t_netloc.endswith("." + domain):
                    return True
        return False

    # ---------- UI ----------

    def _build_ui(self):
        tk.Label(self.frame, text="🌐 Internetverwaltung (Whitelist-Browser)",
                 font=("Arial", 18, "bold"), bg="#f0f2f5").pack(pady=(10, 6))

        self.nb = ttk.Notebook(self.frame)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.browser_tab = tk.Frame(self.nb, bg="#f0f2f5")
        self.nb.add(self.browser_tab, text="Browser")

        self._build_browser_tab(self.browser_tab)

        if self.user_data.get("group") == "Verwaltung":
            self.admin_tab = tk.Frame(self.nb, bg="#f0f2f5")
            self.nb.add(self.admin_tab, text="Whitelist verwalten")
            self._build_admin_tab(self.admin_tab)

    def _build_browser_tab(self, parent):
        topbar = tk.Frame(parent, bg="#f0f2f5")
        topbar.pack(fill="x", padx=8, pady=(8, 6))

        self.btn_back = tk.Button(topbar, text="←", width=3, command=self._go_back)
        self.btn_back.pack(side="left", padx=(0, 4))

        self.btn_forward = tk.Button(topbar, text="→", width=3, command=self._go_forward)
        self.btn_forward.pack(side="left", padx=(0, 8))

        self.btn_reload = tk.Button(topbar, text="⟳", width=3, command=self._reload_current)
        self.btn_reload.pack(side="left", padx=(0, 8))

        self.combo_whitelist = ttk.Combobox(topbar, state="readonly", width=40, values=[])
        self.combo_whitelist.set("Whitelist auswählen…")
        self.combo_whitelist.pack(side="left", padx=(0, 6))
        self.combo_whitelist.bind("<<ComboboxSelected>>", self._open_selected_whitelist)

        self.entry_url = tk.Entry(topbar)
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry_url.bind("<Return>", self._on_go)

        self.btn_go = tk.Button(topbar, text="Öffnen", command=self._on_go)
        self.btn_go.pack(side="left")

        container = tk.Frame(parent, bg="#dfe3e6")
        container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Starte pywebview in einem separaten Thread
        def start_webview():
            self.webview_window = webview.create_window(
                "Browser",
                "",
                width=800,
                height=600,
                resizable=True
            )
            webview.start()

        self.webview_thread = threading.Thread(target=start_webview, daemon=True)
        self.webview_thread.start()

    def _build_admin_tab(self, parent):
        list_frame = tk.Frame(parent, bg="#f0f2f5")
        list_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        tk.Label(list_frame, text="Whitelist", bg="#f0f2f5", font=("Arial", 12, "bold")).pack(anchor="w")
        self.listbox = tk.Listbox(list_frame, height=14)
        self.listbox.pack(fill="both", expand=True, pady=(4, 8))

        edit_frame = tk.Frame(parent, bg="#f0f2f5")
        edit_frame.pack(side="right", fill="y", padx=8, pady=8)

        tk.Label(edit_frame, text="Eintrag (Domain oder vollständige URL):", bg="#f0f2f5").pack(anchor="w", pady=(0, 4))
        self.entry_new = tk.Entry(edit_frame, width=40)
        self.entry_new.pack(anchor="w", pady=(0, 8))

        tk.Button(edit_frame, text="➕ Hinzufügen", bg="#4CAF50", fg="white",
                  command=self._add_entry).pack(fill="x", pady=(0, 6))
        tk.Button(edit_frame, text="✏️ Bearbeiten", command=self._edit_entry).pack(fill="x", pady=(0, 6))
        tk.Button(edit_frame, text="❌ Entfernen", bg="#f44336", fg="white",
                  command=self._remove_entry).pack(fill="x", pady=(0, 6))
        tk.Button(edit_frame, text="🔄 Liste neu laden", command=self._reload_whitelist_ui).pack(fill="x", pady=(12, 0))

        tk.Label(
            edit_frame,
            text="Beispiele:\n• example.com (alle Subdomains)\n• https://example.com/lernportal (nur dieser Pfad)",
            bg="#f0f2f5", justify="left"
        ).pack(anchor="w", pady=(10, 0))

    def _refresh_whitelist_listbox(self):
        if hasattr(self, "listbox"):
            self.listbox.delete(0, tk.END)
            for item in self.whitelist:
                self.listbox.insert(tk.END, item)
        if hasattr(self, "combo_whitelist"):
            self.combo_whitelist["values"] = self.whitelist

    def _reload_whitelist_ui(self):
        self._load_whitelist()
        self._refresh_whitelist_listbox()
        messagebox.showinfo("Aktualisiert", "Whitelist neu geladen.")

    # ---------- Admin-Actions ----------

    def _add_entry(self):
        entry = self.entry_new.get().strip()
        if not entry:
            messagebox.showerror("Fehler", "Bitte einen Eintrag eingeben.")
            return
        if entry in self.whitelist:
            messagebox.showwarning("Hinweis", "Dieser Eintrag ist bereits vorhanden.")
            return
        self.whitelist.append(entry)
        self.whitelist = sorted(list(dict.fromkeys(self.whitelist)))
        self._save_whitelist()
        self.entry_new.delete(0, tk.END)
        self._refresh_whitelist_listbox()

    def _remove_entry(self):
        sel = self.listbox.curselection() if hasattr(self, "listbox") else ()
        if not sel:
            messagebox.showwarning("Hinweis", "Bitte einen Eintrag auswählen.")
            return
        value = self.listbox.get(sel[0])
        if messagebox.askyesno("Löschen bestätigen", f"„{value}“ entfernen?"):
            self.whitelist = [x for x in self.whitelist if x != value]
            self._save_whitelist()
            self._refresh_whitelist_listbox()

    def _edit_entry(self):
        sel = self.listbox.curselection() if hasattr(self, "listbox") else ()
        if not sel:
            messagebox.showwarning("Hinweis", "Bitte einen Eintrag auswählen.")
            return
        old_value = self.listbox.get(sel[0])
        new_value = self.entry_new.get().strip()
        if not new_value:
            messagebox.showerror("Fehler", "Bitte neuen Wert eingeben.")
            return
        if new_value in self.whitelist and new_value != old_value:
            messagebox.showwarning("Hinweis", "Dieser Eintrag existiert bereits.")
            return
        idx = self.whitelist.index(old_value)
        self.whitelist[idx] = new_value
        self.whitelist = sorted(list(dict.fromkeys(self.whitelist)))
        self._save_whitelist()
        self._refresh_whitelist_listbox()

    # ---------- Browsing ----------

    def _open_selected_whitelist(self, event=None):
        value = self.combo_whitelist.get().strip()
        if not value or value == "Whitelist auswählen…":
            return
        url = value
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", url):
            url = "https://" + url
        self._navigate(url)

    def _on_go(self, event=None):
        url = self.entry_url.get().strip()
        self._navigate(url)

    def _navigate(self, url: str):
        if not url:
            return
        url = self._ensure_scheme(url)

        if not self._is_allowed(url):
            messagebox.showerror("Blockiert", "Diese Adresse ist nicht auf der Whitelist.")
            return

        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]
        self.history.append(url)
        self.history_index += 1

        self._load_url(url)
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(0, url)
        self._update_nav_buttons()

    def _load_url(self, url: str):
        if self.webview_window:
            self.webview_window.load_url(url)
        else:
            webbrowser.open(url)

    def _current_url(self):
        if 0 <= self.history_index < len(self.history):
            return self.history[self.history_index]
        return None

    def _go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._load_url(self.history[self.history_index])
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, self.history[self.history_index])
            self._update_nav_buttons()

    def _go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._load_url(self.history[self.history_index])
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, self.history[self.history_index])
            self._update_nav_buttons()

    def _reload_current(self):
        url = self._current_url()
        if url:
            if not self._is_allowed(url):
                messagebox.showerror("Blockiert", "Aktuelle Adresse ist nicht mehr erlaubt.")
                return
            self._load_url(url)

    def _update_nav_buttons(self):
        can_back = self.history_index > 0
        can_forward = self.history_index < len(self.history) - 1
        self.btn_back.configure(state=("normal" if can_back else "disabled"))
        self.btn_forward.configure(state=("normal" if can_forward else "disabled"))
        self.btn_reload.configure(state=("normal" if self._current_url() else "disabled"))

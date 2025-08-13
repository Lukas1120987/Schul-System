# file: about_overlay.py
# Erfordert: pip install customtkinter
import webbrowser
import tkinter as tk
import customtkinter as ctk
from datetime import date

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


ABOUT_CONFIG = {
    "app_name": "SchulSystem",
    "org_website": "https://lukas1120987.github.io/SchulSystem/",
    "responsibles": [
        {
            "role": "Entwickler",
            "name": "Lukas1120987",
            "email": "team.schulsystem@outlook.com",
        },
    ],

    "privacy_text": f"""
Verantwortlich im Sinne der DSGVO für die Verarbeitung personenbezogener Daten im Rahmen der Anwendung „SchulSystem“ ist die
Schule an der das System genutzt wird. Die Datenverarbeitung erfolgt zum Zweck der Schulorganisation, Kommunikation und
pädagogischen Arbeit. Rechtsgrundlagen sind insbesondere Art. 6 Abs. 1 lit. e DSGVO i. V. m. den einschlägigen Schul- und Datenschutzgesetzen des Bundeslandes.

Kategorien von Daten:
• Stammdaten (z. B. Name, Klasse, Rolle)
• Kommunikationsdaten (z. B. Nachrichten im System)
• Unterrichts- und Organisationsdaten (z. B. Stunden- und Vertretungspläne)
• Protokoll-/Nutzungsdaten (technisch erforderlich)

Speicherdauer:
• Grundsätzlich bis zur Erfüllung des jeweiligen Zwecks, darüber hinaus nur, soweit gesetzlich vorgeschrieben.
• Die Schule kann selber festlegen, wann folgende Daten automatisch gelöscht werden:
  • Nachrichten
  • Benachrichtigungen

Betroffenenrechte:
• Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Widerspruch sowie Datenübertragbarkeit nach Maßgabe der DSGVO.
• Beschwerden richten Sie an die zuständige Datenschutzaufsichtsbehörde des Bundeslandes.

Stand: {date.today().strftime("%d.%m.%Y")}
""".strip(),
}


class AboutOverlay(ctk.CTkToplevel):
    def __init__(self, master=None, config: dict = ABOUT_CONFIG):
        super().__init__(master)
        self.title(f"Über – {config.get('app_name','App')}")
        self.geometry("820x560")
        self.resizable(True, True)
        self.config_dict = config
        self._make_ui()

        # Modal/fokusfreundlich
        self.transient(master)
        self.grab_set()
        self.focus()

    def _make_ui(self):
        pad = 16

        # Header
        header = ctk.CTkFrame(self, corner_radius=20)
        header.pack(fill="x", padx=pad, pady=(pad, 8))

        title = ctk.CTkLabel(
            header,
            text=f"ℹ️  {self.config_dict.get('app_name','App')} – Informationen",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.pack(side="left", padx=12, pady=12)

        # Quick actions
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right", padx=12, pady=12)
        ctk.CTkButton(
            actions,
            text="Website öffnen",
            command=lambda: self._open_url(self.config_dict.get("org_website")),
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            actions, text="E-Mail schreiben", command=self._mailto_org
        ).pack(side="left", padx=6)

        # Tabs
        tabs = ctk.CTkTabview(self, corner_radius=18)
        tabs.pack(fill="both", expand=True, padx=pad, pady=(8, pad))

        tab_priv = tabs.add("Datenschutz")
        tab_resp = tabs.add("Verantwortliche")
        tab_contact = tabs.add("Kontakt")

        self._build_privacy_tab(tab_priv)
        self._build_responsibles_tab(tab_resp)
        self._build_contact_tab(tab_contact)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=pad, pady=(0, pad))
        ctk.CTkLabel(
            footer,
            text=f"© {date.today().year} {self.config_dict.get('org_name','')}",
            anchor="w",
        ).pack(side="left")
        ctk.CTkButton(footer, text="Schließen", command=self.destroy).pack(side="right")

    def _build_privacy_tab(self, parent):
        # Scrollbarer Text
        frame = ctk.CTkFrame(parent, corner_radius=16)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        text = tk.Text(
            frame,
            wrap="word",
            relief="flat",
            padx=12,
            pady=12,
            font=("Segoe UI", 11),
        )
        text.pack(side="left", fill="both", expand=True)

        text.insert("1.0", self.config_dict.get("privacy_text", ""))
        text.config(state="disabled")

        scrollbar = ctk.CTkScrollbar(frame, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.config(yscrollcommand=scrollbar.set)

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            row,
            text="Datenschutz per E-Mail anfordern",
            command=self._mailto_privacy_request,
        ).pack(side="left")
        ctk.CTkButton(
            row, text="In Zwischenablage kopieren", command=self._copy_privacy
        ).pack(side="right")

    def _build_responsibles_tab(self, parent):
        wrapper = ctk.CTkScrollableFrame(parent, corner_radius=16)
        wrapper.pack(fill="both", expand=True, padx=10, pady=10)

        for person in self.config_dict.get("responsibles", []):
            card = ctk.CTkFrame(wrapper, corner_radius=18)
            card.pack(fill="x", padx=6, pady=6)

            title = ctk.CTkLabel(
                card,
                text=f"{person.get('role','Rolle')}",
                font=ctk.CTkFont(size=16, weight="bold"),
            )
            title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))

            name = ctk.CTkLabel(card, text=person.get("name", ""))
            name.grid(row=1, column=0, sticky="w", padx=12)

            email = person.get("email", "")
            phone = person.get("phone", "")

            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.grid(row=0, column=1, rowspan=2, sticky="e", padx=10, pady=10)

            ctk.CTkButton(
                btns,
                text="E-Mail",
                width=110,
                command=lambda e=email: self._mailto(e),
            ).pack(side="left", padx=6)
            ctk.CTkButton(
                btns,
                text="Anrufen",
                width=110,
                command=lambda p=phone: self._tel(p),
            ).pack(side="left", padx=6)

            # Kontaktzeile
            ctk.CTkLabel(card, text=f"✉ {email}   ☎ {phone}").grid(
                row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10)
            )

            card.grid_columnconfigure(0, weight=1)

    def _build_contact_tab(self, parent):
        grid = ctk.CTkFrame(parent, corner_radius=16)
        grid.pack(fill="both", expand=True, padx=10, pady=10)

        info = (
            f"{self.config_dict.get('org_name')}\n"
            f"{self.config_dict.get('org_address')}\n\n"
            f"Website: {self.config_dict.get('org_website')}\n"
            f"E-Mail:  {self.config_dict.get('org_email')}\n"
            f"Telefon: {self.config_dict.get('org_phone')}\n"
        )

        ctk.CTkLabel(
            grid, text="Kontakt", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=12, pady=(12, 4))
        box = ctk.CTkTextbox(grid, height=180)
        box.pack(fill="x", padx=12)
        box.insert("1.0", info)
        box.configure(state="disabled")

        row = ctk.CTkFrame(grid, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=12)
        ctk.CTkButton(
            row, text="Website öffnen", command=lambda: self._open_url(self.config_dict.get("org_website"))
        ).pack(side="left", padx=6)
        ctk.CTkButton(row, text="E-Mail schreiben", command=self._mailto_org).pack(
            side="left", padx=6
        )
        ctk.CTkButton(
            row, text="Kontakt kopieren", command=lambda: self._copy_to_clipboard(info)
        ).pack(side="left", padx=6)

        # Kleines Formular für kurze Nachricht
        ctk.CTkLabel(grid, text="Kurze Nachricht (öffnet Ihr E-Mail-Programm):").pack(
            anchor="w", padx=12, pady=(6, 2)
        )
        self.msg_entry = ctk.CTkEntry(grid, placeholder_text="Ihr Anliegen in einem Satz …")
        self.msg_entry.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(
            grid, text="Als E-Mail vorbereiten", command=self._mailto_with_message
        ).pack(padx=12, pady=(0, 12))

    # ---- Helpers ----
    def _open_url(self, url: str | None):
        if url:
            webbrowser.open(url)

    def _mailto(self, email: str | None):
        if email:
            webbrowser.open(f"mailto:{email}")

    def _tel(self, phone: str | None):
        # Öffnet tel:-Links (wirkt v. a. auf Geräten/Apps, die das unterstützen)
        if phone:
            webbrowser.open(f"tel:{phone}")

    def _mailto_org(self):
        self._mailto(self.config_dict.get("org_email"))

    def _mailto_privacy_request(self):
        subject = "Auskunft/Datenkopie nach DSGVO – SchulSystem"
        body = "Sehr geehrte Damen und Herren,\n\nich bitte um Auskunft/Datenkopie gemäß Art. 15 DSGVO.\n\nMit freundlichen Grüßen"
        email = self.config_dict.get("org_email")
        if email:
            webbrowser.open(f"mailto:{email}?subject={self._q(subject)}&body={self._q(body)}")

    def _mailto_with_message(self):
        email = self.config_dict.get("org_email")
        msg = (self.msg_entry.get() or "").strip()
        subject = "Kontakt – SchulSystem"
        if email:
            webbrowser.open(f"mailto:{email}?subject={self._q(subject)}&body={self._q(msg)}")

    def _copy_privacy(self):
        self._copy_to_clipboard(self.config_dict.get("privacy_text", ""))

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        ctk.CTkMessagebox(title="Kopiert", message="In Zwischenablage kopiert.") if hasattr(ctk, "CTkMessagebox") else None

    @staticmethod
    def _q(s: str) -> str:
        from urllib.parse import quote
        return quote(s)

def attach_about_button(parent, text: str = "ℹ️ Über", config: dict = ABOUT_CONFIG):
    """
    Fügt dem übergebenen Container (Frame/Fenster) einen Button hinzu,
    der den Über-Dialog öffnet. Gibt den Button zurück.
    """
    def open_dialog():
        AboutOverlay(parent.winfo_toplevel(), config=config)

    btn = ctk.CTkButton(parent, text=text, command=open_dialog)
    return btn


# ---- Demo / Standalone ----
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Demo – Über-Button")

    # Hauptcontainer
    root = ctk.CTkFrame(app, corner_radius=20)
    root.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        root,
        text="SchulSystem – Demooberfläche",
        font=ctk.CTkFont(size=20, weight="bold"),
    ).pack(pady=(0, 12))

    toolbar = ctk.CTkFrame(root, corner_radius=16)
    toolbar.pack(fill="x", pady=(0, 12))


    about_btn = attach_about_button(toolbar)
    about_btn.pack(side="right", padx=6, pady=6)

    ctk.CTkTextbox(root, height=260, corner_radius=16).pack(fill="both", expand=True)

    app.geometry("900x600")
    app.mainloop()

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # <--- NEU
import random
import time

class InstallAssistantSplash:
    def __init__(self, root, on_continue_callback):
        self.root = root
        self.on_continue_callback = on_continue_callback
        self.progress_value = 0
        self.progress_max = 100
        self.dot_count = 0

        self.start_time = time.time()
        self.min_duration = 1
        self.max_duration = 500

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.overrideredirect(True)
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        root.configure(bg="#1e2a45")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("blue.Horizontal.TProgressbar", troughcolor='#32415e',
                        background='#6fa8dc', thickness=20, bordercolor='#1e2a45')

        self.container = tk.Frame(root, bg="#1e2a45")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # 🔄 LOGO mit PIL laden
        try:
            image = Image.open("logo.png")
            image = image.resize((200, 200))  # Größe anpassen
            self.logo_photo = ImageTk.PhotoImage(image)
            self.logo_label = tk.Label(self.container, image=self.logo_photo, bg="#1e2a45")
            self.logo_label.pack(pady=(0, 30))
        except Exception as e:
            print("Logo konnte nicht geladen werden:", e)

        self.title_label = tk.Label(
            self.container, text="Willkommen bei SchulSystem",
            font=("Segoe UI", 44, "bold"), fg="white", bg="#1e2a45")
        self.title_label.pack(pady=(0, 30))

        self.instructions = tk.Label(
            self.container,
            text="Setup-Assistent für SchulSystem\n"
                 "Bitte warte, bis der Vorgang abgeschlossen ist.",
            font=("Segoe UI", 18), fg="lightgray", bg="#1e2a45", justify="center")
        self.instructions.pack(pady=(0, 20))

        self.loading_label = tk.Label(self.container, text="Lade", font=("Segoe UI", 16),
                                      fg="lightgray", bg="#1e2a45")
        self.loading_label.pack(pady=10)

        self.progress_frame = tk.Frame(self.container, bg="#1e2a45")
        self.progress_frame.pack(pady=20)

        self.progress = ttk.Progressbar(
            self.progress_frame, orient="horizontal", length=400,
            mode="determinate", style="blue.Horizontal.TProgressbar")
        self.progress.pack(side="left")

        self.percent_label = tk.Label(self.progress_frame, text="0%", font=("Segoe UI", 14),
                                      fg="lightgray", bg="#1e2a45")
        self.percent_label.pack(side="left", padx=(10, 0))

        self.progress["maximum"] = self.progress_max
        self.progress["value"] = 0

        root.bind("<h>", lambda e: self.continue_now())

        self.load_progress()

    def load_progress(self):
        if self.progress_value < self.progress_max:
            step = random.randint(1, 2)
            self.progress_value = min(self.progress_value + step, self.progress_max)
            self.progress["value"] = self.progress_value
            self.percent_label.config(text=f"{self.progress_value}%")
            self.animate_loading_text()

            delay = random.randint(10, 130)
            self.root.after(delay, self.load_progress)
        else:
            self.continue_now()

    def animate_loading_text(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.loading_label.config(text="Lade" + "." * self.dot_count)

    def continue_now(self):
        self.root.unbind("<h>")
        elapsed = time.time() - self.start_time

        if elapsed < self.min_duration:
            remaining = int((self.min_duration - elapsed) * 1000)
            self.root.after(remaining, self.on_continue_callback)
        elif elapsed > self.max_duration:
            self.on_continue_callback()
        else:
            self.on_continue_callback()

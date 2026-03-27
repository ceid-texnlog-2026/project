import tkinter as tk
from config import (light_green, card_green, dark_text, title_font,
                    subtitle_font, red, set_background)
from widgets import simple_button, icon_button, bell_header
from models import Admin


class AdminFrame(tk.Frame):
    def __init__(self, master, admin: Admin):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.build()

    def build(self):
        set_background(self)
        bell_header(self)

        tk.Label(self, text="Διαχείριση\nΣυστήματος", font=title_font,
                 bg=light_green, fg=dark_text, justify="center").pack(pady=(10, 16))

        stats_box = tk.Frame(self, bg=card_green)
        stats_box.pack(padx=30, fill="x", pady=6, ipady=10)
        tk.Label(stats_box, text=f"Χρήστες: {self.admin.get_total_users()}",
                 font=subtitle_font, bg=card_green, fg=dark_text).pack(pady=4)
        tk.Label(stats_box, text=f"Νοσοκομεία: {self.admin.get_total_hospitals()}",
                 font=subtitle_font, bg=card_green, fg=dark_text).pack(pady=4)
        tk.Label(stats_box, text="Alerts: 2",
                 font=subtitle_font, bg=card_green, fg=red).pack(pady=4)

        button_grid = tk.Frame(self, bg=light_green)
        button_grid.pack(padx=20, pady=16, fill="x")
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        icon_button(button_grid, "Πιστοποίηση\nΦορέων",  "verify",  0, 0, lambda: None)
        icon_button(button_grid, "Αναφορές /\nΠαράπονα", "reports", 0, 1, lambda: None)

        simple_button(self, "Αποσύνδεση", self.master.show_login).pack(pady=20)

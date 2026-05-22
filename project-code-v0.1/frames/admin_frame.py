import tkinter as tk
from config import (light_green, card_green, dark_text, title_font,
                    subtitle_font, red, set_background)
from widgets import simple_button, icon_button, bell_header
from db import DBManager
from models import Admin


class AdminProfileScreen(tk.Frame):
    def __init__(self, master, admin: Admin):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)
        bell_header(self)

        tk.Label(self, text="Διαχείριση\nΣυστήματος", font=title_font,
                 bg=light_green, fg=dark_text, justify="center").pack(pady=(10, 16))

        stats_box = tk.Frame(self, bg=card_green)
        stats_box.pack(padx=30, fill="x", pady=6, ipady=10)
        tk.Label(stats_box,
                 text=f"Αιμοδότες: {len(self.db.donors)}",
                 font=subtitle_font, bg=card_green, fg=dark_text).pack(pady=4)
        tk.Label(stats_box,
                 text=f"Νοσοκομεία: {len(self.db.hospitals)}",
                 font=subtitle_font, bg=card_green, fg=dark_text).pack(pady=4)

        pending = len(self.db.get_pending_applications())
        open_reports = len(self.db.get_open_reports())
        tk.Label(stats_box,
                 text=f"Εκκρεμή αιτήματα: {pending}",
                 font=subtitle_font, bg=card_green, fg=red).pack(pady=(4, 0))
        tk.Label(stats_box,
                 text=f"Ανοιχτές αναφορές: {open_reports}",
                 font=subtitle_font, bg=card_green, fg=red).pack(pady=(0, 4))

        button_grid = tk.Frame(self, bg=light_green)
        button_grid.pack(padx=20, pady=16, fill="x")
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        icon_button(button_grid, "Πιστοποίηση\nΦορέων", "verify",
                    0, 0, self.go_certification)
        icon_button(button_grid, "Αναφορές /\nΠαράπονα", "reports",
                    0, 1, self.go_reports)

        simple_button(self, "Αποσύνδεση", self.master.show_login).pack(pady=20)

    def go_certification(self):
        from frames.donation_space_cert_frame import CertificationFrame
        self.master.switch(CertificationFrame, self.admin)

    def go_reports(self):
        from frames.reports_frame import ReportsFrame
        self.master.switch(ReportsFrame, self.admin)


AdminFrame = AdminProfileScreen

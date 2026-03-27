import tkinter as tk
from tkinter import messagebox
from config import (BG_LIGHT, BG_CARD, TEXT_DARK, FONT_TITLE,
                    FONT_SUB, ACCENT, set_bg)
from widgets import rounded_btn, grid_btn, bell_header
from models import Admin


class AdminFrame(tk.Frame):
    def __init__(self, master, admin: Admin):
        super().__init__(master, bg=BG_LIGHT)
        self.admin = admin
        self._build()

    def _build(self):
        set_bg(self)
        bell_header(self)

        tk.Label(self, text="Διαχείριση\nΣυστήματος", font=FONT_TITLE,
                 bg=BG_LIGHT, fg=TEXT_DARK, justify="center").pack(pady=(10, 16))

        stats = tk.Frame(self, bg=BG_CARD)
        stats.pack(padx=30, fill="x", pady=6, ipady=10)
        tk.Label(stats, text=f"Χρήστες: {self.admin.get_total_users()}",
                 font=FONT_SUB, bg=BG_CARD, fg=TEXT_DARK).pack(pady=4)
        tk.Label(stats, text=f"Νοσοκομεία: {self.admin.get_total_hospitals()}",
                 font=FONT_SUB, bg=BG_CARD, fg=TEXT_DARK).pack(pady=4)
        tk.Label(stats, text="Alerts: 2",
                 font=FONT_SUB, bg=BG_CARD, fg=ACCENT).pack(pady=4)

        grid = tk.Frame(self, bg=BG_LIGHT)
        grid.pack(padx=20, pady=16, fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        grid_btn(grid, "Πιστοποίηση\nΦορέων",  "verify",  0, 0,
                 lambda: messagebox.showinfo("", "Πιστοποίηση φορέων"))
        grid_btn(grid, "Αναφορές /\nΠαράπονα", "reports", 0, 1,
                 lambda: messagebox.showinfo("", "Αναφορές & Παράπονα"))

        rounded_btn(self, "Αποσύνδεση", self.master.show_login).pack(pady=20)

import tkinter as tk
from tkinter import messagebox
from config import (BG_LIGHT, BG_CARD, TEXT_DARK, TEXT_MID,
                    FONT_TITLE, FONT_SMALL, ACCENT, BTN_DARK,
                    load_icon, set_bg)
from widgets import rounded_btn, grid_btn, bell_header
from models import Donor


class DonorFrame(tk.Frame):
    def __init__(self, master, donor: Donor):
        super().__init__(master, bg=BG_LIGHT)
        self.donor = donor
        self._build()

    def _build(self):
        set_bg(self)
        bell_header(self)

        d = self.donor
        tk.Label(self, text="Καλώς ήρθες,\nΑιμοδότη", font=FONT_TITLE,
                 bg=BG_LIGHT, fg=TEXT_DARK, justify="center").pack(pady=(0, 10))

        last = d.get_last_donation()
        last_str = last.appointment_date.strftime("%d / %m / %Y") if last else "—"
        nxt = d.get_next_appointment()
        nxt_str = nxt.appointment_date.strftime("%d / %m / %Y") if nxt else "—"

        row1 = tk.Frame(self, bg=BG_LIGHT)
        row1.pack(fill="x", padx=20, pady=4)
        self._mini_card(row1, "heart",    "Τελευταία\nΑιμοδοσία", last_str, ACCENT).pack(side="left",  expand=True, fill="both", padx=4)
        self._mini_card(row1, "calendar", "Επόμενο\nΡαντεβού",    nxt_str,  BTN_DARK).pack(side="right", expand=True, fill="both", padx=4)

        grid = tk.Frame(self, bg=BG_LIGHT)
        grid.pack(padx=20, pady=10, fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        grid_btn(grid, "Κλείσε\nΡαντεβού",  "appointment",  0, 0, lambda: messagebox.showinfo("", "Κλείσιμο ραντεβού"))
        grid_btn(grid, "Ανέβασε\nεγγραφα",  "upload",       0, 1, lambda: messagebox.showinfo("", "Ανέβασμα εγγράφων"))
        grid_btn(grid, "Ιστορικό",           "history",      1, 0, lambda: messagebox.showinfo("", "Ιστορικό αιμοδοσιών"))
        grid_btn(grid, "Διαθεσιμότητα",      "availability", 1, 1, self._toggle_availability)

        rounded_btn(self, "Αποσύνδεση", self.master.show_login).pack(pady=16)

    def _mini_card(self, parent, icon_key, label, value, color):
        f = tk.Frame(parent, bg=BG_CARD, bd=0)
        kind, val = load_icon(icon_key, size=32)
        if kind == "image":
            lbl = tk.Label(f, image=val, bg=BG_CARD)
            lbl.image = val
        else:
            lbl = tk.Label(f, text=val, font=("Helvetica", 13, "bold"),
                           bg=BG_CARD, fg=color)
        lbl.pack(pady=(10, 2))
        tk.Label(f, text=label, font=FONT_SMALL, bg=BG_CARD,
                 fg=TEXT_MID, justify="center").pack()
        tk.Label(f, text=value, font=("Helvetica", 11, "bold"),
                 bg=BG_CARD, fg=TEXT_DARK).pack(pady=(2, 10))
        return f

    def _toggle_availability(self):
        self.donor.is_available = not self.donor.is_available
        status = "Διαθέσιμος" if self.donor.is_available else "Μη διαθέσιμος"
        messagebox.showinfo("Διαθεσιμότητα", f"Κατάσταση: {status}")

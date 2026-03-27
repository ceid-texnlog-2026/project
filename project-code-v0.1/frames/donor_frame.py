import tkinter as tk
from config import (light_green, card_green, dark_text, mid_text,
                    title_font, small_font, red, dark_green,
                    get_icon, set_background)
from widgets import simple_button, icon_button, bell_header
from models import Donor


class DonorFrame(tk.Frame):
    def __init__(self, master, donor: Donor):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.build()

    def build(self):
        set_background(self)
        bell_header(self)

        tk.Label(self, text="Καλώς ήρθες,\nΑιμοδότη", font=title_font,
                 bg=light_green, fg=dark_text, justify="center").pack(pady=(0, 10))

        last = self.donor.get_last_donation()
        last_date = last.appointment_date.strftime("%d / %m / %Y") if last else "—"
        next_app = self.donor.get_next_appointment()
        next_date = next_app.appointment_date.strftime("%d / %m / %Y") if next_app else "—"

        info_row = tk.Frame(self, bg=light_green)
        info_row.pack(fill="x", padx=20, pady=4)
        self.small_card(info_row, "heart",    "Τελευταία\nΑιμοδοσία", last_date, red).pack(side="left",  expand=True, fill="both", padx=4)
        self.small_card(info_row, "calendar", "Επόμενο\nΡαντεβού",    next_date, dark_green).pack(side="right", expand=True, fill="both", padx=4)

        button_grid = tk.Frame(self, bg=light_green)
        button_grid.pack(padx=20, pady=10, fill="x")
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        icon_button(button_grid, "Κλείσε\nΡαντεβού",  "appointment",  0, 0, lambda: None)
        icon_button(button_grid, "Ανέβασε\nεγγραφα",  "upload",       0, 1, lambda: None)
        icon_button(button_grid, "Ιστορικό",           "history",      1, 0, lambda: None)
        icon_button(button_grid, "Διαθεσιμότητα",      "availability", 1, 1, self.toggle_availability)

        simple_button(self, "Αποσύνδεση", self.master.show_login).pack(pady=16)

    def small_card(self, parent, icon_name, title, value, color):
        frame = tk.Frame(parent, bg=card_green, bd=0)
        kind, img = get_icon(icon_name, size=32)
        if kind == "image":
            label = tk.Label(frame, image=img, bg=card_green)
            label.image = img
        else:
            label = tk.Label(frame, text=img, font=("Poppins", 13, "bold"),
                             bg=card_green, fg=color)
        label.pack(pady=(10, 2))
        tk.Label(frame, text=title, font=small_font, bg=card_green,
                 fg=mid_text, justify="center").pack()
        tk.Label(frame, text=value, font=("Poppins", 11, "bold"),
                 bg=card_green, fg=dark_text).pack(pady=(2, 10))
        return frame

    def toggle_availability(self):
        self.donor.is_available = not self.donor.is_available

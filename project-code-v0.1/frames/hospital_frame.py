import tkinter as tk
from config import (light_green, card_green, dark_text, mid_text,
                    title_font, subtitle_font, normal_font, red, set_background)
from widgets import simple_button, icon_button, bell_header
from models import Hospital


class HospitalFrame(tk.Frame):
    def __init__(self, master, hospital: Hospital):
        super().__init__(master, bg=light_green)
        self.hospital = hospital
        self.build()

    def build(self):
        set_background(self)
        bell_header(self)

        tk.Label(self, text=self.hospital.name, font=title_font,
                 bg=light_green, fg=dark_text, justify="center").pack(pady=(0, 14))

        button_grid = tk.Frame(self, bg=light_green)
        button_grid.pack(padx=20, pady=6, fill="x")
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)

        icon_button(button_grid, "Επείγουσα\nΕκκληση",    "urgent",       0, 0, self.urgent_appeal)
        icon_button(button_grid, "Καταγραφή\nΑιμοδοσίας", "donation_reg", 0, 1, lambda: None)
        icon_button(button_grid, "Αποθέματα\nΑίματος",    "inventory",    1, 0, self.show_inventory)
        icon_button(button_grid, "Εκδοση\nΒεβαίωσης",     "certificate",  1, 1, lambda: None)

        simple_button(self, "Αποσύνδεση", self.master.show_login).pack(pady=20)

    def show_inventory(self):
        window = tk.Toplevel(self, bg=light_green)
        window.title("Αποθέματα Αίματος")
        window.geometry("280x340")

        tk.Label(window, text="Αποθέματα Αίματος", font=subtitle_font,
                 bg=light_green, fg=dark_text).pack(pady=12)

        for blood_type, quantity in self.hospital.blood_inventory.stock.items():
            is_low = self.hospital.blood_inventory.is_low(blood_type)
            color = red if is_low else dark_text
            row = tk.Frame(window, bg=card_green)
            row.pack(fill="x", padx=20, pady=2, ipady=4)
            tk.Label(row, text=f"  {blood_type}", font=normal_font,
                     bg=card_green, fg=mid_text, width=6, anchor="w").pack(side="left")
            text = f"{quantity} μονάδες{'  (!)' if is_low else ''}"
            tk.Label(row, text=text, font=normal_font,
                     bg=card_green, fg=color).pack(side="right", padx=10)

    def urgent_appeal(self):
        low_types = [b for b in self.hospital.blood_inventory.stock
                     if self.hospital.blood_inventory.is_low(b)]
        if not low_types:
            return

        window = tk.Toplevel(self, bg=light_green)
        window.title("Επείγουσα Εκκληση")
        window.geometry("280x150")
        tk.Label(window, text=f"Χαμηλά αποθέματα:\n{', '.join(low_types)}",
                 font=subtitle_font, bg=light_green, fg=red,
                 justify="center").pack(pady=20)
        tk.Label(window, text="Αποστολή ειδοποίησης σε διαθέσιμους donors.",
                 font=normal_font, bg=light_green, fg=dark_text,
                 wraplength=240, justify="center").pack()

import tkinter as tk
from tkinter import messagebox
from config import (BG_LIGHT, BG_CARD, TEXT_DARK, TEXT_MID,
                    FONT_TITLE, FONT_SUB, FONT_BODY, ACCENT,
                    set_bg)
from widgets import rounded_btn, grid_btn, bell_header
from models import Hospital


class HospitalFrame(tk.Frame):
    def __init__(self, master, hospital: Hospital):
        super().__init__(master, bg=BG_LIGHT)
        self.hospital = hospital
        self._build()

    def _build(self):
        set_bg(self)
        bell_header(self)

        tk.Label(self, text=self.hospital.name, font=FONT_TITLE,
                 bg=BG_LIGHT, fg=TEXT_DARK, justify="center").pack(pady=(0, 14))

        grid = tk.Frame(self, bg=BG_LIGHT)
        grid.pack(padx=20, pady=6, fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        grid_btn(grid, "Επείγουσα\nΕκκληση",     "urgent",       0, 0, self._urgent_appeal)
        grid_btn(grid, "Καταγραφή\nΑιμοδοσίας",  "donation_reg", 0, 1, lambda: messagebox.showinfo("", "Καταγραφή αιμοδοσίας"))
        grid_btn(grid, "Αποθέματα\nΑίματος",      "inventory",    1, 0, self._show_inventory)
        grid_btn(grid, "Εκδοση\nΒεβαίωσης",       "certificate",  1, 1, lambda: messagebox.showinfo("", "Εκδοση βεβαίωσης"))

        rounded_btn(self, "Αποσύνδεση", self.master.show_login).pack(pady=20)

    def _show_inventory(self):
        win = tk.Toplevel(self, bg=BG_LIGHT)
        win.title("Αποθέματα Αίματος")
        win.geometry("280x340")
        tk.Label(win, text="Αποθέματα Αίματος", font=FONT_SUB,
                 bg=BG_LIGHT, fg=TEXT_DARK).pack(pady=12)
        for btype, qty in self.hospital.blood_inventory.stock.items():
            low   = self.hospital.blood_inventory.is_low(btype)
            color = ACCENT if low else TEXT_DARK
            row   = tk.Frame(win, bg=BG_CARD)
            row.pack(fill="x", padx=20, pady=2, ipady=4)
            tk.Label(row, text=f"  {btype}", font=FONT_BODY,
                     bg=BG_CARD, fg=TEXT_MID, width=6, anchor="w").pack(side="left")
            tk.Label(row, text=f"{qty} μονάδες{'  (!)' if low else ''}",
                     font=FONT_BODY, bg=BG_CARD, fg=color).pack(side="right", padx=10)

    def _urgent_appeal(self):
        low = [bt for bt in self.hospital.blood_inventory.stock
               if self.hospital.blood_inventory.is_low(bt)]
        if not low:
            messagebox.showinfo("Επείγουσα Εκκληση",
                                "Δεν υπάρχουν χαμηλά αποθέματα αυτή τη στιγμή.")
        else:
            messagebox.showwarning("Επείγουσα Εκκληση",
                                   f"Χαμηλά αποθέματα: {', '.join(low)}\n"
                                   "Αποστολή ειδοποίησης σε διαθέσιμους donors.")

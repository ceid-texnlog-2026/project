import tkinter as tk
from tkinter import messagebox
from config import (light_green, card_green, dark_green, dark_text,
                    mid_text, title_font, subtitle_font, normal_font,
                    small_font, red, set_background)
from widgets import simple_button
from db import DBManager


class AvailabilityFrame(tk.Frame):
    def __init__(self, master, donor):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Διαθεσιμότητα", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(40, 20))

        # Κάρτα τρέχουσας κατάστασης
        self.status_card = tk.Frame(self, bg=card_green)
        self.status_card.pack(padx=40, fill="x", ipady=20, pady=10)

        tk.Label(self.status_card, text="Τρέχουσα κατάσταση:",
                 font=normal_font, bg=card_green, fg=mid_text).pack(pady=(14, 4))

        self.status_label = tk.Label(self.status_card, font=subtitle_font, bg=card_green)
        self.status_label.pack(pady=(0, 14))

        self.update_status_label()

        # Ενημερωτικό μήνυμα
        info = tk.Frame(self, bg=card_green)
        info.pack(padx=40, fill="x", ipady=10, pady=6)
        tk.Label(info, text="Αν είσαι διαθέσιμος, θα λαμβάνεις\nειδοποιήσεις σε περίπτωση επείγουσας\nανάγκης αίματος.",
                 font=small_font, bg=card_green, fg=mid_text,
                 justify="center", wraplength=280).pack(pady=10)

        # Κουμπί αλλαγής
        self.toggle_btn = simple_button(self, self.get_button_text(), self.confirm_toggle)
        self.toggle_btn.pack(pady=20)

        simple_button(self, "Επιστροφή", self.go_back,
                      color=mid_text).pack()

    def update_status_label(self):
        if self.donor.is_available:
            self.status_label.config(text="Διαθέσιμος", fg=dark_green)
        else:
            self.status_label.config(text="Μη Διαθέσιμος", fg=red)

    def get_button_text(self):
        if self.donor.is_available:
            return "Απενεργοποίηση Διαθεσιμότητας"
        return "Ενεργοποίηση Διαθεσιμότητας"

    def confirm_toggle(self):
        if self.donor.is_available:
            msg = "Θέλεις να απενεργοποιήσεις τη διαθεσιμότητά σου;\nΔεν θα λαμβάνεις πλέον ειδοποιήσεις επείγουσας ανάγκης."
        else:
            msg = "Θέλεις να ενεργοποιήσεις τη διαθεσιμότητά σου;\nΘα λαμβάνεις ειδοποιήσεις σε περίπτωση επείγουσας ανάγκης αίματος."

        confirmed = messagebox.askyesno("Επιβεβαίωση", msg)
        if confirmed:
            self.donor.is_available = not self.donor.is_available
            DBManager().save_user(self.donor)
            self.update_status_label()
            self.toggle_btn.config(text=self.get_button_text())
            messagebox.showinfo("Επιτυχία", "Η διαθεσιμότητά σου ενημερώθηκε!")

    def go_back(self):
        self.master.show_donor(self.donor)
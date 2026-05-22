import tkinter as tk
from tkinter import messagebox

from config import *
from widgets import simple_button, bell_header
from db import DBManager


class CreateAlertFrame(tk.Frame):

    def __init__(self, master, hospital, donors):
        super().__init__(master, bg=light_green)

        self.hospital = hospital
        self.donors = donors

        self.build()

    def build(self):

        self.pack(fill="both", expand=True)

        set_background(self)

        bell_header(self)

        tk.Label(
            self,
            text="Δημιουργία Ειδοποίησης",
            font=title_font,
            bg=light_green,
            fg=dark_text
        ).pack(pady=(5, 15))

        home_box = tk.Frame(
            self,
            bg="#80c8b3"
        )

        home_box.pack(pady=10)

        home_label = tk.Label(
            home_box,
            text="🏥",
            font=("Arial", 34),
            bg="#80c8b3"
        )

        home_label.pack(
            padx=18,
            pady=8
        )

        self.blood_var = tk.StringVar(
            value=""
        )

        blood_menu = tk.OptionMenu(
            self,
            self.blood_var,
            "Επιλογή",
            "A+",
            "A-",
            "B+",
            "B-",
            "AB+",
            "AB-",
            "O+",
            "O-",
            command=lambda value:
            self.update_preview()
        )

        blood_menu.config(
            font=subtitle_font,
            bg=white,
            fg=dark_text,
            width=10
        )

        blood_menu.pack(pady=12)

        tk.Label(
            self,
            text="Αριθμός μονάδων",
            font=normal_font,
            bg=light_green,
            fg=dark_text
        ).pack(pady=(5, 2))

        self.units_entry = tk.Entry(
            self,
            width=12,
            font=normal_font,
            justify="center"
        )

        self.units_entry.pack(pady=6)

        self.units_entry.insert(0, "1")

        self.units_entry.bind(
            "<KeyRelease>",
            lambda event:
            self.update_preview()
        )

        tk.Label(
            self,
            text=f"📍 Τοποθεσία: {self.hospital.name}",
            font=normal_font,
            bg=white,
            fg=dark_text
        ).pack(
            pady=12,
            ipadx=10,
            ipady=6
        )

        self.preview_label = tk.Label(
            self,
            text="",
            font=subtitle_font,
            bg=white,
            fg=dark_text,
            wraplength=330,
            justify="center"
        )

        self.preview_label.pack(
            padx=25,
            pady=15,
            ipadx=10,
            ipady=20,
            fill="x"
        )

        simple_button(
            self,
            "✈  Αποστολή Ειδοποίησης",
            self.publish_alert
        ).pack(pady=15)

        simple_button(
            self,
            "Πίσω",
            self.go_back
        ).pack(pady=5)

        self.update_preview()

    def update_preview(self):

        blood_type = self.blood_var.get()

        units = self.units_entry.get()

        if (
            blood_type == ""
            or blood_type == "Επιλογή"
        ):

            self.preview_label.config(
                text=""
            )

            return

        if units.strip():

            text = (
                f"Επείγουσα ανάγκη για "
                f"{units} μονάδες αίματος "
                f"ομάδας {blood_type}\n\n"
                f"Παρακαλούνται οι εθελοντές "
                f"να προσέλθουν άμεσα."
            )

        else:

            text = (
                f"Επείγουσα ανάγκη για "
                f"αίμα ομάδας {blood_type}\n\n"
                f"Παρακαλούνται οι εθελοντές "
                f"να προσέλθουν άμεσα."
            )

        self.preview_label.config(
            text=text
        )

    def publish_alert(self):

        blood_type = self.blood_var.get()

        if (
            blood_type == ""
            or blood_type == "Επιλογή"
        ):

            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει να επιλέξεις ομάδα αίματος."
            )

            return

        units_text = (
            self.units_entry.get().strip()
        )

        try:

            required_units = int(
                units_text
            )

        except ValueError:

            messagebox.showerror(
                "Σφάλμα",
                "Ο αριθμός μονάδων "
                "πρέπει να είναι αριθμός."
            )

            return

        if required_units <= 0:

            messagebox.showerror(
                "Σφάλμα",
                "Ο αριθμός μονάδων "
                "πρέπει να είναι "
                "μεγαλύτερος από 0."
            )

            return

        try:
            alert, targets = DBManager().send_emergency_alert(
                self.hospital,
                blood_type,
                required_units,
            )

        except Exception:
            messagebox.showerror(
                "Αποτυχία",
                "Αποτυχία αποστολής "
                "ειδοποιήσεων.\n"
                "Δοκιμάστε ξανά αργότερα."
            )
            return

        if targets:
            messagebox.showinfo(
                "Επιτυχία",
                f"Η ειδοποίηση στάλθηκε "
                f"σε {len(targets)} αιμοδότη/ες\n"
                f"με ομάδα αίματος {blood_type}."
            )
        else:
            messagebox.showinfo(
                "Αποστολή",
                f"Δεν βρέθηκαν διαθέσιμοι αιμοδότες\n"
                f"με ομάδα αίματος {blood_type}.\n"
                "Η ειδοποίηση καταγράφηκε."
            )

    def go_back(self):

        from frames.hospital_frame import (
            HospitalFrame
        )

        self.master.switch(
            HospitalFrame,
            self.hospital,
            self.donors
        )
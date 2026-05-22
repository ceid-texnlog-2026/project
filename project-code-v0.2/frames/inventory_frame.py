import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import random

from config import *
from widgets import simple_button, bell_header
from models import BloodUnit
from db import DBManager


class InventoryFrame(tk.Frame):

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
            text="Διαχείριση Αποθεμάτων Αίματος",
            font=subtitle_font,
            bg=light_green,
            fg=dark_text,
            wraplength=360,
            justify="center"
        ).pack(pady=(5, 8))

        self.stock_label = tk.Label(
            self,
            text="",
            font=normal_font,
            bg=white,
            fg=dark_text,
            wraplength=340,
            justify="center"
        )
        self.stock_label.pack(
            padx=20,
            pady=3,
            ipadx=6,
            ipady=4,
            fill="x"
        )

        self.warning_label = tk.Label(
            self,
            text="",
            font=small_font,
            bg=card_green,
            fg=dark_text,
            wraplength=340,
            justify="center"
        )
        self.warning_label.pack(
            padx=20,
            pady=2,
            ipadx=8,
            ipady=3,
            fill="x"
        )

        tk.Label(
            self,
            text="Καταγραφή Νέας Μονάδας",
            font=subtitle_font,
            bg=light_green,
            fg=dark_text
        ).pack(pady=(3, 1))

        self.blood_var = tk.StringVar(value="A+")

        blood_menu = tk.OptionMenu(
            self,
            self.blood_var,
            "A+", "A-", "B+", "B-",
            "AB+", "AB-", "O+", "O-"
        )
        blood_menu.config(
            font=normal_font,
            bg=white,
            fg=dark_text,
            width=14
        )
        blood_menu.pack(pady=2)

        self.product_var = tk.StringVar(value="Αίμα")

        product_menu = tk.OptionMenu(
            self,
            self.product_var,
            "Αίμα",
            "Πλάσμα",
            "Αιμοπετάλια"
        )
        product_menu.config(
            font=normal_font,
            bg=white,
            fg=dark_text,
            width=14
        )
        product_menu.pack(pady=2)

        self.unit_code_entry = tk.Entry(
            self,
            width=22,
            font=normal_font,
            justify="center"
        )
        self.unit_code_entry.pack(pady=2)
        self.unit_code_entry.insert(0, "BAG-001")

        self.collection_date_entry = tk.Entry(
            self,
            width=22,
            font=normal_font,
            justify="center"
        )
        self.collection_date_entry.pack(pady=2)
        self.collection_date_entry.insert(0, "2026-05-01")

        simple_button(
            self,
            "Προσθήκη / Ανανέωση Μονάδων",
            self.add_unit
        ).pack(pady=3)

        tk.Label(
            self,
            text="Ενημέρωση Κατάστασης Μονάδας",
            font=subtitle_font,
            bg=light_green,
            fg=dark_text
        ).pack(pady=(3, 1))

        self.status_code_entry = tk.Entry(
            self,
            width=22,
            font=normal_font,
            justify="center"
        )
        self.status_code_entry.pack(pady=2)
        self.status_code_entry.insert(0, "BAG-001")

        self.status_var = tk.StringVar(value="used")

        status_menu = tk.OptionMenu(
            self,
            self.status_var,
            "used",
            "discarded"
        )
        status_menu.config(
            font=normal_font,
            bg=white,
            fg=dark_text,
            width=14
        )
        status_menu.pack(pady=2)

        simple_button(
            self,
            "Ενημέρωση Κατάστασης",
            self.update_unit_status
        ).pack(pady=4)

        simple_button(
            self,
            "Πίσω",
            self.go_back
        ).pack(pady=2)

        self.refresh_inventory()

    def refresh_inventory(self):
        stock = self.hospital.blood_inventory.stock
        total = sum(stock.values())

        if total == 0:
            self.stock_label.config(
                text=(
                    "Δεν υπάρχει διαθέσιμο απόθεμα.\n"
                    "Καταχωρήστε νέα λήψη αίματος."
                )
            )
        else:
            text = "Τρέχον απόθεμα:\n\n"

            for blood_type, quantity in stock.items():
                text += f"{blood_type}: {quantity} μονάδες\n"

            self.stock_label.config(text=text)

        expiring = self.hospital.blood_inventory.get_expiring_soon_units()

        if not expiring:
            self.warning_label.config(
                text="Δεν υπάρχουν μονάδες που πλησιάζουν στη λήξη."
            )
        else:
            warning = "Προειδοποίηση λήξης:\n\n"

            for unit in expiring:
                warning += (
                    f"{unit.unit_code} - {unit.blood_type} "
                    f"λήγει {unit.expiration_date}\n"
                )

            self.warning_label.config(text=warning)

    def calculate_expiration_date(self, collection_date, product_type):
        if product_type == "whole_blood":
            return collection_date + timedelta(days=35)

        if product_type == "platelets":
            return collection_date + timedelta(days=5)

        if product_type == "plasma":
            return collection_date + timedelta(days=365)

        return collection_date + timedelta(days=35)

    def add_unit(self):
        blood_type = self.blood_var.get()
        product_type = self.product_var.get()
        unit_code = self.unit_code_entry.get().strip()
        collection_text = self.collection_date_entry.get().strip()

        if not unit_code:
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει να εισάγετε μοναδικό κωδικό φιάλης."
            )
            return

        try:
            collection_date = datetime.strptime(
                collection_text,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            messagebox.showerror(
                "Σφάλμα",
                "Η ημερομηνία λήψης πρέπει να είναι στη μορφή YYYY-MM-DD."
            )
            return

        expiration_date = self.calculate_expiration_date(
            collection_date,
            product_type
        )

        unit = BloodUnit(
            blood_type=blood_type,
            quantity=1,
            expiration_date=expiration_date,
            unit_code=unit_code,
            collection_date=collection_date,
            product_type=product_type
        )

        DBManager().save_blood_unit(self.hospital, unit)

        messagebox.showinfo(
            "Επιτυχία",
            f"Η μονάδα καταχωρήθηκε.\n"
            f"Ημερομηνία λήξης: {expiration_date}"
        )

        self.refresh_inventory()

    def update_unit_status(self):
        unit_code = self.status_code_entry.get().strip()
        new_status = self.status_var.get()

        if not unit_code:
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει να εισάγετε κωδικό μονάδας."
            )
            return

        if random.randint(1, 10) == 1:
            messagebox.showerror(
                "Σφάλμα σύνδεσης",
                "Παρουσιάστηκε τεχνικό σφάλμα κατά την ενημέρωση.\n"
                "Προσπαθήστε ξανά."
            )
            return

        unit = DBManager().update_blood_unit_status(
            self.hospital,
            unit_code,
            new_status
        )

        if unit is None:
            messagebox.showerror(
                "Σφάλμα",
                "Δεν βρέθηκε μονάδα με αυτόν τον κωδικό."
            )
            return

        messagebox.showinfo(
            "Επιτυχία",
            "Η κατάσταση της μονάδας ενημερώθηκε επιτυχώς."
        )

        self.refresh_inventory()

    def go_back(self):
        from frames.hospital_frame import HospitalFrame

        self.master.switch(
            HospitalFrame,
            self.hospital,
            self.donors
        )
import tkinter as tk
from tkinter import messagebox

from config import *
from widgets import simple_button, bell_header
from db import DBManager


class RecordDonationFrame(tk.Frame):

    def __init__(self, master, hospital, donors):
        super().__init__(master, bg=light_green)

        self.hospital = hospital
        self.donors = donors
        self.selected_donor = None
        self.donation_confirmed = False

        self.build()

    def build(self):
        self.pack(fill="both", expand=True)

        set_background(self)
        bell_header(self)

        tk.Label(
            self,
            text="Καταγραφή Αιμοδοσίας",
            font=title_font,
            bg=light_green,
            fg=dark_text
        ).pack(pady=(2, 3))

        tk.Label(
            self,
            text="Σάρωση QR Code Εθελοντή",
            font=subtitle_font,
            bg=white,
            fg=dark_text
        ).pack(pady=(3, 2), ipadx=8, ipady=3)

        self.qr_entry = tk.Entry(
            self,
            width=30,
            font=normal_font,
            justify="center"
        )
        self.qr_entry.pack(pady=5)

        self.qr_entry.insert(0, "QR-NIKOS-001")

        simple_button(
            self,
            "Σάρωση QR",
            self.scan_qr
        ).pack(pady=4)

        

        self.search_label = tk.Label(
            self,
            text="Αναζήτηση με όνομα ή ΑΜΚΑ",
            font=normal_font,
            bg=light_green,
            fg=dark_text
        )

        self.search_entry = tk.Entry(
            self,
            width=30,
            font=normal_font,
            justify="center"
        )

        self.search_button = simple_button(
            self,
            "Αναζήτηση",
            self.search_donor
        )

        self.donor_info = tk.Label(
            self,
            text="Δεν έχει ταυτοποιηθεί εθελοντής.",
            font=normal_font,
            bg=white,
            fg=dark_text,
            wraplength=330,
            justify="center"
        )
        self.donor_info.pack(
            padx=20,
            pady=10,
            ipadx=10,
            ipady=12,
            fill="x"
        )

        self.confirm_var = tk.BooleanVar(value=False)

        self.confirm_check = tk.Checkbutton(
            self,
            text="Επιβεβαιώνω ότι η αιμοδοσία ολοκληρώθηκε επιτυχώς",
            variable=self.confirm_var,
            font=small_font,
            bg=light_green,
            fg=dark_text,
            wraplength=330,
            justify="center"
        )
        self.confirm_check.pack(pady=4)

        tk.Label(
            self,
            text="Τύπος αιμοδοσίας",
            font=normal_font,
            bg=light_green,
            fg=dark_text
        ).pack(pady=(5, 2))

        self.donation_type_var = tk.StringVar(value="Αίμα")

        type_menu = tk.OptionMenu(
            self,
            self.donation_type_var,
            "Αίμα",
            "Πλάσμα",
            "Αιμοπετάλια"
        )
        type_menu.config(
            font=normal_font,
            bg=white,
            fg=dark_text,
            width=16
        )
        type_menu.pack(pady=2)

        simple_button(
            self,
            "Καταγραφή Αιμοδοσίας",
            self.record_donation
        ).pack(pady=8)

        simple_button(
            self,
            "Πίσω",
            self.go_back
        ).pack(pady=4)

    def scan_qr(self):
        qr_value = self.qr_entry.get().strip()

        if not qr_value:
            messagebox.showerror(
                "Αποτυχία QR",
                "Το σύστημα δεν αναγνώρισε το QRCode.\n"
                "Αναζητήστε τον εθελοντή με όνομα ή ΑΜΚΑ."
            )
            self.show_manual_search()
            return

        donor = self.find_donor_by_qr(qr_value)

        if donor is None:
            messagebox.showerror(
                "Δεν υπάρχει καταχώρηση",
                "Το σύστημα δεν βρίσκει τα στοιχεία του εθελοντή.\n"
                "Μπορείτε να ξεκινήσετε διαδικασία νέας εγγραφής."
            )
            self.show_manual_search()
            return

        self.selected_donor = donor
        self.display_donor(donor)

    def show_manual_search(self):
        self.search_label.pack(pady=(8, 2))
        self.search_entry.pack(pady=4)
        self.search_button.pack(pady=4)

    def search_donor(self):
        query = self.search_entry.get().strip().lower()

        if not query:
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει να γράψετε όνομα ή ΑΜΚΑ."
            )
            return

        donor = self.find_donor_by_name_or_amka(query)

        if donor is None:
            messagebox.showerror(
                "Δεν υπάρχει καταχώρηση",
                "Ο εθελοντής δεν υπάρχει στο σύστημα.\n"
                "Μπορείτε να ξεκινήσετε διαδικασία νέας εγγραφής."
            )
            return

        self.selected_donor = donor
        self.display_donor(donor)

    def find_donor_by_qr(self, qr_value):
        for donor in self.donors:
            if donor.qr_code == qr_value:
                return donor

        return None

    def find_donor_by_name_or_amka(self, query):
        for donor in self.donors:
            full_name = donor.full_name.lower()
            amka = donor.amka.lower()

            if query == full_name or query == amka:
                return donor

        return None

    def display_donor(self, donor):
        last_donation_text = "Δεν υπάρχει"

        if donor.donations:
            last_donation_text = donor.donations[-1].donation_date

        elif donor.get_last_donation():
            last_donation_text = donor.get_last_donation().appointment_date

        text = (
            f"Όνομα: {donor.full_name}\n"
            f"ΑΜΚΑ: {donor.amka}\n"
            f"Ομάδα αίματος: {donor.blood_type}\n\n"
            f"Τελευταία αιμοδοσία: {last_donation_text}\n"
            f"Κατάσταση: Επιτρέπεται αιμοδοσία"
        )

        self.donor_info.config(text=text)

    def record_donation(self):
        if self.selected_donor is None:
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει πρώτα να ταυτοποιηθεί εθελοντής."
            )
            return

        if not self.confirm_var.get():
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει να επιβεβαιώσετε ότι η αιμοδοσία ολοκληρώθηκε επιτυχώς."
            )
            return

        donation_type_map = {"Αίμα": "whole_blood", "Πλάσμα": "plasma",
                             "Αιμοπετάλια": "platelets"}
        donation_type = donation_type_map.get(self.donation_type_var.get(),
                                              "whole_blood")

        DBManager().record_donation(
            self.hospital,
            self.selected_donor,
            donation_type
        )

        messagebox.showinfo(
            "Επιτυχία",
            "Η αιμοδοσία αποθηκεύτηκε επιτυχώς.\n"
            "Το ιστορικό αιμοδοσιών του εθελοντή ενημερώθηκε."
        )

        self.display_donor(self.selected_donor)

    def go_back(self):
        from frames.hospital_frame import HospitalFrame

        self.master.switch(
            HospitalFrame,
            self.hospital,
            self.donors
        )
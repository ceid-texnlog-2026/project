import os
import random
import tkinter as tk
from tkinter import messagebox

from reportlab.pdfgen import canvas

from config import *
from widgets import simple_button, bell_header
from db import DBManager
from datetime import date as _date
from models import DonationCertificate


class CertificateFrame(tk.Frame):

    def __init__(self, master, hospital, donors):
        super().__init__(master, bg=light_green)

        self.hospital = hospital
        self.donors = donors
        self.selected_donation = None
        self.selected_donor = None
        self.generated_pdf_path = None

        self.build()

    def build(self):
        self.pack(fill="both", expand=True)

        set_background(self)
        bell_header(self)

        tk.Label(
            self,
            text="Έκδοση Βεβαίωσης Αιμοδοσίας",
            font=subtitle_font,
            bg=light_green,
            fg=dark_text,
            wraplength=360,
            justify="center"
        ).pack(pady=(5, 8))

        tk.Label(
            self,
            text="Ολοκληρωμένες αιμοδοσίες",
            font=normal_font,
            bg=white,
            fg=dark_text
        ).pack(pady=(5, 3), ipadx=10, ipady=4)

        self.donation_var = tk.StringVar(value="")

        self.donation_menu = tk.OptionMenu(
            self,
            self.donation_var,
            ""
        )

        self.donation_menu.config(
            font=normal_font,
            bg=white,
            fg=dark_text,
            width=28
        )

        self.donation_menu.pack(pady=5)

        simple_button(
            self,
            "Φόρτωση Στοιχείων",
            self.load_selected_donation
        ).pack(pady=6)

        self.info_box = tk.Label(
            self,
            text="Δεν έχει επιλεγεί αιμοδοσία.",
            font=normal_font,
            bg=white,
            fg=dark_text,
            wraplength=330,
            justify="center"
        )

        self.info_box.pack(
            padx=20,
            pady=10,
            ipadx=10,
            ipady=12,
            fill="x"
        )

        simple_button(
            self,
            "Έκδοση PDF Βεβαίωσης",
            self.issue_certificate
        ).pack(pady=8)

        simple_button(
            self,
            "Πίσω",
            self.go_back
        ).pack(pady=4)

        self.load_completed_donations()

    def load_completed_donations(self):
        donations = [d for d in self.hospital.donations if d.status == "completed"]

        menu = self.donation_menu["menu"]
        menu.delete(0, "end")

        if not donations:
            self.donation_var.set("")
            self.info_box.config(
                text="Δεν υπάρχουν ολοκληρωμένες αιμοδοσίες."
            )
            return

        for index, donation in enumerate(donations):
            donor = self.find_donor_by_donation(donation)

            donor_name = "Άγνωστος εθελοντής"

            if donor:
                donor_name = donor.full_name or donor.username

            option_text = (
                f"{index + 1}. {donor_name} - "
                f"{donation.donation_date} - "
                f"{donation.blood_group}"
            )

            menu.add_command(
                label=option_text,
                command=lambda value=option_text:
                self.donation_var.set(value)
            )

        self.donation_var.set("Επιλέξτε αιμοδοσία")

    def find_donor_by_donation(self, donation):
        for donor in self.donors:
            if donation in donor.donations:
                return donor

        return None

    def load_selected_donation(self):
        selected = self.donation_var.get()

        if not selected or selected == "Επιλέξτε αιμοδοσία":
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει να επιλέξετε αιμοδοσία."
            )
            return

        try:
            index = int(selected.split(".")[0]) - 1
        except ValueError:
            messagebox.showerror(
                "Σφάλμα",
                "Μη έγκυρη επιλογή αιμοδοσίας."
            )
            return

        donations = [d for d in self.hospital.donations if d.status == "completed"]

        if index < 0 or index >= len(donations):
            messagebox.showerror(
                "Σφάλμα",
                "Η αιμοδοσία δεν βρέθηκε."
            )
            return

        donation = donations[index]
        donor = self.find_donor_by_donation(donation)

        if donor is None:
            messagebox.showerror(
                "Σφάλμα",
                "Δεν βρέθηκε ο αιμοδότης για αυτή την αιμοδοσία."
            )
            return

        self.selected_donation = donation
        self.selected_donor = donor

        donor_name = donor.full_name or donor.username

        text = (
            f"Όνομα εθελοντή: {donor_name}\n"
            f"ΑΜΚΑ: {donor.amka}\n"
            f"Ομάδα αίματος: {donor.blood_type}\n\n"
            f"Ημερομηνία αιμοδοσίας: {donation.donation_date}\n"
            f"Φορέας αιμοδοσίας: {donation.organization}\n"
            f"Τύπος αιμοδοσίας: {donation.donation_type}"
        )

        self.info_box.config(text=text)

    def create_pdf(self, donor, donation):
        if random.randint(1, 10) == 1:
            raise Exception("Αποτυχία δημιουργίας PDF.")

        certificates_dir = "certificates"

        if not os.path.exists(certificates_dir):
            os.makedirs(certificates_dir)

        donor_name = donor.full_name or donor.username

        safe_name = donor_name.replace(" ", "_")

        filename = (
            f"certificate_{safe_name}_"
            f"{donation.donation_date}.pdf"
        )

        pdf_path = os.path.join(
            certificates_dir,
            filename
        )

        c = canvas.Canvas(pdf_path)

        c.setFont("Helvetica-Bold", 18)
        c.drawString(
            120,
            780,
            "Blood Donation Certificate"
        )

        c.setFont("Helvetica", 12)

        c.drawString(
            80,
            720,
            f"Donor Name: {donor_name}"
        )

        c.drawString(
            80,
            695,
            f"AMKA: {donor.amka}"
        )

        c.drawString(
            80,
            670,
            f"Blood Type: {donor.blood_type}"
        )

        c.drawString(
            80,
            645,
            f"Donation Date: {donation.donation_date}"
        )

        c.drawString(
            80,
            620,
            f"Organization: {donation.organization}"
        )

        c.drawString(
            80,
            595,
            f"Donation Type: {donation.donation_type}"
        )

        c.drawString(
            80,
            540,
            "This document certifies that the above donor completed a blood donation."
        )

        c.drawString(
            80,
            500,
            f"Issue Date: {donation.donation_date}"
        )

        c.save()

        return pdf_path

    def issue_certificate(self):
        if self.selected_donation is None or self.selected_donor is None:
            messagebox.showerror(
                "Σφάλμα",
                "Πρέπει πρώτα να επιλέξετε και να φορτώσετε μία αιμοδοσία."
            )
            return

        try:
            pdf_path = self.create_pdf(
                self.selected_donor,
                self.selected_donation
            )

        except Exception:
            messagebox.showerror(
                "Σφάλμα δημιουργίας εγγράφου",
                "Το σύστημα απέτυχε να δημιουργήσει το PDF.\n"
                "Μπορείτε να δοκιμάσετε ξανά."
            )
            return

        self.generated_pdf_path = pdf_path

        try:
            cert_number = f"CERT-{self.hospital.user_id}-{len(self.selected_donor.certificates) + 1:03d}"
            certificate = DonationCertificate(
                hospital_id=self.hospital.user_id,
                donor_id=self.selected_donor.user_id,
                certificate_number=cert_number,
                issue_date=_date.today(),
                donation_date=self.selected_donation.donation_date,
                donor_name=self.selected_donor.full_name or self.selected_donor.username,
                organization=self.hospital.name,
                pdf_path=pdf_path,
            )
            DBManager().save_certificate(self.selected_donor, certificate)

        except Exception:
            messagebox.showerror(
                "Σφάλμα αποθήκευσης",
                "Το σύστημα απέτυχε να αποθηκεύσει τη βεβαίωση "
                "στο προφίλ του εθελοντή.\n\n"
                f"Μπορείτε να κατεβάσετε το PDF από:\n{pdf_path}\n\n"
                "Δοκιμάστε ξανά την αποθήκευση αργότερα."
            )
            return

        messagebox.showinfo(
            "Επιτυχία",
            "Η βεβαίωση εκδόθηκε επιτυχώς.\n"
            "Το PDF δημιουργήθηκε και αποθηκεύτηκε στο προφίλ του εθελοντή."
        )

    def go_back(self):
        from frames.hospital_frame import HospitalFrame

        self.master.switch(
            HospitalFrame,
            self.hospital,
            self.donors
        )
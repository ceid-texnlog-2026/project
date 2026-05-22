import tkinter as tk
from tkinter import messagebox, ttk
from config import (light_green, card_green, dark_text, mid_text,
                    title_font, normal_font, small_font, set_background)
from widgets import simple_button
from db import DBManager
from models import Donor, Hospital


def labeled_entry(parent, label_text, show=None):
    tk.Label(parent, text=label_text, font=small_font,
             bg=light_green, fg=mid_text).pack(pady=(6, 0))
    entry = tk.Entry(parent, font=normal_font, width=30,
                     bg=card_green, fg=dark_text,
                     relief="flat", insertbackground=dark_text)
    if show:
        entry.config(show=show)
    entry.pack(pady=2, ipady=5)
    return entry


def _scrollable(parent):
    canvas = tk.Canvas(parent, bg=light_green, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    inner = tk.Frame(canvas, bg=light_green)
    canvas.create_window((0, 0), window=inner, anchor="nw", width=380)
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    return inner


class DonorSignupScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=light_green)
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)
        inner = _scrollable(self)

        tk.Label(inner, text="Εγγραφή Αιμοδότη", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(16, 8))

        self.username = labeled_entry(inner, "Username")
        self.full_name = labeled_entry(inner, "Ονοματεπώνυμο")
        self.email = labeled_entry(inner, "Email")
        self.password = labeled_entry(inner, "Κωδικός", show="*")
        self.amka = labeled_entry(inner, "ΑΜΚΑ (11 ψηφία)")
        self.phone = labeled_entry(inner, "Τηλέφωνο")

        tk.Label(inner, text="Ομάδα αίματος", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(6, 0))
        self.blood_var = tk.StringVar(value="A+")
        ttk.Combobox(inner, textvariable=self.blood_var,
                     values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                     state="readonly", width=10).pack(pady=2)

        simple_button(inner, "Δημιουργία λογαριασμού", self.submit).pack(pady=14)
        simple_button(inner, "Πίσω", lambda: self.master.show_login(),
                      color=mid_text).pack(pady=4)

    def submit(self):
        if not all([self.username.get().strip(),
                    self.email.get().strip(),
                    self.password.get().strip(),
                    self.amka.get().strip()]):
            messagebox.showerror("Σφάλμα",
                                 "Πρέπει να συμπληρώσετε username, email, "
                                 "κωδικό και ΑΜΚΑ.")
            return

        if self.db.email_exists(self.email.get().strip()):
            messagebox.showerror("Σφάλμα",
                                 "Υπάρχει ήδη λογαριασμός με αυτό το email.")
            return

        amka = self.amka.get().strip()
        if len(amka) != 11 or not amka.isdigit():
            messagebox.showerror("Σφάλμα",
                                 "Το ΑΜΚΑ πρέπει να είναι 11 ψηφία.")
            return

        donor = Donor(
            username=self.username.get().strip(),
            email=self.email.get().strip(),
            password=self.password.get().strip(),
            full_name=self.full_name.get().strip(),
            amka=amka,
            blood_type=self.blood_var.get(),
            phone=self.phone.get().strip(),
        )
        self.db.register_donor(donor)
        messagebox.showinfo("Επιτυχία",
                            f"Η εγγραφή ολοκληρώθηκε.\n"
                            f"QR Code: {donor.qr_code}")
        self.master.show_login()


class HospitalSignupScreen(tk.Frame):
    """Hospital self-registers. Account is created uncertified.
    Hospital can then login and submit a certification application."""

    def __init__(self, master):
        super().__init__(master, bg=light_green)
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)
        inner = _scrollable(self)

        tk.Label(inner, text="Εγγραφή Νοσοκομείου", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(16, 6))

        tk.Label(inner,
                 text="Δημιουργήστε λογαριασμό. Μετά τη σύνδεση\n"
                      "θα πρέπει να υποβάλετε αίτηση πιστοποίησης\n"
                      "πριν αποκτήσετε πρόσβαση στις λειτουργίες.",
                 font=small_font, bg=light_green, fg=mid_text,
                 justify="center").pack(pady=(0, 6))

        self.hospital_name = labeled_entry(inner, "Όνομα Φορέα")
        self.username = labeled_entry(inner, "Username")
        self.email = labeled_entry(inner, "Email")
        self.password = labeled_entry(inner, "Κωδικός", show="*")
        self.phone = labeled_entry(inner, "Τηλέφωνο")
        self.address = labeled_entry(inner, "Διεύθυνση")
        self.city = labeled_entry(inner, "Πόλη")
        self.region = labeled_entry(inner, "Περιφέρεια")

        simple_button(inner, "Δημιουργία λογαριασμού", self.submit).pack(pady=14)
        simple_button(inner, "Πίσω", lambda: self.master.show_login(),
                      color=mid_text).pack(pady=4)

    def submit(self):
        if not all([self.hospital_name.get().strip(),
                    self.username.get().strip(),
                    self.email.get().strip(),
                    self.password.get().strip()]):
            messagebox.showerror("Σφάλμα",
                                 "Συμπληρώστε όνομα φορέα, username, email "
                                 "και κωδικό.")
            return

        if self.db.email_exists(self.email.get().strip()):
            messagebox.showerror("Σφάλμα",
                                 "Υπάρχει ήδη λογαριασμός με αυτό το email.")
            return

        hospital = Hospital(
            username=self.username.get().strip(),
            email=self.email.get().strip(),
            password=self.password.get().strip(),
            name=self.hospital_name.get().strip(),
            address=self.address.get().strip(),
            city=self.city.get().strip(),
            region=self.region.get().strip(),
            phone=self.phone.get().strip(),
            service_code="",
        )
        self.db.register_hospital(hospital)
        messagebox.showinfo(
            "Επιτυχία",
            "Ο λογαριασμός δημιουργήθηκε.\n"
            "Συνδεθείτε για να υποβάλετε αίτηση πιστοποίησης."
        )
        self.master.show_login()


HospitalApplicationScreen = HospitalSignupScreen

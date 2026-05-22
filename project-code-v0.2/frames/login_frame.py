import tkinter as tk
from tkinter import ttk, messagebox
from config import (light_green, dark_text, mid_text, title_font,
                    red, normal_font, small_font, get_icon, set_background)
from widgets import simple_button, input_field
from db import DBManager


class LoginScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=light_green)
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        logo_frame = tk.Frame(self, bg="white", bd=0)
        logo_frame.pack(pady=(20, 6), padx=80)
        kind, value = get_icon("logo", size=70)
        if kind == "image":
            label = tk.Label(logo_frame, image=value, bg="white")
            label.image = value
            label.pack(pady=(8, 0))
        else:
            tk.Label(logo_frame, text="RED HOPE", font=("Arial", 18, "bold"),
                     fg=red, bg="white").pack(pady=(8, 0))
            tk.Label(logo_frame, text="Blood for life", font=("Arial", 9),
                     fg=mid_text, bg="white").pack(pady=(0, 8))

        tk.Label(self, text="Σύνδεση", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(14, 6))

        self.email_field, _ = input_field(self, "Email")
        self.password_field, _ = input_field(self, "Κωδικός")

        self.selected_role = tk.StringVar(value="Ρόλος")
        ttk.Combobox(self, textvariable=self.selected_role,
                     values=["Αιμοδότης", "Νοσοκομείο", "Admin"],
                     font=normal_font, width=20, state="readonly").pack(pady=4)

        simple_button(self, "Σύνδεση", self.login).pack(pady=(12, 2))

        tk.Label(self, text="Δημιουργία προφίλ", font=("Arial", 12, "bold"),
                 bg=light_green, fg=dark_text).pack(pady=(14, 4))

        simple_button(self, "Εγγραφή Αιμοδότη", self.go_signup_donor).pack(pady=2)
        simple_button(self, "Εγγραφή Νοσοκομείου",
                      self.go_signup_hospital).pack(pady=2)

        tk.Label(self, text="Default admin: admin@redhope.gr / admin",
                 font=small_font, bg=light_green, fg=mid_text).pack(pady=(14, 0))

    def login(self):
        email = self.email_field.get().strip()
        password = self.password_field.get().strip()
        role = self.selected_role.get()

        if role == "Ρόλος":
            messagebox.showwarning("Σφάλμα", "Επέλεξε ρόλο.")
            return

        user = self.db.authenticate(email, password, role)
        if not user:
            messagebox.showerror("Σφάλμα", "Λάθος στοιχεία σύνδεσης.")
            return

        if getattr(user, "is_suspended", False):
            messagebox.showerror(
                "Λογαριασμός σε αναστολή",
                "Ο λογαριασμός σας έχει ανασταλεί από τη διαχείριση.\n"
                "Επικοινωνήστε με τον διαχειριστή."
            )
            return

        if role == "Αιμοδότης":
            self.master.show_donor(user)
        elif role == "Νοσοκομείο":
            self.master.show_hospital(user)
        else:
            self.master.show_admin(user)

    def go_signup_donor(self):
        from frames.signup_frame import DonorSignupScreen
        self.master.switch(DonorSignupScreen)

    def go_signup_hospital(self):
        from frames.signup_frame import HospitalSignupScreen
        self.master.switch(HospitalSignupScreen)


LoginFrame = LoginScreen

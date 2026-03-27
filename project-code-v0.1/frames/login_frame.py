import tkinter as tk
from tkinter import ttk, messagebox
from config import (light_green, dark_text, mid_text, title_font,
                    red, normal_font, get_icon, set_background)
from widgets import simple_button, input_field


class LoginFrame(tk.Frame):
    def __init__(self, master, users):
        super().__init__(master, bg=light_green)
        self.users = users
        self.build()

    def build(self):
        set_background(self)

        logo_frame = tk.Frame(self, bg="white", bd=0)
        logo_frame.pack(pady=(30, 10), padx=80)
        kind, value = get_icon("logo", size=80)
        if kind == "image":
            label = tk.Label(logo_frame, image=value, bg="white")
            label.image = value
            label.pack(pady=(10, 0))
        else:
            tk.Label(logo_frame, text="RED HOPE", font=("Arial", 18, "bold"),
                     fg=red, bg="white").pack(pady=(10, 0))
            tk.Label(logo_frame, text="Blood for life", font=("Arial", 9),
                     fg=mid_text, bg="white").pack(pady=(0, 10))

        tk.Label(self, text="Συνδεση", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(20, 10))

        self.email_field, _ = input_field(self, "Email")
        self.password_field, _ = input_field(self, "Κωδικός")

        self.selected_role = tk.StringVar(value="Ρόλος")
        ttk.Combobox(self, textvariable=self.selected_role,
                     values=["Αιμοδότης", "Νοσοκομείο", "Admin"],
                     font=normal_font, width=20, state="readonly").pack(pady=6)

        simple_button(self, "Συνδεση", self.login).pack(pady=(16, 4))

        tk.Label(self, text="Δημιουργία προφίλ", font=("Arial", 13, "bold"),
                 bg=light_green, fg=dark_text).pack(pady=(20, 6))

        simple_button(self, "Εγγραφή", lambda: None).pack()

    def login(self):
        email = self.email_field.get().strip()
        password = self.password_field.get().strip()
        role = self.selected_role.get()

        if role == "Ρόλος":
            messagebox.showwarning("Σφάλμα", "Επέλεξε ρόλο.")
            return

        user = self.users.get((email, password, role))
        if not user:
            messagebox.showerror("Σφάλμα", "Λάθος στοιχεία σύνδεσης.")
            return

        if role == "Αιμοδότης":    self.master.show_donor(user)
        elif role == "Νοσοκομείο": self.master.show_hospital(user)
        else:                       self.master.show_admin(user)

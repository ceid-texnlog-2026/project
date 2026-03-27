import tkinter as tk
from tkinter import ttk, messagebox
from config import (BG_LIGHT, TEXT_DARK, TEXT_MID, FONT_TITLE,
                    ACCENT, FONT_BODY, load_icon, set_bg)
from widgets import rounded_btn, field_entry


class LoginFrame(tk.Frame):
    def __init__(self, master, users: dict):
        super().__init__(master, bg=BG_LIGHT)
        self.users = users
        self._build()

    def _build(self):
        set_bg(self)

        # Logo
        logo_frame = tk.Frame(self, bg="white", bd=0)
        logo_frame.pack(pady=(30, 10), padx=80)
        kind, val = load_icon("logo", size=80)
        if kind == "image":
            lbl = tk.Label(logo_frame, image=val, bg="white")
            lbl.image = val
            lbl.pack(pady=(10, 0))
        else:
            tk.Label(logo_frame, text="RED HOPE", font=("Georgia", 18, "bold"),
                     fg=ACCENT, bg="white").pack(pady=(10, 0))
            tk.Label(logo_frame, text="Blood for life", font=("Helvetica", 9),
                     fg=TEXT_MID, bg="white").pack(pady=(0, 10))

        tk.Label(self, text="Συνδεση", font=FONT_TITLE,
                 bg=BG_LIGHT, fg=TEXT_DARK).pack(pady=(20, 10))

        self.email_entry, _ = field_entry(self, "Email")
        self.pass_entry,  _ = field_entry(self, "Κωδικός")

        self.role_var = tk.StringVar(value="Ρόλος")
        ttk.Combobox(self, textvariable=self.role_var,
                     values=["Αιμοδότης", "Νοσοκομείο", "Admin"],
                     font=FONT_BODY, width=20, state="readonly").pack(pady=6)

        rounded_btn(self, "Συνδεση", self._login).pack(pady=(16, 4))

        tk.Label(self, text="Δημιουργία προφίλ", font=("Georgia", 13, "bold"),
                 bg=BG_LIGHT, fg=TEXT_DARK).pack(pady=(20, 6))

        rounded_btn(self, "Εγγραφή", self._register).pack()

    def _login(self):
        email = self.email_entry.get().strip()
        pwd   = self.pass_entry.get().strip()
        role  = self.role_var.get()

        if role == "Ρόλος":
            messagebox.showwarning("Σφάλμα", "Επέλεξε ρόλο.")
            return

        user = self.users.get((email, pwd, role))
        if not user:
            messagebox.showerror("Σφάλμα", "Λάθος στοιχεία σύνδεσης.")
            return

        if role == "Αιμοδότης":    self.master.show_donor(user)
        elif role == "Νοσοκομείο": self.master.show_hospital(user)
        else:                       self.master.show_admin(user)

    def _register(self):
        messagebox.showinfo("Εγγραφή", "Η φόρμα εγγραφής δεν έχει υλοποιηθεί ακόμα.")

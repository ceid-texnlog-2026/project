import tkinter as tk
from tkinter import messagebox, ttk
from config import (light_green, card_green, dark_text, mid_text,
                    title_font, normal_font, small_font, set_background)
from widgets import simple_button
from db import DBManager
from models import Report, Donor


class CreateReportScreen(tk.Frame):
    """Submit a report against another user or hospital.

    Accepts *either* a Donor or a Hospital as the ``user`` argument so the
    same screen can be reused from both profile pages.
    """

    def __init__(self, master, user):
        super().__init__(master, bg=light_green)
        self.user = user
        self.db = DBManager()
        self.build()


    def _reporter_id(self):
        return getattr(self.user, "volunteer_id", None) or self.user.user_id

    def _reporter_name(self):
        return (
            getattr(self.user, "full_name", None)
            or getattr(self.user, "name", None)
            or self.user.username
        )

    def _go_back(self):
        if isinstance(self.user, Donor):
            self.master.show_donor(self.user)
        else:
            self.master.show_hospital(self.user)

    def build(self):
        set_background(self)

        tk.Label(self, text="Δημιουργία Αναφοράς", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 14))

        tk.Label(self,
                 text="Υποβάλετε αναφορά κατά χρήστη ή φορέα.\n"
                      "Ο διαχειριστής θα την αξιολογήσει.",
                 font=small_font, bg=light_green, fg=mid_text,
                 justify="center", wraplength=340).pack(pady=(0, 10))

        # Target type
        tk.Label(self, text="Τύπος αναφερόμενου:", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(6, 0))
        self.target_type_var = tk.StringVar(value="Νοσοκομείο")
        ttk.Combobox(self, textvariable=self.target_type_var,
                     values=["Αιμοδότης", "Νοσοκομείο"],
                     state="readonly", width=20).pack(pady=4)

        tk.Label(self, text="Στοιχείο αναγνώρισης (email / ΑΜΚΑ / όνομα):",
                 font=small_font, bg=light_green, fg=mid_text,
                 wraplength=320).pack(pady=(8, 0))
        self.target_id = tk.Entry(self, font=normal_font, width=30,
                                  bg=card_green, fg=dark_text, relief="flat",
                                  insertbackground=dark_text)
        self.target_id.pack(pady=4, ipady=5)

        tk.Label(self, text="Περιγραφή:", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(8, 0))
        self.description = tk.Text(self, font=normal_font, height=7, width=34,
                                   bg=card_green, fg=dark_text, relief="flat",
                                   insertbackground=dark_text)
        self.description.pack(pady=4, padx=20)

        simple_button(self, "Υποβολή Αναφοράς", self.submit).pack(pady=14)
        simple_button(self, "<- Επιστροφή", self._go_back,
                      color=mid_text).pack()

    def submit(self):
        target = self.target_id.get().strip()
        desc = self.description.get("1.0", tk.END).strip()

        if not target or not desc:
            messagebox.showerror("Σφάλμα",
                                 "Πρέπει να συμπληρώσετε όλα τα πεδία.")
            return

        if len(desc) < 10:
            messagebox.showerror("Σφάλμα",
                                 "Η περιγραφή είναι πολύ σύντομη "
                                 "(τουλάχιστον 10 χαρακτήρες).")
            return

        report = Report(
            description=desc,
            reporter_id=self._reporter_id(),
            reporter_name=self._reporter_name(),
            target_type=self.target_type_var.get(),
            target_identifier=target,
        )
        self.db.create_report(report)
        messagebox.showinfo("Επιτυχία",
                            f"Η αναφορά υποβλήθηκε.\nΑναφορά #: {report.report_id}")
        self._go_back()

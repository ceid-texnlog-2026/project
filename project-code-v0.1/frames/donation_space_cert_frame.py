import os
import tkinter as tk
from tkinter import messagebox
from config import (light_green, card_green, dark_green, dark_text,
                    mid_text, title_font, subtitle_font, normal_font,
                    small_font, red, set_background)
from widgets import simple_button
from db import DBManager
from models import ExternalRegistry


class CertificationRequestScreen(tk.Frame):
    def __init__(self, master, admin):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Πιστοποίηση Φορέων", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 14))

        pending = self.db.get_pending_applications()

        if not pending:
            tk.Label(self,
                     text="Δεν υπάρχουν εκκρεμή αιτήματα\nπιστοποίησης.",
                     font=normal_font, bg=light_green, fg=mid_text,
                     justify="center").pack(pady=40)
        else:
            tk.Label(self, text="Εκκρεμή αιτήματα:",
                     font=subtitle_font, bg=light_green, fg=dark_text).pack(pady=(0, 6))

            list_frame = tk.Frame(self, bg=light_green)
            list_frame.pack(padx=30, fill="x")

            for app in pending:
                row = tk.Frame(list_frame, bg=card_green, cursor="hand2")
                row.pack(fill="x", pady=4, ipady=8)

                tk.Label(row,
                         text=f"  #{app.request_id} - {app.hospital_name}",
                         font=normal_font, bg=card_green, fg=dark_text,
                         anchor="w").pack(side="left", padx=8)
                tk.Label(row, text=f"[{app.status}]",
                         font=small_font, bg=card_green,
                         fg=red).pack(side="right", padx=8)

                row.bind("<Button-1>", lambda e, a=app: self.open_details(a))
                for w in row.winfo_children():
                    w.bind("<Button-1>", lambda e, a=app: self.open_details(a))

        simple_button(self, "<- Επιστροφή", self.go_back,
                      color=mid_text).pack(pady=20)

    def open_details(self, application):
        self.master.switch(RequestDetailsScreen, self.admin, application)

    def go_back(self):
        self.master.show_admin(self.admin)


class RequestDetailsScreen(tk.Frame):
    def __init__(self, master, admin, application):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.application = application
        self.db = DBManager()
        self.registry = ExternalRegistry()
        self.build()

    def build(self):
        set_background(self)

        canvas = tk.Canvas(self, bg=light_green, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        inner = tk.Frame(canvas, bg=light_green)
        canvas.create_window((0, 0), window=inner, anchor="nw", width=380)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        tk.Label(inner, text="Λεπτομέρειες Αίτησης", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(16, 10))

        card = tk.Frame(inner, bg=card_green)
        card.pack(padx=20, fill="x", ipady=8, pady=6)

        app = self.application
        details = [
            ("ID", str(app.request_id)),
            ("Φορέας", app.hospital_name),
            ("Τύπος", app.center_type),
            ("Εκπρόσωπος", app.contact_name),
            ("Email", app.contact_email),
            ("Τηλέφωνο", app.phone),
            ("Πόλη", f"{app.city}, {app.region}"),
            ("Κατάσταση", app.status),
        ]

        for label, value in details:
            row = tk.Frame(card, bg=card_green)
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label + ":", font=small_font,
                     bg=card_green, fg=mid_text, anchor="w").pack(side="left")
            tk.Label(row, text=value or "—", font=normal_font,
                     bg=card_green, fg=dark_text, anchor="e",
                     wraplength=200).pack(side="right")

        tk.Label(inner, text="Δικαιολογητικά:", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(8, 2))
        docs_box = tk.Frame(inner, bg=card_green)
        docs_box.pack(padx=20, fill="x", pady=2)
        if not app.documents:
            tk.Label(docs_box, text="Κανένα", font=small_font,
                     bg=card_green, fg=mid_text).pack(pady=4)
        else:
            for path in app.documents:
                name = os.path.basename(path) if path else "—"
                tk.Label(docs_box, text=f"  • {name}", font=small_font,
                         bg=card_green, fg=dark_text,
                         anchor="w").pack(fill="x", padx=10, pady=1)

        cross_frame = tk.Frame(inner, bg=card_green)
        cross_frame.pack(padx=20, fill="x", ipady=4, pady=6)
        tk.Label(cross_frame, text="Διασταύρωση Εξωτερικού Μητρώου",
                 font=small_font, bg=card_green, fg=mid_text).pack(pady=(6, 2))

        passed = app.cross_reference_passed
        self.cross_status = tk.Label(
            cross_frame,
            text="Επιτυχής Επαλήθευση" if passed else "Εκκρεμεί",
            font=subtitle_font, bg=card_green,
            fg=dark_green if passed else red)
        self.cross_status.pack(pady=(0, 6))

        simple_button(inner, "Επαλήθευση Μητρώου", self.verify_registry,
                      width=26).pack(pady=4)

        btn_frame = tk.Frame(inner, bg=light_green)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Αποδοχή", command=self.accept,
                  bg=dark_green, fg="white", font=normal_font,
                  relief="flat", width=14, pady=6,
                  cursor="hand2").pack(side="left", padx=6)

        tk.Button(btn_frame, text="Απόρριψη", command=self.reject,
                  bg=red, fg="white", font=normal_font,
                  relief="flat", width=14, pady=6,
                  cursor="hand2").pack(side="right", padx=6)

        simple_button(inner, "Ζήτηση Συμπληρωματικών",
                      self.request_documents, width=28).pack(pady=4)

        simple_button(inner, "<- Επιστροφή",
                      lambda: self.master.switch(CertificationRequestScreen,
                                                 self.admin),
                      color=mid_text).pack(pady=6)

    def verify_registry(self):
        ok = self.registry.look_up(self.application.hospital_name,
                                   self.application.contact_email)
        self.application.cross_reference_passed = ok
        self.db.update_application(self.application)
        if ok:
            self.cross_status.config(text="Επιτυχής Επαλήθευση", fg=dark_green)
            messagebox.showinfo("Μητρώο",
                                "Ο φορέας εντοπίστηκε στο εξωτερικό μητρώο.")
        else:
            self.cross_status.config(text="Αποτυχία Επαλήθευσης", fg=red)
            messagebox.showwarning(
                "Μητρώο",
                "Ο φορέας δεν εντοπίστηκε στο εξωτερικό μητρώο.\n"
                "Ζητήστε επικαιροποιημένα στοιχεία."
            )

    def accept(self):
        if not self.application.cross_reference_passed:
            messagebox.showwarning(
                "Σφάλμα",
                "Πρέπει πρώτα να γίνει επιτυχής διασταύρωση\n"
                "με το εξωτερικό μητρώο."
            )
            return

        confirmed = messagebox.askyesno(
            "Αποδοχή",
            "Θέλετε να εγκρίνετε την αίτηση;\n"
            "Ο φορέας θα γίνει πιστοποιημένος."
        )
        if not confirmed:
            return

        hospital = self.db.approve_application(self.application)
        if hospital:
            messagebox.showinfo(
                "Επιτυχία",
                f"Η αίτηση εγκρίθηκε.\n"
                f"Ο φορέας '{hospital.name}' είναι πλέον πιστοποιημένος."
            )
        else:
            messagebox.showwarning(
                "Προσοχή",
                "Η αίτηση εγκρίθηκε, αλλά δεν βρέθηκε ο λογαριασμός φορέα."
            )
        self.master.switch(CertificationRequestScreen, self.admin)

    def reject(self):
        self.master.switch(RejectionScreen, self.admin, self.application)

    def request_documents(self):
        self.db.request_application_documents(self.application)
        messagebox.showinfo(
            "Αποστολή",
            "Στάλθηκε αίτημα για συμπληρωματικά δικαιολογητικά.\n"
            "Προθεσμία: 5 εργάσιμες ημέρες."
        )
        self.master.switch(CertificationRequestScreen, self.admin)


class RejectionScreen(tk.Frame):
    def __init__(self, master, admin, application):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.application = application
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Απόρριψη Αίτησης", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 14))

        tk.Label(self, text="Αιτιολόγηση:",
                 font=subtitle_font, bg=light_green, fg=dark_text).pack(pady=(10, 4))

        text_frame = tk.Frame(self, bg=card_green)
        text_frame.pack(padx=30, fill="x", ipady=4, pady=6)

        self.reason_text = tk.Text(text_frame, font=normal_font,
                                   bg=card_green, fg=dark_text,
                                   relief="flat", height=5, width=35,
                                   insertbackground=dark_text)
        self.reason_text.pack(padx=10, pady=10)

        simple_button(self, "Επιβεβαίωση Απόρριψης",
                      self.confirm_rejection).pack(pady=14)

        simple_button(self, "<- Επιστροφή",
                      lambda: self.master.switch(RequestDetailsScreen,
                                                 self.admin, self.application),
                      color=mid_text).pack()

    def confirm_rejection(self):
        reason = self.reason_text.get("1.0", tk.END).strip()
        if not reason:
            messagebox.showwarning("Σφάλμα", "Εισάγετε αιτιολόγηση.")
            return

        confirmed = messagebox.askyesno(
            "Επιβεβαίωση",
            f"Θέλετε να απορρίψετε την αίτηση;\nΑιτία: {reason}"
        )
        if not confirmed:
            return

        self.db.reject_application(self.application, reason)
        messagebox.showinfo(
            "Ολοκλήρωση",
            "Η αίτηση απορρίφθηκε.\nΟ φορέας ειδοποιήθηκε."
        )
        self.master.switch(CertificationRequestScreen, self.admin)


CertificationFrame = CertificationRequestScreen
CertificationDetailFrame = RequestDetailsScreen
RejectionFrame = RejectionScreen

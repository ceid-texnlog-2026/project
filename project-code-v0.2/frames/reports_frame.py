import tkinter as tk
from tkinter import messagebox
from config import (light_green, card_green, dark_green, dark_text,
                    mid_text, title_font, subtitle_font, normal_font,
                    small_font, red, set_background)
from widgets import simple_button
from db import DBManager


class ReportListScreen(tk.Frame):
    def __init__(self, master, admin):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Διαχείριση Αναφορών", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 14))

        reports = list(self.db.reports)

        if not reports:
            tk.Label(self, text="Δεν υπάρχουν αναφορές.",
                     font=normal_font, bg=light_green, fg=mid_text).pack(pady=40)
        else:
            tk.Label(self, text="Όλες οι αναφορές:",
                     font=subtitle_font, bg=light_green, fg=dark_text).pack(pady=(0, 6))

            list_frame = tk.Frame(self, bg=light_green)
            list_frame.pack(padx=30, fill="x")

            for i, report in enumerate(reports):
                row = tk.Frame(list_frame, bg=card_green, cursor="hand2")
                row.pack(fill="x", pady=4, ipady=8)

                status_color = dark_green if report.status == "closed" else red
                tk.Label(row, text=f"  #{report.report_id} - {report.target_type}",
                         font=normal_font, bg=card_green, fg=dark_text,
                         anchor="w").pack(side="left", padx=8)
                tk.Label(row, text=f"[{report.status}]",
                         font=small_font, bg=card_green,
                         fg=status_color).pack(side="right", padx=8)

                row.bind("<Button-1>", lambda e, r=report: self.open_details(r))
                for w in row.winfo_children():
                    w.bind("<Button-1>", lambda e, r=report: self.open_details(r))

        simple_button(self, "<- Επιστροφή", self.go_back,
                      color=mid_text).pack(pady=20)

    def open_details(self, report):
        self.master.switch(ReportDetailsScreen, self.admin, report)

    def go_back(self):
        self.master.show_admin(self.admin)


class ReportDetailsScreen(tk.Frame):
    def __init__(self, master, admin, report):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.report = report
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Λεπτομέρειες Αναφοράς", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 14))

        card = tk.Frame(self, bg=card_green)
        card.pack(padx=30, fill="x", ipady=10, pady=10)

        details = [
            ("ID", str(self.report.report_id or "—")),
            ("Καταγγέλλων", self.report.reporter_name or "—"),
            ("Αναφερόμενος", f"{self.report.target_type}: {self.report.target_identifier}"),
            ("Κατάσταση", self.report.status),
        ]

        for label, value in details:
            row = tk.Frame(card, bg=card_green)
            row.pack(fill="x", padx=16, pady=4)
            tk.Label(row, text=label + ":", font=small_font,
                     bg=card_green, fg=mid_text, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=normal_font,
                     bg=card_green, fg=dark_text, anchor="e",
                     wraplength=200).pack(side="right")

        desc_box = tk.Frame(self, bg=card_green)
        desc_box.pack(padx=30, fill="x", ipady=8, pady=6)
        tk.Label(desc_box, text="Περιγραφή:", font=small_font,
                 bg=card_green, fg=mid_text).pack(padx=10, pady=(8, 2), anchor="w")
        tk.Label(desc_box, text=self.report.description, font=normal_font,
                 bg=card_green, fg=dark_text, wraplength=300,
                 justify="left").pack(padx=10, pady=(0, 8), anchor="w")

        if self.report.status == "closed":
            tk.Label(self,
                     text=f"Η αναφορά έκλεισε με ενέργεια: {self.report.action}",
                     font=normal_font, bg=light_green,
                     fg=dark_green).pack(pady=20)
            simple_button(self, "<- Επιστροφή",
                          lambda: self.master.switch(ReportListScreen, self.admin),
                          color=mid_text).pack(pady=10)
            return

        tk.Label(self, text="Επιλέξτε ενέργεια:", font=subtitle_font,
                 bg=light_green, fg=dark_text).pack(pady=(10, 6))

        actions_frame = tk.Frame(self, bg=light_green)
        actions_frame.pack(padx=30, fill="x")

        tk.Button(actions_frame, text="Προειδοποίηση",
                  command=lambda: self.take_action("warning"),
                  bg=dark_green, fg="white", font=normal_font,
                  relief="flat", cursor="hand2", pady=6).pack(fill="x", pady=3)

        tk.Button(actions_frame, text="Αναστολή Λογαριασμού",
                  command=lambda: self.take_action("suspension"),
                  bg=red, fg="white", font=normal_font,
                  relief="flat", cursor="hand2", pady=6).pack(fill="x", pady=3)

        tk.Button(actions_frame, text="Απόρριψη Αναφοράς",
                  command=lambda: self.take_action("rejected"),
                  bg=mid_text, fg="white", font=normal_font,
                  relief="flat", cursor="hand2", pady=6).pack(fill="x", pady=3)

        simple_button(self, "Αίτημα Διευκρινίσεων",
                      self.request_clarification, width=26).pack(pady=10)

        simple_button(self, "<- Επιστροφή",
                      lambda: self.master.switch(ReportListScreen, self.admin),
                      color=mid_text).pack(pady=6)

    def take_action(self, action_type):
        self.master.switch(ReportJustificationScreen,
                           self.admin, self.report, action_type)

    def request_clarification(self):
        from datetime import datetime
        confirmed = messagebox.askyesno(
            "Αίτημα Διευκρινίσεων",
            "Αποστολή αιτήματος διευκρινίσεων\nστα εμπλεκόμενα μέρη;"
        )
        if not confirmed:
            return

        self.report.clarification_requested_at = datetime.now()
        self.db.update_report(self.report)


        target = self.db.find_target_user(self.report.target_type,
                                          self.report.target_identifier)
        if target:
            self.db._add_notification(
                target,
                f"Αίτημα διευκρινίσεων από τη διαχείριση\n"
                f"σχετικά με αναφορά #{self.report.report_id}.\n"
                "Παρακαλούμε απαντήστε μέσα από το προφίλ σας."
            )

        reporter = self.db._find_donor_by_id(self.report.reporter_id)
        if reporter is None:
            reporter = self.db._find_hospital_by_id(self.report.reporter_id)
        if reporter:
            self.db._add_notification(
                reporter,
                f"Η διαχείριση ζήτησε διευκρινίσεις\n"
                f"για την αναφορά #{self.report.report_id}."
            )

        self.db.email_service.notify_parties(
            self.report.target_identifier,
            "Αίτημα διευκρινίσεων από τη διαχείριση."
        )
        messagebox.showinfo(
            "Αποστολή",
            "Στάλθηκε αίτημα διευκρινίσεων.\n"
            "Αν δεν ληφθεί απάντηση εντός 48 ωρών,\n"
            "ο λογαριασμός θα ανασταλεί προσωρινά."
        )


class ReportJustificationScreen(tk.Frame):
    def __init__(self, master, admin, report, action_type):
        super().__init__(master, bg=light_green)
        self.admin = admin
        self.report = report
        self.action_type = action_type
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        labels = {
            "warning": "Προειδοποίηση",
            "suspension": "Αναστολή Λογαριασμού",
            "rejected": "Απόρριψη Αναφοράς",
        }
        action_text = labels.get(self.action_type, self.action_type)

        tk.Label(self, text="Αιτιολόγηση Απόφασης", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 10))

        tk.Label(self, text=f"Ενέργεια: {action_text}",
                 font=subtitle_font, bg=light_green, fg=red).pack(pady=(0, 10))

        text_frame = tk.Frame(self, bg=card_green)
        text_frame.pack(padx=30, fill="x", ipady=4, pady=6)

        tk.Label(text_frame, text="Αιτιολόγηση:",
                 font=small_font, bg=card_green, fg=mid_text).pack(
                     padx=10, pady=(10, 4), anchor="w")

        self.justification_text = tk.Text(
            text_frame, font=normal_font, bg=card_green, fg=dark_text,
            relief="flat", height=5, width=35, insertbackground=dark_text)
        self.justification_text.pack(padx=10, pady=(0, 10))

        simple_button(self, "Υποβολή Απόφασης", self.submit_decision).pack(pady=16)

        simple_button(self, "<- Επιστροφή",
                      lambda: self.master.switch(ReportDetailsScreen,
                                                 self.admin, self.report),
                      color=mid_text).pack()

    def submit_decision(self):
        justification = self.justification_text.get("1.0", tk.END).strip()
        if not justification:
            messagebox.showwarning("Σφάλμα", "Εισάγετε αιτιολόγηση.")
            return

        confirmed = messagebox.askyesno(
            "Επιβεβαίωση",
            f"Επιβεβαίωση απόφασης;\n\nΑιτιολόγηση: {justification}"
        )
        if not confirmed:
            return

        self.report.justification = justification
        self.report.action = self.action_type
        self.report.set_status("closed")
        self.db.update_report(self.report)

        target = self.db.find_target_user(self.report.target_type,
                                          self.report.target_identifier)

        if self.action_type == "warning" and target:
            self.db.apply_warning(target, self.report)
        elif self.action_type == "suspension" and target:
            self.db.apply_suspension(target, self.report)

        if target is None and self.action_type != "rejected":
            messagebox.showwarning(
                "Προσοχή",
                "Δεν βρέθηκε ο αναφερόμενος χρήστης στο σύστημα.\n"
                "Η αναφορά έκλεισε χωρίς ενέργεια."
            )
        else:
            messagebox.showinfo(
                "Ολοκλήρωση",
                "Η απόφαση καταχωρήθηκε.\n"
                "Τα εμπλεκόμενα μέρη ειδοποιήθηκαν."
            )
        self.master.switch(ReportListScreen, self.admin)


class ReportResponseScreen(tk.Frame):
    """Allows both the reporter and the reported party to submit a clarification response.

    Parameters
    ----------
    user    : Donor or Hospital object — the user sending the response.
    report  : Report object with a pending clarification request.
    role    : "reporter" | "target" — the user's relationship to this report.
    back_fn : optional callable executed after successful submission (or on Back).
    """

    def __init__(self, master, user, report, back_fn=None, role="target"):
        super().__init__(master, bg=light_green)
        self.user = user
        self.report = report
        self.back_fn = back_fn
        self.role = role
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Απάντηση σε Αναφορά", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 6))

        # Role badge
        role_label = "Εσείς είστε ο Αναφερόμενος" if self.role == "target" \
                     else "Εσείς είστε ο Καταγγέλλων"
        tk.Label(self, text=role_label, font=small_font,
                 bg=card_green, fg=mid_text).pack(
                     fill="x", padx=30, pady=(0, 8), ipady=3)


        card = tk.Frame(self, bg=card_green)
        card.pack(padx=30, fill="x", ipady=8, pady=4)

        details = [
            ("Αναφορά #", str(self.report.report_id or "—")),
            ("Καταγγέλλων", self.report.reporter_name or "—"),
            ("Αναφερόμενος", self.report.target_identifier or "—"),
        ]
        for lbl, val in details:
            row = tk.Frame(card, bg=card_green)
            row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text=lbl + ":", font=small_font,
                     bg=card_green, fg=mid_text, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=normal_font,
                     bg=card_green, fg=dark_text, anchor="e",
                     wraplength=180).pack(side="right")


        desc_box = tk.Frame(self, bg=card_green)
        desc_box.pack(padx=30, fill="x", ipady=4, pady=4)
        tk.Label(desc_box, text="Περιγραφή καταγγελίας:", font=small_font,
                 bg=card_green, fg=mid_text).pack(padx=10, pady=(8, 2), anchor="w")
        tk.Label(desc_box, text=self.report.description, font=normal_font,
                 bg=card_green, fg=dark_text, wraplength=300,
                 justify="left").pack(padx=10, pady=(0, 8), anchor="w")


        tk.Label(self, text="Η απάντησή σας:", font=subtitle_font,
                 bg=light_green, fg=dark_text).pack(pady=(8, 4))

        text_frame = tk.Frame(self, bg=card_green)
        text_frame.pack(padx=30, fill="x", ipady=4, pady=2)
        self.response_text = tk.Text(
            text_frame, font=normal_font, bg=card_green, fg=dark_text,
            relief="flat", height=5, width=35, insertbackground=dark_text)
        self.response_text.pack(padx=10, pady=10)

        simple_button(self, "Αποστολή Απάντησης", self.submit_response).pack(pady=12)
        simple_button(self, "<- Επιστροφή", self._go_back, color=mid_text).pack()

    def submit_response(self):
        text = self.response_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Σφάλμα", "Γράψτε την απάντησή σας.")
            return

        confirmed = messagebox.askyesno(
            "Επιβεβαίωση",
            "Να αποσταλεί η απάντηση στη διαχείριση;"
        )
        if not confirmed:
            return

        self.db.add_report_response(self.report, self.user, text, role=self.role)
        messagebox.showinfo(
            "Επιτυχία",
            "Η απάντησή σας στάλθηκε στη διαχείριση.\n"
            "Θα λάβετε ενημέρωση για την εξέλιξη της υπόθεσης."
        )
        self._go_back()

    def _go_back(self):
        if self.back_fn:
            self.back_fn()
        else:
            self.master.show_donor(self.user)


ReportsFrame = ReportListScreen
ReportDetailFrame = ReportDetailsScreen
ReportJustificationFrame = ReportJustificationScreen

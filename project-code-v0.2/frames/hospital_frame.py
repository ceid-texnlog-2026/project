import tkinter as tk
from tkinter import messagebox

from config import *
from widgets import bell_header, icon_button, simple_button
from db import DBManager

from frames.create_alert_frame import CreateAlertFrame
from frames.record_donation_frame import RecordDonationFrame
from frames.inventory_frame import InventoryFrame
from frames.certificate_frame import CertificateFrame


class HospitalProfileScreen(tk.Frame):
    def __init__(self, master, hospital, donors=None):
        super().__init__(master, bg=light_green)
        self.db = DBManager()
        self.hospital = hospital
        self.donors = donors or self.db.donors
        self.build()

    def build(self):
        self.pack(fill="both", expand=True)
        set_background(self)
        bell_header(self)

        tk.Label(self, text=self.hospital.name or self.hospital.username,
                 font=title_font, bg=light_green, fg=dark_text,
                 wraplength=340, justify="center").pack(pady=(5, 6))

        # Notification badge
        if self.hospital.notifications:
            notif = tk.Frame(self, bg=card_green, cursor="hand2")
            notif.pack(fill="x", padx=20, pady=4, ipady=4)
            tk.Label(notif,
                     text=f"🔔 {len(self.hospital.notifications)} ειδοποιήσεις",
                     font=normal_font, bg=card_green,
                     fg=red).pack(pady=2)
            notif.bind("<Button-1>", lambda e: self.show_notifications())
            for w in notif.winfo_children():
                w.bind("<Button-1>", lambda e: self.show_notifications())

        if not self.hospital.is_certified:
            self._build_uncertified()
        else:
            self._build_certified()

        # ----------------------------------------------------------------
        # Clarification-response banner (UC10 Fix 2 — bidirectional)
        # Visible to BOTH reporter and reported party
        # ----------------------------------------------------------------
        clarif_pairs = self.db.get_all_clarification_reports_for_user(self.hospital)
        if clarif_pairs:
            notif_bar = tk.Frame(self, bg=red, cursor="hand2")
            notif_bar.pack(fill="x", padx=20, pady=(0, 4), ipady=3)
            tk.Label(notif_bar,
                     text=f"⚠ Εκκρεμεί απάντηση σε {len(clarif_pairs)} αναφορά/ές",
                     font=small_font, bg=red, fg="white").pack(pady=2)
            first_report, first_role = clarif_pairs[0]
            notif_bar.bind(
                "<Button-1>",
                lambda e, r=first_report, rl=first_role: self._go_respond(r, rl),
            )
            for w in notif_bar.winfo_children():
                w.bind(
                    "<Button-1>",
                    lambda e, r=first_report, rl=first_role: self._go_respond(r, rl),
                )

        # ----------------------------------------------------------------
        # Submit Report button (UC10 Fix 1 — always visible)
        # ----------------------------------------------------------------
        simple_button(self, "Υποβολή Αναφοράς", self.go_report,
                      color=mid_text).pack(pady=(4, 0))

        simple_button(self, "Αποσύνδεση",
                      self.master.show_login).pack(pady=(6, 8))

    # ------------------------------------------------------------------
    def _build_uncertified(self):
        status_card = tk.Frame(self, bg=card_green)
        status_card.pack(padx=30, fill="x", ipady=10, pady=10)

        tk.Label(status_card, text="Κατάσταση: Μη Πιστοποιημένος",
                 font=subtitle_font, bg=card_green,
                 fg=red).pack(pady=(10, 4))

        active = self.db.get_active_application_for(self.hospital.user_id)
        if active:
            tk.Label(status_card,
                     text=f"Αίτηση #{active.request_id}\n"
                          f"Κατάσταση: {active.status}",
                     font=normal_font, bg=card_green,
                     fg=dark_text, justify="center").pack(pady=(0, 10))
            tk.Label(self,
                     text="Η αίτησή σας αξιολογείται από τον διαχειριστή.\n"
                          "Θα ειδοποιηθείτε όταν ολοκληρωθεί η διαδικασία.",
                     font=small_font, bg=light_green, fg=mid_text,
                     justify="center", wraplength=340).pack(pady=14)
            if active.status == "pending_documents":
                simple_button(self, "Επαναυποβολή Δικαιολογητικών",
                              self.go_resubmit, width=28).pack(pady=8)
        else:
            tk.Label(status_card,
                     text="Πρέπει να υποβάλετε αίτηση πιστοποίησης\n"
                          "για να αποκτήσετε πρόσβαση στις λειτουργίες.",
                     font=normal_font, bg=card_green,
                     fg=dark_text, justify="center",
                     wraplength=300).pack(pady=(0, 10))
            simple_button(self, "Υποβολή Αίτησης Πιστοποίησης",
                          self.go_apply, width=28).pack(pady=14)

    def _build_certified(self):
        tk.Label(self, text="✓ Πιστοποιημένος Φορέας",
                 font=small_font, bg=light_green,
                 fg=dark_green).pack(pady=(0, 6))

        button_grid = tk.Frame(self, bg=light_green)
        button_grid.pack(pady=10)

        icon_button(button_grid, "Επείγουσα\nΈκκληση", "urgent", 0, 0,
                    self.open_alert_frame)
        icon_button(button_grid, "Καταγραφή\nΑιμοδοσίας", "donation_reg", 0, 1,
                    self.open_record_donation_frame)
        icon_button(button_grid, "Αποθέματα\nΑίματος", "inventory", 1, 0,
                    self.open_inventory_frame)
        icon_button(button_grid, "Έκδοση\nΒεβαίωσης", "certificate", 1, 1,
                    self.open_certificate_frame)

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def go_apply(self):
        from frames.hospital_certification_frame import (
            HospitalCertificationApplicationScreen)
        self.master.switch(HospitalCertificationApplicationScreen, self.hospital)

    def go_resubmit(self):
        from frames.hospital_certification_frame import (
            HospitalCertificationApplicationScreen)
        self.master.switch(HospitalCertificationApplicationScreen, self.hospital)

    def open_alert_frame(self):
        self.master.switch(CreateAlertFrame, self.hospital, self.donors)

    def open_record_donation_frame(self):
        self.master.switch(RecordDonationFrame, self.hospital, self.donors)

    def open_inventory_frame(self):
        self.master.switch(InventoryFrame, self.hospital, self.donors)

    def open_certificate_frame(self):
        self.master.switch(CertificateFrame, self.hospital, self.donors)

    def go_report(self):
        from frames.create_report_frame import CreateReportScreen
        self.master.switch(CreateReportScreen, self.hospital)

    def _go_respond(self, report, role="target"):
        from frames.reports_frame import ReportResponseScreen
        self.master.switch(
            ReportResponseScreen,
            self.hospital,
            report,
            lambda: self.master.show_hospital(self.hospital),
            role,
        )

    def show_notifications(self):
        if not self.hospital.notifications:
            messagebox.showinfo("Ειδοποιήσεις",
                                "Δεν υπάρχουν νέες ειδοποιήσεις.")
            return
        text = "\n\n".join(self.hospital.notifications)
        messagebox.showinfo("Ειδοποιήσεις", text)
        self.db.clear_notifications(self.hospital)
        self.master.show_hospital(self.hospital)


HospitalFrame = HospitalProfileScreen

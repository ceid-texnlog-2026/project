import tkinter as tk
from tkinter import messagebox
from config import (light_green, card_green, dark_text, mid_text,
                    title_font, small_font, normal_font, red, dark_green,
                    get_icon, set_background)
from widgets import simple_button, icon_button, bell_header
from db import DBManager
from models import Donor


class ProfileScreen(tk.Frame):
    def __init__(self, master, donor: Donor):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)
        bell_header(self)

        tk.Label(self,
                 text=f"Καλώς ήρθες,\n{self.donor.full_name or self.donor.username}",
                 font=title_font, bg=light_green, fg=dark_text,
                 justify="center").pack(pady=(0, 4))

        if self.donor.notifications:
            notif = tk.Frame(self, bg=card_green, cursor="hand2")
            notif.pack(fill="x", padx=20, pady=2, ipady=4)
            tk.Label(notif,
                     text=f"🔔 {len(self.donor.notifications)} νέες ειδοποιήσεις",
                     font=small_font, bg=card_green, fg=red).pack(pady=2)
            notif.bind("<Button-1>", lambda e: self.show_notifications())
            for w in notif.winfo_children():
                w.bind("<Button-1>", lambda e: self.show_notifications())

        last = self._last_donation_date()
        last_str = last.strftime("%d / %m / %Y") if last else "—"
        next_app = self.donor.get_next_appointment()
        next_date = next_app.appointment_date.strftime("%d / %m / %Y") if next_app else "—"

        info_row = tk.Frame(self, bg=light_green)
        info_row.pack(fill="x", padx=20, pady=2)
        self.small_card(info_row, "heart", "Τελευταία\nΑιμοδοσία",
                        last_str, red).pack(side="left", expand=True, fill="both", padx=4)
        self.small_card(info_row, "calendar", "Επόμενο\nΡαντεβού",
                        next_date, dark_green).pack(side="right", expand=True, fill="both", padx=4)

        button_grid = tk.Frame(self, bg=light_green)
        button_grid.pack(padx=20, pady=8, fill="x")
        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)
        button_grid.columnconfigure(2, weight=1)

        icon_button(button_grid, "Ραντεβού", "appointment", 0, 0, self.go_appointment)
        icon_button(button_grid, "Έγγραφα", "upload", 0, 1, self.go_upload)
        icon_button(button_grid, "Ιστορικό", "history", 0, 2, self.go_history)
        icon_button(button_grid, "Διαθεσιμ.", "availability", 1, 0, self.go_availability)
        icon_button(button_grid, "Αναφορά", "reports", 1, 1, self.go_report)
        icon_button(button_grid, "Ειδοποιήσ.", "urgent", 1, 2, self.show_notifications)

        # Show "respond to report" banner if admin requested clarification
        # (works for BOTH reporter and reported party — UC10 Fix 2)
        clarif_pairs = self.db.get_all_clarification_reports_for_user(self.donor)
        if clarif_pairs:
            notif_bar = tk.Frame(self, bg=red, cursor="hand2")
            notif_bar.pack(fill="x", padx=20, pady=(0, 4), ipady=3)
            tk.Label(notif_bar,
                     text=f"⚠ Εκκρεμεί απάντηση σε {len(clarif_pairs)} αναφορά/ές",
                     font=small_font, bg=red, fg="white").pack(pady=2)
            first_report, first_role = clarif_pairs[0]
            notif_bar.bind("<Button-1>",
                           lambda e, r=first_report, rl=first_role: self.go_respond(r, rl))
            for w in notif_bar.winfo_children():
                w.bind("<Button-1>",
                       lambda e, r=first_report, rl=first_role: self.go_respond(r, rl))

        simple_button(self, "Αποσύνδεση", self.master.show_login).pack(pady=(8, 6))

    def _last_donation_date(self):
        dates = []
        for d in self.donor.donations:
            if d.donation_date:
                dates.append(d.donation_date)
        for a in self.donor.appointments:
            if a.status == "completed" and a.appointment_date:
                dates.append(a.appointment_date)
        return max(dates) if dates else None

    def small_card(self, parent, icon_name, title, value, color):
        frame = tk.Frame(parent, bg=card_green, bd=0)
        kind, img = get_icon(icon_name, size=28)
        if kind == "image":
            label = tk.Label(frame, image=img, bg=card_green)
            label.image = img
        else:
            label = tk.Label(frame, text=img, font=("Arial", 12, "bold"),
                             bg=card_green, fg=color)
        label.pack(pady=(8, 2))
        tk.Label(frame, text=title, font=small_font, bg=card_green,
                 fg=mid_text, justify="center").pack()
        tk.Label(frame, text=value, font=("Arial", 10, "bold"),
                 bg=card_green, fg=dark_text).pack(pady=(2, 8))
        return frame

    def go_availability(self):
        from frames.availability_frame import AvailabilityFrame
        self.master.switch(AvailabilityFrame, self.donor)

    def go_history(self):
        from frames.history_frame import HistoryFrame
        self.master.switch(HistoryFrame, self.donor)

    def go_upload(self):
        from frames.upload_frame import UploadFrame
        self.master.switch(UploadFrame, self.donor)

    def go_appointment(self):
        from frames.appointment_frame import AppointmentFrame
        self.master.switch(AppointmentFrame, self.donor)

    def go_report(self):
        from frames.create_report_frame import CreateReportScreen
        self.master.switch(CreateReportScreen, self.donor)

    def go_respond(self, report, role="target"):
        from frames.reports_frame import ReportResponseScreen
        self.master.switch(
            ReportResponseScreen,
            self.donor,
            report,
            lambda: self.master.show_donor(self.donor),
            role,
        )

    def show_notifications(self):
        if not self.donor.notifications:
            messagebox.showinfo("Ειδοποιήσεις",
                                "Δεν υπάρχουν νέες ειδοποιήσεις.")
            return
        text = "\n\n".join(self.donor.notifications)
        messagebox.showinfo("Ειδοποιήσεις", text)
        self.db.clear_notifications(self.donor)
        self.master.show_donor(self.donor)


DonorFrame = ProfileScreen

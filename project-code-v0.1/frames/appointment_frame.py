import tkinter as tk
from tkinter import messagebox
from datetime import date, timedelta
from config import (light_green, card_green, dark_green, dark_text,
                    mid_text, title_font, subtitle_font, normal_font,
                    small_font, red, set_background)
from widgets import simple_button
from db import DBManager


def generate_slots_for(hospital):
    """Generate 7-day forward availability for a hospital."""
    slots = []
    today = date.today()
    for offset in (3, 5, 7, 10, 14):
        day = today + timedelta(days=offset)
        for time_str in ("09:00", "11:00", "14:00"):
            slots.append({"date": day, "time": time_str})
    return slots


class AppointmentFrame(tk.Frame):
    def __init__(self, master, donor):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Κλείσιμο Ραντεβού", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 14))

        tk.Label(self, text="Επίλεξε Νοσοκομείο / Κέντρο:",
                 font=subtitle_font, bg=light_green,
                 fg=dark_text).pack(pady=(0, 6))

        hospitals = self.db.get_certified_hospitals()

        if not hospitals:
            tk.Label(self,
                     text="Δεν υπάρχουν διαθέσιμα πιστοποιημένα\n"
                          "νοσοκομεία στο σύστημα αυτή τη στιγμή.",
                     font=normal_font, bg=light_green,
                     fg=red, justify="center").pack(pady=30)
        else:
            for hospital in hospitals:
                row = tk.Frame(self, bg=card_green, cursor="hand2")
                row.pack(padx=30, fill="x", pady=3, ipady=8)

                tk.Label(row, text=f"  {hospital.name}",
                         font=normal_font, bg=card_green, fg=dark_text,
                         anchor="w", wraplength=240,
                         justify="left").pack(side="left", padx=8)
                tk.Label(row, text=">>", font=normal_font,
                         bg=card_green, fg=mid_text).pack(side="right", padx=8)

                row.bind("<Button-1>", lambda e, h=hospital: self.select_hospital(h))
                for w in row.winfo_children():
                    w.bind("<Button-1>", lambda e, h=hospital: self.select_hospital(h))

        simple_button(self, "<- Επιστροφή", self.go_back,
                      color=mid_text).pack(pady=20)

    def select_hospital(self, hospital):
        self.master.switch(SlotSelectionFrame, self.donor, hospital)

    def go_back(self):
        self.master.show_donor(self.donor)


class SlotSelectionFrame(tk.Frame):
    def __init__(self, master, donor, hospital):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.hospital = hospital
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text=self.hospital.name, font=title_font,
                 bg=light_green, fg=dark_text, wraplength=340,
                 justify="center").pack(pady=(20, 4))
        addr = ", ".join(p for p in [self.hospital.address,
                                     self.hospital.city] if p) or "—"
        tk.Label(self, text=addr, font=small_font, bg=light_green,
                 fg=mid_text).pack(pady=(0, 10))

        slots = generate_slots_for(self.hospital)

        tk.Label(self, text="Διαθέσιμες ημερομηνίες:",
                 font=subtitle_font, bg=light_green,
                 fg=dark_text).pack(pady=(0, 6))

        if not slots:
            tk.Label(self,
                     text="Δεν υπάρχουν διαθέσιμα ραντεβού.",
                     font=normal_font, bg=light_green, fg=red,
                     justify="center").pack(pady=20)
        else:
            list_frame = tk.Frame(self, bg=light_green)
            list_frame.pack(padx=30, fill="both")

            for slot in slots[:8]:
                row = tk.Frame(list_frame, bg=card_green, cursor="hand2")
                row.pack(fill="x", pady=2, ipady=6)

                date_str = slot["date"].strftime("%d/%m/%Y")
                tk.Label(row, text=f"  {date_str}",
                         font=normal_font, bg=card_green,
                         fg=dark_text).pack(side="left", padx=8)
                tk.Label(row, text=slot["time"],
                         font=subtitle_font, bg=card_green,
                         fg=dark_green).pack(side="right", padx=8)

                row.bind("<Button-1>", lambda e, s=slot: self.select_slot(s))
                for w in row.winfo_children():
                    w.bind("<Button-1>", lambda e, s=slot: self.select_slot(s))

        simple_button(self, "<- Επιστροφή",
                      lambda: self.master.switch(AppointmentFrame, self.donor),
                      color=mid_text).pack(pady=14)

    def select_slot(self, slot):
        self.master.switch(AppointmentConfirmFrame,
                           self.donor, self.hospital, slot)


class AppointmentConfirmFrame(tk.Frame):
    def __init__(self, master, donor, hospital, slot):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.hospital = hospital
        self.slot = slot
        self.db = DBManager()
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Επιβεβαίωση Ραντεβού", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 20))

        card = tk.Frame(self, bg=card_green)
        card.pack(padx=30, fill="x", ipady=10, pady=10)

        details = [
            ("Νοσοκομείο", self.hospital.name),
            ("Διεύθυνση", self.hospital.address or "—"),
            ("Ημερομηνία", self.slot["date"].strftime("%d/%m/%Y")),
            ("Ώρα", self.slot["time"]),
        ]

        for label, value in details:
            row = tk.Frame(card, bg=card_green)
            row.pack(fill="x", padx=16, pady=5)
            tk.Label(row, text=label + ":", font=small_font,
                     bg=card_green, fg=mid_text, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=normal_font,
                     bg=card_green, fg=dark_text, anchor="e",
                     wraplength=220).pack(side="right")

        simple_button(self, "Επιβεβαίωση Ραντεβού", self.confirm).pack(pady=20)

        simple_button(self, "<- Επιστροφή",
                      lambda: self.master.switch(SlotSelectionFrame,
                                                 self.donor, self.hospital),
                      color=mid_text).pack()

    def confirm(self):
        earliest = self.db.check_donation_interval(self.donor, self.slot["date"])
        if earliest is not None:
            messagebox.showwarning(
                "Δεν είναι δυνατό",
                f"Δεν μπορείτε να κλείσετε ραντεβού ακόμα.\n"
                f"Μπορείτε να αιμοδοτήσετε ξανά από:\n"
                f"{earliest.strftime('%d/%m/%Y')}"
            )
            return

        self.db.create_appointment(self.donor, self.hospital,
                                   self.slot["date"], self.slot["time"])
        messagebox.showinfo("Επιτυχία",
                            "Το ραντεβού σας καταχωρήθηκε με επιτυχία!")
        self.master.show_donor(self.donor)

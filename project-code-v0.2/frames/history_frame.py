import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from datetime import date

from config import (light_green, card_green, dark_green, dark_text,
                    mid_text, title_font, subtitle_font, normal_font,
                    small_font, red, set_background)
from widgets import simple_button


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _open_file(path: str):
    """Open a file with the OS default application."""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as exc:
        messagebox.showerror("Σφάλμα", f"Αδυναμία ανοίγματος αρχείου:\n{exc}")


# Map internal donation_type codes → Greek display labels
DONATION_TYPE_LABELS = {
    "whole_blood": "Ολικό αίμα",
    "plasma":      "Πλάσμα",
    "platelets":   "Αιμοπετάλια",
    "Αίμα":        "Ολικό αίμα",
    "Πλάσμα":      "Πλάσμα",
    "Αιμοπετάλια": "Αιμοπετάλια",
}


def _fmt_date(d) -> str:
    if d is None:
        return "—"
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return str(d)


def _donation_type_label(raw: str) -> str:
    return DONATION_TYPE_LABELS.get(raw or "", raw or "—")


# ------------------------------------------------------------------
# Entry builder
# ------------------------------------------------------------------

def _build_entries(donor):
    """Unified list of dicts from donor.donations + completed appointments.

    Each dict has keys: date, type_label, blood_group, organization, obj
    """
    entries = []

    for d in donor.donations:
        if not d.donation_date:
            continue
        entries.append({
            "date":         d.donation_date,
            "type_label":   _donation_type_label(d.donation_type),
            "blood_group":  d.blood_group or "—",
            "organization": d.organization or "—",
            "obj":          d,
            "kind":         "donation",
        })

    for a in donor.appointments:
        if a.status == "completed" and a.appointment_date:
            entries.append({
                "date":         a.appointment_date,
                "type_label":   "Ραντεβού",
                "blood_group":  donor.blood_type or "—",
                "organization": "—",
                "obj":          a,
                "kind":         "appointment",
            })

    entries.sort(key=lambda x: x["date"], reverse=True)
    return entries


# ==================================================================
# HistoryFrame — scrollable list of all donations
# ==================================================================

class HistoryFrame(tk.Frame):
    def __init__(self, master, donor):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Ιστορικό Αιμοδοσιών", font=title_font,
                 bg=light_green, fg=dark_text).pack(pady=(30, 6))

        entries = _build_entries(self.donor)

        # Statistics card
        stats = tk.Frame(self, bg=card_green)
        stats.pack(padx=30, fill="x", ipady=8, pady=(0, 10))
        tk.Label(stats,
                 text=f"Συνολικές αιμοδοσίες: {len(entries)}",
                 font=subtitle_font, bg=card_green, fg=dark_text).pack(pady=(10, 2))
        last_str = _fmt_date(entries[0]["date"]) if entries else "—"
        tk.Label(stats, text=f"Τελευταία: {last_str}",
                 font=normal_font, bg=card_green, fg=mid_text).pack(pady=(0, 10))

        # List
        if not entries:
            tk.Label(self,
                     text="Δεν υπάρχει ακόμα διαθέσιμο\nιστορικό αιμοδοσιών.",
                     font=normal_font, bg=light_green, fg=mid_text,
                     justify="center").pack(pady=16)
        else:
            tk.Label(self, text="Επιλέξτε αιμοδοσία για λεπτομέρειες:",
                     font=small_font, bg=light_green, fg=mid_text).pack(pady=(0, 4))

            list_frame = tk.Frame(self, bg=light_green)
            list_frame.pack(padx=30, fill="x")

            for entry in entries:
                self._make_row(list_frame, entry)

        # Certificates section
        self._build_certificates_section()

        simple_button(self, "<- Επιστροφή", self.go_back,
                      color=mid_text).pack(pady=14)

    def _make_row(self, parent, entry):
        """Create one clickable row for a donation/appointment entry."""
        row = tk.Frame(parent, bg=card_green, cursor="hand2")
        row.pack(fill="x", pady=3, ipady=0)

        # Use grid inside the row for clean two-column layout
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=0)

        # Left block — two lines
        left = tk.Frame(row, bg=card_green)
        left.grid(row=0, column=0, sticky="w", padx=8, pady=6)

        date_str = _fmt_date(entry["date"])
        tk.Label(left,
                 text=f"{date_str}  —  {entry['type_label']}",
                 font=("Arial", 11, "bold"), bg=card_green,
                 fg=dark_text, anchor="w").pack(anchor="w")
        tk.Label(left,
                 text=f"{entry['blood_group']}  •  {entry['organization']}",
                 font=small_font, bg=card_green,
                 fg=mid_text, anchor="w").pack(anchor="w")

        # Right arrow
        tk.Label(row, text="›", font=("Arial", 18, "bold"),
                 bg=card_green, fg=mid_text).grid(row=0, column=1, padx=10)

        # Bindings — click anywhere on the row
        cmd = lambda e, en=entry: self.show_details(en)
        row.bind("<Button-1>", cmd)
        for w in row.winfo_children():
            w.bind("<Button-1>", cmd)
            for ww in w.winfo_children():
                ww.bind("<Button-1>", cmd)

    def _build_certificates_section(self):
        certs = getattr(self.donor, "certificates", [])

        tk.Frame(self, bg=mid_text, height=1).pack(fill="x", padx=30, pady=(12, 0))
        tk.Label(self, text="Βεβαιώσεις Αιμοδοσίας",
                 font=subtitle_font, bg=light_green,
                 fg=dark_text).pack(pady=(8, 4))

        if not certs:
            tk.Label(self, text="Δεν υπάρχουν εκδοθείσες βεβαιώσεις.",
                     font=normal_font, bg=light_green,
                     fg=mid_text).pack(pady=4)
            return

        cert_frame = tk.Frame(self, bg=light_green)
        cert_frame.pack(padx=30, fill="x")

        for cert in sorted(certs, key=lambda c: c.issue_date or date.min, reverse=True):
            row = tk.Frame(cert_frame, bg=card_green)
            row.pack(fill="x", pady=3, ipady=4)
            row.columnconfigure(0, weight=1)
            row.columnconfigure(1, weight=0)

            left = tk.Frame(row, bg=card_green)
            left.grid(row=0, column=0, sticky="w", padx=8, pady=4)
            tk.Label(left,
                     text=cert.certificate_number or "—",
                     font=("Arial", 10, "bold"), bg=card_green,
                     fg=dark_text, anchor="w").pack(anchor="w")
            tk.Label(left,
                     text=f"{_fmt_date(cert.issue_date)}  •  {cert.organization or '—'}",
                     font=small_font, bg=card_green,
                     fg=mid_text, anchor="w").pack(anchor="w")

            if cert.pdf_path and os.path.exists(cert.pdf_path):
                tk.Button(
                    row, text="PDF",
                    font=small_font, bg=dark_green, fg="white",
                    relief="flat", cursor="hand2", padx=8,
                    command=lambda p=cert.pdf_path: _open_file(p),
                ).grid(row=0, column=1, padx=8, pady=4)
            else:
                tk.Label(row, text="—", font=small_font,
                         bg=card_green, fg=mid_text).grid(
                             row=0, column=1, padx=8)

    def show_details(self, entry):
        self.master.switch(DonationDetailScreen, self.donor, entry)

    def go_back(self):
        self.master.show_donor(self.donor)


# ==================================================================
# DonationDetailScreen — full details for a single entry
# ==================================================================

class DonationDetailScreen(tk.Frame):
    def __init__(self, master, donor, entry: dict):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.entry = entry
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Λεπτομέρειες Αιμοδοσίας",
                 font=title_font, bg=light_green,
                 fg=dark_text).pack(pady=(40, 20))

        card = tk.Frame(self, bg=card_green)
        card.pack(padx=30, fill="x", ipady=10, pady=10)

        obj = self.entry["obj"]
        kind = self.entry["kind"]

        # Build detail rows depending on object type
        if kind == "donation":
            details = [
                ("Ημερομηνία",    _fmt_date(obj.donation_date)),
                ("Τύπος",         _donation_type_label(obj.donation_type)),
                ("Ομάδα αίματος", obj.blood_group or "—"),
                ("Ποσότητα",      f"{obj.amount_ml} ml" if obj.amount_ml else "—"),
                ("Οργανισμός",    obj.organization or "—"),
                ("Κατάσταση",     "Ολοκληρώθηκε"),
            ]
            if obj.notes:
                details.append(("Σημειώσεις", obj.notes))
        else:
            # Appointment
            details = [
                ("Ημερομηνία",    _fmt_date(obj.appointment_date)),
                ("Τύπος",         "Ραντεβού αιμοδοσίας"),
                ("Ομάδα αίματος", self.donor.blood_type or "—"),
                ("Κατάσταση",     "Ολοκληρώθηκε"),
                ("Ώρα",           obj.time or "—"),
            ]

        for label, value in details:
            row = tk.Frame(card, bg=card_green)
            row.pack(fill="x", padx=20, pady=5)
            tk.Label(row, text=label + ":", font=small_font,
                     bg=card_green, fg=mid_text, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Arial", 11, "bold"),
                     bg=card_green, fg=dark_text,
                     anchor="e", wraplength=200).pack(side="right")

        simple_button(self, "<- Επιστροφή", self.go_back,
                      color=mid_text).pack(pady=30)

    def go_back(self):
        self.master.switch(HistoryFrame, self.donor)

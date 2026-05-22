import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import date
import os

from config import (light_green, card_green, dark_green, dark_text,
                    mid_text, title_font, subtitle_font, normal_font,
                    small_font, red, set_background)
from widgets import simple_button
from models import MedicalDocument
from db import DBManager

ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]
MAX_SIZE_MB = 5


class UploadFrame(tk.Frame):
    def __init__(self, master, donor):
        super().__init__(master, bg=light_green)
        self.donor = donor
        self.selected_file_path = None
        self.build()

    def build(self):
        set_background(self)

        tk.Label(self, text="Ανάρτηση Ιατρικών\nΕγγράφων",
                 font=title_font, bg=light_green, fg=dark_text,
                 justify="center").pack(pady=(30, 10))

        # File picker button
        select_btn = tk.Button(
            self, text="Επιλογή Αρχείου",
            command=self.select_file,
            bg=card_green, fg=dark_text, font=normal_font,
            relief="flat", bd=0, cursor="hand2",
            width=22, pady=8,
        )
        select_btn.pack(pady=(10, 4))

        tk.Label(self,
                 text="Επιτρέπονται: PDF, JPG, PNG  |  Μέγ. μέγεθος: 5 MB",
                 font=small_font, bg=light_green, fg=mid_text,
                 wraplength=360).pack()

        # File info card
        self.file_card = tk.Frame(self, bg=card_green)
        self.file_card.pack(padx=30, fill="x", ipady=8, pady=14)

        self.file_name_label = tk.Label(
            self.file_card, text="Όνομα: —",
            font=normal_font, bg=card_green, fg=dark_text,
            anchor="w", wraplength=310)
        self.file_name_label.pack(pady=(10, 2), padx=14, anchor="w")

        self.file_type_label = tk.Label(
            self.file_card, text="Τύπος: —",
            font=normal_font, bg=card_green, fg=dark_text, anchor="w")
        self.file_type_label.pack(pady=2, padx=14, anchor="w")

        self.file_size_label = tk.Label(
            self.file_card, text="Μέγεθος: —",
            font=normal_font, bg=card_green, fg=dark_text, anchor="w")
        self.file_size_label.pack(pady=(2, 10), padx=14, anchor="w")

        # Upload button (disabled until a file is selected)
        self.upload_btn = simple_button(
            self, "Μεταφόρτωση Εγγράφου", self.upload_file)
        self.upload_btn.pack(pady=(4, 10))
        self.upload_btn.config(state="disabled", bg=mid_text)

        # Document list
        tk.Label(self, text="Ιατρικά Έγγραφα:",
                 font=subtitle_font, bg=light_green,
                 fg=dark_text).pack(pady=(10, 4))

        self.list_frame = tk.Frame(self, bg=light_green)
        self.list_frame.pack(padx=30, fill="x")
        self.refresh_document_list()

        simple_button(self, "<- Επιστροφή", self.go_back,
                      color=mid_text).pack(pady=16)

    # ------------------------------------------------------------------

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Επιλογή Ιατρικού Εγγράφου",
            filetypes=[("Επιτρεπόμενα αρχεία", "*.pdf *.jpg *.jpeg *.png")],
        )
        if not path:
            return

        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].lower()
        size_mb = os.path.getsize(path) / (1024 * 1024)

        if ext not in ALLOWED_EXTENSIONS:
            messagebox.showerror(
                "Σφάλμα",
                "Μη αποδεκτός τύπος αρχείου.\n"
                "Επιτρέπονται μόνο PDF, JPG, PNG.",
            )
            return

        if size_mb > MAX_SIZE_MB:
            messagebox.showerror(
                "Σφάλμα",
                f"Το αρχείο υπερβαίνει το όριο των {MAX_SIZE_MB} MB.",
            )
            return

        self.selected_file_path = path
        self.file_name_label.config(text=f"Όνομα: {filename}")
        self.file_type_label.config(text=f"Τύπος: {ext.upper()}")
        self.file_size_label.config(text=f"Μέγεθος: {size_mb:.2f} MB")
        self.upload_btn.config(state="normal", bg=dark_green)

    def upload_file(self):
        if not self.selected_file_path:
            return

        filename = os.path.basename(self.selected_file_path)
        doc = MedicalDocument(
            filename=filename,
            upload_date=date.today(),
            document_type=os.path.splitext(filename)[1].lower(),
            file_path=self.selected_file_path,
        )
        DBManager().save_medical_document(self.donor, doc)

        # Reset UI
        self.selected_file_path = None
        self.file_name_label.config(text="Όνομα: —")
        self.file_type_label.config(text="Τύπος: —")
        self.file_size_label.config(text="Μέγεθος: —")
        self.upload_btn.config(state="disabled", bg=mid_text)

        messagebox.showinfo("Επιτυχία", "Το έγγραφο μεταφορτώθηκε με επιτυχία!")
        self.refresh_document_list()

    def refresh_document_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        docs = self.donor.medical_history.documents
        if not docs:
            tk.Label(self.list_frame,
                     text="Δεν υπάρχουν έγγραφα ακόμα.",
                     font=small_font, bg=light_green, fg=mid_text).pack()
            return

        for doc in docs:
            row = tk.Frame(self.list_frame, bg=card_green)
            row.pack(fill="x", pady=3, ipady=6)
            row.columnconfigure(0, weight=1)
            row.columnconfigure(1, weight=0)

            # Truncate very long filenames in the display
            display_name = (doc.filename[:30] + "…"
                            if len(doc.filename) > 30 else doc.filename)
            tk.Label(row, text=f"  {display_name}",
                     font=small_font, bg=card_green, fg=dark_text,
                     anchor="w").grid(row=0, column=0, sticky="w", padx=8)
            tk.Label(row, text=doc.upload_date.strftime("%d/%m/%Y"),
                     font=small_font, bg=card_green, fg=mid_text).grid(
                         row=0, column=1, padx=8)

    def go_back(self):
        self.master.show_donor(self.donor)

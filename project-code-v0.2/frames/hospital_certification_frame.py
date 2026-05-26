import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from config import (light_green, card_green, dark_text, mid_text,
                    title_font, normal_font, small_font, set_background)
from widgets import simple_button
from db import DBManager
from models import Application


ALLOWED_DOC_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE_MB = 10


class HospitalCertificationApplicationScreen(tk.Frame):
    def __init__(self, master, hospital):
        super().__init__(master, bg=light_green)
        self.db = DBManager()
        self.hospital = hospital
        self.selected_files: list[str] = []
        self.existing = self.db.get_active_application_for(hospital.user_id)
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

        title = "Επαναυποβολή Δικαιολογητικών" if self.existing \
                and self.existing.status == "pending_documents" \
                else "Αίτηση Πιστοποίησης"
        tk.Label(inner, text=title, font=title_font,
                 bg=light_green, fg=dark_text, wraplength=340,
                 justify="center").pack(pady=(16, 6))

        tk.Label(inner,
                 text="Συμπληρώστε τα στοιχεία και επισυνάψτε τα\n"
                      "δικαιολογητικά. Η αίτηση θα προωθηθεί στον admin.",
                 font=small_font, bg=light_green, fg=mid_text,
                 justify="center").pack(pady=(0, 8))


        tk.Label(inner, text="Όνομα Φορέα", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(6, 0))
        self.hospital_name = tk.Entry(inner, font=normal_font, width=30,
                                      bg=card_green, fg=dark_text,
                                      relief="flat",
                                      insertbackground=dark_text)
        self.hospital_name.pack(pady=2, ipady=5)
        self.hospital_name.insert(0, self.hospital.name)

        tk.Label(inner, text="Τύπος Φορέα", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(6, 0))
        self.center_type_var = tk.StringVar(value="Δημόσιο Νοσοκομείο")
        ttk.Combobox(inner, textvariable=self.center_type_var,
                     values=["Δημόσιο Νοσοκομείο", "Ιδιωτική Κλινική",
                             "Κέντρο Αιμοδοσίας"],
                     state="readonly", width=24).pack(pady=2)

        self.contact_name = self._entry(inner, "Όνομα Εκπροσώπου")
        self.contact_email = self._entry(inner, "Email Επικοινωνίας",
                                         default=self.hospital.email)
        self.phone = self._entry(inner, "Τηλέφωνο",
                                 default=self.hospital.phone or "")
        self.address = self._entry(inner, "Διεύθυνση",
                                   default=self.hospital.address or "")
        self.city = self._entry(inner, "Πόλη",
                                default=self.hospital.city or "")
        self.region = self._entry(inner, "Περιφέρεια",
                                  default=self.hospital.region or "")

        tk.Label(inner, text="Δικαιολογητικά (PDF/εικόνες)", font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(10, 2))

        self.files_box = tk.Frame(inner, bg=card_green)
        self.files_box.pack(padx=8, pady=4, fill="x")
        self._render_files()

        simple_button(inner, "Επιλογή Αρχείων", self.pick_files,
                      width=22).pack(pady=4)

        simple_button(inner, "Υποβολή Αίτησης", self.submit).pack(pady=14)
        simple_button(inner, "Πίσω",
                      lambda: self.master.show_hospital(self.hospital),
                      color=mid_text).pack(pady=4)

    def _entry(self, parent, label, default=""):
        tk.Label(parent, text=label, font=small_font,
                 bg=light_green, fg=mid_text).pack(pady=(6, 0))
        e = tk.Entry(parent, font=normal_font, width=30,
                     bg=card_green, fg=dark_text,
                     relief="flat", insertbackground=dark_text)
        e.pack(pady=2, ipady=5)
        if default:
            e.insert(0, default)
        return e

    def _render_files(self):
        for w in self.files_box.winfo_children():
            w.destroy()
        if not self.selected_files:
            tk.Label(self.files_box,
                     text="Δεν έχουν επιλεγεί αρχεία.",
                     font=small_font, bg=card_green,
                     fg=mid_text).pack(pady=6)
            return
        for path in self.selected_files:
            row = tk.Frame(self.files_box, bg=card_green)
            row.pack(fill="x", padx=6, pady=2)
            tk.Label(row, text=os.path.basename(path),
                     font=small_font, bg=card_green,
                     fg=dark_text, anchor="w").pack(side="left")
            tk.Button(row, text="X", font=small_font, bg=card_green,
                      fg=mid_text, relief="flat", bd=0, cursor="hand2",
                      command=lambda p=path: self._remove(p)).pack(side="right")

    def _remove(self, path):
        self.selected_files = [p for p in self.selected_files if p != path]
        self._render_files()

    def pick_files(self):
        paths = filedialog.askopenfilenames(
            title="Επιλογή Δικαιολογητικών",
            filetypes=[("Έγγραφα", "*.pdf *.jpg *.jpeg *.png"), ("Όλα τα αρχεία", "*.*")],
        )
        if not paths:
            return
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext not in ALLOWED_DOC_EXTENSIONS:
                messagebox.showerror(
                    "Σφάλμα",
                    f"Μη επιτρεπτός τύπος αρχείου: {os.path.basename(p)}"
                )
                continue
            size_mb = os.path.getsize(p) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                messagebox.showerror(
                    "Σφάλμα",
                    f"Το {os.path.basename(p)} υπερβαίνει τα "
                    f"{MAX_FILE_SIZE_MB}MB."
                )
                continue
            if p not in self.selected_files:
                self.selected_files.append(p)
        self._render_files()

    def submit(self):
        if not self.hospital_name.get().strip() \
                or not self.contact_email.get().strip() \
                or not self.contact_name.get().strip():
            messagebox.showerror(
                "Σφάλμα",
                "Συμπληρώστε όνομα φορέα, εκπρόσωπο και email."
            )
            return

        if not self.selected_files:
            messagebox.showerror(
                "Σφάλμα",
                "Επισυνάψτε τουλάχιστον ένα δικαιολογητικό."
            )
            return

        if self.existing:
            self.existing.documents = list(self.selected_files)
            self.existing.set_status("pending")
            self.db.update_application(self.existing)
            messagebox.showinfo(
                "Επιτυχία",
                f"Επανυποβλήθηκε η αίτηση #{self.existing.request_id}."
            )
        else:
            app = Application(
                center_type=self.center_type_var.get(),
                documents=list(self.selected_files),
                hospital_name=self.hospital_name.get().strip(),
                contact_name=self.contact_name.get().strip(),
                contact_email=self.contact_email.get().strip(),
                phone=self.phone.get().strip(),
                address=self.address.get().strip(),
                city=self.city.get().strip(),
                region=self.region.get().strip(),
            )
            self.db.submit_application(app, self.hospital.user_id)
            messagebox.showinfo(
                "Υποβολή",
                f"Η αίτησή σας #{app.request_id} υποβλήθηκε.\n"
                f"Θα ενημερωθείτε μετά την αξιολόγηση."
            )

        self.master.show_hospital(self.hospital)

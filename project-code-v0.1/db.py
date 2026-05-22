from datetime import datetime, date, timedelta
from models import (Donor, Hospital, Admin, Application, Report,
                    DonationCenter, NotificationService, EmailNotification,
                    MedicalDocument, Donation, Appointment, BloodUnit,
                    DonationCertificate, generate_temp_password)
from database import Database, _parse_date, _parse_datetime


# Minimum interval between donations (days) per Use Case 2 alt flow 2
MIN_DONATION_INTERVAL = 90


def _row_to_user(row):
    role = row["role"]
    if role == "donor":
        u = Donor(
            username=row["username"] or "",
            email=row["email"],
            password=row["password"],
            full_name=row["full_name"] or "",
            amka=row["amka"] or "",
            blood_type=row["blood_type"] or "",
            phone=row["phone"] or "",
        )
        u.qr_code = row["qr_code"] or ""
        u.is_available = bool(row["is_available"])
        u.volunteer_id = row["user_id"]
    elif role == "hospital":
        u = Hospital(
            username=row["username"] or "",
            email=row["email"],
            password=row["password"],
            name=row["name"] or "",
            address=row["address"] or "",
            city=row["city"] or "",
            region=row["region"] or "",
            phone=row["phone"] or "",
            service_code=row["service_code"] or "",
        )
        u.is_certified = bool(row["is_certified"])
        u.must_change_password = bool(row["must_change_password"])
        u.id = row["user_id"]
    else:
        u = Admin(row["username"] or "admin", row["email"], row["password"])
        u.admin_id = row["user_id"]

    u.user_id = row["user_id"]
    u.status = row["status"]
    u.is_suspended = bool(row["is_suspended"])
    return u


class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.db = Database()
        self.donors: list[Donor] = []
        self.hospitals: list[Hospital] = []
        self.admins: list[Admin] = []
        self.applications: list[Application] = []
        self.reports: list[Report] = []
        self.email_service = EmailNotification()
        self.notification_service = NotificationService()

        self._load_from_db()
        self._seed_admin_if_needed()
        self._seed_test_data()
        self._load_notifications()

    # ---------- LOAD ----------

    def _load_from_db(self):
        for row in self.db.load_users():
            user = _row_to_user(row)
            if isinstance(user, Donor):
                self.donors.append(user)
            elif isinstance(user, Hospital):
                self.hospitals.append(user)
            else:
                self.admins.append(user)

        for row in self.db.load_applications():
            app = Application(
                center_type=row["center_type"] or "",
                hospital_name=row["hospital_name"] or "",
                contact_name=row["contact_name"] or "",
                contact_email=row["contact_email"] or "",
                phone=row["phone"] or "",
                address=row["address"] or "",
                city=row["city"] or "",
                region=row["region"] or "",
            )
            app.request_id = row["request_id"]
            app.status = row["status"]
            app.cross_reference_passed = bool(row["cross_reference_passed"])
            app.created_at = _parse_datetime(row["created_at"]) or datetime.now()
            import json
            try:
                app.documents = json.loads(row["documents"] or "[]")
            except Exception:
                app.documents = []
            app.hospital_user_id = row["hospital_user_id"]
            self.applications.append(app)

        for row in self.db.load_reports():
            r = Report(
                description=row["description"] or "",
                reporter_id=row["reporter_id"],
                reporter_name=row["reporter_name"] or "",
                target_type=row["target_type"] or "",
                target_identifier=row["target_identifier"] or "",
            )
            r.report_id = row["report_id"]
            r.status = row["status"]
            r.justification = row["justification"] or ""
            r.action = row["action"] or ""
            r.created_at = _parse_datetime(row["created_at"]) or datetime.now()
            r.clarification_requested_at = _parse_datetime(
                row["clarification_requested_at"] if "clarification_requested_at" in row.keys() else None
            )
            self.reports.append(r)

        for row in self.db.load_appointments():
            donor = self._find_donor_by_id(row["donor_id"])
            if not donor:
                continue
            appt = Appointment(
                donor_id=row["donor_id"],
                center_id=row["hospital_id"],
                appointment_date=_parse_date(row["appointment_date"]) or date.today(),
                time=row["time"] or "",
            )
            appt.appointment_id = row["appointment_id"]
            appt.status = row["status"]
            donor.appointments.append(appt)

        for row in self.db.load_donations():
            donor = self._find_donor_by_id(row["donor_id"])
            hospital = self._find_hospital_by_id(row["hospital_id"])
            donation = Donation(
                donor_id=row["donor_id"],
                donation_date=_parse_date(row["donation_date"]) or date.today(),
                blood_group=row["blood_group"] or "",
                donation_type=row["donation_type"] or "whole_blood",
                amount_ml=row["amount_ml"] or 450,
                organization=row["organization"] or "",
                notes=row["notes"] or "",
            )
            donation.id = row["id"]
            donation.status = row["status"]
            if donor:
                donor.donations.append(donation)
            if hospital:
                hospital.donations.append(donation)

        for row in self.db.load_medical_documents():
            donor = self._find_donor_by_id(row["donor_id"])
            if not donor:
                continue
            doc = MedicalDocument(
                filename=row["filename"] or "",
                upload_date=_parse_date(row["upload_date"]) or date.today(),
                document_type=row["document_type"] or "",
            )
            doc.document_id = row["document_id"]
            doc.file_path = row["file_path"] or ""
            donor.medical_history.add_document(doc)

        for row in self.db.load_certificates():
            donor = self._find_donor_by_id(row["donor_id"])
            cert = DonationCertificate(
                hospital_id=row["hospital_id"] or 0,
                donor_id=row["donor_id"] or 0,
                certificate_number=row["certificate_number"] or "",
                issue_date=_parse_date(row["issue_date"]) or date.today(),
                donation_date=_parse_date(row["donation_date"]),
                donor_name=row["donor_name"] or "",
                organization=row["organization"] or "",
                pdf_path=row["pdf_path"] or "",
            )
            cert.id = row["id"]
            cert.status = row["status"]
            if donor:
                donor.add_certificate(cert)

        for row in self.db.load_blood_units():
            hospital = self._find_hospital_by_id(row["hospital_id"])
            if not hospital:
                continue
            unit = BloodUnit(
                blood_type=row["blood_type"] or "",
                quantity=row["quantity"] or 0,
                expiration_date=_parse_date(row["expiration_date"]) or date.today(),
                unit_code=row["unit_code"] or "",
                collection_date=_parse_date(row["collection_date"]),
                product_type=row["product_type"] or "whole_blood",
            )
            unit.unit_id = row["unit_id"]
            unit.status = row["status"]
            hospital.blood_inventory.units.append(unit)
            if unit.status == "available":
                current = hospital.blood_inventory.stock.get(unit.blood_type, 0)
                hospital.blood_inventory.stock[unit.blood_type] = current + unit.quantity

    def _load_notifications(self):
        for user in self.donors + self.hospitals + self.admins:
            rows = self.db.load_notifications_for(user.user_id)
            user.notifications = [r["message"] for r in rows]

    def _seed_admin_if_needed(self):
        if not self.admins:
            admin = Admin("admin", "admin@redhope.gr", "admin")
            uid = self.db.insert_user("admin", admin)
            admin.user_id = uid
            admin.admin_id = uid
            self.admins.append(admin)

    # ---------- LOOKUPS ----------

    def _find_donor_by_id(self, user_id):
        for d in self.donors:
            if d.user_id == user_id:
                return d
        return None

    def _find_hospital_by_id(self, user_id):
        for h in self.hospitals:
            if h.user_id == user_id:
                return h
        return None

    def get_certified_hospitals(self):
        return [h for h in self.hospitals
                if h.is_certified and not h.is_suspended]

    # ---------- AUTH ----------

    def authenticate(self, email: str, password: str, role: str):
        if role == "Αιμοδότης":
            pool = self.donors
        elif role == "Νοσοκομείο":
            pool = self.hospitals
        else:
            pool = self.admins

        for user in pool:
            if user.email == email and user.password == password:
                return user
        return None

    def email_exists(self, email: str) -> bool:
        return self.db.email_exists(email)

    # ---------- DONOR REGISTRATION ----------

    def register_donor(self, donor: Donor):
        uid = self.db.insert_user("donor", donor)
        donor.user_id = uid
        donor.volunteer_id = uid
        donor.qr_code = f"QR-DONOR-{uid:04d}"
        self.db.update_user(uid, donor)
        self.donors.append(donor)
        return donor

    # ---------- HOSPITAL REGISTRATION ----------

    def register_hospital(self, hospital: Hospital):
        hospital.is_certified = False
        uid = self.db.insert_user("hospital", hospital)
        hospital.user_id = uid
        hospital.id = uid
        if not hospital.service_code:
            hospital.service_code = f"H-{uid:04d}"
            self.db.update_user(uid, hospital)
        self.hospitals.append(hospital)
        return hospital

    def save_user(self, user):
        self.db.update_user(user.user_id, user)

    # ---------- APPLICATION (FOR CERTIFICATION) ----------

    def submit_application(self, application: Application, hospital_user_id: int):
        application.hospital_user_id = hospital_user_id
        application.created_at = datetime.now()
        rid = self.db.insert_application(application)
        application.request_id = rid
        self.applications.append(application)
        return application

    def update_application(self, application: Application):
        self.db.update_application(application)

    def approve_application(self, application: Application):
        application.set_status("approved")
        hospital = self._find_hospital_by_id(application.hospital_user_id)
        if hospital:
            hospital.is_certified = True
            hospital.name = hospital.name or application.hospital_name
            hospital.address = hospital.address or application.address
            hospital.city = hospital.city or application.city
            hospital.region = hospital.region or application.region
            hospital.phone = hospital.phone or application.phone
            self.save_user(hospital)
            self._add_notification(hospital,
                                   "✓ Ο φορέας σας πιστοποιήθηκε επιτυχώς. "
                                   "Πλέον έχετε πρόσβαση σε όλες τις λειτουργίες.")
        self.update_application(application)
        return hospital

    def reject_application(self, application: Application, reason: str):
        application.set_status("rejected")
        self.update_application(application)
        self.email_service.notify_rejection(application.contact_email, reason)
        hospital = self._find_hospital_by_id(application.hospital_user_id)
        if hospital:
            self._add_notification(hospital,
                                   f"✗ Η αίτηση πιστοποίησης απορρίφθηκε.\nΛόγος: {reason}")

    def request_application_documents(self, application: Application):
        application.set_status("pending_documents")
        self.update_application(application)
        self.email_service.request_new_documents(application.contact_email)
        hospital = self._find_hospital_by_id(application.hospital_user_id)
        if hospital:
            self._add_notification(hospital,
                                   "Ο διαχειριστής ζήτησε συμπληρωματικά "
                                   "δικαιολογητικά για την αίτησή σας.")

    def get_active_application_for(self, hospital_user_id: int):
        for app in self.applications:
            if (app.hospital_user_id == hospital_user_id
                    and app.status in ("pending", "pending_documents")):
                return app
        return None

    # ---------- REPORTS ----------

    def create_report(self, report: Report):
        report.created_at = datetime.now()
        rid = self.db.insert_report(report)
        report.report_id = rid
        self.reports.append(report)
        return report

    def update_report(self, report: Report):
        self.db.update_report(report)

    def find_target_user(self, target_type: str, identifier: str):
        identifier = identifier.strip().lower()
        if target_type == "Αιμοδότης":
            for d in self.donors:
                if (d.email.lower() == identifier
                        or (d.amka or "").lower() == identifier
                        or d.username.lower() == identifier):
                    return d
        else:
            for h in self.hospitals:
                if (h.email.lower() == identifier
                        or (h.name or "").lower() == identifier
                        or h.username.lower() == identifier):
                    return h
        return None

    def apply_warning(self, target_user, report: Report):
        msg = (f"⚠ Λάβατε προειδοποίηση από τη διαχείριση.\n"
               f"Αιτιολόγηση: {report.justification}")
        self._add_notification(target_user, msg)

    def apply_suspension(self, target_user, report: Report):
        target_user.is_suspended = True
        target_user.set_status("suspended")
        self.save_user(target_user)
        msg = (f"⛔ Ο λογαριασμός σας ανεστάλη από τη διαχείριση.\n"
               f"Αιτιολόγηση: {report.justification}")
        self._add_notification(target_user, msg)

    def _add_notification(self, user, message: str):
        user.notifications.append(message)
        self.db.insert_notification(user.user_id, message)
        self.notification_service.send_notification(user, message)

    def clear_notifications(self, user):
        user.notifications.clear()
        self.db.clear_notifications_for(user.user_id)

    # ---------- APPOINTMENTS ----------

    def create_appointment(self, donor: Donor, hospital: Hospital,
                           appt_date: date, time: str):
        appt = Appointment(
            donor_id=donor.user_id,
            center_id=hospital.user_id,
            appointment_date=appt_date,
            time=time,
        )
        appt.status = "upcoming"
        aid = self.db.insert_appointment(appt, donor.user_id, hospital.user_id)
        appt.appointment_id = aid
        donor.appointments.append(appt)
        return appt

    def check_donation_interval(self, donor: Donor, target_date: date):
        """Returns the earliest date the donor can next donate, or None if OK."""
        last_donation_date = None
        for d in donor.donations:
            if d.donation_date and (last_donation_date is None
                                    or d.donation_date > last_donation_date):
                last_donation_date = d.donation_date
        for a in donor.appointments:
            if a.status == "completed" and a.appointment_date and \
                    (last_donation_date is None
                     or a.appointment_date > last_donation_date):
                last_donation_date = a.appointment_date

        if last_donation_date is None:
            return None
        earliest = last_donation_date + timedelta(days=MIN_DONATION_INTERVAL)
        if target_date < earliest:
            return earliest
        return None

    # ---------- DONATIONS ----------

    def record_donation(self, hospital: Hospital, donor: Donor,
                        donation_type: str = "whole_blood"):
        donation = Donation(
            donor_id=donor.user_id,
            donation_date=date.today(),
            blood_group=donor.blood_type,
            donation_type=donation_type,
            amount_ml=450,
            organization=hospital.name,
            notes="Καταγραφή αιμοδοσίας",
        )
        donation.status = "completed"
        did = self.db.insert_donation(donation, hospital.user_id)
        donation.id = did
        donor.donations.append(donation)
        hospital.donations.append(donation)
        return donation

    # ---------- MEDICAL DOCUMENTS ----------

    def save_medical_document(self, donor: Donor, doc: MedicalDocument):
        doc_id = self.db.insert_medical_document(doc, donor.user_id)
        doc.document_id = doc_id
        donor.medical_history.add_document(doc)
        return doc

    # ---------- CERTIFICATES ----------

    def save_certificate(self, donor: Donor, certificate: DonationCertificate):
        cid = self.db.insert_certificate(certificate)
        certificate.id = cid
        donor.add_certificate(certificate)
        return certificate

    # ---------- BLOOD UNITS ----------

    def save_blood_unit(self, hospital: Hospital, unit: BloodUnit):
        uid = self.db.insert_blood_unit(unit, hospital.user_id)
        unit.unit_id = uid
        hospital.blood_inventory.add_unit(unit)
        return unit

    def update_blood_unit_status(self, hospital: Hospital, unit_code: str,
                                 new_status: str):
        unit = hospital.blood_inventory.update_unit_status(unit_code, new_status)
        if unit:
            self.db.update_blood_unit_status(unit_code, hospital.user_id,
                                             new_status)
        return unit

    # ---------- LISTS ----------

    def get_pending_applications(self):
        return [a for a in self.applications
                if a.status in ("pending", "pending_documents")]

    def get_open_reports(self):
        return [r for r in self.reports if r.status == "open"]

    def get_reports_as_target(self, identifier: str):
        """Return reports where the given identifier matches the target."""
        identifier_lower = identifier.strip().lower()
        return [
            r for r in self.reports
            if r.target_identifier.strip().lower() == identifier_lower
        ]

    def get_clarification_pending_reports(self, identifier: str):
        """Reports targeting this identifier that have a clarification request pending."""
        return [
            r for r in self.get_reports_as_target(identifier)
            if r.status == "open" and r.clarification_requested_at is not None
        ]

    def get_all_clarification_reports_for_user(self, user):
        """All open reports with a pending clarification where the user is either
        the *reporter* (submitted the complaint) or the *reported* party (target)."""
        uid = user.user_id
        identifier_lower = (getattr(user, "email", "") or "").strip().lower()
        seen = set()
        result = []
        for r in self.reports:
            if r.status != "open" or r.clarification_requested_at is None:
                continue
            if r.report_id in seen:
                continue
            is_target = r.target_identifier.strip().lower() == identifier_lower
            is_reporter = r.reporter_id == uid
            if is_target or is_reporter:
                seen.add(r.report_id)
                result.append((r, "target" if is_target else "reporter"))
        return result  # list of (Report, role_str)

    # ---------- EMERGENCY ALERTS ----------

    def send_emergency_alert(self, hospital, blood_type: str, required_units: int):
        """Send persistent emergency alert notifications to all matching available donors."""
        from models import Alert
        alert = Alert(hospital.name, blood_type, required_units)
        hospital.alerts.append(alert)

        import random
        if random.randint(1, 10) == 1:
            raise Exception("Αποτυχία αποστολής ειδοποιήσεων.")

        targets = []
        for donor in self.donors:
            if not donor.is_available:
                continue
            if donor.blood_type == blood_type:
                msg = (
                    f"ΕΠΕΙΓΟΝ: Ανάγκη για {required_units} "
                    f"μονάδες αίματος {blood_type}\n"
                    f"Νοσοκομείο: {hospital.name}"
                )
                self._add_notification(donor, msg)
                targets.append(donor)

        return alert, targets

    # ---------- REPORT RESPONSES ----------

    def add_report_response(self, report, responder, response_text: str, role: str = ""):
        """Record a clarification response from either the reporter or the reported party."""
        responder_name = (
            getattr(responder, "full_name", None)
            or getattr(responder, "name", None)
            or responder.username
        )
        role_label = {
            "reporter": "Καταγγέλλων",
            "target": "Αναφερόμενος",
        }.get(role, "Χρήστης")
        msg = (
            f"Απάντηση σε Αναφορά #{report.report_id}\n"
            f"Από ({role_label}): {responder_name}\n\n"
            f"{response_text}"
        )
        for admin in self.admins:
            self._add_notification(admin, msg)

    # ---------- SEED ----------

    def _seed_test_data(self):
        """Seed a test donor with historical donations so UC3 can be demonstrated."""
        TEST_EMAIL = "test@redhope.gr"
        if self.db.email_exists(TEST_EMAIL):
            return  # already seeded

        from datetime import date
        from models import Donor, Donation

        donor = Donor(
            username="test_donor",
            email=TEST_EMAIL,
            password="test123",
            full_name="Νίκος Παπαδόπουλος",
            amka="12345678901",
            blood_type="A+",
            phone="6900000001",
        )
        donor.is_available = True
        uid = self.db.insert_user("donor", donor)
        donor.user_id = uid
        donor.volunteer_id = uid
        donor.qr_code = f"QR-NIKOS-001"
        self.db.update_user(uid, donor)
        self.donors.append(donor)

        # Insert 3 historical donations
        past_dates = [
            date(2025, 5, 1),
            date(2024, 12, 1),
            date(2024, 7, 1),
        ]
        for d_date in past_dates:
            donation = Donation(
                donor_id=uid,
                donation_date=d_date,
                blood_group="A+",
                donation_type="whole_blood",
                amount_ml=450,
                organization="Σπόρος Ζωής",
                notes="Ιστορικό (seed)",
            )
            donation.status = "completed"
            did = self.db.insert_donation(donation, None)
            donation.id = did
            donor.donations.append(donation)

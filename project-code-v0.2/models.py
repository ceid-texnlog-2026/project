from datetime import date, datetime, timedelta
import random
import secrets


class UserAccount:
    def __init__(self, username: str, email: str, password: str):
        self.user_id: int = None
        self.username = username
        self.email = email
        self.password = password
        self.status: str = "active"
        self.is_suspended: bool = False
        self.notifications: list[str] = []

    def set_status(self, status: str):
        self.status = status

    def logout(self):
        print(f"{self.username} αποσυνδεθηκε.")


class MedicalDocument:
    def __init__(self, filename: str, upload_date: date,
                 document_type: str = "", file_path: str = ""):
        self.document_id: int = None
        self.filename = filename
        self.upload_date = upload_date
        self.document_type = document_type
        self.file_path = file_path
        self.is_valid: bool = True

    def validate_document(self) -> bool:
        allowed = [".pdf", ".jpg", ".jpeg", ".png"]
        return any(
            self.filename.lower().endswith(ext)
            for ext in allowed
        )


class MedicalHistory:
    def __init__(self):
        self.history_id: int = None
        self.donor_id: int = None
        self.blood_type: str = None
        self.documents: list[MedicalDocument] = []

    def add_document(self, document: MedicalDocument):
        self.documents.append(document)


class Donation:
    def __init__(
        self,
        donor_id: int,
        donation_date: date,
        blood_group: str,
        donation_type: str = "whole_blood",
        amount_ml: int = 450,
        organization: str = "",
        notes: str = ""
    ):
        self.id: int = None
        self.donor_id = donor_id
        self.donation_date = donation_date
        self.blood_group = blood_group
        self.donation_type = donation_type
        self.amount_ml = amount_ml
        self.organization = organization
        self.status: str = "completed"
        self.notes = notes

    def get_info(self) -> dict:
        return {
            "id": self.id,
            "donor_id": self.donor_id,
            "date": self.donation_date,
            "blood_group": self.blood_group,
            "amount_ml": self.amount_ml,
            "status": self.status,
        }

    def update_status(self, status: str):
        self.status = status


class DonationStatistics:
    def __init__(self, donor_id: int, donations: list[Donation]):
        self.stats_id: int = None
        self.donor_id = donor_id
        self.donations = donations

    def total_donations(self) -> int:
        return len(self.donations)

    def total_amount(self) -> int:
        return sum(d.amount_ml for d in self.donations)

    def calculate_stats(self) -> dict:
        return {
            "total_donations": self.total_donations(),
            "total_amount_ml": self.total_amount(),
        }


class DonationCertificate:
    def __init__(
        self,
        hospital_id: int,
        donor_id: int,
        certificate_number: str,
        issue_date: date,
        donation_date: date = None,
        donor_name: str = "",
        organization: str = "",
        pdf_path: str = ""
    ):
        self.id: int = None
        self.hospital_id = hospital_id
        self.donor_id = donor_id
        self.certificate_number = certificate_number
        self.issue_date = issue_date
        self.donation_date = donation_date
        self.donor_name = donor_name
        self.organization = organization
        self.pdf_path = pdf_path
        self.status: str = "issued"

    def create(self):
        pass


class Appointment:
    def __init__(
        self,
        donor_id: int,
        center_id: int,
        appointment_date: date,
        time: str = ""
    ):
        self.appointment_id: int = None
        self.donor_id = donor_id
        self.center_id = center_id
        self.appointment_date = appointment_date
        self.time = time
        self.status: str = "upcoming"

    def create(self):
        pass

    def cancel(self):
        self.status = "cancelled"


class DonationCenter:
    def __init__(self, name: str, address: str):
        self.center_id: int = None
        self.name = name
        self.address = address
        self.available_slots: list[dict] = []

    def get_availability(self) -> list[dict]:
        return self.available_slots


class Donor(UserAccount):
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = "",
        amka: str = "",
        blood_type: str = "",
        date_of_birth: date = None,
        gender: str = "",
        phone: str = ""
    ):
        super().__init__(username, email, password)

        self.volunteer_id: int = None
        self.full_name = full_name
        self.amka = amka
        self.qr_code: str = ""
        self.blood_type = blood_type
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.phone = phone

        self.medical_history = MedicalHistory()
        self.medical_history.blood_type = blood_type

        self.is_available: bool = False
        self.appointments: list[Appointment] = []
        self.donations: list[Donation] = []
        self.certificates: list[DonationCertificate] = []

    def get_info(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "blood_type": self.blood_type,
            "is_available": self.is_available,
        }

    def add_donation(self, donation: Donation):
        self.donations.append(donation)

    def add_certificate(self, certificate: DonationCertificate):
        self.certificates.append(certificate)

    def get_last_donation(self):
        completed = [
            a for a in self.appointments
            if a.status == "completed"
        ]

        if not completed:
            return None

        return max(
            completed,
            key=lambda a: a.appointment_date
        )

    def get_next_appointment(self):
        upcoming = [
            a for a in self.appointments
            if a.status == "upcoming"
        ]

        if not upcoming:
            return None

        return min(
            upcoming,
            key=lambda a: a.appointment_date
        )

    def get_statistics(self) -> DonationStatistics:
        return DonationStatistics(
            self.volunteer_id,
            self.donations
        )


class BloodUnit:
    def __init__(
        self,
        blood_type: str,
        quantity: int,
        expiration_date: date,
        unit_code: str = "",
        collection_date: date = None,
        product_type: str = "whole_blood"
    ):
        self.unit_id: int = None
        self.unit_code = unit_code
        self.blood_type = blood_type
        self.quantity = quantity
        self.collection_date = collection_date
        self.expiration_date = expiration_date
        self.product_type = product_type
        self.status: str = "available"

    def update_status(self, status: str):
        self.status = status


class BloodInventory:
    def __init__(self):
        self.inventory_id: int = None
        self.last_updated: datetime = datetime.now()

        self.stock: dict[str, int] = {
            "A+": 0,
            "A-": 0,
            "B+": 0,
            "B-": 0,
            "AB+": 0,
            "AB-": 0,
            "O+": 0,
            "O-": 0,
        }

        self.units: list[BloodUnit] = []

    def is_low(self, blood_type: str, threshold: int = 5) -> bool:
        return self.stock.get(blood_type, 0) < threshold

    def check_inventory(self) -> dict:
        return self.stock

    def check_availability(self, blood_type: str) -> bool:
        return self.stock.get(blood_type, 0) > 0

    def add_unit(self, blood_unit: BloodUnit):
        self.units.append(blood_unit)

        if blood_unit.status == "available":
            current = self.stock.get(blood_unit.blood_type, 0)
            self.stock[blood_unit.blood_type] = current + blood_unit.quantity

        self.last_updated = datetime.now()

    def update_unit_status(self, unit_code: str, new_status: str):
        for unit in self.units:
            if unit.unit_code == unit_code:
                old_status = unit.status
                unit.update_status(new_status)

                if old_status == "available" and new_status in ["used", "discarded"]:
                    current = self.stock.get(unit.blood_type, 0)
                    self.stock[unit.blood_type] = max(0, current - unit.quantity)

                self.last_updated = datetime.now()
                return unit

        return None

    def get_expiring_soon_units(self, days: int = 7):
        today = date.today()
        expiring = []

        for unit in self.units:
            if unit.status == "available":
                days_left = (unit.expiration_date - today).days

                if 0 <= days_left <= days:
                    expiring.append(unit)

        return expiring


class Alert:
    def __init__(
        self,
        hospital_name: str,
        blood_type: str,
        required_units: int
    ):
        self.hospital_name = hospital_name
        self.blood_type = blood_type
        self.required_units = required_units
        self.status: str = "active"
        self.created_at: datetime = datetime.now()


class Hospital(UserAccount):
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        name: str,
        address: str,
        city: str,
        region: str,
        phone: str,
        service_code: str
    ):
        super().__init__(username, email, password)

        self.id: int = None
        self.name = name
        self.address = address
        self.city = city
        self.region = region
        self.phone = phone
        self.service_code = service_code

        self.blood_inventory = BloodInventory()
        self.appointments: list[Appointment] = []
        self.donations: list[Donation] = []
        self.alerts: list[Alert] = []
        self.is_certified: bool = False
        self.must_change_password: bool = False

    def send_urgent_appeal(
        self,
        blood_type: str,
        required_units: int,
        donors: list[Donor]
    ):
        alert = Alert(
            self.name,
            blood_type,
            required_units
        )

        self.alerts.append(alert)

        if random.randint(1, 10) == 1:
            raise Exception(
                "Αποτυχία αποστολής ειδοποιήσεων."
            )

        targets = []

        for donor in donors:
            if donor.is_available and donor.blood_type == blood_type:
                notification = (
                    f"ΕΠΕΙΓΟΝ: Ανάγκη για {required_units} "
                    f"μονάδες αίματος {blood_type}\n"
                    f"Νοσοκομείο: {self.name}"
                )

                donor.notifications.append(notification)
                targets.append(donor)

        return alert, targets

    def record_donation(
        self,
        donor: Donor,
        donation_type: str = "whole_blood"
    ):
        donation = Donation(
            donor_id=donor.volunteer_id or 1,
            donation_date=date.today(),
            blood_group=donor.blood_type,
            donation_type=donation_type,
            amount_ml=450,
            organization=self.name,
            notes="Καταγραφή αιμοδοσίας από νοσοκομείο"
        )

        donor.add_donation(donation)
        self.donations.append(donation)

        return donation

    def get_completed_donations(self):
        return [
            donation for donation in self.donations
            if donation.status == "completed"
        ]

    def save_certificate_to_donor(
        self,
        donor: Donor,
        donation: Donation,
        pdf_path: str
    ):
        if random.randint(1, 10) == 1:
            raise Exception(
                "Αποτυχία αποθήκευσης βεβαίωσης στο προφίλ του εθελοντή."
            )

        certificate_number = f"CERT-{len(donor.certificates) + 1:03d}"

        certificate = DonationCertificate(
            hospital_id=self.id or 1,
            donor_id=donor.volunteer_id or 1,
            certificate_number=certificate_number,
            issue_date=date.today(),
            donation_date=donation.donation_date,
            donor_name=donor.full_name or donor.username,
            organization=self.name,
            pdf_path=pdf_path
        )

        donor.add_certificate(certificate)

        return certificate


class HospitalEmployee:
    def __init__(
        self,
        employee_id: int,
        name: str,
        username: str,
        hospital_id: int,
        role: str = "nurse"
    ):
        self.employee_id = employee_id
        self.name = name
        self.username = username
        self.hospital_id = hospital_id
        self.role = role


class Application:
    def __init__(
        self,
        center_type: str,
        documents: list = None,
        hospital_name: str = "",
        contact_name: str = "",
        contact_email: str = "",
        phone: str = "",
        address: str = "",
        city: str = "",
        region: str = "",
    ):
        self.request_id: int = None
        self.status: str = "pending"
        self.center_type = center_type
        self.documents: list = documents or []
        self.hospital_name = hospital_name
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.phone = phone
        self.address = address
        self.city = city
        self.region = region
        self.created_at: datetime = datetime.now()
        self.cross_reference_passed: bool = False

    def get_info(self) -> dict:
        return {
            "request_id": self.request_id,
            "status": self.status,
            "center_type": self.center_type,
            "hospital_name": self.hospital_name,
        }

    def set_status(self, status: str):
        self.status = status


class Report:
    def __init__(
        self,
        description: str,
        reporter_id: int = None,
        reporter_name: str = "",
        target_type: str = "",
        target_identifier: str = "",
    ):
        self.report_id: int = None
        self.description = description
        self.status: str = "open"
        self.justification: str = ""
        self.reporter_id = reporter_id
        self.reporter_name = reporter_name
        self.target_type = target_type
        self.target_identifier = target_identifier
        self.action: str = ""
        self.created_at: datetime = datetime.now()
        self.clarification_requested_at: datetime = None

    def get_info(self) -> dict:
        return {
            "report_id": self.report_id,
            "description": self.description,
            "status": self.status,
            "reporter_name": self.reporter_name,
            "target": f"{self.target_type}: {self.target_identifier}",
        }

    def set_status(self, status: str):
        self.status = status


class Admin(UserAccount):
    def __init__(self, username: str, email: str, password: str):
        super().__init__(username, email, password)

        self.admin_id: int = None
        self.users: list[Donor] = []
        self.hospitals: list[Hospital] = []
        self.applications: list[Application] = []
        self.reports: list[Report] = []

    def get_total_users(self) -> int:
        return len(self.users)

    def get_total_hospitals(self) -> int:
        return len(self.hospitals)


class ExternalRegistry:
    def __init__(self, registry_name: str = "Εθνικό Μητρώο Φορέων"):
        self.registry_name = registry_name

    def look_up(self, hospital_name: str, service_code: str = "") -> bool:
        if not hospital_name or len(hospital_name) < 3:
            return False
        return random.randint(1, 10) > 2


class Timer:
    def __init__(self, duration_hours: int = 48):
        self.timer_id: int = None
        self.duration = duration_hours
        self.start_time: datetime = None
        self.expired: bool = False

    def start_timer(self):
        self.start_time = datetime.now()
        self.expired = False

    def expire(self):
        if not self.start_time:
            return False
        if datetime.now() - self.start_time >= timedelta(hours=self.duration):
            self.expired = True
        return self.expired


class EmailNotification:
    def __init__(self):
        self.sent_emails: list[dict] = []

    def _log(self, to: str, subject: str, body: str):
        self.sent_emails.append({
            "to": to, "subject": subject, "body": body,
            "sent_at": datetime.now(),
        })
        print(f"[EMAIL → {to}] {subject}")

    def send_temp_credentials(self, email: str, temp_password: str):
        self._log(email, "Προσωρινά credentials",
                  f"Ο προσωρινός κωδικός σας είναι: {temp_password}")

    def request_new_documents(self, email: str):
        self._log(email, "Συμπληρωματικά δικαιολογητικά",
                  "Παρακαλούμε υποβάλετε επικαιροποιημένα δικαιολογητικά εντός 5 ημερών.")

    def request_update_data(self, email: str):
        self._log(email, "Ενημέρωση στοιχείων",
                  "Παρακαλούμε ενημερώστε τα στοιχεία αδειοδότησης.")

    def notify_rejection(self, email: str, reason: str):
        self._log(email, "Απόρριψη αιτήματος", f"Λόγος: {reason}")

    def notify_parties(self, email: str, message: str):
        self._log(email, "Ενημέρωση αναφοράς", message)

    def notify_admin(self, message: str):
        self._log("admin@redhope.gr", "Ειδοποίηση Admin", message)


class NotificationService:
    def __init__(self):
        self.notification_service_id = 1
        self.device_notifications_enabled = True
        self.emergency_notifications_enabled = True
        self.log: list[dict] = []

    def send_notification(self, user, message: str):
        self.log.append({
            "to": getattr(user, "username", "?"),
            "message": message,
            "sent_at": datetime.now(),
        })

    def enable_emergency_notifications(self, user):
        user.is_available = True

    def disable_emergency_notifications(self, user):
        user.is_available = False


class NotificationController:
    def __init__(self, service: NotificationService = None):
        self.notification_id = 1
        self.service = service or NotificationService()

    def send_notification(self, user, message: str):
        self.service.send_notification(user, message)


class DonationRecord:
    def __init__(self, donation: Donation):
        self.id_donation = donation.id
        self.donation = donation

    def create(self):
        return self.donation


def generate_temp_password() -> str:
    return secrets.token_urlsafe(6)


HospitalEmployee.__init__.__doc__ = "Domain stub for hospital employee role"
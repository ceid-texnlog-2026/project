from datetime import date


class User:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

    def logout(self):
        print(f"{self.username} αποσυνδέθηκε.")


class MedicalDocument:
    def __init__(self, filename: str, upload_date: date):
        self.filename = filename
        self.upload_date = upload_date


class MedicalHistory:
    def __init__(self):
        self.blood_type: str = None
        self.documents: list[MedicalDocument] = []

    def add_document(self, document: MedicalDocument):
        self.documents.append(document)

    def total_donations(self):
        pass


class Donor(User):
    def __init__(self, username: str, email: str, password: str):
        super().__init__(username, email, password)
        self.medical_history = MedicalHistory()
        self.is_available: bool = False
        self.appointments: list = []

    def get_last_donation(self):
        completed = [
            a for a in self.appointments if a.status == "completed"
        ]
        if not completed:
            return None
        return max(completed, key=lambda a: a.appointment_date)

    def get_next_appointment(self):
        upcoming = [
            a for a in self.appointments if a.status == "upcoming"
        ]
        if not upcoming:
            return None
        return min(upcoming, key=lambda a: a.appointment_date)


class BloodInventory:
    def __init__(self):
        self.stock: dict[str, int] = {
            "A+": 0, "A-": 0,
            "B+": 0, "B-": 0,
            "AB+": 0, "AB-": 0,
            "O+": 0, "O-": 0,
        }

    def is_low(self, blood_type: str, threshold: int = 5) -> bool:
        return self.stock.get(blood_type, 0) < threshold


class Hospital(User):
    def __init__(self, username: str, email: str, password: str,
                 name: str, address: str, city: str,
                 region: str, phone: str, service_code: str):
        super().__init__(username, email, password)
        self.name = name
        self.address = address
        self.city = city
        self.region = region
        self.phone = phone
        self.service_code = service_code
        self.blood_inventory = BloodInventory()
        self.appointments: list = []

    def send_urgent_appeal(self, blood_type: str, donors: list[Donor]):
        targets = [
            d for d in donors
            if d.is_available and d.medical_history.blood_type == blood_type
        ]
        return targets


class Admin(User):
    def __init__(self, username: str, email: str, password: str):
        super().__init__(username, email, password)
        self.users: list[User] = []
        self.hospitals: list[Hospital] = []

    def get_total_users(self) -> int:
        return len(self.users)

    def get_total_hospitals(self) -> int:
        return len(self.hospitals)

import tkinter as tk
from datetime import date

import config
from config import BG_LIGHT, load_background
from models import Donor, Hospital, Admin
from frames.login_frame    import LoginFrame
from frames.donor_frame    import DonorFrame
from frames.hospital_frame import HospitalFrame
from frames.admin_frame    import AdminFrame

#  Demo δεδομένα
class MockAppointment:
    def __init__(self, status, appointment_date):
        self.status = status
        self.appointment_date = appointment_date

demo_donor = Donor("nikos", "nikos@mail.com", "1234")
demo_donor.medical_history.blood_type = "A+"
demo_donor.is_available = True
demo_donor.appointments = [
    MockAppointment("completed", date(2026, 1, 12)),
    MockAppointment("upcoming",  date(2026, 6, 20)),
]

demo_hospital = Hospital(
    username="gen_hosp", email="hosp@mail.com", password="1234",
    name="Κέντρο Αιμοδοσίας", address="Λεωφ. Αθηνών 10",
    city="Αθήνα", region="Αττική", phone="210-0000000",
    service_code="GH-001"
)
demo_hospital.blood_inventory.stock = {
    "A+": 12, "A-": 3, "B+": 8, "B-": 2,
    "AB+": 6, "AB-": 1, "O+": 15, "O-": 4
}

demo_admin = Admin("admin1", "admin@mail.com", "1234")
demo_admin.users = [demo_donor]
demo_admin.hospitals = [demo_hospital]

USERS = {
    ("nikos@mail.com", "1234", "Αιμοδότης"):  demo_donor,
    ("hosp@mail.com",   "1234", "Νοσοκομείο"): demo_hospital,
    ("admin@mail.com",  "1234", "Admin"):       demo_admin,
}

#main app
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Red Hope")
        self.geometry("400x700")
        self.resizable(False, False)
        self.configure(bg=BG_LIGHT)
        self.current_frame = None

        load_background()
        self.show_login()

    def switch(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):       self.switch(LoginFrame, USERS)
    def show_donor(self, d):    self.switch(DonorFrame, d)
    def show_hospital(self, h): self.switch(HospitalFrame, h)
    def show_admin(self, a):    self.switch(AdminFrame, a)


if __name__ == "__main__":
    app = App()
    app.mainloop()

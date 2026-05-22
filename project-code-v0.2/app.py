import tkinter as tk
from config import light_green, load_background
from db import DBManager
from frames.login_frame import LoginFrame
from frames.donor_frame import DonorFrame
from frames.hospital_frame import HospitalFrame
from frames.admin_frame import AdminFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Red Hope")
        self.geometry("400x700")
        self.resizable(False, False)
        self.configure(bg=light_green)
        self.current_frame = None
        self.db = DBManager()
        load_background()
        self.show_login()

    def switch(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.switch(LoginFrame)

    def show_donor(self, donor):
        self.switch(DonorFrame, donor)

    def show_hospital(self, hospital):
        self.switch(HospitalFrame, hospital, self.db.donors)

    def show_admin(self, admin):
        self.switch(AdminFrame, admin)


if __name__ == "__main__":
    app = App()
    app.mainloop()

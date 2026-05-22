from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk

assets_folder = Path(__file__).parent / "assets"

light_green = "#c8d9d6"
card_green = "#a8c5bf"
dark_green = "#4a7c74"
white = "#ffffff"
dark_text = "#1e2d2b"
mid_text = "#3a5a54"
red = "#e05a3a"

title_font = ("Arial", 20, "bold")
subtitle_font = ("Arial", 13, "bold")
normal_font = ("Arial", 11)
button_font = ("Arial", 12, "bold")
small_font = ("Arial", 10)

icon_files = {
    "logo":         "logo.png",
    "bell":         "bell.png",
    "heart":        "heart.png",
    "calendar":     "calendar.png",
    "appointment":  "appointment.png",
    "upload":       "upload.png",
    "history":      "history.png",
    "availability": "availability.png",
    "urgent":       "alert.png",
    "donation_reg": "donation_reg.png",
    "inventory":    "inventory.png",
    "certificate":  "certificate.png",
    "verify":       "verify.png",
    "reports":      "report.png",
}

background_photo = None


def get_icon(name, size=40):
    path = assets_folder / icon_files.get(name, "")
    if path.exists():
        img = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        return ("image", photo)
    return ("text", name)


def load_background():
    global background_photo
    path = assets_folder / "background.png"
    if path.exists():
        img = Image.open(path).resize((400, 700), Image.LANCZOS)
        background_photo = ImageTk.PhotoImage(img)


def set_background(frame):
    if background_photo:
        label = tk.Label(frame, image=background_photo)
        label.place(x=0, y=0, relwidth=1, relheight=1)
        label.lower()

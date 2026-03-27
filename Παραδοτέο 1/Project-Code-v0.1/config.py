from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

ASSETS_DIR = Path(__file__).parent / "assets"

#colors
BG_LIGHT = "#c8d9d6"
BG_CARD  = "#a8c5bf"
BTN_DARK = "#4a7c74"
BTN_TEXT = "#ffffff"
TEXT_DARK = "#1e2d2b"
TEXT_MID  = "#3a5a54"
ACCENT    = "#e05a3a"

#fonts
FONT_TITLE = ("Georgia", 20, "bold")
FONT_SUB   = ("Georgia", 13, "bold")
FONT_BODY  = ("Helvetica", 11)
FONT_BTN   = ("Helvetica", 12, "bold")
FONT_SMALL = ("Helvetica", 10)

#icons
ICONS = {
    "logo":         ("logo.png",          "[LOGO]"),
    "bell":         ("bell.png",          "[!]"),
    "heart":        ("heart.png",         "[+]"),
    "calendar":     ("calendar.png",      "[ΗΜ]"),
    "appointment":  ("appointment.png",   "[ΡΑΝ]"),
    "upload":       ("upload.png",        "[UP]"),
    "history":      ("history.png",       "[ΙΣΤ]"),
    "availability": ("availability.png",  "[ΔΙΑ]"),
    "urgent":       ("alert.png",         "[!!!]"),
    "donation_reg": ("donation_reg.png",  "[ΚΑΤ]"),
    "inventory":    ("inventory.png",     "[ΑΠΟ]"),
    "certificate":  ("certificate.png",   "[ΒΕΒ]"),
    "verify":       ("verify.png",        "[ΠΙΣ]"),
    "reports":      ("report.png",        "[ΑΝΑ]"),
}

_icon_cache: dict = {}
_bg_image = None

def load_icon(key: str, size: int = 40):
    cache_key = (key, size)
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]

    filename, fallback = ICONS.get(key, ("", key))
    path = ASSETS_DIR / filename

    if PIL_AVAILABLE and path.exists():
        img = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _icon_cache[cache_key] = ("image", photo)
        return ("image", photo)

    _icon_cache[cache_key] = ("text", fallback)
    return ("text", fallback)

def load_background():
    global _bg_image
    bg_path = ASSETS_DIR / "background.png"
    if PIL_AVAILABLE and bg_path.exists():
        img = Image.open(bg_path).resize((400, 700), Image.LANCZOS)
        _bg_image = ImageTk.PhotoImage(img)

def set_bg(frame):
    if _bg_image:
        lbl = __import__("tkinter").Label(frame, image=_bg_image)
        lbl.place(x=0, y=0, relwidth=1, relheight=1)
        lbl.lower()

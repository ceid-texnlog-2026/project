import tkinter as tk
from tkinter import ttk
from config import (BG_CARD, BG_LIGHT, BTN_DARK, BTN_TEXT,
                    TEXT_DARK, TEXT_MID, FONT_BTN, FONT_BODY,
                    FONT_SMALL, load_icon, set_bg)


def rounded_btn(parent, text, command, bg=BTN_DARK, fg=BTN_TEXT, width=22):
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg, font=FONT_BTN,
                     relief="flat", bd=0, cursor="hand2",
                     width=width, pady=8)


def field_entry(parent, placeholder):
    frame = tk.Frame(parent, bg=BG_CARD, bd=0)
    entry = tk.Entry(frame, font=FONT_BODY, bg=BG_CARD, fg=TEXT_MID,
                     relief="flat", bd=0, width=28,
                     insertbackground=TEXT_DARK)
    entry.insert(0, placeholder)

    def on_focus_in(e):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=TEXT_DARK)
            if "Κωδικός" in placeholder:
                entry.config(show="*")

    def on_focus_out(e):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg=TEXT_MID, show="")

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    frame.pack(fill="x", padx=30, pady=6, ipady=10, ipadx=10)
    entry.pack(padx=10, pady=4)
    return entry, frame


def grid_btn(parent, text, icon_key, row, col, command):
    f = tk.Frame(parent, bg=BG_CARD, cursor="hand2")
    f.grid(row=row, column=col, padx=8, pady=8, sticky="nsew", ipadx=6, ipady=14)

    kind, val = load_icon(icon_key, size=40)
    if kind == "image":
        lbl = tk.Label(f, image=val, bg=BG_CARD)
        lbl.image = val
    else:
        lbl = tk.Label(f, text=val, font=("Helvetica", 13, "bold"),
                       bg=BG_CARD, fg=TEXT_MID)
    lbl.pack(pady=(10, 2))

    tk.Label(f, text=text, font=("Poppins", 10, "bold"),
             bg=BG_CARD, fg=TEXT_DARK, wraplength=120,
             justify="center").pack(pady=(0, 10))

    f.bind("<Button-1>", lambda e: command())
    for w in f.winfo_children():
        w.bind("<Button-1>", lambda e: command())
    return f


def bell_header(parent):
    header = tk.Frame(parent, bg=BG_LIGHT)
    header.pack(fill="x", padx=16, pady=(10, 0))
    kind, val = load_icon("bell", size=24)
    if kind == "image":
        lbl = tk.Label(header, image=val, bg=BG_LIGHT, cursor="hand2")
        lbl.image = val
    else:
        lbl = tk.Label(header, text=val, font=("Poppins", 14, "bold"),
                       bg=BG_LIGHT, fg=TEXT_DARK, cursor="hand2")
    lbl.pack(side="right")

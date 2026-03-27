import tkinter as tk
from tkinter import ttk
from config import (card_green, light_green, dark_green, white,
                    dark_text, mid_text, button_font, normal_font,
                    small_font, get_icon)


def simple_button(parent, text, action, color=dark_green, text_color=white, width=22):
    return tk.Button(parent, text=text, command=action,
                     bg=color, fg=text_color, font=button_font,
                     relief="flat", bd=0, cursor="hand2",
                     width=width, pady=8)


def input_field(parent, placeholder):
    frame = tk.Frame(parent, bg=card_green, bd=0)
    field = tk.Entry(frame, font=normal_font, bg=card_green, fg=mid_text,
                     relief="flat", bd=0, width=28, insertbackground=dark_text)
    field.insert(0, placeholder)

    def on_click(e):
        if field.get() == placeholder:
            field.delete(0, tk.END)
            field.config(fg=dark_text)
            if "Κωδικός" in placeholder:
                field.config(show="*")

    def on_leave(e):
        if field.get() == "":
            field.insert(0, placeholder)
            field.config(fg=mid_text, show="")

    field.bind("<FocusIn>", on_click)
    field.bind("<FocusOut>", on_leave)
    frame.pack(fill="x", padx=30, pady=6, ipady=10, ipadx=10)
    field.pack(padx=10, pady=4)
    return field, frame


def icon_button(parent, text, icon_name, row, col, action):
    frame = tk.Frame(parent, bg=card_green, cursor="hand2")
    frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew", ipadx=6, ipady=14)

    kind, value = get_icon(icon_name, size=40)
    if kind == "image":
        label = tk.Label(frame, image=value, bg=card_green)
        label.image = value
    else:
        label = tk.Label(frame, text=value, font=("Poppins", 13, "bold"),
                         bg=card_green, fg=mid_text)
    label.pack(pady=(10, 2))

    tk.Label(frame, text=text, font=("Poppins", 10, "bold"),
             bg=card_green, fg=dark_text, wraplength=120,
             justify="center").pack(pady=(0, 10))

    frame.bind("<Button-1>", lambda e: action())
    for w in frame.winfo_children():
        w.bind("<Button-1>", lambda e: action())
    return frame


def bell_header(parent):
    header = tk.Frame(parent, bg=light_green)
    header.pack(fill="x", padx=16, pady=(10, 0))
    kind, value = get_icon("bell", size=24)
    if kind == "image":
        label = tk.Label(header, image=value, bg=light_green, cursor="hand2")
        label.image = value
    else:
        label = tk.Label(header, text=value, font=("Poppins", 14, "bold"),
                         bg=light_green, fg=dark_text, cursor="hand2")
    label.pack(side="right")

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import time
import sys

ctk.set_appearance_mode("system")
ctk.deactivate_automatic_dpi_awareness()
ctk.set_widget_scaling(1.2)

root = ctk.CTk()

root_width = 800
root_height = 1008
    
x_root = root.winfo_screenwidth()
y_root = root.winfo_screenheight()
horizontal_pos_root = int(x_root/2-root_width/2)


def start_caesar():

    caesar = ctk.CTkToplevel(root)

    caesar_width = 600
    caesar_height = 800

    x_caesar = caesar.winfo_screenwidth()
    y_caesar = caesar.winfo_screenheight()
    horizontal_pos_caesar = int(x_caesar/2-caesar_width/4)
    caesar.geometry(f"{caesar_width}x{caesar_height}+{horizontal_pos_caesar}+0")
    caesar.configure(fg_color=("#FFF9D6","#2B2D42"))
    caesar.columnconfigure(0,weight=1)
    root.overrideredirect(False)

    create_title_bar(caesar,title_text="Julius - Caesar Cipher")

    resize_grip = ctk.CTkLabel(
            master=caesar,
            text="◢",
            font=("Arial", 14),
            text_color=("gray40", "gray60"),
            cursor="sizing",
            width=20,
            height=20
        )


    resize_grip.place(relx=1.0, rely=1.0, anchor="se", x=-2, y=-2)
    resize_grip.bind("<Button-1>", lambda e: start_resize(e, caesar))
    resize_grip.bind("<B1-Motion>", lambda e: do_resize(e, caesar))

    mode_text = "☼" if ctk.get_appearance_mode() == "Dark" else "☽" 


    mode_toggle = ctk.CTkButton(master=caesar, text=mode_text, hover_color=("#5D6D7E", "#FAF1CA"), fg_color="transparent", font=(
        "Helvetica", 16, "bold"), text_color=("#7F2122", "#F4D03F"), width=30, corner_radius=0, command=toggle_mode)
    mode_toggle.grid(row=2, column=0, sticky="e", padx=8, pady=6)
    mode_toggle.bind("<Enter>", lambda e: mode_toggle.configure(
        fg_color=("#5D6D7E", "#FAF1CA"), text_color=("#F4D03F", "#FACD1E")))
    mode_toggle.bind("<Leave>", lambda e: mode_toggle.configure(
        fg_color='transparent', text_color=("#7F2122", "#F4D03F")))

    caesar.wm_attributes('-type', 'splash')

    caesar.update_idletasks()

    if sys.platform.startswith("linux"):
        caesar.wm_attributes('-type', 'utility')
    else:
        caesar.overrideredirect(True)


def create_title_bar(window, title_text="Julius - Classical cipher tool"):
    title_bar = ctk.CTkFrame(master=window, fg_color=("#FAF1CA", "#313342"))
    title_bar.grid(row=0, column=0, sticky='ew')
    title_bar.columnconfigure(0, weight=1)

    title_label = ctk.CTkLabel(
        master=title_bar,
        text=title_text,
        font=("Constantine", 14, 'bold'),
        fg_color="transparent",
        text_color=("#7F2122", "#F4D03F")
    )
    title_label.grid(row=0, column=0, sticky="ns")

    minimise_button = ctk.CTkButton(
        master=title_bar, text="—", hover_color=("#5D6D7E", "#FAF1CA"),
        fg_color="transparent", font=("Helvetica", 16, "bold"),
        text_color=("#7F2122", "#F4D03F"), width=35, corner_radius=0,
        command=lambda: minimise_window(window)
    )
    minimise_button.grid(row=0, column=1, sticky="e")

    maximise_button = ctk.CTkButton(
        master=title_bar, text="☐", hover_color=("#5D6D7E", "#FAF1CA"),
        fg_color="transparent", font=("Helvetica", 16, "bold"),
        text_color=("#7F2122", "#F4D03F"), width=35, corner_radius=0
    )
    maximise_button.grid(row=0, column=2, sticky="e")
    maximise_button.configure(command=lambda: maximise_window(window, maximise_button))

    close_button = ctk.CTkButton(
        master=title_bar, text="X", hover_color=("#5D6D7E", "#FAF1CA"),
        fg_color="transparent", font=("Helvetica", 16, "bold"),
        text_color=("#7F2122", "#F4D03F"), width=35, corner_radius=0,
        command=window.destroy
    )
    close_button.grid(row=0, column=3, sticky="e")

    seperator = ttk.Separator(master=window,orient="horizontal")
    seperator.grid(row=1,column=0,sticky="ew")

    # Drag bindings scoped to this specific window
    for widget in (title_bar, title_label):
        widget.bind("<Button-1>", lambda e: start_move(e, window))
        widget.bind("<B1-Motion>", lambda e: do_move(e, window))

    # Hover color bindings for all three buttons
    for btn in (close_button, maximise_button, minimise_button):
        btn.bind("<Enter>", lambda e, b=btn: b.configure(
            fg_color=("#5D6D7E", "#FAF1CA"), text_color=("#F4D03F", "#D32929")))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(
            fg_color='transparent', text_color=("#7F2122", "#F4D03F")))

    return title_bar

def toggle_mode():

    if ctk.get_appearance_mode() == 'Dark':
        mode_toggle.configure(text="☽")
        ctk.set_appearance_mode("light")
    else:
        mode_toggle.configure(text="☼")
        ctk.set_appearance_mode("dark")



def splash_animation():
    full_text = "Welcome to Julius..."
    typed_text = ""
    root.wm_attributes('-type','splash')

    root_width = 500
    root_height = 300
    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)
    vertical_pos_root = int(y_root/2-root_height/2)
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
    root.configure(fg_color=("#FFF9D6","#2B2D42"))
    root.update()

    for char in full_text:
        typed_text += char
        greeting_label.configure(text=typed_text)
        greeting_label.update()
        time.sleep(0.15)


def maximise_window(window, button):
    x_root = window.winfo_screenwidth()
    y_root = window.winfo_screenheight()
    horizontal_pos_root = int(x_root/2 - root_width/2)

    fullscreen_width = int(window.winfo_screenwidth())
    fullscreen_height = int(window.winfo_screenheight())
    
    # Store state on the window object so it persists across clicks
    if not getattr(window, "is_maximised", False):
        window.geometry(f"{fullscreen_width}x{fullscreen_height}+0+0")
        window.is_maximised = True
        button.configure(text="⮺")
        window.update()
    else:
        window.wm_attributes('-type', 'normal')    
        window.update_idletasks()
        window.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+0")
        button.configure(text="☐")
        window.update_idletasks()
        window.is_maximised = False


def check_window_state(window):
    
    if window.state() != "iconic":
        window.overrideredirect(True)  
        window.update_idletasks()
    else:
    
        window.after(300, check_window_state)


def minimise_window(window):

    if sys.platform.startswith('linux'):
        window.iconify()

    else:
    
        window.update_idletasks()
        window.overrideredirect(False)
        window.state("iconic")
        check_window_state()


drag_data = {"x": 0, "y": 0}

def start_move(event,window):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def do_move(event,window):
    deltax = event.x - drag_data["x"]
    deltay = event.y - drag_data["y"]
    x = window.winfo_x() + deltax
    y = window.winfo_y() + deltay
    window.geometry(f"+{x}+{y}")


resize_data = {"x": 0, "y": 0, "width": 0, "height": 0}

def start_resize(event,window):
    resize_data["x"] = event.x_root
    resize_data["y"] = event.y_root
    resize_data["width"] = window.winfo_width()
    resize_data["height"] = window.winfo_height()

def do_resize(event,window):
    delta_x = event.x_root - resize_data["x"]
    delta_y = event.y_root - resize_data["y"]

    # Keeping a minimum size of 450x350 so the window doesn't disappear
    new_width = max(450, resize_data["width"] + delta_x)
    new_height = max(350, resize_data["height"] + delta_y)
    window.geometry(f"{new_width}x{new_height}")


greeting_label = ctk.CTkLabel(master=root,text_color=("#7F212","#F4D03F"),font=("Praetorium BB",24,"bold"))
greeting_label.pack(pady=100)

splash_animation()
greeting_label.destroy()

## TODO: configure dark and light modes using color pallettes in references, add naivgation button


root.title("Julius — Classical Cipher De/Encoder")
root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+0")
root.configure(fg_color=("#FFF9D6","#2B2D42"))
root.columnconfigure(0,weight=1)
root.overrideredirect(False)
create_title_bar(root,title_text="Julius - Classical Cipher Tool")



welcome_frame= ctk.CTkFrame(master=root,fg_color=("#FAF1CA","#2B2D42"))
welcome_frame.grid(row=3,column=0,sticky="ns")

caesar_button = ctk.CTkButton(master=welcome_frame,text="Caesar Cipher",width=200,height=100,corner_radius=15,font=("Castelforte",16,"bold"), command=start_caesar)
caesar_button.grid(row=3,column=0,sticky="ew",pady=20)

# atbash_button = ctk.CTkButton()

# vigenere_button = ctk.CTkButton()

# playfair_button = ctk.CTkButton()




resize_grip = ctk.CTkLabel(
    master=root,
    text="◢",
    font=("Arial", 14),
    text_color=("gray40", "gray60"),
    cursor="sizing",
    width=20,
    height=20
)
resize_grip.place(relx=1.0,rely=1.0,anchor="se",x=-2,y=-2)
resize_grip.bind("<Button-1>", lambda e: start_resize(e,root))
resize_grip.bind("<B1-Motion>", lambda e: do_resize(e,root))

mode_text = "☼" if ctk.get_appearance_mode() == "Dark" else "☽" 

mode_toggle = ctk.CTkButton(master=root,text=mode_text,hover_color=("#5D6D7E","#FAF1CA"),fg_color="transparent",font=("Helvetica",16,"bold"),text_color=("#7F2122","#F4D03F"),width=30,corner_radius=0,command=toggle_mode)
mode_toggle.grid(row=2,column=0 ,sticky="e",padx=8,pady=6)
mode_toggle.bind("<Enter>", lambda e: mode_toggle.configure(fg_color=("#5D6D7E","#FAF1CA"),text_color=("#F4D03F","#FACD1E")))
mode_toggle.bind("<Leave>", lambda e: mode_toggle.configure(fg_color='transparent',text_color=("#7F2122","#F4D03F")))

root.wm_attributes('-type', 'utility')

root.after(4000,root.update)

root.mainloop()
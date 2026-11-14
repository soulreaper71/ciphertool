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

def toggle_mode():

    if ctk.get_appearance_mode() == 'Dark':
        mode_toggle.configure(text="☽")
        ctk.set_appearance_mode("light")
    else:
        mode_toggle.configure(text="☼")
        ctk.set_appearance_mode("dark")


window_maximised =  False

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


def maximise_window():
    
    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)

    fullscreen_width = int(root.winfo_screenwidth())
    fullscreen_height = int(root.winfo_screenheight())

    global window_maximised

    if not window_maximised:
        root.geometry(f"{fullscreen_width}x{fullscreen_height}+0+0")
        window_maximised = True
        maximise_button.configure(text="⮺")
        root.update()
    else:
        root.wm_attributes('-type','normal')    
        root.update_idletasks()
        root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+0")
        maximise_button.configure(text="☐")
        root.update_idletasks()
        window_maximised = False

def check_window_state():
    
    if root.state() != "iconic":
        root.overrideredirect(True)  
        root.update_idletasks()
    else:
    
        root.after(300, check_window_state)


def minimise_window():

    if sys.platform.startswith('linux'):
        root.iconify()

    else:
    
        root.update_idletasks()
        root.overrideredirect(False)
        root.state("iconic")
        check_window_state()


drag_data = {"x": 0, "y": 0}

def start_move(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def do_move(event):
    deltax = event.x - drag_data["x"]
    deltay = event.y - drag_data["y"]
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")


resize_data = {"x": 0, "y": 0, "width": 0, "height": 0}

def start_resize(event):
    resize_data["x"] = event.x_root
    resize_data["y"] = event.y_root
    resize_data["width"] = root.winfo_width()
    resize_data["height"] = root.winfo_height()

def do_resize(event):
    delta_x = event.x_root - resize_data["x"]
    delta_y = event.y_root - resize_data["y"]

    # Keep a minimum size of 450x350 so the window doesn't disappear
    new_width = max(450, resize_data["width"] + delta_x)
    new_height = max(350, resize_data["height"] + delta_y)
    root.geometry(f"{new_width}x{new_height}")


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

title_bar = ctk.CTkFrame(master=root,fg_color=("#FAF1CA","#313342"))
title_bar.grid(row=0,column=0,sticky='ew')
title_bar.columnconfigure(0,weight=1)

title_label = ctk.CTkLabel(master=title_bar, text="Julius - Classical cipher tool",font=("Constantine",14,'bold'),fg_color="transparent",text_color=("#7F2122","#F4D03F"))
title_label.grid(row=0,column=0,sticky="ns")

close_button = ctk.CTkButton(master=title_bar, text="X",hover_color=("#5D6D7E","#FAF1CA"),fg_color="transparent",font=("Helvetica",16,"bold"),text_color=("#7F2122","#F4D03F"),width=35,corner_radius=0,command=root.destroy)
close_button.grid(row=0,column=3,sticky="e")

maximise_button = ctk.CTkButton(master=title_bar, text="☐",hover_color=("#5D6D7E","#FAF1CA"),fg_color="transparent",font=("Helvetica",16,"bold"),text_color=("#7F2122","#F4D03F"),width=35,corner_radius=0,command=maximise_window)
maximise_button.grid(row=0,column=2,sticky="e")

minimise_button = ctk.CTkButton(master=title_bar, text="—",hover_color=("#5D6D7E","#FAF1CA"),fg_color="transparent",font=("Helvetica",16,"bold"),text_color=("#7F2122","#F4D03F"),width=35,corner_radius=0,command=minimise_window)
minimise_button.grid(row=0,column=1,sticky="e")


title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)
title_label.bind("<Button-1>", start_move)
title_label.bind("<B1-Motion>", do_move)


close_button.bind("<Enter>", lambda e: close_button.configure(fg_color=("#5D6D7E","#FAF1CA"),text_color=("#F4D03F","#D32929")))
close_button.bind("<Leave>", lambda e: close_button.configure(fg_color='transparent',text_color=("#7F2122","#F4D03F")))
maximise_button.bind("<Enter>", lambda e: maximise_button.configure(fg_color=("#5D6D7E","#FAF1CA"),text_color=("#F4D03F","#D32929")))
maximise_button.bind("<Leave>", lambda e: maximise_button.configure(fg_color='transparent',text_color=("#7F2122","#F4D03F")))
minimise_button.bind("<Enter>", lambda e: minimise_button.configure(fg_color=("#5D6D7E","#FAF1CA"),text_color=("#F4D03F","#D32929")))
minimise_button.bind("<Leave>", lambda e: minimise_button.configure(fg_color='transparent',text_color=("#7F2122","#F4D03F")))

seperator = ttk.Separator(master=root,orient="horizontal")
seperator.grid(row=1,column=0,sticky="ew")

welcome_frame= ctk.CTkFrame(master=root,fg_color=("#FAF1CA","#2B2D42"))





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
resize_grip.bind("<Button-1>", start_resize)
resize_grip.bind("<B1-Motion>", do_resize)

mode_text = "☼" if ctk.get_appearance_mode() == "Dark" else "☽" 

mode_toggle = ctk.CTkButton(master=root,text=mode_text,hover_color=("#5D6D7E","#FAF1CA"),fg_color="transparent",font=("Helvetica",16,"bold"),text_color=("#7F2122","#F4D03F"),width=30,corner_radius=0,command=toggle_mode)
mode_toggle.grid(row=2,column=0 ,sticky="e",padx=8,pady=6)
mode_toggle.bind("<Enter>", lambda e: mode_toggle.configure(fg_color=("#5D6D7E","#FAF1CA"),text_color=("#F4D03F","#FACD1E")))
mode_toggle.bind("<Leave>", lambda e: mode_toggle.configure(fg_color='transparent',text_color=("#7F2122","#F4D03F")))

root.wm_attributes('-type', 'utility')

root.after(4000,root.update)

root.mainloop()
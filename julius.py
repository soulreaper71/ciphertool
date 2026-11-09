import tkinter as tk
from tkinter import ttk
import time

# Theme
BG_COLOUR_LIGHT = "#FFF9D6"
FG_COLOUR_LIGHT = ""
ABG_COLOUR_LIGHT = ""
AFG_COLOUR_LIGHT = ""
BG_COLOUR_DARK = ""
FG_COLOUR_DARK = ""
ABG_COLOUR_DARK = ""
AFG_COLOUR_DARK = ""
TEXT_COLOUR = "#7F2122"

# splash

def splash_animation():
    full_text = "Welcome to Julius..."
    typed_text = ""
    root.overrideredirect(True)

    root_width = 500
    root_height = 300

    root.title("Julius — Classical Cipher De/Encoder")  
    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)
    vertical_pos_root = int(y_root/2-root_height/2)
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
    root.configure(background=BG_COLOUR_LIGHT)
    root.update()

    for char in full_text:
        typed_text += char
        greeting_label.config(text=typed_text,background=root.cget("background"))
        greeting_label.update()
        time.sleep(0.1)



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




root = tk.Tk()

style = ttk.Style()
style.configure("title.TLabel", font=("Praetorium BB",24,'bold'),foreground=TEXT_COLOUR,padx=3,pady=3)
style.map("close_button.TButton",background=[("active","#D32929")],foreground=[("active","#D32929"),([],"#D32929")])

greeting_label = ttk.Label(master=root, style='title.TLabel', background=root.cget("background"))
greeting_label.pack(pady=50)

splash_animation()
greeting_label.destroy()

## TODO: configure dark and light modes using color pallettes in references, add naivgation button

root_width = 500
root_height = 700
    
x_root = root.winfo_screenwidth()
y_root = root.winfo_screenheight()
horizontal_pos_root = int(x_root/2-root_width/2)
vertical_pos_root = int(y_root/2-root_height/2)
root.title("Julius — Classical Cipher De/Encoder")
root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
root.configure(background=BG_COLOUR_LIGHT)
root.columnconfigure(0,weight=1)
root.overrideredirect(False)

title_bar = tk.Frame(master=root,background="white")
title_bar.grid(row=0,column=0,sticky='ew')
title_bar.columnconfigure(0,weight=1)

title_label = ttk.Label(master=title_bar, text="Julius - The En/DeCoder for all Classical cipher",font=("Praetorium BB",14,'bold'),foreground='#7F2122', background=title_bar.cget("background"))
title_label.grid(row=0,column=0,padx=5,sticky="ns")



close_button = tk.Button(master=title_bar, text="X",activebackground="#D32929",activeforeground="white",background=title_bar.cget("background"),relief='flat',foreground=TEXT_COLOUR,font=("Helvetica",10,"bold"),width=4,command=root.destroy)
close_button.grid(row=0,column=1,sticky="e")

title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)
title_label.bind("<Button-1>", start_move)
title_label.bind("<B1-Motion>", do_move)

close_button.bind("<Enter>", lambda e: close_button.config(bg="#D32929"))
close_button.bind("<Leave>", lambda e: close_button.config(bg=title_bar.cget("background")))

seperator = ttk.Separator(master=root)
seperator.grid(row=1,column=0,sticky="ew")

root.overrideredirect(True)
root.after(10, root.focus_force)

welcome_frame = tk.Frame(master=root)
welcome_frame.grid(row=0,column=0)

root.after(4000,root.update)


root.mainloop()
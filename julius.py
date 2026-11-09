import tkinter as tk
from tkinter import ttk
import time


# splash

def splash_animation():
    full_text = "Welcome to Julius..."
    typed_text = ""
    root.overrideredirect(True)

    root_width = 500
    root_height = 300
    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)
    vertical_pos_root = int(y_root/2-root_height/2)
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
    root.configure(background="#FFF9D6")
    root.update()

    for char in full_text:
        typed_text += char
        greeting_label.config(text=typed_text,background=root.cget("background"))
        greeting_label.update()
        time.sleep(0.2)

def maximise_window():
    fullscreen_width = int(root.winfo_screenwidth())
    fullscreen_height = int(root.winfo_screenheight())
    root.geometry(f"{fullscreen_width}x{fullscreen_height}+0+0")
    root.update()

def restore_window():
    root_width = 700
    root_height = 900

    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)
    vertical_pos_root = int(y_root/2-root_height/2)
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")

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
style.configure("title.TLabel", font=("Praetorium BB",24,'bold'),foreground="#7F2122",padx=3,pady=3)

greeting_label = ttk.Label(master=root, style='title.TLabel', background=root.cget("background"))
greeting_label.pack(pady=50)

splash_animation()
greeting_label.destroy()

## TODO: configure dark and light modes using color pallettes in references, add naivgation button
root_width = 700
root_height = 900
    
x_root = root.winfo_screenwidth()
y_root = root.winfo_screenheight()
horizontal_pos_root = int(x_root/2-root_width/2)
vertical_pos_root = int(y_root/2-root_height/2)
root.title("Julius — Classical Cipher De/Encoder")
root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
root.configure(background="#FAF1CA")
root.columnconfigure(0,weight=1)
root.overrideredirect(False)

title_bar = tk.Frame(master=root,background="#FFFBDB")
title_bar.grid(row=0,column=0,sticky='ew')
title_bar.columnconfigure(0,weight=1)

title_label = ttk.Label(master=title_bar, text="Julius - Classical cipher tool",font=("Constantine",14,'bold'),foreground='#7F2122', background=title_bar.cget("background"))
title_label.grid(row=0,column=0,sticky="ns")

close_button = tk.Button(master=title_bar, text="X",activebackground="#D32929",activeforeground="white",background=title_bar.cget("background"),relief='flat',foreground="#7F2122",font=("Helvetica",11,"bold"),width=4,command=root.destroy)
close_button.grid(row=0,column=3,sticky="e")

maximise_button = tk.Button(master=title_bar, text="☐",activeforeground="white",background=title_bar.cget("background"),relief='flat',foreground="#7F2122",font=("Helvetica",11,"bold"),width=4,command=maximise_window)
maximise_button.grid(row=0,column=2,sticky="e")

restore_button = tk.Button(master=title_bar, text="—",activeforeground="white",background=title_bar.cget("background"),relief='flat',foreground="#7F2122",font=("Helvetica",11,"bold"),width=3,command=restore_window)
restore_button.grid(row=0,column=1,sticky="e")

title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)
title_label.bind("<Button-1>", start_move)
title_label.bind("<B1-Motion>", do_move)

close_button.bind("<Enter>", lambda e: close_button.config(bg="#D32929"))
close_button.bind("<Leave>", lambda e: close_button.config(bg=title_bar.cget("background")))
maximise_button.bind("<Enter>", lambda e: maximise_button.config(bg="#5D6D7E"))
maximise_button.bind("<Leave>", lambda e: maximise_button.config(bg=title_bar.cget("background")))
restore_button.bind("<Enter>", lambda e: restore_button.config(bg="#5D6D7E"))
restore_button.bind("<Leave>", lambda e: restore_button.config(bg=title_bar.cget("background")))

seperator = ttk.Separator(master=root)
seperator.grid(row=1,column=0,sticky="ew")

root.overrideredirect(True)
root.after(10, root.focus_force)

welcome_frame = tk.Frame(master=root)
welcome_frame.grid(row=0,column=0)

root.after(4000,root.update)

root.mainloop()
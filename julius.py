import tkinter as tk
from tkinter import ttk
import time
import sys




root = tk.Tk()

root_width = 800
root_height = 1008
    
x_root = root.winfo_screenwidth()
y_root = root.winfo_screenheight()
horizontal_pos_root = int(x_root/2-root_width/2)

# splash
window_maximised =  False

def splash_animation():
    full_text = "Welcome to Julius..."
    typed_text = ""
    root.wm_attributes('-type', 'splash')

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
        maximise_button.config(text="⮺")
        root.update()
    else:
        root.wm_attributes('-type','normal')
        root.update_idletasks()
        root.geometry("")
        root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+0")
        maximise_button.config(text="☐")
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



style = ttk.Style()
style.configure("title.TLabel", font=("Praetorium BB",24,'bold'),foreground="#7F2122",padx=3,pady=3)

greeting_label = ttk.Label(master=root, style='title.TLabel', background=root.cget("background"))
greeting_label.pack(pady=50)

splash_animation()
greeting_label.destroy()

## TODO: configure dark and light modes using color pallettes in references, add naivgation button


root.title("Julius — Classical Cipher De/Encoder")
root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+0")
root.configure(background="#FAF1CA")
root.columnconfigure(0,weight=1)
root.overrideredirect(False)

title_bar = tk.Frame(master=root,background="#FFFBDB")
title_bar.grid(row=0,column=0,sticky='ew')
title_bar.columnconfigure(0,weight=1)

title_label = ttk.Label(master=title_bar, text="Julius - Classical cipher tool",font=("Constantine",14,'bold'),foreground='#7F2122', background=title_bar.cget("background"))
title_label.grid(row=0,column=0,sticky="ns")

close_button = tk.Button(master=title_bar, text="X",activebackground="#D32929",activeforeground="#FACD1E",background=title_bar.cget("background"),relief='flat',foreground="#7F2122",font=("Helvetica",11,"bold"),width=4,command=root.destroy)
close_button.grid(row=0,column=3,sticky="e")

maximise_button = tk.Button(master=title_bar, text="☐",activebackground="#5D6D7E",activeforeground="#D9A05B",background=title_bar.cget("background"),relief='flat',foreground="#7F2122",font=("Praetorium BB",13,"bold"),width=4,command=maximise_window)
maximise_button.grid(row=0,column=2,sticky="e")

minimise_button = tk.Button(master=title_bar, text="—",activebackground="#5D6D7E",activeforeground="#D9A05B",background=title_bar.cget("background"),relief='flat',foreground="#7F2122",font=("Praetorium BB",13,"bold"),width=3,command=minimise_window)
minimise_button.grid(row=0,column=1,sticky="e")



title_bar.bind("<Button-1>", start_move)
title_bar.bind("<B1-Motion>", do_move)
title_label.bind("<Button-1>", start_move)
title_label.bind("<B1-Motion>", do_move)

close_button.bind("<Enter>", lambda e: close_button.config(bg="#D32929",fg="#FACD1E"))
close_button.bind("<Leave>", lambda e: close_button.config(bg=title_bar.cget("background"),fg="#7F2122"))
maximise_button.bind("<Enter>", lambda e: maximise_button.config(bg="#5D6D7E",fg="#D9A05B"))
maximise_button.bind("<Leave>", lambda e: maximise_button.config(bg=title_bar.cget("background"),fg="#7F2122"))
minimise_button.bind("<Enter>", lambda e: minimise_button.config(background="#5D6D7E",foreground="#D9A05B"))
minimise_button.bind("<Leave>", lambda e: minimise_button.config(background=title_bar.cget("background"),foreground="#7F2122"))

seperator = ttk.Separator(master=root)
seperator.grid(row=1,column=0,sticky="ew")

root.wm_attributes('-type', 'utility')

welcome_frame = tk.Frame(master=root)
welcome_frame.grid(row=0,column=0)

root.after(4000,root.update)

root.mainloop()
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

    root.title("Julius — Classical Cipher De/Encoder")
    x_root = root.winfo_screenwidth()
    y_root = root.winfo_screenheight()
    horizontal_pos_root = int(x_root/2-root_width/2)
    vertical_pos_root = int(y_root/2-root_height/2)
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos_root}+{vertical_pos_root}")
    root.configure(background='#FFF5E6')
    root.update()

    for char in full_text:
        typed_text += char
        greeting_label.config(text=typed_text,background=root.cget("background"))
        greeting_label.update()
        time.sleep(0.1)




root = tk.Tk()



style = ttk.Style()
style.configure("title.TLabel", font=("Praetorium BB",24,'bold'),foreground='#7F2122',padx=3,pady=3)

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
root.configure(background='#FFF5E6')
root.overrideredirect(False)


root.after(4000,root.update)


root.mainloop()
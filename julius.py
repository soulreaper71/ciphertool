import tkinter as tk
from tkinter import ttk


# splash

def splash_animation(letter=0):
    full_text = "Welcome to Julius..."

    greeting_label.config(text=full_text[:letter + 1])

    if letter < len(full_text) - 1:
        boot.after(100, splash_animation, letter + 1)

boot = tk.Tk()

boot_width = 400
boot_height = 200

boot.title("Julius — Classical Cipher De/Encoder")
x = boot.winfo_screenwidth()
y = boot.winfo_screenheight()
horizontal_pos = int(x/2-400/2)
vertical_pos = int(y/2-200/2)
boot.geometry(f"{boot_width}x{boot_height}+{horizontal_pos}+{vertical_pos}")
boot.configure(background='#FFF5E6')


style = ttk.Style()
style.configure("title.TLabel", font=("Constantine",20,'bold'),foreground='#7F2122',padx=3,pady=3)

greeting_label = ttk.Label(master=boot, style='title.TLabel', background=boot.cget("background"))

greeting_label.pack(pady=50)

## TODO: Animate loading with greeting_label, configure dark and light modes using color pallettes in references, add naivgation buttons
splash_animation()

def main():
    boot.destroy()

    root = tk.Tk()
    
    root_width = 500
    root_height = 700
    
    x = root.winfo_screenwidth()
    y = root.winfo_screenheight()
    horizontal_pos = int(x/2-500/2)
    vertical_pos = int(y/2-700/2)
    root.title("Julius — Classical Cipher De/Encoder")
    root.geometry(f"{root_width}x{root_height}+{horizontal_pos}+{vertical_pos}")
    root.configure(background='#FFF5E6')


    root.mainloop()

boot.after(3000,main)

boot.mainloop() 
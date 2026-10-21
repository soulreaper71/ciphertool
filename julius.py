import tkinter as tk
from tkinter import ttk


# homepage

window = tk.Tk()

window_width = 400
window_height = 600

window.title("Julius — Classical Cipher De/Encoder")
window.update_idletasks()
x = window.winfo_screenwidth()
y = window.winfo_screenheight()
horizontal_pos = int(x/2-400/2)
vertical_pos = int(y/2-600/2)
window.geometry(f"{window_width}x{window_height}+{horizontal_pos}+{vertical_pos}")
window.rowconfigure(0,weight=1)
window.columnconfigure(0,weight=1)

greeting_label = ttk.Label(master=window, text="Welcome to Julius", font=("Times New Roman",16))
greeting_label.grid(row=0,column=0,padx=0,pady=0,sticky='n')


window.mainloop() 
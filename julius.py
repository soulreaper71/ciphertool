import tkinter as tk
from tkinter import ttk


# homepage

window = tk.Tk()

window_width = 400
window_height = 600

window.title("Julius — Classical Cipher De/Encoder")
x = window.winfo_screenwidth()
y = window.winfo_screenheight()
horizontal_pos = int(x/2-400/2)
vertical_pos = int(y/2-600/2)
window.geometry(f"{window_width}x{window_height}+{horizontal_pos}+{vertical_pos}")
window.rowconfigure(0,weight=1)
window.columnconfigure(0,weight=1)
window.configure(background='#FFF5E6')


style = ttk.Style()
style.configure("title", font=("APOSTROPHIC",24,'bold'),foreground='#7F2122',padx=3,pady=3,)

greeting_label = ttk.Label(master=window, text="Welcome to Julius", style='title',background=window.cget("background"))
greeting_label.place(relx=0.5,rely=0.5,height=40,width=300,anchor=tk.CENTER)


window.mainloop() 
from tkinter import *
from tkinter import filedialog

def open_file():
    filepath = filedialog.askopenfilename()
    with open(filepath, 'rt') as f:
        print(f.read())

window = Tk()
button = Button(text="Open", command = open_file)
button.pack()

window.mainloop()

# nannf
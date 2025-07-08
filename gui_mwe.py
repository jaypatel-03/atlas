import tkinter as tk
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='gui_mwe.log', level=logging.DEBUG)

window = tk.Tk()
window.title("My First GUI")
window.geometry("400x300")

label = tk.Label(window, text='Hello!')  # again 'label' is just a name
logging.debug(f"Label created with text: {label['text']}")


# 'pack()' is a 'geometry manager'; it tells our app to put this widget on the window
label.pack()

window.mainloop()

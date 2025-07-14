import subprocess
import tkinter as tk
import logging

# subprocess.run(["ls", "-l"])

logger = logging.getLogger(__name__)
logging.basicConfig(filename='gui_mwe.log', level=logging.DEBUG)

w = tk.Tk()
w.title("My First GUI")
w.geometry("400x300")
'''
label = tk.Label(w, text='Hello!')  # again 'label' is just a name
logging.debug(f"Label created with text: {label['text']}")
# 'pack()' is a 'geometry manager'; it tells our app to put this widget on the window
label.pack()
'''
def button_clicked():
    subprocess.run(["echo", "Hello, World!"])
    
tk.Label(w, text="Text").grid(row=0)
tk.Button(w, text="Stop", width = 25, command=button_clicked).grid(row=1)

# command = w.destroy without () as otherwise it runs the command

# btn.pack()
# , command=w.destroy()



w.mainloop()





class windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Adding a title to the window
        self.wm_title("Test Application")

        # creating a frame and assigning it to container
        container = tk.Frame(self, height=400, width=600)
        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames themselves later but let's add the components to the dictionary.
        for F in (MainPage, SidePage, CompletionScreen):
            frame = F(container, self)

            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.show_frame(MainPage)
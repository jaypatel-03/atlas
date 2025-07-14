import subprocess
try:
    import tkinter as tk # Python 3.x
    from tkinter import messagebox
except ImportError:
    import Tkinter as tk # Python 2.x
    from Tkinter import messagebox
import logging
import re # RegEx support


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(filename=f'as.log', level=logging.DEBUG)

class LoadModuleInfo(tk.Tk):
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self,*args,**kwargs)
        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)
        # w.title("Module Info")
        
        self.frames = {}
        
        frame = InputScreen(window,self)
        self.frames[InputScreen] = frame
        frame.grid(row=0, column=0, sticky="nswe")
        self.show_frame(InputScreen)  # Shows the input screen 
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

class InputScreen(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent) # inherits from main class
        
        # TODO: decide whether to keep default values 
        tk.Label(self, text="Module Serial Number \n (e.g. 20UPGM22110039) ").grid(row=0)
        e_mod_sn = tk.Entry(self, bg='white', fg='grey')
        e_mod_sn.grid(row=0, column=1)

        # e_mod_sn.insert(0, "GM2320017")
        e_mod_sn.bind("<FocusIn>", self.__handle_focus_in, add="+")         # Delete default text on click
        
        tk.Label(self, text="Local Serial Number \n (e.g. OX0006)").grid(row=1)
        e_local_sn = tk.Entry(self, bg='white', fg='grey')
        # e_local_sn.insert(0, "OX0006")
        e_local_sn.bind("<FocusIn>", self.__handle_focus_in, add="+")         # Delete default text on click
        e_local_sn.grid(row=1, column=1)

        # TODO: insert link (on hover?) to how to look up/assign local serial number
        
        # Radio buttons to select version
        versions = ["v1.1", "v2"]
        lbl_version = tk.Label(self, text=f"Version:")
        lbl_version.grid(row=2, rowspan=2, column=0)
        version = tk.StringVar(self, f"{versions[0]}")
        r = 0
        for v in versions:
            tk.Radiobutton(self, text=v, variable=version, value=v).grid(row=2 + r, column=1)# TODO: command 
            r += 1
        
        # Radio buttons to select warm or cold test     
        temps = ["Warm test", "Cold test"]
        lbl_temp = tk.Label(self, text=f"Temperature:")
        lbl_temp.grid(row=5, rowspan=2, column=0)
        temp = tk.StringVar(self, f"{temps[0][0:4].lower()}")
        r = 0
        for t in temps:
            tk.Radiobutton(self, text=t, variable=temp, value=t[0:4].lower()).grid(row=5 + r, column=1)# TODO: command 
            r += 1

        # Validate serial numbers and generate config files
        tk.Button(self, text="Load", width = 25, command=lambda : self.validate_module_info(e_mod_sn.get(),e_local_sn.get(),version.get())).grid(row=15)

    
    def __handle_focus_in(self,event=None):
        # event.widget.delete(0, tk.END)
        event.widget.config(fg='black')
        
    def validate_module_info(self, mod_sn : str, local_sn : str, version : str) -> bool:
        '''Validates module info entered and downloads config files from database if successful
        
        Args:
            mod_sn : String containing the global module serial number
            local_sn : String containing the local (Oxford) module serial number
        Returns:
            int : Success (0) or failure (1) code. 
        '''
        logging.debug("Load button pressed")
        logging.debug(f"{version=}")
        flag = False
        if re.search(r"^OX[0-9]{4}$", local_sn) is None:
            logging.info(f"Invalid local serial number {local_sn}, should be of the form OX####") # ^___$ are anchors to force exact matches
            messagebox.askretrycancel("askretrycancel", f"Invalid local serial number {local_sn}, should be of the form OX####")
        elif re.search(r"^20UPGM2[0-9]{7}$", mod_sn) is None:
            logging.info(f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########")
            messagebox.askretrycancel("askretrycancel", f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########")
        elif re.search(r"^20UPGM2321[0-9]{4}$", mod_sn) is not None and version == "v1.1":
            logging.info("Module serial number suggests this may be a v2 module.")
            flag = messagebox.askokcancel("askokcancel","Module serial number suggests this may be a v2 module.")
        elif re.search(r"^20UPGM2211[0-9]{4}$", mod_sn) is not None and version == "v2":
            logging.info("Module serial number suggests this may be a v1.1 module.")
            flag = messagebox.askokcancel("askokcancel","Module serial number suggests this may be a v1.1 module.")
        else:
            flag = True
        if flag:
            subprocess.run(["echo" ,"cd", "Module_QC/module-qc-database-tools"])
            subprocess.run(["echo", "mqdbt", "generate-yarr-config", "-sn", mod_sn, "-o", local_sn])
            subprocess.run(["echo", "cd", "../Yarr"])
        return True

    

if __name__ == "__main__":
    l = LoadModuleInfo()
    l.mainloop()
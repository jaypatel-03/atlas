import subprocess
import tkinter as tk
from tkinter import messagebox
import logging
import re # RegEx support
from module_test_data import ModuleTestData


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class LoadModuleInfo(tk.Tk):
    def __init__(self, mod_data : ModuleTestData, *args, **kwargs):
       
        tk.Tk.__init__(self, *args,**kwargs)
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
        
        tk.Label(self, text="Module Serial Number \n (e.g. 20UPGM22110039) ").grid(row=0)
        e_mod_sn = tk.Entry(self, bg='white', fg='black')
        e_mod_sn.grid(row=0, column=1)
        

        tk.Label(self, text="Local ID \n (e.g. OX0006)").grid(row=1)
        e_local_id = tk.Entry(self, bg='white', fg='black')
        e_local_id.grid(row=1, column=1)

        # TODO: insert link (on hover?) to how to look up/assign local serial number
        
        # Radio buttons to select version
        versions = ["v1.1", "v2"]
        lbl_version = tk.Label(self, text=f"Version:")
        lbl_version.grid(row=2, rowspan=2, column=0)
        
        self.version = tk.StringVar(self, f"{versions[0]}")
        r = 0
        for v in versions:
            tk.Radiobutton(self, text=v, variable=self.version, value=v).grid(row=2 + r, column=1)# TODO: command 
            r += 1
        
        # Radio buttons to select warm or cold test     
        temps = ["Warm test", "Cold test"]
        lbl_temp = tk.Label(self, text=f"Temperature:")
        lbl_temp.grid(row=5, rowspan=2, column=0)
        
        self.temp = tk.StringVar(self, f"{temps[0][0:4].lower()}")
        r = 0
        for t in temps:
            tk.Radiobutton(self, text=t, variable=self.temp, value=t[0:4].lower(), command = lambda : self.select_test_temp(mod_data)).grid(row=5 + r, column=1) 
            r += 1

        # Validate serial numbers and generate config files
        tk.Button(self, text="Load", width = 25, command = lambda : self.validate_module_info(mod_data, e_mod_sn.get().strip(),e_local_id.get().strip(),self.version.get())).grid(row=15)
        
        tk.Button(self, text="Yield", width = 25, command = lambda : print(vars(mod_data))).grid(row=15, column=2)

    
    def select_test_temp(self,mod_data : ModuleTestData) -> None:
        logging.debug(f"{self.temp.get()=}")
        mod_data.temp = self.temp.get()
        
    def validate_module_info(self,mod_data : ModuleTestData, mod_sn : str, local_id : str, version : str) -> None:
        '''Validates module info entered and downloads config files from database if successful
        
        Args:
            mod_sn : String containing the global module serial number
            local_sn : String containing the local (Oxford) module identifier
        Returns:
            int : Success (0) or failure (1) code. 
        '''
        logging.debug("Load button pressed")
        logging.debug(f"{version=}")
        
        msg : str
        flag = True
        if re.search(r"^OX[0-9]{4}$", local_id) is None:
            msg = f"Invalid local ID {local_id}, should be of the form OX####" # ^___$ are anchors to force exact matches
            logging.info(msg) 
            messagebox.askretrycancel("askretrycancel", msg)
            
        elif re.search(r"^20UPGM2[0-9]{7}$", mod_sn) is None:
            logging.info(f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########")
            messagebox.askretrycancel("askretrycancel", f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########.")
            
        elif re.search(r"^20UPGM2321[0-9]{4}$", mod_sn) is not None and version == "v1.1":
            logging.info("Module serial number suggests this may be a v2 module.")
            flag = messagebox.askyesno("yesno","Module serial number suggests this may be a v2 module. Continue anyway?")
            
        elif re.search(r"^20UPGM2211[0-9]{4}$", mod_sn) is not None and version == "v2":
            logging.info("Module serial number suggests this may be a v1.1 module.")
            flag = messagebox.askyesno("askyesno","Module serial number suggests this may be a v1.1 module.Continue anyway?")
        else:
            flag = True
            
        if flag:   
            subprocess.run(["echo" ,"cd", "Module_QC/module-qc-database-tools"])
            subprocess.run(["echo", "mqdbt", "generate-yarr-config", "-sn", mod_sn, "-o", local_id])
            subprocess.run(["echo", "cd", "../Yarr"])
            mod_data.loc_id = local_id
            mod_data.mod_sn = mod_sn
            mod_data.version = version

    
if __name__ == "__main__":
    mod_data = ModuleTestData()
    l = LoadModuleInfo(mod_data)
    l.mainloop()
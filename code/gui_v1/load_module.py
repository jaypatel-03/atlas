import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from module_test_data import ModuleTestData
from test_block import TestBlock
import re # RegEx support
# from module_loading_screen import InputScreen
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TestSuite(tk.Tk):
    def __init__(self, mod_data : ModuleTestData, *args, **kwargs):
       
        tk.Tk.__init__(self, *args,**kwargs)
        self.title("ATLAS Module Testing - Test Suite")
        # Creating Menubar
        menubar = tk.Menu(self)

        # Adding File Menu and commands
        file = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label ='File', menu = file)
        file.add_command(label ='New Test', command = None)
        file.add_command(label ='Save', command = None)
        file.add_separator()
       
        self.config(menu=menubar)
       
        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)
        
        
        self.frames = {}
        c=0
        for F in [PrelimTests, MinHealthTests, Tuning, PixelFailTests]:
            frame = F(window, self, mod_data)
            self.frames[F] = frame
            frame.grid(row=c, column=0, sticky="nswe")
            c+=1
            self.show_frame(F)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()


class LoadModuleInfo(tk.Tk):
    def __init__(self, mod_data : ModuleTestData, *args, **kwargs):
       
        tk.Tk.__init__(self, *args,**kwargs)
        self.title("ATLAS Module Testing - Module Loader")

       
        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)
        
        
        self.frames = {}
        frame = InputScreen(window,self)
        self.frames[InputScreen] = frame
        frame.grid(row=0, column=0, sticky="nswe")
        self.show_frame(InputScreen)  # Shows the input screen
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

     
class PrelimTests(TestBlock):
    test_name = "Preliminary Tests"
    
    def __init__(self,parent,controller, mod_data):
        super().__init__(parent, controller, mod_data)
        tk.Button(self, text="Display eye diagram", command=lambda : self.plot_eye_diagram(parent)).grid(row=1, column=2)

    def get_test_list(self, mod_data : ModuleTestData):
        # TODO: add temperature check
        if mod_data.stage == "post":
            return ['eyeDiagram', 'IV-MEASURE', 'corecolumnscan']
        elif mod_data.stage == "final_cold":
            return ['eyeDiagram', 'IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'DATA-TRANSMISSION', 'corecolumnscan']
        return ['eyeDiagram', 'IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'LP-MODE', 'DATA-TRANSMISSION', 'corecolumnscan']
    
    def plot_eye_diagram(self, master, file : str = r"/home/jayp/atlas/code/gui_v1/logs/eyeDiagram.log" ): 
        #TODO modify with pwd?
        data = []
        try:
            with open(file) as f:
                lines = f.readline()
                while not lines.__contains__("0 | "):
                    lines = f.readline()
                for i in range(32):
                    line = lines.replace('\n', '')
                    parts = [x.strip() for x in line.split('|')]
                    row = [float(val) for val in parts[1:-1]]
                    data.append(row)
                    lines = f.readline()
            self.open_eyediagram_popup(master, data)
            
        except FileNotFoundError as e:
            logging.info(f"{e}: Run eye diagram first")
    
    def open_eyediagram_popup(self, master, data : list):
        # TODO: incorporate into plot_eye_diagram?
        top = tk.Toplevel(master)
        top.geometry("300x500")
        top.title("eyeDiagram")
        
        fig = plt.Figure(figsize=(5,5), dpi=100)
        plot1 = fig.add_subplot(111)
        plot1.imshow(data, cmap='winter')
        plot1.set_ylabel("Channel")
        plot1.set_xlabel("Lane")
        
        canvas = FigureCanvasTkAgg(fig, master = top)
        canvas.draw()
        canvas.get_tk_widget().pack()
        # TODO: add option to disable chip

class MinHealthTests(TestBlock):
    test_name = "Mininum Health Tests"   
    def get_test_list(self, mod_data):
        return ["std_digitalscan", "std_analogscan", "std_thresholdscan_hr", "std_totscan -t 6000"]

class Tuning(TestBlock):
    test_name = "Tuning"
    def get_test_list(self, mod_data):
        _, _, _, version, _ = self.check_mod_data_loaded(mod_data)
        return ["std_tune_globalthreshold -t 1700", "std_tune_globalpreamp -t 6000 7", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"] if version == "v2" else ["std_tune_globalthreshold -t 1700", "std_totscan -t 6000", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_retune_globalthreshold -t 1700", "std_retune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"]

class PixelFailTests(TestBlock):
    test_name = "Pixel Fail"
    def get_test_list(self, mod_data):
        if mod_data.stage == "final_cold":
            return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan", "selftrigger_source -p", "selftrigger_source"]
        return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan"]
            
class InputScreen(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent) # inherits from main class
        
        # Input module serial numbers and Oxford ID
        tk.Label(self, text="Module Serial Number \n (e.g. 20UPGM22110039) ").grid(row=0)
        e_mod_sn = tk.Entry(self, bg='white', fg='black')
        e_mod_sn.insert(0,"20UPGM22110038")
        e_mod_sn.grid(row=0, column=1)
        

        tk.Label(self, text="Local ID \n (e.g. OX0006)").grid(row=1)
        e_local_id = tk.Entry(self, bg='white', fg='black')
        e_local_id.insert(0, "OX0001")
        e_local_id.grid(row=1, column=1)

        # TODO: insert link (on hover?) to how to look up/assign local serial number
        
        # Radio buttons to select version
        versions = ["v1.1", "v2"]
        lbl_version = tk.Label(self, text=f"Version:")
        lbl_version.grid(row=2, rowspan=2, column=0)
        
        self.version = tk.StringVar(self, f"{versions[0]}")
        r = 0
        for v in versions:
            tk.Radiobutton(self, text=v, variable=self.version, value=v, command = lambda : self.set_mod_data("version",self.version.get(), mod_data)).grid(row=2 + r, column=1) 
            r += 1
        
        # Radio buttons to select warm or cold test     
        stages = {"Initial (warm)" : "init", "Post-Parylene (warm)" : "post", "Final (warm)" : "final_warm", "Final (cold)" : "final_cold"}
        lbl_stage = tk.Label(self, text=f"Testing Stage \n (selects relevant tests):")
        lbl_stage.grid(row=5, column=0, rowspan=5)
        
        self.stage = tk.StringVar(self, f"{stages['Initial (warm)']}")
        r = 0
        for t in stages.keys():
            tk.Radiobutton(self, text=t, variable=self.stage, value=stages[t], command = lambda : self.set_mod_data("stage",self.stage.get(),mod_data)).grid(row=5 + r, column=1) 
            r += 1
        
        # Boolean flag from checkbox as to whether to overwrite existing config files 
        check_overwrite_config_flag = tk.BooleanVar()
        check_config = tk.Checkbutton(self, text="Overwrite configs?", variable=check_overwrite_config_flag, onvalue=True, offvalue=False).grid(row=r+6,column=1)
        
        tk.Label(self, text="Module_QC directory \n (typically ~/Module_QC)").grid(row=0, column=2)
        e_home_path = tk.Entry(self)
        # e_home_path.insert(0,"~/Module_QC") TODO: change back
        e_home_path.insert(0,"/home/jayp/atlas")
        e_home_path.grid(row=0, column=3)
        

        # Validate serial numbers and generate config files
        tk.Button(self, text="Load & generate configs", width = 25, command = lambda : self.validate_module_info(controller, mod_data, e_mod_sn.get().strip(),e_local_id.get().strip(),self.version.get(), check_overwrite_config_flag.get(), e_home_path.get().strip())).grid(row=15)
        
        
        tk.Button(self, text="Yield", width = 25, command = lambda : print(vars(mod_data))).grid(row=15, column=2)

    
    def set_mod_data(self, attr : str, value : str, mod_data : ModuleTestData):
        logging.info(f"Set {attr} to {value}")
        if not hasattr(mod_data, attr):
            raise AttributeError(f"{mod_data!r} has no attribute {attr!r}")
        setattr(mod_data, attr, value)
    
        
    def validate_module_info(self,master, mod_data : ModuleTestData, mod_sn : str, local_id : str, version : str, overwrite_config : bool, home_path : str) -> None:
        '''Validates module info entered and downloads config files from database if successful
        
        Args:
            mod_sn : String containing the global module serial number
            local_sn : String containing the local (Oxford) module identifier
        Returns:
            None : if attempting to unintentionally rewrite config files 
        '''
        logging.info("Load button pressed")
        
        if home_path == "":
            home_path = mod_data.home_path
        elif home_path.endswith('/'):
            home_path = home_path[0:-2]
        
        self.set_mod_data("home_path", home_path, mod_data)
        
        msg : str
        flag = True
        if re.search(r"^OX[0-9]{4}$", local_id) is None:
            msg = f"Invalid local ID {local_id}, should be of the form OX####" # ^___$ are anchors to force exact matches
            logging.info(msg) 
            messagebox.askretrycancel("askretrycancel", msg)
            return
        elif re.search(r"^20UPGM2[0-9]{7}$", mod_sn) is None:
            logging.info(f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########")
            messagebox.askretrycancel("askretrycancel", f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########.")
            return 
        elif (re.search(r"^20UPGM2321[0-9]{4}$", mod_sn) is not None or re.search(r"^20UPGM2421[0-9]{4}$", mod_sn) is not None ) and version == "v1.1":
            logging.info("Module serial number suggests this may be a v2 module.")
            flag = messagebox.askyesno("yesno","Module serial number suggests this may be a v2 module. Continue anyway?")
            
        elif re.search(r"^20UPGM2211[0-9]{4}$", mod_sn) is not None and version == "v2":
            logging.info("Module serial number suggests this may be a v1.1 module.")
            flag = messagebox.askyesno("askyesno","Module serial number suggests this may be a v1.1 module.Continue anyway?")
               
        else:
            flag = True
            
        if flag:
            logging.info("Module info looks reasonable.")
            mod_data.loc_id = local_id
            mod_data.mod_sn = mod_sn
            mod_data.version = version
            tk.Label(self, text=f"Module {local_id} loaded at {datetime.now().strftime('%H:%M:%S')}", fg='green').grid(row=16, column=0)
            
            # Test whether the config files exist and will be unwittingly overwritten
            if not overwrite_config and os.path.isdir(f"{home_path}/module-qc-database-tools/{local_id}"):
                messagebox.showerror("showerror", "Config files already exist, decide whether to overwrite or not.")
                return 
            subprocess.run(["echo" ,"cd", f"{mod_data.home_path}/module-qc-database-tools"])
            subprocess.run(["echo", "mqdbt", "generate-yarr-config", "-sn", mod_sn, "-o", local_id])
            subprocess.run(["echo", "cd", mod_data.home_path])
            master.destroy()    


def new_module(mod_data : ModuleTestData):
    win = LoadModuleInfo(mod_data)
    win.mainloop()
    win = TestSuite(mod_data)
    win.mainloop()
    
if __name__ == "__main__":
    mod_data = ModuleTestData()
    new_module(mod_data)
    # l = TestSuite(mod_data)
    # l.mainloop()
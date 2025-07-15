import subprocess
import tkinter as tk
from tkinter import messagebox
import logging
import re # RegEx support
from module_test_data import ModuleTestData
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
        
        frame = TestScreen(window,self)
        self.frames[TestScreen] = frame
        frame.grid(row=0, column=1, sticky="nswe")
        self.show_frame(TestScreen)  # Shows the input screen 
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

class TestScreen(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self,text="0. eyeDiagram").grid(row=0)
        btn_eye = tk.Button(self, text="Run eye diagram", command=lambda : self._run_eye_diagram(btn_eye, mod_data))
        btn_eye.grid(row=0, column=1)
        tk.Button(self, text="Display eye diagram", command=lambda : self.plot_eye_diagram(parent)).grid(row=0, column=2)

        
        qc_tests = ['IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'LP-MODE', 'DATA-TRANSMISSION']
        qc_test_buttons = []
        r = 0
        for test in qc_tests:
            tk.Label(self, text=f"{r + 1}. {test}").grid(row=r + 1)
            quick_btn = tk.Button(self, text=f"Run {test}", command=lambda r=r: self._run_qc_test(qc_test_buttons[r],qc_tests[r], mod_data))
            qc_test_buttons.append(quick_btn)
            quick_btn.grid(row=r + 1, column=1)
            r += 1
        print(qc_test_buttons)

    def _run_eye_diagram(self, button : tk.Button, mod_data : ModuleTestData):
        # TODO: add comment
        eye_diagram_template = "bin/eyeDiagram -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
        
        loc_id, mod_sn,temp, _ = self._check_mod_data_loaded(mod_data)
        cmd = eye_diagram_template.format(loc_id=loc_id, mod_sn=mod_sn, temp=temp)
        if loc_id is not None:
            logging.info("Run eyeDiagram")
            subprocess.run(['echo', cmd, "> /home/jayp/atlas/code/gui_v1/logs/eyeDiagram.log"]) # TODO: change save location
            button.configure(bg="green")
            
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
        
    def _run_qc_test(self, button : tk.Button, test : str, mod_data : ModuleTestData):
        loc_id, mod_sn,temp, version = self._check_mod_data_loaded(mod_data)
        
        if loc_id is not None:
            qc_tool_template = "measurement-{test} -c ../configs/new_hw_config_{version}.json -m ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
            
            logging.info(f"Run {test}")
            cmd = qc_tool_template.format(loc_id=loc_id, mod_sn=mod_sn, temp=temp, test=test, version=version)
            
            subprocess.run(['echo', cmd])
            button.configure(bg="green")
        
   
    def _run_tuning_test(self, test : str, mod_data : ModuleTestData):
        yarr_template = "bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/rd53b/{test} -Wh"
        
        tuning_v1 = ["std_tune_globalthreshold -t 1700", "std_totscan -t 6000", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_retune_globalthreshold -t 1700", "std_retune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"]

        tuning_v2 = ["std_tune_globalthreshold -t 1700", "std_tune_globalpreamp -t 6000 7", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"]
        
        if test == "std_thresholdscan_zerobias":
            print("Ramp down Keithley HV")
        elif test == "std_noisescan":
            print("HV:")
            # test if hv is biased 
            # ramp back to -120 if not
        
    def _check_mod_data_loaded(self, mod_data : ModuleTestData) -> tuple[str, str, str, str] | None:
        '''Tests whether all the module testing properties have been loaded
        
        Args:
            mod_data : Module test data
        Returns:
            mod_data.loc_id, mod_data.mod_sn,mod_data.temp, mod_data.version | None, None, None, None 
        
        '''
        try:
            return mod_data.loc_id, mod_data.mod_sn,mod_data.temp, mod_data.version
        except AttributeError:
            messagebox.showerror("showerror", "Module info has not been loaded correctly, try load again.")
            return None, None, None, None

class InputScreen(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent) # inherits from main class
        
        tk.Label(self, text="Module Serial Number \n (e.g. 20UPGM22110039) ").grid(row=0)
        e_mod_sn = tk.Entry(self, bg='white', fg='black')
        e_mod_sn.insert(0,"20UPGM22110038")
        e_mod_sn.grid(row=0, column=1)
        

        tk.Label(self, text="Local ID \n (e.g. OX0006)").grid(row=1)
        e_local_id = tk.Entry(self, bg='white', fg='black')
        e_local_id.insert(0, "OX0001")
        e_local_id.grid(row=1, column=1)

        # TODO: insert link (on hover?) to how to look up/assign local serial number
        
        # Radio qc_test_buttons to select version
        versions = ["v1.1", "v2"]
        lbl_version = tk.Label(self, text=f"Version:")
        lbl_version.grid(row=2, rowspan=2, column=0)
        
        self.version = tk.StringVar(self, f"{versions[0]}")
        r = 0
        for v in versions:
            tk.Radiobutton(self, text=v, variable=self.version, value=v).grid(row=2 + r, column=1) 
            r += 1
        
        # Radio qc_test_buttons to select warm or cold test     
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
        
        # tk.Button(self, text="Yield", width = 25, command = lambda : print(vars(mod_data))).grid(row=15, column=2)

    
    def select_test_temp(self,mod_data : ModuleTestData) -> None:
        '''Selects whether it is a warm or cold test and saves the info to the ModuleTestData object.
        '''
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
        logging.info("Load button pressed")
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
            tk.Label(self, text=f"Module {local_id} loaded at {datetime.now().strftime('%H:%M:%S')}", fg='green').grid(row=15, column=1)
            # TODO: add existence/overwrite check for config files   
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
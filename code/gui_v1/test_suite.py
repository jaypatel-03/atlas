from test_interface import TestInterface 
from module_test_data import ModuleTestData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
import json
import logging

class PrelimTests(TestInterface):
    test_name = "Preliminary Tests"
    
    def __init__(self,parent,controller, mod_data):
        super().__init__(parent, controller, mod_data)
        tk.Button(self, text="View", command=lambda : self.plot_eye_diagram(parent, mod_data)).grid(row=1, column=2)

    def get_test_list(self, mod_data : ModuleTestData):
        if mod_data.stage == "post":
            return ['eyeDiagram', 'IV-MEASURE', 'corecolumnscan']
        elif mod_data.stage == "final_cold":
            return ['eyeDiagram', 'IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'DATA-TRANSMISSION', 'corecolumnscan']
        return ['eyeDiagram', 'IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'LP-MODE', 'DATA-TRANSMISSION', 'corecolumnscan']
    
    def plot_eye_diagram(self, master, mod_data : ModuleTestData, file : str = r"./logs/eyeDiagram.log"): 
        logging.debug("Plotting eyeDiagram")
        data = []
        delay = []
        # ANSI escape sequence (\x1b[) + Select Graphic Rendition subset for colours (32 = green, 0 = black). Adds colour to eyeDiagram output
        green = r'\x1b[32m'
        black = r'\x1b[0m'
        try:
            with open(file) as f:
                lines = f.readline()
                logging.debug("Reading line")
                while "0 | " not in lines:
                    lines = f.readline()
                for _ in range(32):
                    line = lines.encode('unicode_escape').decode() # remove weird encoding and convert to bash string
                    line = line.replace(green, '').replace(black, '')
                    line = line.replace('\n', '')
                    print(line)
                    parts = [x.strip() for x in line.split('|')]
                    row = [float(val) for val in parts[1:-1]]
                    data.append(row)
                    lines = f.readline()
                while not "Determining" in lines:
                    lines = f.readline()
                for _ in range(16):
                    lines = f.readline()
                    delay.append("green" if "width" in lines else "red")
                self.open_eyediagram_popup(master, data, delay, mod_data)
            
        except FileNotFoundError as e:
            logging.info(f"{e}: Run eye diagram first")
    
    def open_eyediagram_popup(self, master, data : list, delay : list, mod_data : ModuleTestData):
        # TODO: incorporate into plot_eye_diagram?
        top = tk.Toplevel(master)
        top.transient(master)
        top.title("eyeDiagram")
        
        fig = plt.Figure(figsize=(5,5), dpi=100)
        plot1 = fig.add_subplot(111)
        plot1.imshow(data, cmap='winter')
        plot1.set_ylabel("Channel")
        plot1.set_xlabel("Lane")
        
        canvas = FigureCanvasTkAgg(fig, master = top)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0)
        
        enabled = self.chip_enabled(mod_data)
        i = 0
        for d in delay:
            tk.Label(top, text= f"{i}. " + ("Delay found" if d == "green" else "Delay not found"), fg=d).grid(row=i+1)
            i += 1
        
        i = 0
        self.checkbox_flags = []
        self.checkbox = []
        for a in enabled:
            self.checkbox_flags.append(tk.IntVar(value=a))
            self.chk = tk.Checkbutton(top, text=f"Chip {i+1}", variable=self.checkbox_flags[i], onvalue=True, offvalue=False)
            self.chk.grid(row=i+1, column=1)
            self.checkbox.append(self.chk)
            if bool(a):
                self.chk.select()
            i += 1
        logging.debug(f"{self.checkbox_flags=}")
        ok_btn =tk.Button(top, text="OK",command = lambda : self.disable_chips(top,mod_data, [s.get() for s in self.checkbox_flags])).grid(row=18, columnspan=2)
    
    def chip_enabled(self, mod_data : ModuleTestData) -> list:
        loc_id, mod_sn, temp, _ = self.check_mod_data_loaded(mod_data)
        enabled = []
        home_path = mod_data.home_path
        file = f"{home_path}/module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
        
        
        with open(file, "r") as jsonfile:
            data = json.load(jsonfile)
            logging.info("Read successful")
        for a in range(4):
            logging.debug(f"Chip {a} enabled: {data['chips'][a]['enable']} ")
            enabled.append((int(data['chips'][a]['enable'])))
        return enabled
    
    def disable_chips(self, master, mod_data : ModuleTestData, chk_boxes : list):
        loc_id, mod_sn, temp, _ = self.check_mod_data_loaded(mod_data)
        home_path = mod_data.home_path
        file = f"{home_path}/module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
        with open(file, "r") as jsonfile:
            data = json.load(jsonfile)
        data_edited = data # to preserve original data in case of RW error    
        with open(file, "w") as jsonfile:
            for a in range(4):
                data_edited['chips'][a]['enable'] = chk_boxes[a]
            try:
                json.dump(data_edited, jsonfile, indent=2)
            except:
                logging.critical("JSON RW error : unable to save new config")
                messagebox.showerror("showerror", "JSON RW error : unable to save new config")
                json.dump(data, jsonfile, indent=2)
                    
            logging.info("Config edited")   
        master.destroy()

class MinHealthTests(TestInterface):
    test_name = "Mininum Health Tests"   
    def get_test_list(self, mod_data):
        return ["std_digitalscan", "std_analogscan", "std_thresholdscan_hr", "std_totscan -t 6000"]

class Tuning(TestInterface):
    test_name = "Tuning"
    def get_test_list(self, mod_data):
        _, _, _, version = self.check_mod_data_loaded(mod_data)
        return ["std_tune_globalthreshold -t 1700", "std_tune_globalpreamp -t 6000 7", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"] if version == "v2" else ["std_tune_globalthreshold -t 1700", "std_totscan -t 6000", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_retune_globalthreshold -t 1700", "std_retune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"]

class PixelFailTests(TestInterface):
    test_name = "Pixel Fail"
    def get_test_list(self, mod_data):
        if mod_data.stage == "final_cold":
            return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan", "selftrigger_source -p", "selftrigger_source"]
        return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan"]

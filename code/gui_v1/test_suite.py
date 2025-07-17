from test_interface import TestInterface 
from module_test_data import ModuleTestData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk 
import json
import logging

class PrelimTests(TestInterface):
    test_name = "Preliminary Tests"
    
    def __init__(self,parent,controller, mod_data):
        super().__init__(parent, controller, mod_data)
        tk.Button(self, text="View", command=lambda : self.plot_eye_diagram(parent)).grid(row=1, column=2)
        tk.Button(self, text="View", command=lambda : self.chip_delays(parent,mod_data)).grid(row=1, column=2)

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
        top.transient(master)
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
    
    def chip_delays(self, master, mod_data : ModuleTestData):
        loc_id, mod_sn, temp, _, home_path = self.check_mod_data_loaded(mod_data)
        file = f"{home_path}/module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
        print(file)
        with open(file, "r") as jsonfile:
            data = json.load(jsonfile)
            logger.info("Read successful")
        print(f"{data!r}")    

class MinHealthTests(TestInterface):
    test_name = "Mininum Health Tests"   
    def get_test_list(self, mod_data):
        return ["std_digitalscan", "std_analogscan", "std_thresholdscan_hr", "std_totscan -t 6000"]

class Tuning(TestInterface):
    test_name = "Tuning"
    def get_test_list(self, mod_data):
        _, _, _, version, _ = self.check_mod_data_loaded(mod_data)
        return ["std_tune_globalthreshold -t 1700", "std_tune_globalpreamp -t 6000 7", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"] if version == "v2" else ["std_tune_globalthreshold -t 1700", "std_totscan -t 6000", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_retune_globalthreshold -t 1700", "std_retune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"]

class PixelFailTests(TestInterface):
    test_name = "Pixel Fail"
    def get_test_list(self, mod_data):
        if mod_data.stage == "final_cold":
            return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan", "selftrigger_source -p", "selftrigger_source"]
        return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan"]

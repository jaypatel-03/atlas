from gui.test_interface import TestInterface 
from gui.module_test_data import ModuleTestData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
import json
import logging

class EyeDiagram(TestInterface):
    test_name = "Communication"
    
    def __init__(self, parent, controller, mod_data):
        super().__init__(parent, controller, mod_data)
        tk.Label(self, text="2.").grid(row=2, column=0)
        tk.Button(self, text="View", command=lambda : self.sanitise_plot_eye_diagram(parent, mod_data)).grid(row=2, column=1)
    
    def get_test_list(self, mod_data : ModuleTestData):
        
        return ["eyeDiagram"]
    
    def gen_cmd(self, mod_data : ModuleTestData):
        return "{echo}cd {home_path}/Yarr ; {echo}bin/eyeDiagram -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json" if mod_data.dry_run else "{echo}cd {home_path}/Yarr ; {echo}bin/eyeDiagram -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json > {pwd}/gui/logs/eyeDiagram.log" # if statement removes pipe output for dry runs
        
    
    def sanitise_plot_eye_diagram(self, master, mod_data : ModuleTestData, file : str = r"./gui/logs/eyeDiagram.log"): 
        """Reads and sanitises the shell output of the eyeDiagram script. Removes new line breaks, removes pipe delimiter, and removes shell colour information. 
        
        Args:
            master: controlling tk.Frame to pass through to other functions 
            mod_data
            file (str): path to eyeDiagram.log. Default is ./logs/eyeDiagram.log
        
        """
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
    
    def open_eyediagram_popup(self, master, eye_diag : list[int], delay : list[bool], mod_data : ModuleTestData):
        """Plots the heatmap for the eyeDiagram, as well as whether suitable delays have been found or not and gives the option (as checkboxes) to disable or re-enable particular chips.
        
        Args: 
            master: Controlling tk.Frame so that a popup can be added on top.
            eye_diag (list[int]): sanitised link quality values from eye diagram shell output (output of sanitise_plot_eye_diagram function)
            delay (list[bool]): list of booleans indicating whether a delay has been successfully found for a certain lane (output of sanitise_plot_eye_diagram function)
        """
        # TODO: incorporate into plot_eye_diagram?
        top = tk.Toplevel(master)
        top.transient(master)
        top.title("eyeDiagram")
        
        # plots the heatmap for the eyeDiagram 
        fig = plt.Figure(figsize=(5,5), dpi=100)
        plot1 = fig.add_subplot(111)
        plot1.imshow(eye_diag, cmap='winter')
        plot1.set_ylabel("Channel")
        plot1.set_xlabel("Lane")
        
        canvas = FigureCanvasTkAgg(fig, master = top)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0)
        
        # uses the output from the processed config JSON to create labels stating whether a suitable delay has been found for each lane. 
        enabled = self.chip_enabled(mod_data)
        i = 0
        for d in delay:
            tk.Label(top, text= f"{i}. " + ("Delay found" if d == "green" else "Delay not found"), fg=d).grid(row=i+1)
            i += 1
        
        # creates a column of checkboxes to allow for disabling/enabling particular ASICS. 
        i = 0
        self.checkbox_flags = []
        self.checkbox = []
        for a in enabled:
            self.checkbox_flags.append(tk.IntVar(value=a))
            self.chk = tk.Checkbutton(top, text=f"Chip {i+1}", variable=self.checkbox_flags[i], onvalue=True, offvalue=False)
            self.chk.grid(row=i+1, column=1)
            self.checkbox.append(self.chk)
            if bool(a):
                self.chk.select() #turn on checkboxes corresponding to on chips. 
            i += 1
        logging.debug(f"{self.checkbox_flags=}")
        ok_btn =tk.Button(top, text="OK",command = lambda : self.disable_chips(top,mod_data, [s.get() for s in self.checkbox_flags])).grid(row=18, columnspan=2)
    
    def chip_enabled(self, mod_data : ModuleTestData) -> list[int]:
        """Reads the relevant config file, located in module-qc-database-tools, to output which ASICs are turned on.
        
        Args:
            mod_data: ModuleTestData object containing ID and serial number 
        Returns:
            enabled: list of integers in [0,1] designating whether the corresponding ASIC is off or on.  
        """
        loc_id, mod_sn, temp, _ = self.check_mod_data_loaded(mod_data)
        enabled = []
        home_path = mod_data.home_path
        file = f"{home_path}/module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
        logging.debug(f"Opening {file}")
        with open(file, "r") as jsonfile:
            data = json.load(jsonfile)
            logging.info("Read successful")
        for a in range(4):
            logging.debug(f"Chip {a} enabled: {data['chips'][a]['enable']} ")
            enabled.append((int(data['chips'][a]['enable'])))
        return enabled
    
    def disable_chips(self, master, mod_data : ModuleTestData, chk_boxes : list):
        """Writes to the config JSON with updated information (from checkboxes) as to which ASICS are to be turned off or on. If there is any write error, the original data is written in stead. 
        
        Args:
            master: controlling tk.Frame so that the popup can be closed
            mod_data: ModuleTestData object containing local ID and serial number, as well as whether it is a warm or cold test so that the correct JSON file can be located.
            chk_boxes (list[int]): list of integers corresponding to whether chip[i] is off (0) or on (1). 
        """
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


class PrelimTests(TestInterface):
    test_name = "Preliminary Tests"
    
    def __init__(self,parent,controller, mod_data):
        super().__init__(parent, controller, mod_data)


    def get_test_list(self, mod_data : ModuleTestData):
        if mod_data.stage == "post":
            return ['IV-MEASURE', 'corecolumnscan']
        elif mod_data.stage == "final_cold":
            return ['IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'DATA-TRANSMISSION', 'corecolumnscan']
        return ['IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'LP-MODE', 'DATA-TRANSMISSION', 'corecolumnscan']
    
    def gen_cmd(self, mod_data):
        return "{echo}cd {home_path}/module-qc-tools ; pwd ; {echo}measurement-{test} -c ../configs/new_hw_config_{version}.json -m ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json"
    
    

class MinHealthTests(TestInterface):
    test_name = "Mininum Health Tests"   
    def get_test_list(self, mod_data):
        return ["std_digitalscan", "std_analogscan", "std_thresholdscan_hr", "std_totscan -t 6000"]
    
    def gen_cmd(self, mod_data: ModuleTestData):
        return "{echo}cd {home_path}/Yarr ; {echo}bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/rd53b/{test} -Wh" if mod_data.version == "v1.1" else "{echo}cd {home_path}/Yarr ; {echo}bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/itkpixv2/{test} -Wh" # changes the config file depending on v1 or v2

class Tuning(TestInterface):
    test_name = "Tuning"
    def get_test_list(self, mod_data):
        _, _, _, version = self.check_mod_data_loaded(mod_data)
        return ["std_tune_globalthreshold -t 1700", "std_tune_globalpreamp -t 6000 7", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"] if version == "v2" else ["std_tune_globalthreshold -t 1700", "std_totscan -t 6000", "std_tune_globalthreshold -t 1700", "std_tune_pixelthreshold -t 1500", "std_retune_globalthreshold -t 1700", "std_retune_pixelthreshold -t 1500", "std_thresholdscan_hd", "std_totscan -t 6000"]
    
    def gen_cmd(self, mod_data: ModuleTestData):
        return "{echo}cd {home_path}/Yarr ; {echo}bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/rd53b/{test} -Wh" if mod_data.version == "v1.1" else "{echo}cd {home_path}/Yarr ; {echo}bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/itkpixv2/{test} -Wh" # changes the config file depending on v1 or v2

class PixelFailTests(TestInterface):
    test_name = "Pixel Fail"
    def get_test_list(self, mod_data):
    
        if mod_data.stage == "final_cold":
            return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan", "selftrigger_source -p", "selftrigger_source"]
        return ["std_discbumpscan", "std_mergedbumpscan -t 1500", "std_thresholdscan_zerobias", "std_noisescan"]
    
    def gen_cmd(self, mod_data: ModuleTestData):
        """"Returns the template for the pixel fail test scripts, changing the config depending on the chip version """
        return "{echo}cd {home_path}/Yarr ; {echo}bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/rd53b/{test} -Wh" if mod_data.version == "v1.1" else "{echo}cd {home_path}/Yarr ; {echo}bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/itkpixv2/{test} -Wh" # changes the config file depending on v1 or v2
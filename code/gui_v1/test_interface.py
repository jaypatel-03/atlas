import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from module_test_data import ModuleTestData
import datetime
import threading 

class TestInterface(tk.Frame):
    test_name = "Base Test"
    _TEST_TIMES = {
        "IV-MEASURE" : 10,
        "ADC-CALIBRATION" : 4,
        "ANALOG-READBACK" : 45,
        "SLDO" : 15,
        "VCAL-CALIBRATION" : 5,
        "INJECTION-CAPACITANCE" : 2,
        "LP-MODE" : 10,
        "std_thresholdscan_hr" : 10,
        "std_tune_pixelthreshold -t 1500" : 2,
        "std_thresholdscan_hd" : 5,
        "std_discbumpscan" : 3,
        "std_thresholdscan_zerobias" : 4,
        "selftrigger_source" : 30
    }

    def __init__(self, parent, controller, mod_data):
        super().__init__(parent) #this calls tk.Frame.__init__(self, parent)
        
        tk.Label(self, text=self.test_name).grid(row=0, columnspan=2)
        self.test_list = self.get_test_list(mod_data)
        self.make_buttons(controller, self.test_list, mod_data)  # TODO: Assumes mod_data is available
        
    def get_test_list():
        # to be overrided
        return [] 
    
    def check_mod_data_loaded(self, mod_data : ModuleTestData) -> tuple[str, str, str, str] | None:
        '''Tests whether all the module testing properties have been loaded
        
        Args:
            mod_data : Module test data
        Returns:
            mod_data.loc_id, mod_data.mod_sn,mod_data.temp, mod_data.version | None, None, None, None 
        
        '''
        try:
            return mod_data.loc_id, mod_data.mod_sn,mod_data.temp, mod_data.version, mod_data.home_path
        except AttributeError:
            messagebox.showerror("showerror", "Module info has not been loaded correctly, try load again.")
            return None, None, None, None

    def run_test(self, master, button : tk.Button, test : str, mod_data : ModuleTestData):
        loc_id, mod_sn, temp, version, home_path = self.check_mod_data_loaded(mod_data)            
        
        if loc_id is not None:
            # TODO: remove echos 
            # TODO: remove sleeps
            if test in ['IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'LP-MODE', 'DATA-TRANSMISSION']:
                template = "echo cd {home_path}/module-qc-tools ; echo measurement-{test} -c ../configs/new_hw_config_{version}.json -m ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json ; sleep 2"
            elif test == "eyeDiagram":
                template = "echo cd {home_path}/Yarr ; echo bin/eyeDiagram -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json ; sleep 2" # TODO: change output directory
                # TODO: add pipe out to > /home/jayp/atlas/code/gui_v1/logs/eyeDiagram.log 
            else:
                template = "echo cd {home_path}/Yarr ; echo bin/scanConsole -r configs/controller/specCfg-rd53b-16x1.json -c ../module-qc-database-tools/{loc_id}/{mod_sn}/{mod_sn}_L2_{temp}.json -s configs/scans/rd53b/{test} -Wh ; sleep 2"
                
            logging.info(f"Running {test}")
            cmd = template.format(home_path=home_path, loc_id=loc_id, mod_sn=mod_sn, temp=temp, test=test, version=version)
            
            if test.__contains__("zerobias"):
                print("HV source to 0V")
                self.open_popup(master, test, cmd) # TODO: change command back to just cmd
                print("HV source to -120V")
            else:
                self.open_popup(master, test, cmd) # TODO: change command back to just cmd
            button.configure(bg="green")

    def make_buttons(self, master, tests : list, mod_data : ModuleTestData):
        # TODO can return r+1 and list of buttons
        test_buttons = []
        r = 0
        for test in tests:
            tk.Label(self, text=f"{r + 1}.").grid(row=r + 1) #TODO: alternative add  {test.split(' ')[0]} to label, BUTTON_NAMES?
            test_name = ' '.join(test.split(' ')[0].split('_')[1:]) if test.__contains__("_") else test
            quick_btn = tk.Button(self, text=f"{test_name}", command=lambda r=r: self.run_test(master,test_buttons[r],tests[r], mod_data))
            test_buttons.append(quick_btn)
            quick_btn.grid(row=r + 1, column=1)
            r += 1
            
    def open_popup(self, master, test : str, cmd : str):
        # TODO: incorporate into plot_eye_diagram?
        popup = tk.Toplevel(master)
        popup.title(f"{test}")
        popup.geometry("500x100")
        popup.transient(master)
        popup.grab_set()
        
        time = self._TEST_TIMES[test] if test in self._TEST_TIMES else 1
        tk.Label(popup, text=f"Running {test}, will take approx {time} mins. \n ETA: {(datetime.datetime.now()+datetime.timedelta(minutes=int(time))).strftime('%H:%M')}").pack(fill='x', pady=10)
        
        
        progbar = ttk.Progressbar(popup, mode='indeterminate')
        progbar.pack(expand=True, fill="x", padx=20, pady=10)
        progbar.start(10)
        
        def on_done():
            progbar.stop()
            popup.destroy()
            messagebox.showinfo("Done", "Finished!")
            
        self.run_cmd(cmd, on_done)
        
    def run_cmd(self, cmd, on_done):
        
        def task():
            subprocess.run(cmd, shell=True) # This blocks the main thread 
            on_done() # callback in main thread
        threading.Thread(target=task, daemon=True).start()
        
    
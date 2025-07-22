import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from gui.module_test_data import ModuleTestData
import datetime
import threading 
import os
import time
import signal
class TestInterface(tk.Frame):
    """ Interface (or base class) from which all the sets of tests inherit. 
    
    This defines the basic behaviour for a pre-defined set of tests including making a set of buttons, running the associated scripts. 

    """
    test_name = "Base Test"
    # Dictionary of estimated time of running for the named tests. Any tests executed not listed below will assume to take 1 minute. 
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
    PWD = os.getcwd()
    _QC_TESTS =  ['IV-MEASURE', 'ADC-CALIBRATION', 'ANALOG-READBACK', 'SLDO', 'VCAL-CALIBRATION', 'INJECTION-CAPACITANCE', 'LP-MODE', 'DATA-TRANSMISSION']
    def __init__(self, parent, controller, mod_data):
        super().__init__(parent) #this calls tk.Frame.__init__(self, parent)
        tk.Label(self, text=self.test_name).grid(row=0, columnspan=2) # Title of set of test 
        self.test_list = self.get_test_list(mod_data) 
        self.make_buttons(controller, self.test_list, mod_data)        
    
    def get_test_list():
        # to be overrided by child classes.
        return [] 
    
    def check_mod_data_loaded(self, mod_data : ModuleTestData):
        """Tests whether all the module testing properties have been saved into the ModuleTestData file. NB: Only checks for existence, not validity - we assume that the imported data is all reasonable. 
        
        Args:
            mod_data: Module test data
        Returns:
            mod_data.loc_id, mod_data.mod_sn, mod_data.temp, mod_data.version | None, None, None, None: Throws an exception and returns None if the attributes don't exist.
        """
        try:
            return mod_data.loc_id, mod_data.mod_sn,mod_data.temp, mod_data.version
        except AttributeError:
            messagebox.showerror("showerror", "Module info has not been loaded correctly, try load again.")
            return None, None, None, None

    def run_test(self, master, button : tk.Button, test : str, mod_data : ModuleTestData):
        """ Locates and runs the script requested, autofilling module information. 
        
        Args:
            master: Window containing the frame 
            button: tkinter button triggering the script 
            test: name of script
            mod_data: ModuleTestData object with module data (SN, local ID etc) loaded.
        """
        loc_id, mod_sn, temp, version = self.check_mod_data_loaded(mod_data)            
        
        home_path = mod_data.home_path
        dry_run = mod_data.dry_run 
        
        
        if loc_id is not None:
            template = self.gen_cmd(mod_data)
           
            echo = ""
            if dry_run:
                template += " ; sleep 2" # simulates the script taking some time 
                echo = "echo "
            template += " ; {echo}cd {pwd}" # returns to original GUI directory after executing script. Use this instead of os changedir to emulate the dry run 
                    
            logging.info(f"Running {test}")
            cmd = template.format(echo=echo, home_path=home_path, loc_id=loc_id, mod_sn=mod_sn, temp=temp, test=test, version=version, pwd=self.PWD) # fills module information
            logging.debug(f"********** \n CMD: {cmd} \n ***********")
            if "zerobias" in test: # TODO: implement HV ramping for zerobias test + (temp, LV, HV) checks for other tests  
                messagebox.showinfo("show info", "HV source to 0V")
                time.sleep(1) 
                self.open_popup(master, test, cmd) 
                messagebox.showinfo("show info", "HV source to -120V")
            else:
                self.open_popup(master, test, cmd) 
            button.configure(bg="green")
            
    def gen_cmd() -> str:
        """"Returns the command template for the relevant test scripts, changing the config depending on the chip version and temperature; to be overridden by child classes. """
        return ""
    
    def make_buttons(self, master, tests : list, mod_data : ModuleTestData):
        """Loops over list of tests and makes corresponding buttons. Strips the std_prefix in YARR scans.
        
        Args:
            master: controlling tk.Frame
            tests: list[strings] of test names
            mod_data: ModuleTestData object containing information about the module to pass through to button functions. 
        """
        test_buttons = []
        r = 0
        for test in tests:
            tk.Label(self, text=f"{r + 1}.").grid(row=r + 1)
            test_name = ' '.join(test.split(' ')[0].split('_')[1:]) if "_" in test else test
            quick_btn = tk.Button(self, text=f"{test_name}", command=lambda r=r: self.run_test(master,test_buttons[r],tests[r], mod_data))
            test_buttons.append(quick_btn)
            quick_btn.grid(row=r + 1, column=1)
            r += 1
            
    def open_popup(self, master, test : str, cmd : str, override : bool = False):
        """Opens small popup window with progress bar and executes the script for the test. Also defines actions to be taken after the test script has been executed (on_done).
        
        Args:
            master: controlling Frame (Test Suite)
            test (str): name of the test, with any flags
            cmd (str) : shell command to be executed, including any cd to relevant dirs, cd back to working dir
        """
        popup = tk.Toplevel(master)
        popup.title(f"{test}")
        popup.transient(master)
        popup.grab_set()
        
        time = self._TEST_TIMES[test] if test in self._TEST_TIMES else 1
        tk.Label(popup, text=f"Running {test}, will take approx {time} mins. \n ETA: {(datetime.datetime.now()+datetime.timedelta(minutes=int(time))).strftime('%H:%M')}").pack(fill='x', pady=10)
        
        
        progbar = ttk.Progressbar(popup, mode='indeterminate')
        progbar.pack(expand=True, fill="x", padx=20, pady=10)
        kill_btn = tk.Button(popup, text="Murder", command=self.kill_proc).pack()
        progbar.start(10)
        
        
        def on_done():
            progbar.stop()
            popup.destroy()
            messagebox.showinfo("Done", "Finished!")
        
        self.run_cmd(cmd, on_done)
        
    def run_cmd(self, cmd : str, on_done):
        """"Threaded subprocess run (shell command).
        Args:
            cmd (str): shell command to be executed, including prepended cd to script dir
            on_done (function): function to define behaviour after command has been executed (e.g., stop progress bar and close popup).
        """
        
        # TODO: implement failure protocol. 
        def task(): 
            self.proc = subprocess.Popen(cmd, shell=True,preexec_fn=os.setsid) # This blocks the main thread 
            self.proc.wait()
            on_done() # callback in main thread
        threading.Thread(target=task, daemon=True).start()
        
    
    def kill_proc(self):
        if hasattr(self, 'proc') and self.proc.poll() is None:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
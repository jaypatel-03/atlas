import tkinter as tk
import logging
from gui.module_test_data import ModuleTestData
from gui.test_suite import *
import re 
import os 
import subprocess
from datetime import datetime 

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
            frame.grid(row=0, column=c, sticky="nswe")
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
        frame = InputScreen(window,self, mod_data)
        self.frames[InputScreen] = frame
        frame.grid(row=0, column=0, sticky="nswe")
        self.show_frame(InputScreen)  # Shows the input screen
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()
           
class InputScreen(tk.Frame):
    
    def __init__(self,parent,controller, mod_data):
        tk.Frame.__init__(self,parent) # inherits from main class
        
        # Input module serial numbers and Oxford ID
        tk.Label(self, text="Module Serial Number \n (e.g. 20UPGM22110039) ").grid(row=0)
        e_mod_sn = tk.Entry(self, bg='white', fg='black')
        e_mod_sn.insert(0,"20UPGM22110561")
        e_mod_sn.grid(row=0, column=1)
        

        tk.Label(self, text="Local ID \n (e.g. OX0006)").grid(row=1)
        e_local_id = tk.Entry(self, bg='white', fg='black')
        e_local_id.insert(0, "OX0006")
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
        tk.Checkbutton(self, text="Overwrite configs?", variable=check_overwrite_config_flag, onvalue=True, offvalue=False).grid(row=r+6,column=1)
        
        tk.Label(self, text="Module_QC directory \n (typically ~/Module_QC)").grid(row=0, column=2)
        e_home_path = tk.Entry(self)
        # e_home_path.insert(0,"~/Module_QC") TODO: change back
        e_home_path.insert(0,mod_data.home_path)
        e_home_path.grid(row=0, column=3)
        

        # Validate serial numbers and generate config files
        tk.Button(self, text="Load & generate configs", width = 25, command = lambda : self.validate_module_info(controller, mod_data, e_mod_sn.get().strip(),e_local_id.get().strip(),self.version.get(), check_overwrite_config_flag.get(), e_home_path.get().strip())).grid(row=15)
        
    
    def set_mod_data(self, attr : str, value : str, mod_data : ModuleTestData):
        logging.info(f"Set {attr} to {value}")
        if not hasattr(mod_data, attr):
            raise AttributeError(f"{mod_data!r} has no attribute {attr!r}")
        setattr(mod_data, attr, value)
    
        
    def validate_module_info(self,master, mod_data : ModuleTestData, mod_sn : str, local_id : str, version : str, overwrite_config : bool, home_path : str) -> None:
        '''Validates module info entered and downloads config files from database if successful
        
        Args:
            mod_sn: String containing the global module serial number
            local_sn: String containing the local (Oxford) module identifier
        Returns:
            None: if attempting to unintentionally rewrite config files 
        '''
        logging.info("Load button pressed")
        echo = "echo" if mod_data.dry_run else ""
        if home_path == "":
            home_path = mod_data.home_path
        elif home_path.endswith('/'):
            home_path = home_path[0:-2]
        
        self.set_mod_data("home_path", home_path, mod_data)
                  
        if self.regex_validation(local_id, mod_sn, version):
            logging.info("Module info looks reasonable.")
            # Write data to ModuleTestData object 
            mod_data.loc_id = local_id
            mod_data.mod_sn = mod_sn
            mod_data.version = version
            
            logging.info(f"Module {local_id} loaded at {datetime.now().strftime('%H:%M:%S')} with : {vars(mod_data)=}")
            
            # Test whether the config files exist and will be unwittingly overwritten
            path_to_dir = fr"{home_path}/module-qc-database-tools/{local_id}"
            
            if not overwrite_config and os.path.isdir(path_to_dir):
                messagebox.showerror("showerror", "Config files already exist, decide whether to overwrite or not.")
                return
            elif overwrite_config and os.path.isdir(path_to_dir):
                new_path = fr"{path_to_dir}_{datetime.now().strftime(r'%d%m%y_%H%M')}/"
                os.mkdir(new_path)
                cmd = "mkdir " + new_path 
                subprocess.run(cmd, shell=True)
                logging.debug(f"Run mkdir {path_to_dir}_{datetime.now().strftime(r'%d%m%y_%H%M')}/")
                subprocess.run([echo, "rsync", "-r", path_to_dir, new_path], shell=True)
                logging.debug(f"rsync -r {path_to_dir} {new_path}")
                
            logging.debug(f"Run cd {mod_data.home_path}/module-qc-database-tools")
            subprocess.run([echo ,"cd", f"{mod_data.home_path}/module-qc-database-tools"], shell=True)
            logging.debug(f"Run mwdbt generate-yarr-config -sn {mod_sn} -o {local_id}")
            subprocess.run([echo, "mqdbt", "generate-yarr-config", "-sn", mod_sn, "-o", local_id], shell=True)
            logging.debug(f"cd {mod_data.home_path}")
            subprocess.run([echo, "cd", mod_data.home_path], shell=True)
            master.destroy()    
       
    def regex_validation(self, local_id : str, mod_sn : str, version : str) -> bool:
        """ Performs RegEx validation on the local ID and the module serial number, with the option to manually override. Also test to see if the module serial number indicates a v1.1 module or v2. 
        # TODO: FINISH 
        Args: 
             
        """
        
        if re.search(r"^OX[0-9]{4}$", local_id) is None:
        # ^___$ are anchors to force exact matches
            logging.info(f"Invalid local ID {local_id}, should be of the form OX####.") 
            return messagebox.askyesno("askyesno", f"Invalid local ID {local_id}, should be of the form OX####. \n Continue anyway?")
        elif re.search(r"^20UPGM2[0-9]{7}$", mod_sn) is None:
            logging.info(f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########")
            return messagebox.askyesno("askyesno", f"Invalid module serial number {mod_sn}, should be of the form 20UPGM########. \n Continue anyway?")
        elif (re.search(r"^20UPGM2321[0-9]{4}$", mod_sn) is not None or re.search(r"^20UPGM2421[0-9]{4}$", mod_sn) is not None ) and version == "v1.1":
            logging.info("Module serial number suggests this may be a v2 module.")
            return messagebox.askyesno("yesno","Module serial number suggests this may be a v2 module. \n Continue anyway?")
        elif re.search(r"^20UPGM2211[0-9]{4}$", mod_sn) is not None and version == "v2":
            logging.info("Module serial number suggests this may be a v1.1 module.")
            return messagebox.askyesno("askyesno","Module serial number suggests this may be a v1.1 module. \n Continue anyway?")   
        else:
             return True
            
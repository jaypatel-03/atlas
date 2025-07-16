class ModuleTestData:
    def __init__(self) -> None:
        self.loc_id : str
        self.mod_sn : str
        self.temp : str = "warm"
        self.version : str
        self.temp : str
        self.port_keithley : str
        self.port_chiller : str
        self.port_peltier : str
        self.port_lvsupply : str
        self.home_path : str = "~/Module_QC/"
        
        '''
        lv_psu : HMP4040 ASRL/dev/ttyHMP4040b::INSTR
        hv_psu : Keithley2410 ASRL/dev/ttyUSB0::INSTR
        chiller 
        
        '''
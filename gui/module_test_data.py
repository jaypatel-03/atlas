import logging
import json 

class ModuleTestData:
    _STAGE_TEMP_MAP = {
        "init" : "warm",
        "post" : "warm",
        "final_warm" : "warm",
        "final_cold" : "cold",
    }
    
    def __init__(self, cfg : str = "./gui/config.json", stage : str = "init", dry_run : int = 2) -> None:
        
        with open(cfg, "r") as jsonfile:
            cfg_data = json.load(jsonfile)
            self.dry_run = bool(int(cfg_data['dry_run'])) if dry_run == 2 else bool(int(dry_run))
        self.home_path : str = cfg_data['default_home_path']
        self.loc_id : str = ""
        self.mod_sn : str = ""
        self.version : str = ""

        logging.info(f"*******************DRY RUN*******************" if self.dry_run else f"^^^^^^^^^^^^^^^^^^^^^ACTIVE RUN^^^^^^^^^^^^^^^^^^^^^" )
        
        '''
        self.home_path : str = "~/Module_QC"
        self.port_hv_psu : str = "ASRL/dev/ttyUSB0::INSTR"
        self.port_chiller : str = ""
        self.port_peltier : str = "ASRL/dev/ttyHMP4040b::INSTR" # not sure about this one
        self.port_lv_psu : str = "ASRL/dev/ttyHMP4040b::INSTR" 
        '''
        
        # To be overwritten by setter 
        self._stage: str | None = None
        self.temp: str | None = None

        # Use the property so temp is set consistently
        self.stage = stage

    @property
    def stage(self) -> str:
        return self._stage

    @stage.setter
    def stage(self, value: str):
        if value not in self._STAGE_TEMP_MAP:
            raise ValueError(
                f"Unknown stage {value!r}. Valid stages: {', '.join(self._STAGE_TEMP_MAP)}"
            )
        self._stage = value
        self.temp = self._get_temp_for_stage(value)
        logging.debug(f"Setter ran: stage={value!r} -> temp={self.temp!r}")

    def _get_temp_for_stage(self, stage: str) -> str:
        return self._STAGE_TEMP_MAP[stage]
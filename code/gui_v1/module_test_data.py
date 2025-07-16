import logging

class ModuleTestData:
    _STAGE_TEMP_MAP = {
        "init" : "warm",
        "post" : "warm",
        "final_warm" : "warm",
        "final_cold" : "cold",
    }
    def __init__(self, stage: str = "init") -> None:
        self.loc_id : str = ""
        self.mod_sn : str = ""
        self.version : str = ""
        self.home_path : str = ""
        # Backing fields; will be overwritten by the property setter call below
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
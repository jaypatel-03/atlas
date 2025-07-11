import time

from constellation.core.configuration import load_config
from constellation.core.controller import ScriptableController
from constellation.core.satellite import Satellite 
from constellation.core.message.cscp1 import SatelliteState

# from constellation.core.cli import main_entry_point

Test = Satellite.Mariner

# Settings
config_file_path = "code/config.toml"
n_satellites = 2
group_name = "edda"

# Create controller
ctrl = ScriptableController(group_name)
constellation = ctrl.constellation

# Load configuration
cfg = load_config(config_file_path)

constellation.initialize(cfg)
ctrl.await_state(SatelliteState.INIT)
print(constellation.satellites)

# Wait until all satellites are connected
while len(constellation.satellites) < n_satellites:
    print("Waiting for satellites...")
    time.sleep(0.5)
print("Loaded")

# Initialize and launch

constellation.launch()
ctrl.await_state(SatelliteState.ORBIT)

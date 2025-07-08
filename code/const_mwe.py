import time

from constellation.core.configuration import load_config
from constellation.core.controller import ScriptableController
from constellation.core.satellite import Satellite 

# from constellation.core.cli import main_entry_point


# Settings
config_file_path = "code/config.toml"

group_name = "edda"

# Create controller
ctrl = ScriptableController(group_name)
constellation = ctrl.constellation

# Load configuration
cfg = load_config(config_file_path)
Satellite.do_initializing(cfg)
Satellite.Mariner.launch()
print(constellation.satellites)

'''


class ExampleSatellite(Satellite):
    def __init__(self, name):
        # Initialize base class with satellite name
        super().__init__(name)

    def do_initializing(self):
        self.logger.info("Satellite is initializing.")
        self.set_state_ready()  # Transition to READY state

    def do_starting(self):
        self.logger.info("Satellite is starting.")
        self.set_state_running()  # Transition to RUNNING state

    def do_running(self):
        self.logger.info("Satellite is running.")
        self.set_state_running()  # Remain in RUNNING (can include tasks here)

    def do_stopping(self):
        self.logger.info("Satellite is stopping.")
        self.set_state_ready()  # Return to READY state

    def do_resetting(self):
        self.logger.info("Satellite is resetting.")
        self.set_state_idle()  # Return to IDLE


def main():
    # Entry point using Constellation's CLI support
    main_entry_point(ExampleSatellite)


if __name__ == "__main__":
    main()

'''
'''
# Wait until all satellites are connected
while len(constellation.satellites) < n_satellites:
    print("Waiting for satellites...")
    time.sleep(0.5)
    constellation.initialize(cfg)
    constellation.launch()
    print("End")
'''
'''
# Start a parameter scan for the key "interval"
for ivl in range(0, 100, 10):
    # Reconfigure one of the satellites to the new parameter value
    recfg = {"interval": ivl}
    constellation.Sputnik.reconfigure(recfg)

    # Wait until ll states are back in the ORBIT state
    ctrl.await_state(SatelliteState.ORBIT)

    # Repeat this measurement four times:
    for run in range(1, 4):
        # Start the run
        constellation.start(f"i{ivl}_r{run}")
        ctrl.await_state(SatelliteState.RUN)

        # Run for 15 seconds
        time.sleep(15)

        # Stop the run and await ORBIT state of all satellites
        constellation.stop()
        ctrl.await_state(SatelliteState.ORBIT)
'''
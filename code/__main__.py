"""
SPDX-FileCopyrightText: 2024 DESY and the Constellation authors
SPDX-License-Identifier: EUPL-1.2

Provides the entry point for the Mariner example satellite
"""
import time 
import logging

from constellation.core.logging import setup_cli_logging
from constellation.core.satellite import SatelliteArgumentParser
from constellation.core.configuration import Configuration
from constellation.core.controller import ScriptableController
from constellation.satellites.Mariner.Mariner import Mariner
from constellation.core.configuration import load_config
from constellation.core.message.cscp1 import SatelliteState

def main(args=None):
    """Demonstrator satellite serving as prototype for new satellites"""
    '''
    # Get a dict of the parsed arguments
    # parser = SatelliteArgumentParser(description=main.__doc__)
    # args = vars(parser.parse_args(args))
    # setup_cli_logging(args.pop("level"))
    '''
    setup_cli_logging("CRITICAL")

    config_file_path = "code/config.toml"
    config = Configuration(load_config(config_file_path))

    sat = Mariner(
        name="One",
        group="alpha",
        interface="lo",     # or "eth0" / "wlan0" for real network
        cmd_port=5001,
        hb_port=5002,
        mon_port=5003,
    )

    '''
    # Create controller
    ctrl = ScriptableController("alpha")
    print(ctrl.constellation.Mariner.get_state())
    ctrl.constellation.initialize({})
    print(ctrl.constellation.Mariner.One.get_status())
    
    
    # while ctrl.constellation.Mariner.:
    #     print("Waiting for initialization...")
    #     time.sleep(0.5)
    # ctrl.constellation.launch()
    '''
    
    print(sat.do_initializing(config))
    ctrl = ScriptableController("alpha")
    constellation = ctrl.constellation
    print(sat.do_launching())

    print(sat.do_starting("Run1"))
    print(constellation.Mariner.One.get_brightness())
    
    print(constellation.get_status())
    print(sat.do_run(94))
    print(sat.do_landing())
    print(sat.do_stopping())
    
    

if __name__ == "__main__":
    main()

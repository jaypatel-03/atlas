Thermal Cycle Control Script (with software interlock)
==========================================================================

Thermal cycle control script, designed to work with the Oxford OPMD ATLAS Module Testing setup and hardware interlock

Requirements:
- *nix OS
- Python 3.x
- PyQt5
- [icicle](https://gitlab.cern.ch/icicle/icicle.git) in ```pidcontroller-bugfix``` branch 
- [tricicle](https://gitlab.cern.ch/icicle/tricicle.git) with ```pip install -e  ".[qt5]"```
- xterm (?)
- Oxford hardware interlock system [itk-dcs-interlock](https://gitlab.cern.ch/sfkoch/itk-dcs-interlock.git) with relevant instrument naming rules and CRIO drivers (TODO: add full instructions)

At the start of the script, there are a set of constants to be defined by the user as the default parameters for the thermal cycle. These can be overriden by CLI arguments as follows:



Example Peltier config: 
```
[[pidcontroller]]
power_instrument = "HMP4040"
power_resource = "ASRL/dev/ttyHMP4040b"
power_channel = 1
power_type = "current"
measure_instrument = "ITkDCSInterlock"
measure_resource = "TCPIP::localhost::9898::SOCKET"
measure_channel = 1
measure_type = "PT100:TEMP"
simulate = false
Kp = -1.5
Ki = -0.085
Kd = -0.01
setpoint = 15                # degrees C
starting_output = 0.0        # amps
sample_time = 0.5            # seconds
output_limits = [ 0.0, 4.0 ]  # amps
proportional_on_measurement = false
differential_on_measurement = true
```

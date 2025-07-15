# Plan

TODO:
- Ask about ssh into machine 
- Radiation training 
- CERN + ATLAS login 
- OPMD wiki login 
- LocalDB + Flask login
- Do you upload the minimum health tests, tuning and pixel fails all together? Yes
- More useful to have first part of each SN autofilled?
- Add automatic validation? <https://www.pythonguis.com/tutorials/input-validation-tkinter/#input-validation-strategies-in-gui-apps>
- Don't overwrite existing config

## Overview + Notes

Specify ports for Keithley?

Copy over swinterlock code - ask about ssh into machine. 

<https://www.digitalocean.com/community/tutorials/tkinter-working-with-classes>

Include eyeDiagram plot

Add upload reminder after each scan?
How to add progress bar/loading screen
Add analysis backend?

1) Open and initialise
2) Connect to Keithley and R&S supplies through appropriate ports
3) Bias HV and LV supplies 
4) Temperature check
5) 


1) Mount 
2) Vacuum on + dry air on, check gauge and maybe test nominal
3) Interlock on 
4) Turn chiller on (5 deg above)
5) Start SCPI interface (interlock GUI)
6) Set Peltier temp (GUI)
7) Turn on LV
8) Ramp up HV supply slowly
9) Wait ~1 min for temperature to stabilise 
10) Check that temp > dewpoint 

11) Generate YARR config with serial number (-sn) from Flask interface
    "mqdbt generate-yarr-config -sn $MODULE_SN -o $LOCAL_MODULE_NAME"
12) eyeDiagram - display Python plot output 
13) IV-MEASURE: display loading bar? Simple approximate timer? 
14) ADC-Calibration
15) Analog Readback: adjust trim bits to fine-tune I_ref
15) SLDO: rerun test if linearity fails? 

IV-Measure:
Looking for breakdown above 120V
May fail at low temp due to noise spiked being interpreted as delta functions and failing the QC linearity requirements

SLDO:
A/D = Analog/Digital

VDDD: digital output voltage ()

Chips operate at 1.2V, 2V max

I_shunt = excess current 

Number of wirebonds control the voltage/current going into the chips

Often fails: VDDD/A linearity, spike in v_in => rerun test first 

Analog readback:

Ring oscillator 

Freq proportional to VDDD

Freq also changes due to radiation damage 

25 sacrificial wirebonds - need to withstand around 8g of force 

Parylene coating reduces sparking (radiation damage over lifetime will mean we need to bias higher to 600V)

Activity: Bq/Ci (SI 37 GBq)

Exposure: C/kg, Rontgen 

Absorbed dose: Gray (100 rad), rad

Dose equivalent: Sievert


Default value:
```python
tk.Label(self, text="Module Serial Number \n (e.g. 20UPGM22110039) ").grid(row=0)
e_mod_sn = tk.Entry(self, bg='white', fg='grey')
e_mod_sn.grid(row=0, column=1)

e_mod_sn.insert(0, "GM2320017")
e_mod_sn.bind("<FocusIn>", self.__handle_focus_in, add="+")         # Delete default text on click


def __handle_focus_in(self,event=None):
    # event.widget.delete(0, tk.END)
    event.widget.config(fg='black')
    
    
```
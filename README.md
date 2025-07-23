# ATLAS Module Electrical Testing GUI

RTD: <https://atlas-summer-project.readthedocs.io/en/latest/>
 
To add:
- venv instructions

Requirements:
- *nix OS (or WSL on Windows)
- tkinter: GUI backend ```sudo apt-get install python3-tk``` for Debian-based systems or ```sudo dnf install python3-tkinter``` for Fedora/Alma
- Python version => 3.9
- Python venv library 
- Python matplotlib library
- Clone of [module-qc-tools](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-database-tools) AND INSTALL
- Clone of [module-qc-database-tools](https://gitlab.cern.ch/atlas-itk/pixel/module/module-qc-database-tools) AND INSTALL
- Clone of [Yarr scans](https://yarr.web.cern.ch/yarr/install/) 
- The following directory structure:
```bash
~ 
└── Module_QC
    ├── module-qc-database-tools
    ├── module-qc-tools
    ├── Yarr
``` 

The gui/config.json file contains the following data:
```json
{
    "default_home_path" : "/home/jayp/atlas",
    "dry_run" : 1,
    "_comment" : "Dry run: [0 = wet run, 1 = dry run], overriden by -d flag. "
}
```

Where ```dry_run``` can take the following values:
- 0: indicating a live run
- 1: indicating a dry run, only echoing the shell commands

Any CLI arguments specified by the ```-d``` flag override the config file. 

1. Activate ```venv``` and install ```matplotlib```
2. Navigate to install directory
3. ```git clone https://github.com/jaypatel-03/atlas```
4. ```cd``` to the install root directory 
5. ```python -m gui -c ./```



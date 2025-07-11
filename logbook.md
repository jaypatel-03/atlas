# Logbook

## TO DO

Core column issue? Hybrid chip configuration

Types of LGADs geometries - AC, PIN

Tkinter vs wxPython vs PyQt

Core column task force - Wednesday

What is meson?

## 07/07/2025

Install Constellation

```conda create -n atlas python=3.11```

```git clone https://gitlab.desy.de/constellation/constellation.git```

```pip install meson-python meson ninja```

```pip install --no-build-isolation --editable ".[cli,influx,keithley]"```

## 08/07/2025

Most stable version is currently 0.5:

```pip install ConstellationDAQ[cli,influx,keithley]===0.5```

Things in square brackets are optional extras (command line interface, TODO influx?, connect to keithley power source)

To install C++ version:

```git clone https://gitlab.desy.de/constellation/constellation.git```


```bash
sudo apt install build-essential
sudo apt install meson g++ ninja-build
sudo apt install qt6-base-dev
meson setup build -Dbuildtype=debugoptimized -Dwerror=false
meson compile -C build
```

To install MissionControl, need system-wide installation:
```meson install -C build```

Created environment.yml installation file

## 09/07/2025

ATLAS module assembly shadowing - 4 axis gantry robot

Software written in LABVIEW

1) Read datum and align - creates file with position vectors 
2) Pick up module and place

Check vacuum connections

Placement head - unscrew and check squidgy bits

## 11/07/2025



## Constellation

Here is a basic overview page https://constellation.pages.desy.de/

Notes on constellation:

Satellite is the equivalent of a device
https://gitlab.desy.de/constellation/constellation/-/blob/main/cxx/constellation/satellite/Satellite.hpp?ref_type=heads

Control protocol is commands where the device needs to respond (FSM transitions, get list of commands, get type, etc.)

Monitoring protocol is logging, anyone can subscribe. Could be direct log level or it could be temperature values etc.

Data transmission - point to point, maximise throughput

Heartbeat protocol - we assume to run autonomously. If software interlock dies then what do you do? Configure frequency for a heartbeat from the satellite (running, error, etc). Each satellite registers to all heartbeats on the constellation, and if one of them goes into error or stops then go into safe state

Software interlock integrated inside device

Run control is a controller class

Watchdog could be used to listen to monitoring stream and send out heartbeat



New class would be watchdog, which listens and has a heartbeat 

Heartbeat contains state of sender and time interval for next to arrive (timeout set by sender)

Run: self-contained measurement(s). Transition into RUN state and out 

TODO: multicast packet

TODO: ephemeral port defined in RFC 6335

TODO: basic network protocols

Satellite (receives commands): instrument controlling code and data receivers. React to commands from controllers, listen to other heartbeat messages, distribute log messages and telemetry data

Controller (sends commands): user interface, nodes which send commands via control protocol. GUI, CLI interfaces are controllers.

Listener (only consumes): log message interfaces/telemetry

There are transitional states where corresponding code may be run (initializing, launching, landing, starting, stopping, reconfiguring [e.g. varying HV supply rather than landing (ramping down) and launching (ramping up to new HV)]).

### Satellite

Type.Name

Status may change whilst remaining in same state

TODO: CSCP protocol <https://constellation.pages.desy.de/framework_reference/protocols.html>,

![alt text](img/plantuml-72500fffddee71d18891c765bfd7bc33fd82bccf.svg)

Initialisation involves reception of configuration from controller. FIRST CONNECTION TO INSTRUMENT HARDWARE.

Orbit: ready for DAQ

Run: DAQ

## Acronyms

LGAD = low-gain avalanche diode, 10x 100x gain so quick response

TCAD
SDE = stochastic DE
SPROCESS = simulates fabrication process

SCADA = Supervisory control and data acquisition

YARR = Yet Another Rapid Readout <https://github.com/Yarr/Yarr>

CSCP = Constellation Satellite Control Protocol

CDTP = Constellation Data Transfer Protocol 

CHIRP = Constellation Host Identification & Reconnaissance Protocol (IPv4 protocol)

CMDP = Constellation Monitoring Distribution Protocol 


## Testing procedure

Left ribbon connects to power, right to DAQ

1. Mount 
2. Check vacuum seal (bottom right graph + check flow meter. If not nominal, check compressed air valve)
3. Attach ribbon cables 
4. Close lid and seal
5. Turn cooler on (set to 5 deg above target temperature)
6. Double check R&S power supply parameters against checklist and set 'Output' to on
7. Turn PID cooler on (GUI) and monitor chuck temperature - this connects to the R&S power supply.
8. Interlock on (bottom checkbox)
9. Bias Keithley slowly to -0.120kV - monitor current to ensure it is limited

Reverse search = Ctrl + R

Make sure to change dir name to OX####

Add ```-wh``` tag to minimum health tests to upload data

YARR configs: v1.1 = rd53b dir; v2 = itkpix dir

Turn bias off for zero bias and TURN BACK ON afterwards (press 'Local' on Keithley)

Remember to leave box closed 


## Conda

mkdir
wget 
sh
<path to anaconda>/bin/conda shell.bash hook > ~/anaconda.sh

add "source anaconda.sh" to .bashrc or .bash_profile

## Git

### Installing Git

<http://joemaller.com/908/how-to-install-git-on-a-shared-host/>

Prerequisites: gcc, ssh (test by gcc --version)

If you see something like /usr/bin/gcc: Permission denied you don’t have access to the GCC compiler and will not be able to build the Git binaries from source. 
Update your $PATH

None of this will work if you don’t update the $PATH environment variable. In most cases, this is set in .bashrc. Using .bashrc instead of .bash_profile updates $PATH for interactive and non-interactive sessions–which is necessary for remote Git commands. Edit .bashrc and add the following line:

export PATH=$HOME/bin:$PATH

Be sure ‘~/bin’ is at the beginning since $PATH is searched from left to right; to execute local binaries first, their location has to appear first. Depending on your server’s configuration there could be a lot of other stuff in there, including duplicates.

    $ mkdir src
    $ cd src

Grab the most recent source tarball from Github. When this post was updated, the current Git release was version 1.7.10.1:

    $ curl -LO https://github.com/git/git/tarball/v1.7.10.1

Untar the archive and cd into the new directory:

    $ tar -xzvf v1.7.10.1
    $ cd git-git-9dfad1a

By default, Git installs into ~/bin which is perfect for shared hosting. Earlier versions required adding a prefix to the configure script (like this), but none of that is necessary anymore. If you do need to change the install location of Git, just specify a prefix to the Make command as described in Git’s INSTALL file.

With all that taken care of, installation is simple:

    $ make
    $ make install
    [lots of words...]

That should be it, check your installed version like this:

    $ git --version

It’s now safe to delete the src folder containing the downloaded tarball and source files



### 

    git init
    git pull <https://github.com/InfiniteJay/B9-Project>
VSCode Add remote
    git push --set-upstream B9-Project master
    git lfs pull

OR

Install Github CLI, gh create 

    git lfs migrate import --include="*.png"

To ignore 

create .gitignore file 
MAKE SURE ENCODING IS UTF8 otherwise this will not work 

Add regex to ignore (e.g *.png MT/Pictures/*)

Having disconnected from remote, if git fetch returns:
    fatal: couldn't find remote ref refs/heads/master

Run:
    $ git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"

src <https://stackoverflow.com/questions/11623862/fetch-in-git-doesnt-get-all-branches>

### Setup 

…or create a new repository on the command line

```git
echo "# atlas" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/jaypatel-03/atlas.git
git push -u origin main
```

…or push an existing repository from the command line
```
git remote add origin https://github.com/jaypatel-03/atlas.git
git branch -M main
git push -u origin main
```

## SSH

Add config file to jay/.ssh/config 

cat id.pub file 
Add key to GitLab and GitHub


## Linux tips
    
    find <path> -maxdepth <n> -name "filename*" -print

    find <something> | xargs <command like ls -l or cat>    
    
    rsync -v <source> <destination>

Through WSL

    rsync -av -e "ssh -J jesu4129@bastion.physics.ox.ac.uk" French.txt jesu4129@pplxint12.physics.ox.ac.uk:./copy




### Copying to remote

    scp -J jesu4129@bastion.physics.ox.ac.uk .\file jesu4129@pplxint12.physics.ox.ac.uk:./copy

Add function to Powershell profile (echo $profile)

    function SSH-Copy {
        scp -J jesu4129@bastion.physics.ox.ac.uk .\$args jesu4129@pplxint12.physics.ox.ac.uk:./copy
    }


### Example Satellite Class

```python
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
```
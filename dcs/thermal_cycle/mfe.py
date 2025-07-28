from icicle.pidcontroller import PIDController
import subprocess, shutil, time, threading

class PeltierManager:
    def __init__(self, resource="TCPIP::localhost::19898::SOCKET"):
        self._pid = PIDController(resource=resource)
        self._lock = threading.Lock()

    def set_state(self, channel: int, state: bool):
        with self._lock:
            pelt = self._pid.channel("TemperatureChannel", channel)
            with pelt: state = pelt.state
            
    def read_state(self, channel: int) -> bool:
        with self._lock:
            pelt = self._pid.channel("TemperatureChannel", channel)
            return pelt.state



def open_tricicle(config_file):
    print(shutil.which("pidcontroller-ui"))
    return subprocess.Popen([shutil.which("pidcontroller-ui"), "-c", config_file, "-a"], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


manager = PeltierManager()
tricicle = open_tricicle("../configs/pidcontroller.toml")

p = PIDController(resource="TCPIP::localhost::19898::SOCKET")

try:
    for j in range(1,5):
        modules = range(1, j+1)
        print(f"Testing with modules: {modules}")
        # pelt = [p.channel("TemperatureChannel", i) for i in modules]
        for i in modules:
            print(f"Peltier {i} state: {manager.read_state(i)}")
            manager.set_state(i, True)  # Enable the peltier
            print(f"->{manager.read_state(i)}")  # Check if the peltier is enabled
            
except Exception as e:
    print(f"Error occurred: {e}")

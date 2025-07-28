from icicle.pidcontroller import PIDController
import threading
import time

# Shared PID controller for all 4 peltiers
p = PIDController(resource="TCPIP::localhost::19898::SOCKET")

# Control pelt2 and pelt3
pelt2 = p.channel("STATE", 2)
pelt3 = p.channel("STATE", 3)

try:
    print("Turning off pelt2")
    pelt2.state = False  # this should work
    time.sleep(0.1)

    print("Turning off pelt3")
    pelt3.state = False  # this may trigger the crash
except Exception as e:
    print(f"Error occurred: {e}")



class PeltierManager:
    def __init__(self, resource="TCPIP::localhost::19898::SOCKET"):
        self._pid = PIDController(resource=resource)
        self._lock = threading.Lock()

    def set_state(self, channel: int, state: bool):
        with self._lock:
            pelt = self._pid.channel("TemperatureChannel", channel)
            pelt.state = state

manager = PeltierManager()

# Usage
# manager.set_state(2, False)
# manager.set_state(3, False)
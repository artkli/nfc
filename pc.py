import wakeonlan
import subprocess
import time

from icmplib import ping
from h import PCARP, SHOST, PCHOST, PCSC


class Pc:
    def __init__(self):
        self.arp = PCARP
        self.interface = SHOST

    def __del__(self):
        pass
    
    close = __del__

    def isOn(self):
        try:
            p = ping(PCHOST, count=1, timeout=2)
        except:
            return False
        if p.packets_received == 0:
            return False
        return True

    def on(self):
        wakeonlan.send_magic_packet(self.arp, interface=self.interface)
        return True

    def off(self):
        command = PCSC.split()
        call = subprocess.run(command, stdout=subprocess.PIPE, encoding='UTF8')
        return True if call.returncode == 0 else False


if __name__ == "__main__":
    p = Pc()
    print(p.isOn())
    print("starting ...")
    print(p.on())
    time.sleep(30)
    print(p.isOn())
    print("stopping ...")
    print(p.off())
    p.close()

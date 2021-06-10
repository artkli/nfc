import eiscp
import time
from h import VSXHOST


TV = "tv"
BD = "bd"
SAT = "sat"
CD = "cd"
FM = "fm"
AM = "am"
NET = "net"
PC = "game"
USB = "usb"
BT = "bluetooth"

ST1 = 0.5
ST2 = 2.0
ST3 = 3.0
ST4 = 10.0


class Vsx:
    def __init__(self, host=VSXHOST):
        self.host = host
        self.dev = eiscp.eISCP(self.host)

    def __del__(self):
        self.dev.disconnect()
    
    close = __del__

    def __decode(self, tuple):
        if CD in tuple[1]:
            return CD
        if BD in tuple[1]:
            return BD
        if PC in tuple[1]:
            return PC
        if NET in tuple[1]:
            return NET
        if SAT in tuple[1]:
            return SAT
        if USB in tuple[1]:
            return USB
        return tuple[1]

    def on(self):
        if not self.isOn():
            if "on" in self.dev.command("power on"):
                time.sleep(ST2)
                return True
            else:
                return False

    def off(self):
        if self.isOn():
            if "off" in self.dev.command("power off"):
                return True
            else:
                return False

    def isOn(self):
        if "on" in self.dev.command("power query"):
            return True
        else:
            return False

    def cecOn(self):
        if "off" in self.dev.command("hdmi-cec query"):
            time.sleep(ST3)
            return self.dev.command("hdmi-cec on")
        else:
            return "on"

    def cecOff(self):
        if "on" in self.dev.command("hdmi-cec query"):
            time.sleep(ST3)
            return self.dev.command("hdmi-cec off")
        else:
            return "off"

    def getVolume(self):
        return int(self.dev.command("volume query")[1])

    def setVolume(self, vol):
        if vol < 0:
            vol = 0
        if vol > 164:
            vol = 164
        return self.dev.command("volume " + str(vol))
    
    def getSource(self):
        return self.__decode(self.dev.command("source query"))

    def setSource(self, src):
        start_time = time.time()
        while True:
            st = self.__decode(self.dev.command("source " + src))
            if st != src:
                return True
            if time.time() - start_time > ST4:
                return False
            time.sleep(ST1)
    
    def setTV(self):
        return self.setSource(TV)

    def setBD(self):
        return self.setSource(BD)

    def setSAT(self):
        return self.setSource(SAT)

    def setCD(self):
        return self.setSource(CD)

    def setFM(self):
        return self.setSource(FM)

    def setAM(self):
        return self.setSource(AM)

    def setNET(self):
        return self.setSource(NET)

    def setPC(self):
        return self.setSource(PC)

    def setUSB(self):
        return self.setSource(USB)

    def setBT(self):
        return self.setSource(BT)


if __name__ == "__main__":
    v = Vsx()
    print("VSX is ON" if v.isOn() else "VSX is OFF")
    print("starting ...")
    v.on()
    time.sleep(30)
    print("VSX is ON" if v.isOn() else "VSX is OFF")
    print("stopping ...")
    v.off()
    time.sleep(10)
    print("VSX is ON" if v.isOn() else "VSX is OFF")
    v.close()

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
        if "on" in self.dev.command("power on"):
            return True
        else:
            return False

    def off(self):
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
        return self.dev.command("hdmi-cec on")

    def cecOff(self):
        return self.dev.command("hdmi-cec off")

    def getVolume(self):
        return self.dev.command("volume query")

    def setVolume(self, vol):
        if vol < 0:
            vol = 0
        if vol > 164:
            vol = 164
        return self.dev.command("volume " + str(vol))
    
    def getSource(self):
        return self.__decode(self.dev.command("source query"))

    def setSource(self, src):
        return self.__decode(self.dev.command("source " + src))
    
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
    if not v.isOn():
        v.on()

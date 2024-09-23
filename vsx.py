import sys
import eiscp
import time

from datetime import datetime
from h import VSXHOST, DEBUG


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
SB = "strm-box"
DOLBY = "dolby-atmos"
STEREO = "all-ch-stereo"
DTS = "dts-x"
ON = "on"
OFF = "off"

ST1 = 0.8
ST2 = 2.0
ST3 = 8.0
ST4 = 12.0


currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class Vsx:
    def __init__(self, host=VSXHOST):
        self.host = host
        self.dev = None
        self.__reconnect()

    def __del__(self):
        if not self.__isDisconnected():
            self.dev.disconnect()
        self.dev = None
    
    close = __del__

    def __isDisconnected(self):
        return self.dev is None

    def __reconnect(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if not self.__isDisconnected():
            self.dev.disconnect()

        start_time = time.time()
        while True:
            try:
                self.dev = eiscp.eISCP(self.host)
            except:
                self.dev = None
            if not self.__isDisconnected():
                return True
            if time.time() - start_time > ST3:
                return False
            time.sleep(ST1)

    def __decode(self, thistuple):
        if CD in thistuple[1]:
            return CD
        if BD in thistuple[1]:
            return BD
        if PC in thistuple[1]:
            return PC
        if SB in thistuple[1]:
            return SB
        if NET in thistuple[1]:
            return NET
        if SAT in thistuple[1]:
            return SAT
        if USB in thistuple[1]:
            return USB
        if DOLBY in thistuple[1]:
            return DOLBY
        if DTS in thistuple[1]:
            return DTS
        if STEREO in thistuple[1]:
            return STEREO
        if ON in thistuple[1]:
            return ON
        if OFF in thistuple[1]:
            return OFF
        return thistuple[1]

    def __command(self, comm, val):
        if self.__isDisconnected():
            self.__reconnect()
        start_time = time.time()
        while True:
            time.sleep(ST1)
            try:
                st = self.__decode(self.dev.command(comm + " " + val))
            except:
                self.__reconnect()
                st = False
            if isinstance(st, str):
                time.sleep(ST1)
                return st
            if time.time() - start_time > ST3:
                return False

    def on(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if not self.isOn():
            r = self.__command("power", ON)
            time.sleep(ST2)
            return ON == r

    def off(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if self.isOn():
            return OFF == self.__command("power", OFF)

    def isOn(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return ON == self.__command("power", "query")

    def isCecOn(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return ON == self.__command("hdmi-cec", "query")
    
    def cecOn(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if self.isCecOn():
            return True
        else:
            r = self.__command("hdmi-cec", ON)
            # time.sleep(ST1)
            return ON == r

    def cecOff(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if self.isCecOn():
            r = self.__command("hdmi-cec", OFF)
            # time.sleep(ST1)
            return ON == r
        else:
            return True
        
    def getVolume(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        start_time = time.time()
        while True:
            time.sleep(ST1)
            try:
                st = int(self.dev.command("volume query")[1])
            except:
                self.__reconnect()
                st = False
            if isinstance(st, int):
                return st
            if time.time() - start_time > ST4:
                return False

    def setVolume(self, vol):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if vol < 0:
            vol = 0
        if vol > 164:
            vol = 164
        start_time = time.time()
        while True:
            time.sleep(ST1)
            try:
                st = int(self.dev.command("volume " + str(vol))[1])
            except:
                self.__reconnect()
                st = False
            if isinstance(st, int):
                return st
            if time.time() - start_time > ST4:
                return False
    
    def getSource(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__command("source", "query")

    def setSource(self, src):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__command("source", src)
    
    def setTV(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(TV)

    def setBD(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(BD)

    def setSAT(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(SAT)

    def setCD(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(CD)

    def setFM(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(FM)

    def setAM(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(AM)

    def setNET(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(NET)

    def setPC(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(PC)

    def setSB(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(SB)

    def setUSB(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(USB)

    def setBT(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.setSource(BT)

    def setEnter(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__command("setup", "enter")
        # try:
        #     self.dev.command("setup enter")
        # except:
        #     pass
        # return True

    def getAudio(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__command("listening-mode", "query")

    def getAudioAll(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__command("audio-information", "query")
 
    def setAudio(self, src):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__command("listening-mode", src)

    def setStereo(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        s = self.getAudio()
        if s == STEREO:
            return True
        else:
            return self.setAudio(STEREO)

    def setDolby(self):
        if DEBUG:
            print(f"[VSX] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        s = self.getAudio()
        if s == DOLBY:
            return True
        else:
            return self.setAudio(DOLBY)


if __name__ == "__main__":
    v = Vsx()

    print("VSX is ON" if v.isOn() else "VSX is OFF")

    print("starting ...")
    v.on()
    time.sleep(5)

    print("get audio ...")
    print(v.getAudio())
    time.sleep(5)
    print("get audioAll ...")
    print(v.getAudioAll())
    time.sleep(5)
    print("set Stereo ...")
    print(v.setStereo())
    time.sleep(5)
    print("is CEC on ...")
    print(v.isCecOn())
    time.sleep(5)
    print("set Dolby ...")
    print(v.setDolby())
    time.sleep(5)
    print("set vol 40 ...")
    print(v.setVolume(84))
    time.sleep(5)
    print("set vol 35 ...")
    print(v.setVolume(94))
    time.sleep(5)
    print("get vol ...")
    print(v.getVolume())
    time.sleep(5)
    print("get src ...")
    s = v.getSource()
    print(s)
    time.sleep(5)
    print("set src TV ...")
    print(v.setTV())
    time.sleep(5)
    print("set src prev ...")
    print(v.setSource(s))
    time.sleep(5)

    print("stopping ...")
    v.off()
    time.sleep(5)
    print("VSX is ON" if v.isOn() else "VSX is OFF")

    v.close()

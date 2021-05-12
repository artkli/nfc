import socket
import sys
import time
from h import TVHOST, TVPORT1, TVPORT2


ST1 = 0.1
ST2 = 0.3
ST3 = 2.0


VOL2 = 64

class Tv:
    def __init__(self):
        pass

    def __del__(self):
        pass
    
    close = __del__    

    def __lircSend(self, dev, key):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect("/var/run/lirc/lircd")
        time.sleep(ST1)
        s.sendall("SEND_ONCE " + dev + " " + key + "\n")
        time.sleep(ST1)
        s.close()

    def __isPortOpen(self, ip=TVHOST, port=TVPORT1, timeout=ST3):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                    time.sleep(ST1)
                    s.connect((ip, int(port)))
                    s.shutdown(socket.SHUT_RDWR)
                    return True
            except:
                    return False
            finally:
                    s.close()

    def isOn(self):
        if not self.__isPortOpen(TVHOST, TVPORT2):
            return False
        else:
            if self.__isPortOpen():
                return True
            else:
                return False

    def on(self, decoder=False):
        if not self.isOn():
            if decoder:
                self.__lircSend("CANAL", "POWER")
                time.sleep(ST2)
            self.__lircSend("tv", "KEY_POWER")

    def off(self, decoder=False):
        if self.isOn():
            if decoder:
                self.__lircSend("CANAL", "POWER")
                time.sleep(ST2)
            self.__lircSend("tv", "KEY_POWER")

    def decoderRec(self):
        self.__lircSend("CANAL", "REC")

    def decoderOn(self):
        self.__lircSend("CANAL", "POWER")

    decoderOff = decoderOn

    def decoderStop(self):
        self.__lircSend("CANAL", "STOP")
        time.sleep(ST2)
        self.__lircSend("tv", "KEY_OK")

    def decoderList(self):
        self.__lircSend("CANAL", "LIST")


if __name__ == "__main__":
    t = Tv()
    print("TV is ON" if t.isOn() else "TV is OFF")
    print("starting ...")
    t.on(True)
    time.sleep(30)
    print("TV is ON" if t.isOn() else "TV is OFF")
    print("stopping ...")
    t.off(True)
    time.sleep(10)
    print("TV is ON" if t.isOn() else "TV is OFF")
    t.close()

import telnetlib
import time
from h import BDHOST, BDPORT


ST1 = 0.1
ST2 = 0.2
ST3 = 0.3
ST4 = 0.5
ST5 = 1.0
ST6 = 7.0
ST7 = 20.0


POWERON = b"PN\n\r"
POWEROFF = b"PF\n\r"
OPEN = b"OP\n\r"
CLOSE = b"CO\n\r"
STOP2 = b"99RJ\n\r"
PLAY = b"PL\n\r"
MODE = b"?P\n\r"

STOP = b"/A181AF38/RU\n\r"
UP = b"/A184FFFF/RU\n\r"
DOWN = b"/A185FFFF/RU\n\r"
MENU = b"/A181AFB0/RU\n\r"
ENTER = b"/A181AFEF/RU\n\r"
LEFT = b"/A187FFFF/RU\n\r"
RIGHT = b"/A186FFFF/RU\n\r"
NEXT = b"/A181AF3D/RU\n\r"
PREV = b"/A181AF3E/RU\n\r"
RETURN = b"/A181AFF4/RU\n\r"
EXIT = b"/A181AF20/RU\n\r"

STOPTUPLE = (EXIT, RETURN, STOP, STOP, RETURN, RETURN, RETURN, RETURN, EXIT)

HDMION = (UP, ENTER, DOWN, DOWN, ENTER, UP, UP, UP, UP, UP, ENTER, ENTER, RETURN, RETURN, RETURN, RETURN, RETURN)
HDMIOFF = (UP, ENTER, DOWN, DOWN, ENTER, UP, UP, UP, UP, UP, ENTER, UP, ENTER, RETURN, RETURN, RETURN, RETURN, RETURN)

class Bdp:
    def __init__(self, host=BDHOST, port=BDPORT):
        self.host = host
        self.port = port
        self.dev = telnetlib.Telnet(self.host, self.port)

    def __del__(self):
        self.dev.close()

    close = __del__

    def __send(self, command):
        self.dev.write(command)
        time.sleep(ST1)
        answer = self.dev.read_until(b"\n", 5).decode("UTF-8")
        if answer[0] == "R":
            return True
        else:
            return False
    
    def __sendTuple(self, input):
        for i in input:
            if not self.__send(i):
                return False
            if i == ENTER:
                time.sleep(ST4)    
            time.sleep(ST3)
        return True

    def hdmiOn(self):
        if not self.isOn():
            return False
        time.sleep(ST6)
        if not self.__sendTuple(STOPTUPLE):
            return False
        time.sleep(ST5)
        if not self.__send(MENU):
            return False
        time.sleep(ST5)
        return self.__sendTuple(HDMION)

    def hdmiOff(self):
        if not self.isOn():
            return False
        time.sleep(ST6)
        if not self.__sendTuple(STOPTUPLE):
            return False
        time.sleep(ST5)
        if not self.__send(MENU):
            return False
        time.sleep(ST5)
        return self.__sendTuple(HDMIOFF)

    def on(self):
        if not self.isOn():
            if self.__send(POWERON):
                start_time = time.time()
                while True:
                    st = self.status()
                    if st[0] == "P":
                        return True
                    if time.time() - start_time > ST7:
                        return False
                    time.sleep(ST4)
            else:
                return False
        else:
            return False

    def off(self):
        if self.isOn():
            if self.__send(POWEROFF):
                start_time = time.time()
                while True:
                    st = self.status()
                    if st[0] != "P":
                        return True
                    if time.time() - start_time > ST7:
                        return False
                    time.sleep(ST4)
            else:
                return False
        else:
            return False

    def status(self):
        self.dev.write(MODE)
        time.sleep(ST1)
        answer = self.dev.read_until(b"\n", 5).decode("UTF-8")
        return answer

    def isOn(self):
        if self.status()[0] == "P":
            return True
        else:
            return False


if __name__ == "__main__":
    b = Bdp()
    print("BDP is ON" if b.isOn() else "BDP is OFF")
    print("starting ...")
    b.on()
    print("BDP is ON" if b.isOn() else "BDP is OFF")
    time.sleep(4)
    print("hdmi on ...")
    b.hdmiOn()
    time.sleep(4)
    print("hdmi off ...")
    b.hdmiOff()
    time.sleep(9)
    print("stopping ...")
    b.off()
    print("BDP is ON" if b.isOn() else "BDP is OFF")

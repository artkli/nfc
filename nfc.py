import os
import sys
import time

from datetime import datetime
from influxdb import InfluxDBClient

from vsx import Vsx, CD, AM, NET, BT, FM, BD, TV, SAT, PC, SB, BT
from bdp import Bdp
from tv import Tv
from pc import Pc
from led import Led
from h import USER, DB, PASS, DEBUG


ST1 = 1.0
ST2 = 2.0
STF = 0.1
SFL = 30
VOL1 = 84
VOL2 = 84
VOL3 = 44

FILE_SAT = "/run/lock/nfc-sat.lock"
FILE_CD = "/run/lock/nfc-cd.lock"
FILE_RADIO = "/run/lock/nfc-radio.lock"
FILE_NET = "/run/lock/nfc-net.lock"
FILE_FILM = "/run/lock/nfc-film.lock"
FILE_PC = "/run/lock/nfc-pc.lock"
FILE_BT = "/run/lock/nfc-bt.lock"
FILE_OFF = ""

FILE_LOCK = "/run/lock/nfc.lock"

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

def setFile(file):
    if DEBUG:
        print(f"[NFC] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
    vd = 0
    if file == FILE_OFF:
        for f in (FILE_SAT, FILE_CD, FILE_RADIO, FILE_NET, FILE_FILM, FILE_PC, FILE_BT):
            if os.path.exists(f):
                os.remove(f)
    for c, f in enumerate([FILE_SAT, FILE_CD, FILE_RADIO, FILE_NET, FILE_FILM, FILE_PC, FILE_BT]):
        if f == file:
            vd = c + 1
            if not os.path.exists(file):
                open(f, 'x')
        else:
            if os.path.exists(f):
                os.remove(f)

    v = Vsx()
    if v.isOn() and v.getSource() == TV:
        vd = 8
    v.close()

    data = [{
        "measurement": "home",
        "time": datetime.now(),
        "fields": {
            "value": vd
        }
    }]
    client = InfluxDBClient('localhost', 8086, USER, PASS, DB)
    client.switch_database(DB)
    client.write_points(data)
    client.close()


class HomeTheatre:
    def __init__(self, tv, br, vsx, decoder, pc, vsx_set):
        self.tv = tv
        self.br = br
        self.vsx = vsx
        self.decoder = decoder
        self.pc = pc
        self.vsx_set = vsx_set

    def __eq__(self, other):
        return self.tv == other.tv and \
               self.br == other.br and \
               self.vsx == other.vsx and \
               self.pc == other.pc and \
               self.vsx_set == other.vsx_set

    def __sub__(self, other):
        if self.tv == other.tv:
            tv = 0
        elif self.tv:
            tv = -1
        else:
            tv = 1
        if self.br == other.br:
            br = 0
        elif self.br:
            br = -1
        else:
            br = 1
        if self.vsx == other.vsx:
            vsx = 0
        elif self.vsx:
            vsx = -1
        else:
            vsx = 1
        if other.vsx_set == SAT and self.vsx_set != SAT:
            decoder = 1
        elif other.vsx_set != SAT and self.vsx_set == SAT:
            decoder = -1
        else:
            decoder = 0
        if self.pc == other.pc:
            pc = 0
        elif self.pc:
            pc = -1
        else:
            pc = 1
        return tv, br, vsx, decoder, pc, other.vsx_set

    def __str__(self):
        return " ".join((str(self.tv), str(self.br), str(self.vsx), str(self.decoder), str(self.pc), str(self.vsx_set)))


TELEVISION = HomeTheatre(True, False, True, True, False, SAT)
MUSIC = HomeTheatre(False, True, True, False, False, CD)
RADIO = HomeTheatre(False, False, True, False, False, FM)
NETRADIO = HomeTheatre(False, False, True, False, False, NET)
BLUETOOTH = HomeTheatre(False, False, True, False, False, BT)
BAMP1 = HomeTheatre(True, False, True, False, True, SB)
COMPUTER = HomeTheatre(True, False, True, False, False, PC)
FILM = HomeTheatre(True, True, True, False, False, BD)
TVAPP = HomeTheatre(True, False, True, False, False, TV)
OFFHT = HomeTheatre(False, False, False, False, False, False)

def run(arg):
    l = Led()
    l.on()

    if DEBUG:
        print(f"[NFC] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
    mustend = time.time() + SFL
    while time.time() < mustend:
        if not os.path.exists(FILE_LOCK):
            break
        time.sleep(STF)
        l.off()
        time.sleep(STF)
        l.on()
    open(FILE_LOCK, 'x')

    v = Vsx()
    b = Bdp()
    t = Tv()
    p = Pc()

    def tvOff():
        if DEBUG:
            print(f"[NFC] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        v.cecOff()
        time.sleep(ST1)
        t.off()
        time.sleep(ST2)
        v.cecOn()
        time.sleep(ST1)

    def tvOn():
        if DEBUG:
            print(f"[NFC] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        t.on()
        time.sleep(ST2)

    def vsxSet(val):
        if DEBUG:
            print(f"[NFC] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        v.cecOn()
        if val == CD:
            v.setCD()
            v.setVolume(VOL1)
            v.setStereo()
        elif val == NET:
            v.setNET()
            v.setVolume(VOL3)
            time.sleep(ST2)
            v.setEnter()
            time.sleep(ST1)
            v.setEnter()
            time.sleep(ST1)
            v.setEnter()
            v.setStereo()
        elif val == FM:
            v.setFM()
            v.setVolume(VOL1)
            v.setStereo()
        elif val == BT:
            v.setBT()
            v.setVolume(VOL1)
            v.setDolby()
        elif val == BD:
            v.setBD()
            v.setVolume(VOL1)
            v.setDolby()
        elif val == SAT:
            v.setSAT()         
            v.setVolume(VOL2)
            v.setDolby()
            t.setHdmi3()
        elif val == SB:
            v.setSB()
            v.setVolume(VOL2)
            v.setDolby()

    # deviceOn = [t.on, b.on, v.on, t.decoderOn, p.on, vsxSet]
    deviceOn = [tvOn, b.on, v.on, t.decoderOn, p.on, vsxSet]
    deviceOff = [tvOff, b.off, v.off, t.decoderOff, p.off, vsxSet]

    def changeHt(ht):
        if DEBUG:
            print(f"[NFC] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
            print(f"[NFC] o {datetime.now()} ht {ht}")
        for i, value in enumerate(ht):
            if value == -1:
                deviceOff[i]()
            elif value == 1:
                deviceOn[i]()
            elif type(value) == str:
                deviceOn[len(ht)-1](value)

    if v.isOn():
        vSource = v.getSource()
        currentHt = HomeTheatre(t.isOn(), b.isOn(), True, True if vSource == SAT else False, p.isOn(), vSource)
    else:
        currentHt = HomeTheatre(t.isOn(), b.isOn(), False, False, p.isOn(), False)

    if arg == 'sat':
        newHt = TELEVISION
        fn = FILE_SAT
    elif arg == 'canal':
        vsxSet(SAT)
    elif arg == 'cd':
        newHt = MUSIC
        fn = FILE_CD
    elif arg == 'radio':
        newHt = RADIO
        fn = FILE_RADIO
    elif arg == 'bt':
        newHt = BLUETOOTH
        fn = FILE_BT
    elif arg == 'net':
        newHt = NETRADIO
        fn = FILE_NET
    elif arg == 'film':
        newHt = FILM
        fn = FILE_FILM
    elif arg == 'pc':
        newHt = BAMP1
        fn = FILE_PC
    else:
        p.close()
        t.close()
        b.close()
        v.close()
        if os.path.exists(FILE_LOCK):
            os.remove(FILE_LOCK)
        sys.exit(1)

    if currentHt == newHt or currentHt not in (TELEVISION, MUSIC, RADIO, BLUETOOTH, NETRADIO, FILM, BAMP1, OFFHT):
        changeHt(currentHt - OFFHT)
        setFile(FILE_OFF)
    else:
        changeHt(currentHt - newHt)
        setFile(fn)

    p.close()
    t.close()
    b.close()
    v.close()

    if os.path.exists(FILE_LOCK):
        os.remove(FILE_LOCK)

    l.off()
    l.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(sys.argv[1].lower())
    else:
        sys.exit(1)

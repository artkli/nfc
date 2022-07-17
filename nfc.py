import os
import sys
import time
from vsx import Vsx, CD, AM, NET, BT, FM, BD, TV, SAT, PC, SB
from bdp import Bdp
from tv import Tv
from pc import Pc

ST1 = 1.0
ST2 = 2.0
VOL1 = 84
VOL2 = 84
VOL3 = 44

FILE_SAT = "/home/pi/alexa/nfc-sat.lock"
FILE_CD = "/home/pi/alexa/nfc-cd.lock"
FILE_RADIO = "/home/pi/alexa/nfc-radio.lock"
FILE_NET = "/home/pi/alexa/nfc-net.lock"
FILE_FILM = "/home/pi/alexa/nfc-film.lock"
FILE_PC = "/home/pi/alexa/nfc-pc.lock"
FILE_OFF = ""

FILE_LOCK = "/home/pi/nfc/app/nfc.lock"


def setFile(file):
    if file == FILE_OFF:
        for f in (FILE_SAT, FILE_CD, FILE_RADIO, FILE_NET, FILE_FILM, FILE_PC):
            if os.path.exists(f):
                os.remove(f)
    if not os.path.exists(file):
        for f in (FILE_SAT, FILE_CD, FILE_RADIO, FILE_NET, FILE_FILM, FILE_PC):
            if f == file:
                open(f, 'x')
            else:
                if os.path.exists(f):
                    os.remove(f)


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
BAMP1 = HomeTheatre(True, False, True, False, True, SB)
COMPUTER = HomeTheatre(True, False, True, False, False, PC)
FILM = HomeTheatre(True, True, True, False, False, BD)
TVAPP = HomeTheatre(True, False, True, False, False, TV)
OFFHT = HomeTheatre(False, False, False, False, False, False)


def run(arg):
    mustend = time.time() + 30
    while time.time() < mustend:
        if not os.path.exists(FILE_LOCK):
            break
        time.sleep(0.5)
    open(FILE_LOCK, 'x')

    v = Vsx()
    b = Bdp()
    t = Tv()
    p = Pc()

    def tvOff():
        v.cecOff()
        t.off()
        v.cecOn()

    def vsxSet(val):
        time.sleep(ST1)
        if val == CD:
            v.setVolume(VOL1)
            v.setCD()
        elif val == NET:
            v.setVolume(VOL3)
            v.setNET()
            time.sleep(ST2)
            v.setEnter()
            time.sleep(ST1)
            v.setEnter()
            time.sleep(ST1)
            v.setEnter()
        elif val == FM:
            v.setVolume(VOL1)
            v.setFM()
        elif val == BD:
            v.setVolume(VOL1)
            v.setBD()
        elif val == SAT:
            v.setVolume(VOL2)
            v.setSAT()
            t.setHdmi3()
        elif val == SB:
            v.setVolume(VOL2)
            v.setSB()

    deviceOn = [t.on, b.on, v.on, t.decoderOn, p.on, vsxSet]
    deviceOff = [tvOff, b.off, v.off, t.decoderOff, p.off, vsxSet]

    def changeHt(ht):
        for i, v in enumerate(ht):
            if v == -1:
                deviceOff[i]()
            elif v == 1:
                deviceOn[i]()
            elif type(v) == str:
                deviceOn[len(ht)-1](v)

    if v.isOn():
        vSource = v.getSource()
        currentHt = HomeTheatre(t.isOn(), b.isOn(), True, True if vSource == SAT else False, p.isOn(), vSource)
    else:
        currentHt = HomeTheatre(t.isOn(), b.isOn(), False, False, p.isOn(), False)

    if arg == 'sat':
        newHt = TELEVISION
        fn = FILE_SAT
    elif arg == 'cd':
        newHt = MUSIC
        fn = FILE_CD
    elif arg == 'radio':
        newHt = RADIO
        fn = FILE_RADIO
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

    if currentHt == newHt or currentHt not in (TELEVISION, MUSIC, RADIO, NETRADIO, FILM, BAMP1, OFFHT):
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


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(sys.argv[1].lower())
    else:
        sys.exit(1)

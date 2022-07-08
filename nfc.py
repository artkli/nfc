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
            v.setCD()
            v.setVolume(VOL1)
        elif val == NET:
            v.setNET()
            v.setVolume(VOL3)
            time.sleep(ST2)
            v.setEnter()
            time.sleep(ST1)
            v.setEnter()
            time.sleep(ST1)
            v.setEnter()
        elif val == FM:
            v.setFM()
            v.setVolume(VOL1)
        elif val == BD:
            v.setBD()
            v.setVolume(VOL1)
        elif val == SAT:
            v.setSAT()
            v.setVolume(VOL2)
            t.setHdmi3()
        elif val == SB:
            v.setSB()
            v.setVolume(VOL2)

    deviceOn = [t.on, b.on, v.on, t.decoderOn, p.on, vsxSet]
    deviceOff = [tvOff, b.off, v.off, t.decoderOff, p.off, vsxSet]

    def changeHt(ht):
        for i, v in enumerate(ht):
            if v == -1:
                deviceOff[i]()
            elif v == 1:
                deviceOn[i]()
            elif type(v) == str:
                deviceOn[5](v)

    if v.isOn():
        vSource = v.getSource()
        currentHt = HomeTheatre(t.isOn(), b.isOn(), True, True if vSource == SAT else False, p.isOn(), vSource)
    else:
        currentHt = HomeTheatre(t.isOn(), b.isOn(), False, False, p.isOn(), False)

    if arg == 'sat':
        newHt = TELEVISION
    elif arg == 'cd':
        newHt = MUSIC
    elif arg == 'radio':
        newHt = RADIO
    elif arg == 'net':
        newHt = NETRADIO
    elif arg == 'film':
        newHt = FILM
    elif arg == 'pc':
        newHt = BAMP1
    else:
        p.close()
        t.close()
        b.close()
        v.close()
        sys.exit(1)

    if currentHt == newHt:
        changeHt(currentHt - OFFHT)
    else:
        changeHt(currentHt - newHt)

    p.close()
    t.close()
    b.close()
    v.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(sys.argv[1].lower())
    else:
        sys.exit(1)

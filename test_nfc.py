import os
import sys
import time
from vsx import Vsx, CD, AM, NET, BT, FM, BD, TV, SAT, PC, SB
from bdp import Bdp
from tv import Tv
from pc import Pc
from nfc import HomeTheatre, setFile
from nfc import TELEVISION, MUSIC, RADIO, NETRADIO, BAMP1, COMPUTER, FILM, TVAPP, OFFHT
from nfc import FILE_SAT, FILE_CD, FILE_RADIO, FILE_NET, FILE_FILM, FILE_PC, FILE_OFF
from nfc import FILE_LOCK


def run():
    mustend = time.time() + 30
    while time.time() < mustend:
        if os.path.exists(FILE_LOCK):
            time.sleep(0.5)
        else:
            break
    if os.path.exists(FILE_LOCK):
        os.remove(FILE_LOCK)
    open(FILE_LOCK, 'x')

    v = Vsx()
    b = Bdp()
    t = Tv()
    p = Pc()

    if v.isOn():
        vSource = v.getSource()
        currentHt = HomeTheatre(t.isOn(), b.isOn(), True, True if vSource == SAT else False, p.isOn(), vSource)
    else:
        currentHt = HomeTheatre(t.isOn(), b.isOn(), False, False, p.isOn(), False)
       
    if currentHt == TELEVISION:
        setFile(FILE_SAT)
    elif currentHt == MUSIC:
        setFile(FILE_CD)
    elif currentHt == RADIO:
        setFile(FILE_RADIO)
    elif currentHt == NETRADIO:
        setFile(FILE_NET)
    elif currentHt == FILM:
        setFile(FILE_FILM)
    elif currentHt == BAMP1:
        setFile(FILE_PC)
    else:
        setFile(FILE_OFF)

    p.close()
    t.close()
    b.close()
    v.close()
    if os.path.exists(FILE_LOCK):
        os.remove(FILE_LOCK)

if __name__ == "__main__":
    run()

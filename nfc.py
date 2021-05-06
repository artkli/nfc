import sys
import time
from vsx import Vsx, CD, FM, BD, TV, SAT
from bdp import Bdp
from tv import Tv

ST = 2.0
VOL1 = 84
VOL2 = 64

def checkOn():
    v = Vsx()
    b = Bdp()
    t = Tv()

    if v.isOn():
        if t.isOn() and not b.isOn() and v.getSource() == SAT:
            answer = SAT
        elif t.isOn() and b.isOn() and v.getSource() == BD:
            answer = BD
        elif not t.isOn() and b.isOn() and v.getSource() == CD:
            answer = CD
        elif not t.isOn() and not b.isOn() and v.getSource() == FM:
            answer = FM
        else:
            answer = 'other'
    else:
        answer = 'off'

    t.close()
    b.close()
    v.close()

    return answer


if __name__ == "__main__":
    if len(sys.argv) == 2:
        status = checkOn()

        if sys.argv[1].lower() == 'sat':
            if status == SAT:
                Tv().off(True)
                Vsx().off()
            else:
                if status == 'other':
                    Tv().on()
                elif Tv().isOn():
                    Tv().decoderOn()
                else:
                    Tv().on(True)
                Bdp().off()
                v = Vsx()
                v.on()
                v.setSAT()
                v.close()

        elif sys.argv[1].lower() == 'rec':
            Tv().decoderRec()

        elif sys.argv[1].lower() == 'list':
            if status == SAT:
                Tv().decoderList()

        elif sys.argv[1].lower() == 'stop':
            Tv().decoderRec()

        elif sys.argv[1].lower() == 'cd':
            if status == CD:
                Bdp().off()
                Vsx().off()
            else:
                b = Bdp()
                b.on()
                b.hdmiOff()
                v = Vsx()
                v.on()
                v.setCD()
                v.setVolume(VOL1)
                v.cecOff()
                if status == SAT:
                    Tv().off(True)
                else:
                    Tv().off()
                time.sleep(ST)
                v.cecOn()
                b.close()
                v.close()

        elif sys.argv[1].lower() == 'radio':
            if status == FM:
                Vsx().off()
            else:
                v = Vsx()
                v.on()
                v.setFM()
                v.setVolume(VOL1)
                v.cecOff()
                Bdp().off()
                if status == SAT:
                    Tv().off(True)
                else:
                    Tv().off()
                time.sleep(ST)
                v.cecOn()
                v.close()

        elif sys.argv[1].lower() == 'film':
            if status == BD:
                Vsx().off()
                b = Bdp()
                b.hdmiOff()
                b.off()
                b.close()
                Tv().off()
            else:
                v = Vsx()
                b = Bdp()
                b.on()
                b.hdmiOn()
                v.on()
                v.setBD()
                v.setVolume(VOL1)
                Tv().on()
                b.close()
                v.close()

        else:
            sys.exit(1)

    else:
        sys.exit(1)

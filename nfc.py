import sys
from vsx import Vsx, CD, FM, BD, TV, SAT
from bdp import Bdp
from tv import Tv

VOL1 = 84
VOL2 = 64

def checkOn():
    v = Vsx()
    b = Bdp()
    t = Tv()

    if v.isOn():
        tOn = t.isOn()
        bOn = b.isOn()
        vSource = v.getSource()
        if tOn and not bOn and vSource == SAT:
            answer = SAT
        elif tOn and bOn and vSource == BD:
            answer = BD
        elif not tOn and bOn and vSource == CD:
            answer = CD
        elif not tOn and not bOn and vSource == FM:
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
            v = Vsx()
            b = Bdp()

            if status == SAT:
                Tv().off(True)
                v.off()
            elif status == 'other':
                Tv().off()
                v.off()
                b.hdmiOff()
                b.off()
            else:
                if status == BD:
                    Tv().decoderOn()
                    b.hdmiOff()
                    b.off()
                elif status == CD:
                    Tv().on(True)
                    b.off()
                else:
                    Tv().on(True)
                v.on()
                v.setSAT()
                v.setVolume(VOL2)
            b.close()
            v.close()

        elif sys.argv[1].lower() == 'rec':
            Tv().decoderRec()

        elif sys.argv[1].lower() == 'list':
            if status == SAT:
                Tv().decoderList()

        elif sys.argv[1].lower() == 'stop':
            Tv().decoderRec()

        elif sys.argv[1].lower() == 'cd':
            v = Vsx()
            b = Bdp()
            if status == CD:
                b.off()
                v.off()
            elif status == 'other':
                Tv().off()
                v.off()
                b.hdmiOff()
                b.off()
            else:
                v.on()
                v.setCD()
                v.setVolume(VOL1)
                v.cecOff()
                if status == SAT:
                    Tv().off(True)
                else:
                    Tv().off()
                b.on()
                b.hdmiOff()
                v.cecOn()
            b.close()
            v.close()

        elif sys.argv[1].lower() == 'radio':
            v = Vsx()
            b = Bdp()
            if status == FM:
                v.off()
            elif status == 'other':
                Tv().off()
                v.off()
                b.hdmiOff()
                b.off()
            else:
                v.on()
                v.setFM()
                v.setVolume(VOL1)
                v.cecOff()
                if status == SAT:
                    Tv().off(True)
                else:
                    Tv().off()
                if status == BD:
                    b.hdmiOff()
                b.off()
                v.cecOn()
            b.close()
            v.close()

        elif sys.argv[1].lower() == 'film':
            v = Vsx()
            b = Bdp()
            if status == BD or status == 'other':
                v.off()
                b.hdmiOff()
                b.off()
                Tv().off()
            else:
                v.on()
                b.on()
                if status == SAT:
                    Tv().decoderOff()
                v.setBD()
                v.setVolume(VOL1)
                b.hdmiOn()
                Tv().on()
            b.close()
            v.close()

        else:
            sys.exit(1)

    else:
        sys.exit(1)

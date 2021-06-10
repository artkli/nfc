import socket
import sys
import os
import time
import requests
import wakeonlan

from samsungtvws import SamsungTVWS

from h import TVHOST, DHOST, TVPORT1, TVPORT2, TVARP


sys.path.append('../')

ST1 = 0.1
ST2 = 0.3
ST3 = 2.0
ST4 = 10.0

VOL2 = 64

class Tv:
    def __init__(self):
        self.address = 'http://' + DHOST + ':8080/control/rcu'

        token_file = os.path.dirname(os.path.realpath(__file__)) + '/tv-token'
        self.tvr = SamsungTVWS(host=TVHOST, port=8002, token_file=token_file)

    def __del__(self):
        pass
    
    close = __del__    

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
        start_time = time.time()
        while True:
            s1 = 1 if self.__isPortOpen() else 0
            s2 = 2 if self.__isPortOpen(TVHOST, TVPORT2) else 0
            st = s1 + s2
            if st == 3:
                return True
            elif st == 0:
                return False
            if time.time() - start_time > ST4:
                return False
            time.sleep(ST2)

    def on(self, decoder=False):
        if decoder:
            requests.post(self.address, data={'Keypress': 'Key' + 'StandBy'}, timeout=ST3)
            time.sleep(ST2)
        start_time = time.time()
        while True:
            wakeonlan.send_magic_packet(TVARP)
            if self.isOn():
                return True
            if time.time() - start_time > ST4:
                return False

    def setHdmi3(self):
        time.sleep(ST3)
        if self.isOn():
            self.tvr.send_key('KEY_SOURCE')
            self.tvr.send_key('KEY_DOWN')
            self.tvr.send_key('KEY_UP')
            for i in range(10):
                self.tvr.send_key('KEY_LEFT')
            for i in range(3):
                self.tvr.send_key('KEY_RIGHT')
            self.tvr.send_key('KEY_ENTER')

    def off(self, decoder=False):
        if self.isOn():
            if decoder:
                requests.post(self.address, data={'Keypress': 'Key' + 'StandBy'}, timeout=ST3)
                time.sleep(ST2)
            self.tvr.shortcuts().power()

    def decoderOn(self):
        requests.post(self.address, data={'Keypress': 'Key' + 'StandBy'}, timeout=ST3)

    decoderOff = decoderOn


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

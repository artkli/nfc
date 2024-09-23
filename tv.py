import json
import time
import websocket
import sys
import os
import base64
import requests
import socket
import wakeonlan
import ssl

from icmplib import ping
from datetime import datetime

from h import TVHOST, TVTOKEN, TVNAME, TVPORT1, TVPORT2, TVPORT3, TVPORT4, TVARP, TVWARP, DHOST, TVRNAME, DEBUG

ST1 = 0.5
ST2 = 1.0
ST3 = 6.0
ST4 = 15.0
ST5 = 60.0

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
sys.path.append('../')
token_file_name = os.path.dirname(os.path.realpath(__file__)) + '/token-tv'

class Tv():
    def __init__(self):
        self.decoder_url = 'http://' + DHOST + ':8080/control/rcu'
        self.token = self.__readToken()
        self.name = self.__encodeName(TVRNAME)
        self.tv_url = f'wss://{TVHOST}:{TVPORT3}/api/v2/channels/samsung.remote.control?name={self.name}&token={self.token}'
        self.connection = None
        self.connected = False

    @staticmethod
    def __encodeName(string):
        return base64.b64encode(string.encode()).decode("utf-8")

    def __readResponse(self):
        resp = self.connection.recv()
        resp = json.loads(resp)

        ignored_events = ['ms.remote.touchDisable', 'ed.edenTV.update', 'ms.remote.touchEnable']

        if resp['event'] in ignored_events:
            resp = self.__readResponse()
        return resp

    def __saveToken(self, token):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        with open(token_file_name, 'w') as token_file:
            token_file.write(token)

    def __readToken(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        try:
            with open(token_file_name) as token_file:
                return token_file.readline()
        except:
            return ""

    def __connect(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        self.connection = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.connection.connect(self.tv_url)
        response = self.__readResponse()
        if response['event'] != "ms.channel.connect":
            self.close()
            raise Exception(response)
        if response.get('data'):
            self.connected = True
            if response.get('data').get('token') != None:
                self.__saveToken(response.get('data').get('token'))
        time.sleep(ST1)
        
    def __reconnect(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        self.close()
        time.sleep(ST2)
        if self.__isPortOpen():
            self.__connect()
        
    def __del__(self):
        self.close()

    def close(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if self.connected:
            self.connection.close()
            self.connection = None
            self.connected = False

    def __isPortOpen(self, ip=TVHOST, port=TVPORT3, time_out=ST4):
        try:
            p = ping(ip, count=1, timeout=time_out)
        except:
            return False
        if p.packets_received == 0:
            return False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(time_out)
        try:
            s.connect((ip, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except:
            return False
        finally:
            s.close()

    def isOn(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        return self.__isPortOpen()

    def on(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        wakeonlan.send_magic_packet(TVWARP)
        wakeonlan.send_magic_packet(TVARP)
        start_time = time.time()
        while True:
            time.sleep(ST1)
            if self.__isPortOpen():
                break
            if time.time() - start_time > ST4:
                return False
        time.sleep(ST2)
        self.__connect()
        return True         

    def off(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if self.isOn():
            if not self.connected:
                self.__connect()
            self.power()
            start_time = time.time()
            while True:
                time.sleep(ST1)
                if not self.__isPortOpen():
                    return True
                if time.time() - start_time > ST5:
                    return False

    def send_key(self, key):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        payload = json.dumps({
            'method': 'ms.remote.control',
            'params': {
                'Cmd': 'Click',
                'DataOfCmd': key,
                'Option': 'false',
                'TypeOfRemote': 'SendRemoteKey'
            }
        })
        start_time = time.time()
        while True:
            time.sleep(ST1)
            try:
                st = self.connection.send(payload)
            except:
                self.__reconnect()
                st = False
                time.sleep(ST1)
            if isinstance(st, int):
                time.sleep(ST1)
                return True
            if time.time() - start_time > ST3:
                return False


    def power(self):
        self.send_key('KEY_POWER')

    def home(self):
        self.send_key('KEY_HOME')

    def menu(self):
        self.send_key('KEY_MENU')

    def source(self):
        self.send_key('KEY_SOURCE')

    def guide(self):
        self.send_key('KEY_GUIDE')

    def tools(self):
        self.send_key('KEY_TOOLS')

    def info(self):
        self.send_key('KEY_INFO')

    def up(self):
        self.send_key('KEY_UP')

    def down(self):
        self.send_key('KEY_DOWN')

    def left(self):
        self.send_key('KEY_LEFT')

    def right(self):
        self.send_key('KEY_RIGHT')

    def enter(self):
        self.send_key('KEY_ENTER')

    def back(self):
        self.send_key('KEY_RETURN')

    def hdmi(self):
        self.send_key('KEY_HDMI')

    def channel(self, ch):
        for c in str(ch):
            self.digit(c)
        self.enter()

    def digit(self, d):
        self.send_key('KEY_' + d)

    def channel_up(self):
        self.send_key('KEY_CHUP')

    def channel_down(self):
        self.send_key('KEY_CHDOWN')

    def volume_up(self):
        self.send_key('KEY_VOLUP')

    def volume_down(self):
        self.send_key('KEY_VOLDOWN')

    def mute(self):
        self.send_key('KEY_MUTE')

    def setHdmi3(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        if self.isOn():
            time.sleep(ST4)
            self.__reconnect()
            self.send_key('KEY_HOME')
            time.sleep(ST2)
            self.send_key('KEY_RIGHT')
            time.sleep(ST2)
            self.send_key('KEY_ENTER')
            """
            time.sleep(ST2)
            self.send_key('KEY_RETURN')
            time.sleep(ST2)
            self.send_key('KEY_RETURN')
            time.sleep(ST2)
            self.send_key('KEY_6')
            """

    def decoderOn(self):
        if DEBUG:
            print(f"[TV] o {datetime.now()} jestem w funkcji {currentFuncName()} wywołanej z {currentFuncName(1)}")
        try:
            requests.post(self.decoder_url, data={'Keypress': 'Key' + 'StandBy'}, timeout=ST3)
            rv = True
        except:
            rv = False
        return rv

    decoderOff = decoderOn

if __name__ == "__main__":
    t = Tv()
    print("włączony?")
    print(t.isOn())
    time.sleep(5)
    print("Off ...")
    t.off()
    print("tv off")
    t.decoderOff()
    print("dekoder off")
    time.sleep(5)
    print("On ...")
    t.on()
    print("tv on")
    t.decoderOn()
    print("dekoder on")
    t.close()

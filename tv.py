import sys
import os
import time
import requests
import aiohttp
import asyncio
import socket
import pysmartthings
import wakeonlan

from icmplib import ping
from samsungtvws import SamsungTVWS

from h import TVHOST, TVTOKEN, TVNAME, TVPORT1, TVPORT2, TVPORT3, TVARP, DHOST

DNSIP  = "8.8.8.8"
STHOST = "api.smartthings.com"
STPORT = 443

ST1 = 0.5
ST2 = 1.0
ST3 = 3.0
ST4 = 10.0

VOL2 = 84

class Tv:
    def __init__(self):
        sys.path.append('../')
        self.token = TVTOKEN
        self.address = 'http://' + DHOST + ':8080/control/rcu'
        self.online = self.__isPortOpen(STHOST, STPORT)

        token_file = os.path.dirname(os.path.realpath(__file__)) + '/tv-token'
        self.tvr = SamsungTVWS(host=TVHOST, port=TVPORT3, token_file=token_file)

    def __del__(self):
        self.tvr.close()
    
    close = __del__

    def __isPortOpen(self, ip=TVHOST, port=TVPORT1, timeout=ST4):
        try:
            p = ping(DNSIP, count=1, timeout=ST3)
        except:
            return False
        if p.packets_received == 0:
            return False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((ip, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            return True
        except:
            return False
        finally:
            s.close()

    async def __findTv(self, api):
        devices = await api.devices()
        for device in devices :
            if device.label == TVNAME:
                return device
        return None

    async def __foundTv(self):
        async with aiohttp.ClientSession() as session:
            api = pysmartthings.SmartThings(session, self.token)
            self.tv = await self.__findTv(api)
            return self.tv

    async def __on(self):
        async with aiohttp.ClientSession() as session:
            api = pysmartthings.SmartThings(session, self.token)
            self.tv = await self.__findTv(api)
            await self.tv.command("main", "switch", "on")

    async def __off(self):
        async with aiohttp.ClientSession() as session:
            api = pysmartthings.SmartThings(session, self.token)
            self.tv = await self.__findTv(api)
            await self.tv.command("main", "switch", "off")

    async def __isOn(self):
        async with aiohttp.ClientSession() as session:
            api = pysmartthings.SmartThings(session, self.token)
            self.tv = await self.__findTv(api)
            await self.tv.status.refresh()
            return self.tv.status.switch

    def foundTv(self):
        if self.online:
            return False if asyncio.run(self.__foundTv()) is None else True 
        else:
            return False

    def isOn(self):
        if self.online:
            return asyncio.run(self.__isOn())
        else:
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

    def decoderOn(self):
        try:
            requests.post(self.address, data={'Keypress': 'Key' + 'StandBy'}, timeout=ST3)
            rv = True
        except:
            rv = False
        return rv

    decoderOff = decoderOn

    def on(self, decoder=False):
        if decoder:
            if not self.decoderOn():
                return False

        if self.online:
            asyncio.run(self.__on())
        
        wakeonlan.send_magic_packet(TVARP)

    def off(self, decoder=False):
        if self.isOn():
            if decoder:
                self.decoderOff()
            if self.online:
                asyncio.run(self.__off())
            else:
                self.tvr.shortcuts().power()

    def setHdmi3(self):
        if self.isOn():
            time.sleep(ST4)
            self.tvr.send_key('KEY_HOME')
            time.sleep(ST1)
            self.tvr.send_key('KEY_RIGHT')
            time.sleep(ST1)
            self.tvr.send_key('KEY_ENTER')
            """
            time.sleep(ST2)
            self.tvr.send_key('KEY_RETURN')
            time.sleep(ST1)
            self.tvr.send_key('KEY_RETURN')
            time.sleep(ST1)
            self.tvr.send_key('KEY_6')
            """


if __name__ == "__main__":
    t = Tv()
    print(t.foundTv())
    print("TV is ON" if t.isOn() else "TV is OFF")
    print("starting ...")
    t.on(False)
    print("HDMI3 ...")
    time.sleep(3)
    t.setHdmi3()
    time.sleep(10)
    print("TV is ON" if t.isOn() else "TV is OFF")
    print("stopping ...")
    t.off(False)
    time.sleep(10)
    print("TV is ON" if t.isOn() else "TV is OFF")
    t.close()

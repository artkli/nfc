from systemd import journal
import json
import paho.mqtt.client as mqtt
import datetime
import eiscp

from influxdb import InfluxDBClient
from h import VSXHOST
from nfc import run
from vsx import Vsx
from led import Led

DB = 'baza'
USER = 'pep'
PASS = 'pep'

DEBUG = True


def save_przycisk(state):
    data = [{
        "measurement": "przycisk",
        "time": datetime.datetime.utcnow(),
        "fields": {
            "value": state
        }
    }]

    client = InfluxDBClient('localhost', 8086, USER, PASS, DB)
    client.switch_database(DB)
    client.write_points(data)
    client.close()

def save_start(state):
    data = [{
        "measurement": "tv_start",
        "time": datetime.datetime.utcnow(),
        "fields": {
            "value": state
        }
    }]

    client = InfluxDBClient('localhost', 8086, USER, PASS, DB)
    client.switch_database(DB)
    client.write_points(data)
    client.close()

def mes(s):
    if DEBUG == True:
        journal.write(s)
        # print(s)
    else:
        pass


def on_message(mqttc, obj, msg):
    mes("Przycisk: coś przyszło")
    j = json.loads(str(msg.payload.decode("utf-8","ignore")))
    mes("Przycisk: {}".format(j))

    if 'action' in j.keys():
        state = str(j["action"])

        v = Vsx()
        von = v.isOn()
        v.close()

        mes("Przycisk: {} | VSX on: {}".format(state, von))

        if state == 'single':
            save_przycisk(1)
            if not von:
                Led().blink()
                run("sat")
                save_start(1)
                mes("Przycisk: ON")
        elif state == 'double':
            save_przycisk(2)
            if von:
                Led().twice()
                run("sat")
                save_start(2)
                mes("Przycisk: OFF")

    mes("Przycisk: obsłużone")


def on_connect(mqttc, obj, flags, reason_code, properties):
    if reason_code == 0:
        mes("Podłączony")
        save_przycisk(3)
    else:
        mes("Nie podłączony")


def on_disconnect(mqttc, userdata, reason_code, properties):
    if reason_code != 0:
        mes("Utracone połaczenie. Łaczę ponownie")
        save_przycisk(3)
        mqttc.reconnect()


mes("Program started")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.connect("127.0.0.1", 1883, 60)
mqttc.subscribe("zigbee2mqtt/przycisk", 0)

mqttc.loop_forever()

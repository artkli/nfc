import logging
from systemd import journal
import os
import json
import paho.mqtt.client as mqtt
import time
import datetime
import eiscp
from influxdb import InfluxDBClient
from h import VSXHOST
from nfc import FILE_LOCK, run


DB = 'baza'
USER = 'pep'
PASS = 'pep'

PATH_LOCK = FILE_LOCK[:FILE_LOCK.rfind("/")]
FLAG = True
START = False
DEBUG = False


def save_motion(state):
    data = [{
        "measurement": "motion",
        "time": datetime.datetime.utcnow(),
        "fields": {
            "value": 1 if state else 0
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
            "value": 1 if state else 0
        }
    }]

    client = InfluxDBClient('localhost', 8086, USER, PASS, DB)
    client.switch_database(DB)
    client.write_points(data)
    client.close()


def mes(s):
    if DEBUG == True:
        journal.write(s)
        logging.info(s)
    else:
        pass


def on_message_org(mqttc, obj, msg):
    global FLAG, START
    c1 = 0
    c2 = 0

    time.sleep(0.3)
    mustend = time.time() + 200
    while time.time() < mustend:
        if FLAG:
            break
        time.sleep(0.1)
        c1 += 1
    FLAG = False
    
    j = json.loads(str(msg.payload.decode("utf-8","ignore")))
    save_motion(j["occupancy"])
    state = repr(j["occupancy"])
    files = [file for file in os.listdir(PATH_LOCK) if file.startswith('nfc') and file.endswith('.lock')]
    if j["occupancy"] == True:
        mustend = time.time() + 180
        time.sleep(0.5)
        while time.time() < mustend:
            if not os.path.exists(FILE_LOCK):
                break
            time.sleep(0.1)
            c2 += 1
        v = eiscp.eISCP(VSXHOST)
        von = "on" in v.command("power query")
        v.disconnect()
        mes("Motion: {} | Flags: {} | VSX on: {} | Loops: {}, {}".format(state, files, von, c1, c2))
        if not von:
            mes("Start")
            run("sat")
            mes("Started")
            START = True
        else:
            START = False
    else:
        mes("Motion: {} | Flags: {} | Loops: {}, {}".format(state, files, c1, c2))
        START = False
    save_start(START)
    FLAG = True


def on_message(mqttc, obj, msg):
    
    j = json.loads(str(msg.payload.decode("utf-8","ignore")))
    save_motion(j["occupancy"])


if DEBUG == True:
    logging.basicConfig(filename='/home/pi/nfc/app/motion.log', level=logging.INFO, format='%(asctime)s - %(message)s')
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1", 1883, 60)
mqttc.subscribe("zigbee2mqtt/motion", 0)

mqttc.loop_forever()

import socket
import sys


def lirc_send(dev, key):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect("/var/run/lirc/lircd")
    s.sendall("SEND_ONCE " + dev + " " + key + "\n")
    s.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1].lower() == 'tv':
            lirc_send("CANAL", "POWER")
            lirc_send("tv", "KEY_POWER")
        elif sys.argv[1].lower() == 'rec':
            lirc_send("CANAL", "REC")
        elif sys.argv[1].lower() == 'list':
            lirc_send("CANAL", "LIST")
        elif sys.argv[1].lower() == 'stop':
            lirc_send("CANAL", "STOP")
            lirc_send("tv", "KEY_OK")
        else:
            sys.exit(1)
    else:
        sys.exit(1)

import RPi.GPIO as GPIO
from time import sleep

LED_PORT = 16
ST = 0.3

class Led:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PORT, GPIO.OUT)

    def on(self):
        GPIO.output(LED_PORT, GPIO.LOW)

    def off(self):
        GPIO.output(LED_PORT, GPIO.HIGH)

    def blink(self):
        self.on()
        sleep(ST)
        self.off()
        sleep(ST)

    def twice(self):
        self.blink()
        sleep(ST)
        self.blink()
        sleep(ST)

    def __del__(self):
        GPIO.cleanup()
    
    close = __del__

if __name__ == "__main__":
    l = Led()

    print("Led once")
    l.blink()
    sleep(2)
    print("Led twice")
    l.twice()

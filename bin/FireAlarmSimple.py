#!/usr/bin/env python3
#
# Authors: Yipeng Sun

import sys

from time import sleep

try:
    import RPi.GPIO as GPIO
except (ModuleNotFoundError, ImportError):
    import fake_rpi

    sys.modules["RPi"] = fake_rpi.RPi
    sys.modules["smbus"] = fake_rpi.smbus

    import RPi.GPIO as GPIO


if __name__ == "__main__":  # ensure that script is being run from terminal
    ch = int(sys.argv[1])
    interval = 0.1

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    try:
        while True:
            readout = GPIO.input(ch)
            if readout == 0:
                print("Fire!")
            sleep(interval)

    except KeyboardInterrupt:
        GPIO.cleanup()

#!/usr/bin/env python3
#
# Authors: Yipeng Sun

import RPi.GPIO as GPIO
from threading import Thread


class FireAlarm(Thread):
    def __init__(self, stop_event, *args, ch=8, interval=0.1, **kwargs):
        self.stop_event = stop_event
        self.ch = ch
        self.interval = interval

        # Use the Board numbering
        GPIO.setmode(GPIO.BOARD)

        # To quote from:
        # https://www.raspberrypi.org/forums/viewtopic.php?t=87292
        #   The pull-up/downs supply some voltage so that the GPIO will have a
        #   defined value UNTIL overridden by a stronger force.
        #   You should set a pull-down (to 0) when you expect the stronger force
        #   to pull it up to 1.
        #   You should set a pull-up (to 1) when you expect the stronger force
        #   to pull it down to 0.
        #   Maybe we don't need this parameter after all.
        # GPIO.setup(self.ch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.ch, GPIO.IN)

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            if self.read_channel() == 1:
                self.alarm()

    def cleanup(self):
        GPIO.cleanup()

    def read_channel(self):
        return GPIO.input(self.ch)

    def alarm(self):
        print("Fire!!!")


if __name__ == "__main__":
    import sys

    alarm = AlarmSetup(ch=int(sys.argv[1]))

    while True:
        try:
            if alarm.read_channel() == 0:
                print("Fire!")
        except KeyboardInterrupt:
            break

    alarm.cleanup()

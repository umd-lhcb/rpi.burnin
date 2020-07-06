#!/usr/bin/env python3
#
# Authors: Yipeng Sun

from threading import Thread
from time import sleep

try:
    import RPi.GPIO as GPIO
except (ModuleNotFoundError, ImportError):
    import sys
    import fake_rpi

    sys.modules["RPi"] = fake_rpi.RPi
    sys.modules["smbus"] = fake_rpi.smbus

    import RPi.GPIO as GPIO


class FireAlarm(Thread):
    def __init__(
        self,
        stop_event,
        *args,
        ch=8,
        interval=0.1,
        debounce=60,
        gpio_init_cleanup=True,
        **kwargs
    ):
        self.stop_event = stop_event
        self.ch = ch
        self.interval = interval
        self.debounce = debounce
        self.gpio_init_cleanup = gpio_init_cleanup

        # Use the Board numbering
        if self.gpio_init_cleanup:
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

        # Must set pin to pull-up (to 1) because fire alarm will start high
        # and pull low (pull-down to 0) once the alarm triggers.
        GPIO.setup(self.ch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            if self.read_channel() == 0:
                self.alarm()
                sleep(self.debounce)

    def cleanup(self):
        if self.gpio_init_cleanup:
            GPIO.cleanup()
        self.join()

    def read_channel(self):
        return GPIO.input(self.ch)

    def alarm(self):
        print("Fire!")

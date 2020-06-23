#!/usr/bin/env python3
#
# Authors: Jorge Ramirez Ortiz, Nitzan Hershberg, Yipeng Sun

from threading import Thread
from time import sleep

try:
    import RPi.GPIO as GPIO
except (ModuleNotFoundError, ImportError):
    import sys
    import fake_rpi

    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['smbus'] = fake_rpi.smbus

    import RPi.GPIO as GPIO


class WaterAlarm(Thread):
    def __init__(
        self, stop_event, *args, ch=9, interval=0.1, alarmThreshold=2,
        debounce=60, **kwargs
    ):
        self.stop_event = stop_event
        self.ch = ch
        self.interval = interval
        self.alarmThreshold = alarmThreshold
        self.debounce = debounce

        # 'leak_counter' variable can be used to guard against false alarms.
        #
        # This class will monitor the input pin for a HIGH. It is default LOW
        # due to an internal pulldown resistor. It will probe every 0.1 seconds,
        # and if it detects a leak, then the 'leak_counter' variable will
        # increase by one.
        #
        # It seems as if 1 hit to leak_counter can be safely ignored, even tiny
        # drops that run across the sensor trigger the sensor at least twice.
        #
        # Anything more than 5 hits is a major leak (the sensor is in a puddle
        # of water)
        self.leak_counter = 0

        GPIO.setmode(GPIO.BOARD)

        # nominal: no water means circuit is open & BCM 17 is LOW due to
        #          PULLDOWN
        # water detected: leak sensor closes, becomes 2M ohm resistor & BCM 17
        #                 is HIGH
        GPIO.setup(self.ch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # activate pin

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            if self.read_channel() == 1:
                self.leak_counter += 1
                if self.leak_counter >= self.alarmThreshold:
                    self.alarm()
                    sleep(self.debounce)

    def cleanup(self):
        GPIO.cleanup(self.ch)
        self.join()

    def read_channel(self):
        return GPIO.input(self.ch)

    def alarm(self):
        print("Water!")

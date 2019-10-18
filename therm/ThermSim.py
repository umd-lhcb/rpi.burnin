#!/usr/bin/env python
#
# Authors: Jorge Ramirez, Yipeng Sun, Derek Colby
# Last Change: Mon Sep 30, 2019 at 12:44 PM -0400

import logging
import sys
import random

from pathlib import Path
from threading import Thread, Event

logger = logging.getLogger(__name__)

lowerBound = float(sys.argv[2])
upperBound = float(sys.argv[3])
relayState = False


class ThermSensor(Thread):
    def __init__(
        self,
        stop_event,
        globalQueue,
        *args,
        sensor=None,
        displayName=None,
        interval=5,
        temp=25.0,
        **kwargs
    ):
        self.globalQueue = globalQueue
        self.stop_event = stop_event
        self.sensor = sensor
        self.displayName = displayName
        self.interval = interval
        self.temp = temp
        self.false_alarm_list = []

        super().__init__(*args, **kwargs)

    def run(self):
        self.announce()

        while not self.stop_event.wait(self.interval):
            data = self.get()
            self.print_therm(self.sensor, self.displayName, data)
            self.globalQueue.put(data)

    def get(self):
        self.newTemp()
        return self.temp

    def newTemp(self):
        global relayState
        if relayState == False:
            self.temp += 0.2 + round(random.uniform(-0.2, 0.2), 1)
        else:
            self.temp -= 0.2 + round(random.uniform(-0.2, 0.2), 1)

        if self.temp > upperBound:
            relayState = True
        elif self.temp < lowerBound:
            relayState = False

    def cleanup(self):
        self.join()

    def announce(self):
        logger.info(
            "Starting: read from {}, with a display name of {}".format(
                self.sensor, self.displayName
            )
        )

    @staticmethod
    def print_therm(sensor_name, displayName, data):
        print(
            (
                "Sensor {} (from file {}) detects {}".format(
                    displayName, sensor_name, data
                )
            )
        )


###########
# Helpers #
###########
def detect_sensors():
    return ["sens1", "sens2"]


def list_all_sensors(**kwargs):
    sensor_list = detect_sensors(**kwargs)

    for sensor in sensor_list:
        print("Detected the following sensor: {}".format(sensor))


if __name__ == "__main__":
    # detect sensors and assign threads
    sensor_path = detect_sensors()
    sensor_list = []
    stop_event = Event()

    # create new threads
    for i in range(len(sensor_path)):
        sensor_list.append(
            ThermSensor(
                stop_event,
                sensor=sensor_path[i],
                displayName=str(i),
                interval=int(sys.argv[1]),
            )
        )

    # start new threads once all have been initialized
    for sensor in sensor_list:
        sensor.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    # cleanup in the end
    stop_event.set()
    for sensor in sensor_list:
        sensor.cleanup()

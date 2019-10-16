#!/usr/bin/env python
#
# Authors: Derek Colby
# Last Change: Wed Oct 2, 2019 at 4:39 PM -0400

import sys

from threading import Thread, Event
import queue

from therm import ThermSensor as ther
from relay import RelayControl

lowerBound = int(sys.argv[2])
upperBound = int(sys.argv[3])
globalQueue = queue.Queue()


class Control(Thread):
    sensor_list = []
    relay_list = []

    def __init__(self, stop_event, *args, chState=False, **kwargs):
        # detect thermistors and assign threads
        sensor_path = ther.detect_sensors()
        # create new threads
        for i in range(len(sensor_path)):
            self.sensor_list.append(
                ther.ThermSensor(
                    stop_event,
                    globalQueue,
                    sensor=sensor_path[i],
                    displayName=str(i),
                    interval=int(sys.argv[1]),
                )
            )

        # detect relays and assign threads
        relay_path = RelayControl.api.get_all_device_paths()
        # create new threads
        for i in range(len(relay_path)):
            self.relay_list.append(
                RelayControl.RelayControl(
                    stop_event, relay=relay_path[i], displayName=str(i)
                )
            )
        # starts thermistor threads, begin readout
        for sensor in self.sensor_list:
            sensor.start()
        for relay in self.relay_list:
            relay.start()

        self.stop_event = stop_event
        self.chState = chState

        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            data = globalQueue.get()
            if data == "quit":
                globalQueue.task_done()
                return
            if data > upperBound:
                print("data>upper")
                for i in range(len(self.relay_list)):
                    self.relay_list[i].set(1, RelayControl.ON)
                    self.relay_list[i].set(2, RelayControl.ON)
                self.chState = True
            if data < lowerBound:
                print("data<lower")
                for i in range(len(self.relay_list)):
                    self.relay_list[i].set(1, RelayControl.OFF)
                    self.relay_list[i].set(2, RelayControl.OFF)
                self.chState = False
            globalQueue.task_done()

    def cleanup(self):
        for sensor in self.sensor_list:
            sensor.stop_event.set()
            sensor.cleanup()
        for relay in self.relay_list:
            relay.stop_event.set()
            relay.cleanup()

        self.join()
        globalQueue.join()


if __name__ == "__main__":
    stop_event = Event()
    controller = Control(stop_event)
    controller.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Preparing for 'graceful' shutdown...")

    stop_event.set()
    globalQueue.put("quit")
    controller.cleanup()

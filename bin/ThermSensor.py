#!/usr/bin/env python3
#
# Authors: Jorge Ramirez, Yipeng Sun, Derek Colby

import sys
from threading import Event
from pathlib import Path
from queue import Queue

try:
    from rpi.burnin.ThermSensor import ThermSensor
except Exception:
    sys.path.insert(0, "..")
    from rpi.burnin.ThermSensor import ThermSensor


def detect_sensors(
    sensor_dir="/sys/bus/w1/devices",
    sensor_name_prefix="28-00000",
    sensor_file_name="w1_slave",
):
    scan_dir = Path(sensor_dir)  # set directory to be scanned
    sensor_list = []

    print("Detecting sensors and adding to list...")
    for item in scan_dir.iterdir():
        if item.is_dir() and item.stem[:8] == sensor_name_prefix:
            sensor = item / Path(sensor_file_name)
            sensor_list.append(sensor)
            print("sensor {} appended.".format(item.stem))

    return sensor_list


def list_all_sensors(**kwargs):
    sensor_list = detect_sensors(**kwargs)

    for sensor in sensor_list:
        print("Detected the following sensor: {}".format(sensor.stem))


def get_all_sensors(stop_event, queue):
    # detect sensors and assign threads
    sensor_path = detect_sensors()
    sensor_list = []

    # create new threads
    for i in range(len(sensor_path)):
        sensor_list.append(
            ThermSensor(
                stop_event,
                queue,
                sensor=sensor_path[i],
                displayName=str(i),
                interval=int(sys.argv[1]),
            )
        )
    return sensor_list


if __name__ == "__main__":
    stop_event = Event()
    queue = Queue()
    sensor_list = get_all_sensors(stop_event, queue)

    # start new threads once all have been initialized
    for sensor in sensor_list:
        sensor.start()

    try:
        while True:
            print(queue.get())
    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    # cleanup in the end
    stop_event.set()
    for sensor in sensor_list:
        sensor.cleanup()

#!/usr/bin/env python3
#
# Authors: Yipeng Sun, Derek Colby

import sys
from threading import Event
from queue import Queue
from time import sleep

# from relay.RelayAPI import *
try:
    from rpi.burnin.USBRelay import RelayControl, get_all_device_paths
except Exception:
    sys.path.insert(0, "..")
    from rpi.burnin.USBRelay import RelayControl, get_all_device_paths


if __name__ == "__main__":
    relay_paths = get_all_device_paths()
    sleep_time = int(sys.argv[1])
    stop_event = Event()
    queue = Queue()

    controller = RelayControl(stop_event, queue)
    controller.start()

    try:
        while True:
            # turn on/off relays with certain interval
            for p in relay_paths:
                for idx in range(2):
                    queue.put('{},{},on')
                    sleep(sleep_time)
                    queue.put('{},{},on')

    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    # cleanup in the end
    stop_event.set()
    controller.cleanup()

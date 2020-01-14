#!/usr/bin/env python3
#
# Authors: Yipeng Sun, Derek Colby

import sys
from threading import Event

# from relay.RelayAPI import *
try:
    from rpi.burnin.USBRelay import ON, OFF, RelayControl, get_all_device_paths
except Exception:
    sys.path.insert(0, '..')
    from rpi.burnin.USBRelay import ON, OFF, RelayControl, get_all_device_paths


if __name__ == "__main__":
    # detect sensors and assign threads
    relay_path = get_all_device_paths()
    controller_list = []
    stop_event = Event()

    # create new threads
    for i in range(len(relay_path)):
        controller_list.append(
            RelayControl(stop_event, relay=relay_path[i], displayName=str(i))
        )

    # start new threads once all have been initialized
    for controller in controller_list:
        controller.start()

    try:
        while True:
            # turn on/off relays with certain interval
            pass
    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    # cleanup in the end
    stop_event.set()
    for controller in controller_list:
        controller.cleanup()

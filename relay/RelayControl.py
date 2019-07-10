#!/usr/bin/env python
#
# Authors: Yipeng Sun
# Last Change: Wed Jul 10, 2019 at 01:26 PM -0400

import logging

from threading import Thread, Event
from .RelayAPI import get_all_device_path

logger = logging.getLogger(__name__)


class RelayControl(Thread):
    def __init__(self, stop_event, *args,
                 relay=None, displayName=None, interval=5,
                 **kwargs):
        self.stop_event = stop_event
        self.relay = relay
        self.displayName = displayName

        super().__init__(*args, **kwargs)

    def run(self):
        self.announce()

    def get(self):
        pass

    def set(self, status):
        pass

    def cleanup(self):
        self.join()

    def announce(self):
        logger.info("Starting: read from {}, with a display name of {}".format(
            self.sensor.stem, self.displayName
        ))


if __name__ == '__main__':
    # detect sensors and assign threads
    relay_path = get_all_device_path()
    controller_list = []
    stop_event = Event()

    # create new threads
    for i in range(len(relay_path)):
        controller_list.append(
            RelayControl(stop_event, relay=relay_path[i], displayName=str(i)))

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

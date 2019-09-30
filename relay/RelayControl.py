#!/usr/bin/env python
#
# Authors: Yipeng Sun, Derek Colby
# Last Change: Mon Sep 30, 2019 at 12:43 PM -0400

import sys
import logging

from threading import Thread, Event

# from relay.RelayAPI import *
import relay.RelayAPI as api

ON = 0xFF
OFF = 0xFD
logger = logging.getLogger(__name__)


class RelayControl(Thread):
    def __init__(
        self, stop_event, *args, relay=None, displayName=None, **kwargs
    ):
        self.stop_event = stop_event
        self.relay = relay
        self.displayName = displayName

        super().__init__(*args, **kwargs)

    def run(self):
        self.announce()

    def get(self):
        api.get_relay_state(self.relay)

    def set(self, channel, status):
        api.set_relay_state(self.relay, channel, status)

    def cleanup(self):
        for i in range(2):
            self.set(i + 1, OFF)
        self.join()

    def announce(self):
        logger.info(
            "Starting: relay control from {}, with a display name of {}".format(
                self.relay, self.displayName
            )
        )


if __name__ == "__main__":
    # detect sensors and assign threads
    relay_path = api.get_all_device_paths()
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

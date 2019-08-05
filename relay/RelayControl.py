#!/usr/bin/env python
#
# Authors: Yipeng Sun
# Last Change: Wed Jul 10, 2019 at 01:26 PM -0400

import sys
import logging

from threading import Thread, Event
from RelayAPI import *

logger = logging.getLogger(__name__)

# run with one argument to be used as interval

class RelayControl(Thread):
    def __init__(self, stop_event, *args,
                 relay=None, displayName=None, interval=5, hyst=1,
                 **kwargs):
        self.stop_event = stop_event
        self.relay = relay
        self.displayName = displayName
        self.interval = interval
        self.hyst = hyst

        super().__init__(*args, **kwargs)

    def run(self):
        self.announce()
        self.control()


    def get(self):
        get_relay_state(self.relay)

    def set(self, channel, status):
        set_relay_state(self.relay, channel, status)


    def control(self):
        while not self.stop_event.wait(self.interval):
            self.set(1, ON)
            print("relay 1 on")
            time.sleep(self.interval)
            self.set(2, ON)
            print("relay 2 on")
            time.sleep(self.interval)
            self.set(1, OFF)
            self.set(2, OFF)
            print("both off")

    def cleanup(self):
        for i in range(len(controller_list)):
            self.set(i + 1, OFF)
            self.set(i + 2, OFF)
        self.join()

    def announce(self):
        logger.info("Starting: read from {}, with a display name of {}".format(
            self.relay, self.displayName
        ))


if __name__ == '__main__': 
    # detect sensors and assign threads
    relay_path = get_all_device_paths()
    controller_list = []
    stop_event = Event()
    
   
    # create new threads
    for i in range(len(relay_path)):
        controller_list.append(
            RelayControl(stop_event, relay=relay_path[i], displayName=str(i), interval=int(sys.argv[1])))

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

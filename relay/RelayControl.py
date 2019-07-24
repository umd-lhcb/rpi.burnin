#!/usr/bin/env python
#
# Authors: Yipeng Sun
# Last Change: Wed Jul 10, 2019 at 01:26 PM -0400

import sys
import logging

from threading import Thread, Event
from RelayAPI import *
# the inserted path must be changed to folder containing ThermSensor.py
sys.path.insert(0, '/home/student/data/derek/rpi.burnin/therm/')
import ThermSensor as therm

# To run:
#   give 3 numbers
#   first is interval in seconds between temp measurments
#   second is the amount +/- of deviation that is accepted
#   third is target temperature in Celsius

logger = logging.getLogger(__name__)

# create thermistor list
sensor_list = therm.get_all_sensors()

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
        self.hyst = float(sys.argv[2])
        target_temp = float(sys.argv[3])
        
        self.control(target_temp)
        #self.sim(target_temp)

    def get(self):
        get_relay_state(self.relay)

    def set(self, channel, status):
        set_relay_state(self.relay, channel, status)


    def control(self, target_temp):
        # input target temp and attempts to keep within hyst
        # each thermistor correlates to its own relay
         while not self.stop_event.wait(self.interval):
            for i in range(len(sensor_list)):
                sensor = sensor_list[i]
                meas_temp = sensor.get()
                print(meas_temp)
                if meas_temp > target_temp + self.hyst:
                    self.set(i + 1, ON)
                elif meas_temp < target_temp - self.hyst:
                    self.set(i + 1, OFF)

    def sim(self, target):
        # simulates cooling and heating with relay actions
        measTemp = 25
        relay_state = 0
        while not self.stop_event.wait(self.interval):
            if relay_state == 0:
                delTemp = 0.5
            else:
                delTemp = -0.5
            measTemp += delTemp
            print(measTemp)
            if measTemp < target - self.hyst:
                relay_state = 0
                print("relay off")
            elif measTemp > target + self.hyst:
                relay_state = 1
                print("relay on")

    def cleanup(self):
        for i in range(len(sensor_list)):
            self.set(i + 1, OFF)
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

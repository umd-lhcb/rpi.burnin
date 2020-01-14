#!/usr/bin/env python3
#
# Authors: Jorge Ramirez, Yipeng Sun, Derek Colby

from threading import Thread


class ThermSensor(Thread):
    def __init__(
        self,
        stop_event,
        queue,
        *args,
        sensor=None,
        display_name=None,
        interval=5,
        **kwargs
    ):
        self.stop_event = stop_event
        self.queue = queue
        self.sensor = sensor
        self.display_name = display_name
        self.interval = interval
        self.false_alarm_list = []

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait(self.interval):
            data = self.get()
            if data is not None:
                self.queue.put(data)

    def get(self):
        with self.sensor.open() as f:
            contents = f.readlines()
            # extract raw data into variable "temp_string"
            data_pos = contents[1].find("t=")
            temp_string = contents[1].strip()[data_pos + 2 :]
        temp = self.thermal_readout_guard(temp_string)
        return temp

    def cleanup(self):
        self.join()

    def thermal_readout_guard(self, temp_string):
        temp = int(temp_string) / 1000  # add decimal point to data

        # Ignore it for the first two consecutive '85.0'
        if temp == 85.0:
            self.false_alarm_list.append(temp)
            if len(self.false_alarm_list) > 2:
                # We have received more than 2 consecutive '85.0', which means
                # that we should spit out '85.0' faithfully.
                pass
            else:
                # Suppress '85.0' on the basis that this is likely a fluke.
                temp = None

        else:
            self.false_alarm_list = []

        return temp

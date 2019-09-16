import sys

from threading import Thread, Event
import queue

from therm import ThermSim as ther
from relay import RelayControl

lowerBound = int(sys.argv[2])
upperBound = int(sys.argv[3])
Global_Queue = queue.Queue()

class Control(Thread):
    def __init__(self, stop_event, relay,
            *args, chState=False, **kwargs):
        self.stop_event = stop_event
        self.relay = relay
        self.chState = chState

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event:
            data = Global_Queue.get()
            if data > upperBound:
                for i in range(len(self.relay)):
                    self.relay[i].set(1, RelayControl.ON)
                    self.relay[i].set(2, RelayControl.ON)
                self.chState = not self.chState
            if data < lowerBound:
                for i in range(len(self.relay)):
                    self.relay[i].set(1, RelayControl.OFF)
                    self.relay[i].set(2, RelayControl.OFF)
                self.chState = not self.chState
            Global_Queue.task_done()

    def cleanup(self):
        for i in range(len(self.relay)):
            self.relay[i].set(1, RelayControl.OFF)
            self.relay[i].set(2, RelayControl.OFF)
        self.join()


if __name__ == '__main__':
    # detect thermistors and assign threads
    sensor_path = ther.detect_sensors()
    sensor_list = []
    stop_event = Event()
    # create new threads
    for i in range(len(sensor_path)):
        sensor_list.append(
            ther.ThermSensor(stop_event, Global_Queue,
                        sensor=sensor_path[i], displayName=str(i),
                        interval=int(sys.argv[1])))

    # detect relays and assign threads
    relay_path = RelayControl.get_all_device_paths()
    relay_list = []
    stop_event = Event()
    # create new threads
    for i in range(len(relay_path)):
        relay_list.append(
                RelayControl.RelayControl(stop_event, 
                    relay=relay_path[i], displayName=str(i), 
                    interval=int(sys.argv[1])))

    #starts thermistor threads, begin readout
    for sensor in sensor_list:
        sensor.start()

    controller = Control(stop_event, relay_list)
    controller.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Preparing for 'graceful' shutdown...")

    stop_event.set()
    controller.cleanup()

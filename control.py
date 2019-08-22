import sys

from threading import Thread, Event

from therm import ThermSim as ther
from relay import RelayControl

lowerBound = int(sys.argv[2])
upperBound = int(sys.argv[3])

class control(Thread):
    def __init__(self, stop_event, thermistor, relay, channel,
            *args, interval=5, chState=False, **kwargs):
        self.stop_event = stop_event
        self. thermistor = thermistor
        self.relay = relay
        self.channel = channel
        self.interval = interval
        self.chState = chState

        super().__init__(*args, **kwargs)

    def run(self):
        self.thermistor.start()
        #self.relay.start()

        while not self.stop_event.wait(self.interval):
            data = self.thermistor.get()
            if data > upperBound:
                self.relay.set(self.channel, RelayControl.ON)
                self.chState = not self.chState
            if data < lowerBound:
                self.relay.set(self.channel, RelayControl.OFF)
                self.chState = not self.chState


    def cleanup(self):
        self.relay.set(self.channel, RelayControl.OFF)
        self.thermistor.cleanup()
        self.join()


if __name__ == '__main__':
    # detect thermistors and assign threads
    sensor_path = ther.detect_sensors()
    sensor_list = []
    stop_event = Event()
    # create new threads
    for i in range(len(sensor_path)):
        sensor_list.append(
            ther.ThermSensor(stop_event,
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

    pair_list = []
    for i in range(len(sensor_list)):
        pair_list.append(
                control(stop_event, 
                    sensor_list[i], relay_list[0], i+1,  
                    interval = int(sys.argv[1])))
    for pair in pair_list:
        pair.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Preparing for 'graceful' shutdown...")

    stop_event.set()
    for pair in pair_list:
        pair.cleanup()

#!/usr/bin/env python3
#
# Authors: Jorge Ramirez Ortiz, Nitzan Hershberg, Yipeng Sun

import sys
from threading import Event

try:
    from rpi.burnin.WaterAlarm import WaterAlarm
except Exception:
    sys.path.insert(0, "..")
    from rpi.burnin.WaterAlarm import WaterAlarm


if __name__ == "__main__":  # ensure that script is being run from terminal
    stop_event = Event()

    print("Initializing water leak detector...")
    alarm = WaterAlarm(stop_event, ch=int(sys.argv[1]))
    alarm.start()

    try:
        alarm.join()
    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    stop_event.set()
    alarm.cleanup()

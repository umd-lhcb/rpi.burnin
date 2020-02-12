#!/usr/bin/env python3
#
# Authors: Yipeng Sun

import sys
from threading import Event

try:
    from rpi.burnin.FireAlarm import FireAlarm
except Exception:
    sys.path.insert(0, "..")
    from rpi.burnin.FireAlarm import FireAlarm


if __name__ == "__main__":  # ensure that script is being run from terminal
    stop_event = Event()

    print("Initializing fire detector...")
    alarm = FireAlarm(stop_event, ch=int(sys.argv[1]))
    alarm.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    stop_event.set()
    alarm.cleanup()

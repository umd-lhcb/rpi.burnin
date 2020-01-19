#!/usr/bin/env python3
#
# Authors: Yipeng Sun, Derek Colby

import sys
import time

try:
    from rpi.burnin.USBRelay import (
        get_all_device_paths,
        set_relay_state,
        ON,
        OFF,
    )
except Exception:
    sys.path.insert(0, "..")
    from rpi.burnin.USBRelay import (
        get_all_device_paths,
        set_relay_state,
        ON,
        OFF,
    )


def test_relay(delay):
    test = get_all_device_paths()
    print(test)

    set_relay_state(test[0], 1, OFF)  # ensure it is turned off
    set_relay_state(test[0], 2, OFF)

    print(
        "Beginning loop with a {} second cycles. Ctrl+C to stop".format(delay)
    )

    cycles = 0  # counter
    try:
        while True:
            print("Turning Relay On")
            set_relay_state(test[0], 1, ON)
            set_relay_state(test[0], 2, ON)
            time.sleep(delay)

            print("Turning Relay Off")
            set_relay_state(test[0], 1, OFF)
            set_relay_state(test[0], 2, OFF)
            time.sleep(delay)
            cycles += 1
            if cycles == 1:
                print(cycles, "Cycle completed")
            else:
                print(cycles, "Cycles completed")

    except KeyboardInterrupt:
        print("Preparing for graceful shutdown...")

    set_relay_state(test[0], 1, OFF)  # ensure it is turned off
    set_relay_state(test[0], 2, OFF)
    print("Test Concluded")


if __name__ == "__main__":
    relay_paths = get_all_device_paths()
    sleep_time = int(sys.argv[1])

    test_relay(sleep_time)

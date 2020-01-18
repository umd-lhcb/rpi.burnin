#!/usr/bin/env python3
#
# Authors: Yipeng Sun, Jorge Ramirez, Derek Colby

import hid
import time
from threading import Thread

# These are found from 'lsusb'; it is formatted as: (vendor_id, product_id)
RELAY_ID = (0x16C0, 0x05DF)
CMD_SET_ALIAS = 0xFA
ON = 0xFF
OFF = 0xFD


#################################
# Operations on multiple relays #
#################################


def print_all(device_id=RELAY_ID):
    for d in hid.enumerate(*device_id):
        print(d)


def get_all_device_paths(device_id=RELAY_ID):
    return [d["path"] for d in hid.enumerate(*device_id)]


################################
# Operations on a single relay #
################################


def get_device_alias(path):
    return chr_list(get_feature_report(path)[1:6])


def set_device_alias(path, alias):
    if len(alias) > 5:
        raise ValueError("The length of the alias should not exceed 5.")
    else:
        cmd = [0, CMD_SET_ALIAS]
        cmd += ord_str(alias)
        cmd += [0] * (9 - len(cmd))

        send_cmd(path, cmd)


def get_relay_number(path):
    dev = hid.device()

    dev.open_path(path)
    num = int(dev.get_product_string()[-1])
    dev.close()

    return num


def set_relay_state(path, idx, state=ON):
    cmd = [0]
    cmd.append(state)
    cmd.append(idx)
    cmd += [0] * (9 - len(cmd))

    send_cmd(path, cmd)


def get_relay_state(path, num_of_relays=2):
    state_of_all_chs = get_feature_report(path)[-1]
    if num_of_relays == 2:
        return get_relay_state_two_chs(state_of_all_chs)
    else:
        return "Unimplemented for relay with {} channels".format(num_of_relays)


###########
# Helpers #
###########


def ord_str(string):
    return [ord(char) for char in string]


def chr_list(list_of_int):
    chars = [chr_quiet(n) for n in list_of_int]
    return "".join(chars)


def chr_quiet(n):
    if n < 32:
        return ""
    else:
        return chr(n)


def send_cmd(path, cmd):
    dev = hid.device()
    dev.open_path(path)
    dev.send_feature_report(cmd)
    dev.close()


def get_feature_report(path, lower_bd=0, upper_bd=9):
    dev = hid.device()
    dev.open_path(path)
    msg = dev.get_feature_report(lower_bd, upper_bd)
    dev.close()

    return msg


def get_relay_state_two_chs(state):
    state_map = {
        0: {"CH1": "OFF", "CH2": "OFF"},
        1: {"CH1": "ON", "CH2": "OFF"},
        2: {"CH1": "OFF", "CH2": "ON"},
        3: {"CH1": "ON", "CH2": "ON"},
    }
    return state_map[state]


def test_relay(delay=15):
    test = get_all_device_paths()  # default seconds to pause between cycles

    print("Starting configuration:")
    print(get_relay_state(test[0]))
    print(get_all_device_paths())

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


#########################
# Relay control wrapper #
#########################
# FIXME: This wrapper currently doesn't work.


class RelayControl(Thread):
    def __init__(
        self, stop_event, queue, *args, **kwargs
    ):
        self.stop_event = stop_event
        self.queue = queue

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_event.wait():
            relay_path, idx, state = self.queue.get().split(',')
            set_relay_state(relay_path, idx, self.translate_state(state))

    def cleanup(self):
        self.join()

    @staticmethod
    def translate_state(state):
        if state.lower() == 'on':
            return ON
        elif state.lower() == 'off':
            return OFF
        else:
            raise ValueError('Unknown state: {}'.format(state))

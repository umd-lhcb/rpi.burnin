#!/usr/bin/env python
#
# Authors: Yipeng Sun
# Last Change: Wed Nov 07, 2018 at 09:48 PM -0500

import hid

# These are found from 'lsusb'; it is formatted as: (vendor_id, product_id)
RELAY_ID = (0x16c0, 0x05df)
CMD_SET_ALIAS = 0xfa
ON = 0xff
OFF = 0xfd


#################################
# Operations on multiple relays #
#################################

def print_all(device_id=RELAY_ID):
    for d in hid.enumerate(*device_id):
        print(d)


def get_all_device_paths(device_id=RELAY_ID):
    return [d['path'] for d in hid.enumerate(*device_id)]


################################
# Operations on a single relay #
################################

def get_device_alias(path):
    return chr_list(get_feature_report(path)[1:6])


def set_device_alias(path, alias):
    if len(alias) > 5:
        raise ValueError('The length of the alias should not exceed 5.')
    else:
        cmd = [0, CMD_SET_ALIAS]
        cmd += ord_str(alias)
        cmd += [0] * (9-len(cmd))

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
    cmd += [0] * (9-len(cmd))

    send_cmd(path, cmd)


def get_relay_state(path, num_of_relays=2):
    state_of_all_chs = get_feature_report(path)[-1]
    if num_of_relays == 2:
        return get_relay_state_two_chs(state_of_all_chs)
    else:
        return 'Unimplemented for relay with {} channels'.format(num_of_relays)


###########
# Helpers #
###########

def ord_str(string):
    return [ord(char) for char in string]


def chr_list(list_of_int):
    chars = [chr_quiet(n) for n in list_of_int]
    return ''.join(chars)


def chr_quiet(n):
    if n < 32:
        return ''
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
        0: {'CH1': 'OFF', 'CH2': 'OFF'},
        1: {'CH1': 'ON',  'CH2': 'OFF'},
        2: {'CH1': 'OFF', 'CH2': 'ON'},
        3: {'CH1': 'ON',  'CH2': 'ON'}
    }
    return state_map[state]
#!/usr/bin/env python
#
# Authors: Yipeng Sun
# Last Change: Wed Nov 07, 2018 at 04:57 PM -0500

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
    dev = hid.device()

    dev.open_path(path)
    alias = chr_list(dev.get_feature_report(0, 9)[1:6])
    dev.close()

    return alias


def set_device_alias(path, alias):
    if len(alias) > 5:
        raise ValueError('The length of the alias should not exceed 5.')
    else:
        cmd = [0, CMD_SET_ALIAS]
        cmd += ord_str(alias)
        cmd += [0] * (9-len(cmd))

        dev = hid.device()

        dev.open_path(path)
        dev.send_feature_report(cmd)
        dev.close()


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

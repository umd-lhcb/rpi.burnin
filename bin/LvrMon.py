#!/usr/bin/env python3
#
# Author: Phoebe Hamilton, Rohan Rajagopalan

import threading
import time
import curses
import os
import unicodedata
import sys
from math import sqrt

try:
    from rpi.burnin.ADCPi import ADCPi
except Exception:
    sys.path.insert(0, '..')
    from rpi.burnin.ADCPi import ADCPi


def main():
    stdscr = curses.initscr()
    """
    Main program function
    """
    start_time = time.time()
    try:
        adc1 = ADCPi(0x6E, 0x6F, 12)
    except Exception:
        print("Failed to open i2c to ADC1!")
        return
    try:
        adc2 = ADCPi(0x6C, 0x6D, 12)
    except Exception:
        print("Failed to open i2c to ADC2!")
        return
    try:
        adc3 = ADCPi(0x6A, 0x6B, 12)
    except Exception:
        print("Failed to open i2c to ADC3!")
        return
    try:
        adc4 = ADCPi(0x68, 0x69, 12)
    except Exception:
        print("Failed to open i2c to ADC4!")
        return
    the_adcs = [adc1, adc2, adc3, adc4]
    try:
        for adcnum in range(0, 4, 1):
            the_adcs[adcnum].arm_channel(1)
        ch_assignments = []

        for nums in range(0, 8, 1):
            ch_assignments.append("i_SENSE_MON" + str(nums + 1))

        for nums in range(0, 8, 1):
            ch_assignments.append("V_SENSE_MON" + str(nums + 1))

        for nums in range(0, 8, 1):
            ch_assignments.append("V_REGUL_OUT" + str(nums + 1))

        ch_assignments.append("Vin_FPGA_3V3")
        ch_assignments.append("Vin_FPGA_1V5")
        ch_assignments.append("V_OPAMP_RAIL")
        ch_assignments.append("PLAT_THERM_A")
        ch_assignments.append("PLAT_THERM_B")
        ch_assignments.append("BLANK")
        ch_assignments.append("BLANK")
        ch_assignments.append("BLANK")

        # python dictionary (Channel: [fancy name, fancy reading, bare reading])
        collect = {
            "ADC Channel 1": ["blank", "blank", 0],
            "ADC Channel 2": ["blank", "blank", 0],
            "ADC Channel 3": ["blank", "blank", 0],
            "ADC Channel 4": ["blank", "blank", 0],
            "ADC Channel 5": ["blank", "blank", 0],
            "ADC Channel 6": ["blank", "blank", 0],
            "ADC Channel 7": ["blank", "blank", 0],
            "ADC Channel 8": ["blank", "blank", 0],
            "ADC Channel 9": ["blank", "blank", 0],
            "ADC Channel 10": ["blank", "blank", 0],
            "ADC Channel 11": ["blank", "blank", 0],
            "ADC Channel 12": ["blank", "blank", 0],
            "ADC Channel 13": ["blank", "blank", 0],
            "ADC Channel 14": ["blank", "blank", 0],
            "ADC Channel 15": ["blank", "blank", 0],
            "ADC Channel 16": ["blank", "blank", 0],
            "ADC Channel 17": ["blank", "blank", 0],
            "ADC Channel 18": ["blank", "blank", 0],
            "ADC Channel 19": ["blank", "blank", 0],
            "ADC Channel 20": ["blank", "blank", 0],
            "ADC Channel 21": ["blank", "blank", 0],
            "ADC Channel 22": ["blank", "blank", 0],
            "ADC Channel 23": ["blank", "blank", 0],
            "ADC Channel 24": ["blank", "blank", 0],
            "ADC Channel 25": ["blank", "blank", 0],
            "ADC Channel 26": ["blank", "blank", 0],
            "ADC Channel 27": ["blank", "blank", 0],
            "ADC Channel 28": ["blank", "blank", 0],
            "ADC Channel 29": ["blank", "blank", 0],
            "ADC Channel 30": ["blank", "blank", 0],
            "ADC Channel 31": ["blank", "blank", 0],
            "ADC Channel 32": ["blank", "blank", 0],
        }

        for i in range(1, 33, 1):

            collect["ADC Channel " + str(i)][0] = ch_assignments[i - 1]

        while True:

            this_time = time.time()

            # read from adc channels and print to screen
            # collects data from each ADC read and stores in dictionary
            arm_threads = [None, None, None, None]

            for chNum in range(1, 9, 1):
                for nADC in range(0, 4, 1):
                    test_time = time.time()
                    split_1 = time.time()
                    # get that voltage
                    if (
                        "BLANK"
                        in collect["ADC Channel " + str(8 * nADC + chNum)][0]
                    ):
                        reading = 0
                    else:
                        reading = the_adcs[nADC].read_curr_voltage()

                    nextCh = (chNum % 8) + 1
                    split_2 = time.time()
                    the_adcs[nADC].arm_channel(nextCh)
                    end_test = time.time()

                    if "i_SENSE" in ch_assignments[8 * nADC + chNum - 1]:
                        V_ref = collect[
                            "ADC Channel "
                            + str(ch_assignments.index("Vin_FPGA_1V5") + 1)
                        ][2]
                        i_val = (reading * (17310 / 16800) - V_ref) / 0.16667
                        collect["ADC Channel " + str(8 * nADC + chNum)][1] = (
                            str.format("{0:0.2f}", i_val) + "A    "
                        )
                    elif "PLAT_THERM" in ch_assignments[8 * nADC + chNum - 1]:
                        Vin = collect[
                            "ADC Channel "
                            + str(ch_assignments.index("Vin_FPGA_3V3") + 1)
                        ][2]
                        RT = 0
                        if Vin - reading != 0:
                            RT = reading * 1000 / (Vin - reading)
                            if RT > 0:
                                RT = 1 / (
                                    1 / RT - 1 / 16800
                                )  # the voltage divider (10k:6.8k) on the ADC is another path to ground and changes R2-- fix it
                                R0 = 1000.0
                                c = R0 - RT
                                b = 3.9083e-3 * R0
                                a = -5.775e-7 * R0
                                disc = b * b - 4 * a * c
                                if disc < 0:
                                    disc = 0
                                Temp = (-b + sqrt(disc)) / (2 * a)
                            else:
                                temp = -98
                        else:
                            Temp = -99
                        collect["ADC Channel " + str(8 * nADC + chNum)][1] = (
                            str.format("{0:0.1f}", Temp) + "C    "
                        )
                    else:
                        collect["ADC Channel " + str(8 * nADC + chNum)][1] = (
                            str.format("{0:0.3f}", reading) + "V    "
                        )
                    collect["ADC Channel " + str(8 * nADC + chNum)][2] = reading

            # print (collect)

            # CTRL + C to end program
            # wait 0.2 seconds before reading the pins again
            counter = 0
            stdscr.addstr(
                0,
                0,
                time.asctime()
                + " ("
                + str.format("{0:0.1f}", 1000 * (time.time() - this_time))
                + ")",
            )
            offset = 1
            for i in collect:
                if (counter % 9) == 0:
                    counter += 2
                else:
                    counter += 1
                if "BLANK" in collect[i][0]:
                    continue
                stdscr.addstr(
                    counter + offset,
                    0,
                    i + "\t" + collect[i][0] + "\t" + collect[i][1],
                )
                # stdscr.addstr(counter,0,i+"\t"+collect[i][0]+"\t"+collect[i][1]+"\t\t\t"+str(collect[i][2]))

            stdscr.addstr(0, 0, "TEST")
            stdscr.refresh()

    except KeyboardInterrupt:
        pass
    except Exception:
        print("exception ", sys.exc_info())
        pass


if __name__ == "__main__":
    curses.wrapper(main())

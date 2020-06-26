#!/usr/bin/env python3
#
# Author: Phoebe Hamilton, with base from Rohan Rajagopalan

import curses
import sys
from math import sqrt, ceil, pow
import time
from cursesmenu import *
from cursesmenu.items import *

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    import fake_rpi
    sys.modules['RPi'] = fake_rpi.RPi
    sys.modules['smbus'] = fake_rpi.smbus

from rpi.burnin.ADCPi import ADCPi

pins = [11, 12, 13, 15, 16, 18, 22, 7]
JP_assignments=[0,1,1,0,2,3,3,2,4,5,5,4]

DSUB_pins = {'Group  1':[[1,12,0],[2.4e3,2.4e3,2.4e3,2.4e3,2.4e3,2.4e3]] #start from 1 because zero is special
             ,'Group  2':[[2,12,0],[700,700,700,1.7,700,1.7]]
             ,'Group  3':[[3,12,0],[1.9,700,700,1.9,1.8,1.8]]
             ,'Group  4':[[4,12,0],[2400,2400,2400,2400,1.8,1.8]]
             ,'Group  5':[[5,12,0],[700,700,700,1.5,1.5,1.5]]
             ,'Group  6':[[6,12,0],[1.6,700,700,1.6,1.6,1.6]]
             ,'Group  7':[[7,12,0],[2.2,2.4e3,2.2,2.2,2.2,2.1]]
             ,'Group  8':[[8,12,0],[2.2,700,2.2,2.2,2.2,2.2]]
             ,'Group  9':[[9,12,0],[2.4e3,2.4e3,2.4e3,2.4e3,2.4e3,2.4e3]]
             ,'Group 10':[[10,12,0],[1.6,700,700,1.6,1.6,1.6]]
             ,'Group 11':[[11,12,0],[2.4e3,2.4e3,2.4e3,2.4e3,2.4e3,2.4e3]]
             ,'Group 12':[[12,12,0],[2.4e3,2.4e3,2.4e3,2.3,2.4e3,2.3]]
             ,'Group 13':[[13,12,0],[700,700,700,700,700,700]]
             ,'Group 14':[[14,12,0],[700,700,700,700,2,2]]
             ,'Group 15':[[15,12,0],[2,700,2,2,2,2]]
             ,'Group 16':[[0,10,0],[700,700,700,700,700,700]] #16 is wired to 10
             ,'Group 17':[[0,1,0],[700,700,700,700,700,700]]
             ,'Group 18':[[0,2,0],[700,700,700,2,700,2]]
            # ,'Group 19':[[0,3,0],[700,700,700,700,700,700]]
            # ,'Group 20':[[0,4,0],[700,700,700,700,700,700]]
            # ,'Group 21':[[0,5,0],[700,700,700,700,700,700]]
            # ,'Group 22':[[0,6,0],[700,700,700,700,700,700]]
            # ,'Group 23':[[0,7,0],[700,700,700,700,700,700]]
            #,'Group 24':[[0,8,0],[700,700,700,700,700,700]]
             ,'Sense P1/JDA/W':[[0,11,0],[10,10,10,10,10,10]]
             ,'Sense P2/___/_':[[0,12,0],[10,10,10,10,10,10]]
             ,'Sense P3/JDB/E':[[0,13,0],[10,10,10,10,10,10]]
             ,'Sense P4/___/_':[[0,14,0],[10,10,10,10,10,10]]
             }



try:
    adc = ADCPi(0x68, 0x69, 16)
except Exception:
    print("Failed to open i2c to ADC!")
    pass


def loop(stdscr,n):
    stdscr.clear()
    stdscr.timeout(1)
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    stdscr.keypad(1)
    press = stdscr.getch()
    start_time = time.time()
    Vref=0.0
    curses.init_pair(1,curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4,curses.COLOR_RED, curses.COLOR_BLACK)
    while press != ord('j'):
        this_time=time.time()
        line=2
        offset=0
        height,width=stdscr.getmaxyx()
        for key in DSUB_pins:
            press=stdscr.getch()
            if press == ord('j'):
                return

            bin1 = [int(x) for x in list('{0:04}'.format(int('{0:0b}'.format(DSUB_pins[key][0][0]))))]
            bin2 = [int(x) for x in list('{0:04}'.format(int('{0:0b}'.format(DSUB_pins[key][0][1]))))]
            bin1.reverse()
            bin2.reverse()
            binary=[]
            for i in bin1:
                binary.append(i)
            for i in bin2:
                binary.append(i)
            for i in pins:
                #binary = [0,0,1,1,1,1,1,1]
                try:
                    GPIO.output(i, binary[pins.index(i)])
                except:
                    print("exception",sys.exc_info())
                    pass
            time.sleep(0.125)
            R0=910
            Vref=adc.read_voltage(8)
            if(DSUB_pins[key][0][0]==0):
                reading = adc.read_voltage(2)
                R0=909.7
            else:
               R0=908.3
               reading = adc.read_voltage(1)
            try:
                R=reading*R0/(Vref-reading)
            except ZeroDivisionError:
                R=1e12
            if(R < 16800):
                try:
                    R=1/(1/R-1/16800.)
                except ZeroDivisionError:
                    R=120

                if(DSUB_pins[key][0][0]==0):
                    R=R-2*60
                else:
                    R=R-2*65
            else:
                R=999999

            stdscr.addstr(0,0,time.asctime()+" ("+str.format("{0:0.1f}",1000*(time.time()-this_time))+")"+" \tVref="+str(Vref)+"V        ")
            #stdscr.addstr(line,offset,key+"\t"+f"{R:9.1f}"+" Ohm"+"\t("+str.format("{0:0.2f}",reading)+" V)            ")
            target = DSUB_pins[key][1][JP_assignments[n]]
            color = min(4,ceil(abs(R-target)/(0.86*sqrt(pow(5*sqrt(target/100),2)+pow(0.03*R,2)+49))))
            stdscr.addstr(line,offset,key+"\t"+f"{R:9.1f}"+" Ohm\t"+f"{target:6.1f}"+" Ohm",curses.color_pair(color))
            stdscr.refresh()
            line=line+1
            if(line >= height):
                line=2
                offset=int(width/2)

        stdscr.addstr(0,0,time.asctime()+" ("+str.format("{0:0.1f}",1000*(time.time()-this_time))+")"+" \tVref="+str(Vref)+"V        ")
        stdscr.refresh()
        press=stdscr.getch()
    stdscr.clear()

def main(a):
    stdscr = curses.initscr()
    GPIO.setmode(GPIO.BOARD)
    # S0-3 => Bit 1-4 (11, 12, 13, 15)

    num = 0
    count = 0
    t = .5
    x = 0
    for i in pins:
        try:
            GPIO.setup(i, GPIO.OUT)
        except Exception:
            print("GPIO setup error")
            return
    try:
        menu=CursesMenu("Select Saved JPx for Comparison")
        for i in range(0,12,1):
            item=FunctionItem("JP"+str(i),loop,[stdscr,i])
            menu.append_item(item)
        menu.start()
        menu.join()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
        curses.wrapper(main)

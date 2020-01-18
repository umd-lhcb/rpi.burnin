# rpi.burnin
This library provides an interface from the various Raspberry Pi models for
burn-in related activities.


## Dependencies
Install required packages with:
```
pip3 install --user -r ./requirements.txt
```


## Usage
**Note**: All scripts in `bin` assumes you run them in the `bin` folder.

### `bin/Continuity.py`
Continuity checker for the backplane testing.

Invoke with:
```
cd bin
python3 .Continuity.py
```

* `Ctrl-C` to quit
* `j` at any time to select another pigtail reference map



### `bin/ThermSensor.py`
`ThermSensor.py` is a script that reads the output files made by the DS18B20
thermometers and runs a multithreaded process with each thread dedicated to
reading and outputting the data values from one thermometer.  Written by Jorge
Ramirez, improvements by Yipeng Sun.

#### Setup
For Raspbian, in the raspberry pi's `/boot/config.txt`, add the following line:
```
dtoverlay=w1-gpio,pullup=1
```
For NixOS, it should already be configured.

The thermistors are wired in parallel by connecting their GND to the VDD pins,
and then both to shared ground (Pin 6). The DQ pin carries the data signal into
the 1-Wire [(aka BCM4 or Pin7)](https://pinout.xyz/pinout/1_wire) interface.
A pulldown resistor is included by connecting the data line to the 3.3v pin (pin 1)
as required by the 1-wire interface.

![Thermistor wiring diagram](docs/thermistor_wiring.png)

Our lab has streamlined the process of having several dozen thermistors.
Each thermistor has the GND pin wrapped around the VDD pin and soldered
and all three pins are covered in gel for rigidity. A breakout board was
produced with one rail for each thermistor's GND connection, and one rail
for each thermistor's data line. Both rails have a wire that allow connection
to their corresponding pin (GND -> pin 6, Data -> pin 7) and a 4.7k resistor
was soldered onto the data rail with a wire to connect to the 3.3v pin (pin 1).

On our setup, the blue wire corresponds to the data line, the red wire is
the pulldown resistor's 3.3v connection, and the black wire is ground.

#### Manual Usage
The `ThermSensor.py` script will automatically loop and output the temperature
values for every connected thermistor. Run the script with an integer value
to specify the delay between each readout in seconds:
```
cd bin
python3 ./ThermSensor.py 4
```


### `bin/WaterAlarm.py`
`WaterAlarm.py` is a script that uses the LS2600 leak sensor in order to monitor
for leaks. If the LS2600 has both contacts in water, the sensor will close the
circuit and then the script will sense the High and track for how long in the
variable 'leak counter'.

Written by Jorge Ramirez, improvements by Yipeng Sun.


### `rpi.burnin.USBRelay.py`
USB relay control for `Van Ooijen Technische Informatica`. Currently only APIs
are implemented, as they have not been wrapped into worker classes that can be
used directly in the burn-in system.

With Jorge Ramirez's schematic, valves control functionality has been
confirmed.

#### Setup
Copy the udev rule in `udev_rules/50-usb-relay-dct-tech.rules` under
`/etc/udev/rules.d/` directory, so that everyone (not just `root` user) has
read/write access to this type of USB relays.

The CP100 Rain Bird Solenoid Valve is connected to the NO (normally open) terminal of the
USB Relay so that water will only flow when the Relay turns on and the switch is flipped.
Tests showed that the reverse-current created by the solenoid's voltage spike was enough to
damage the relay and force it to reset. A 60V 5.5A diode was included in the circuit to allow
a back channel for the reverse-current to dissipate.

![Single valve diagram](docs/lhcb_valve_diagram.png)

Multiple valves can be connected, each valve can share the common connection to the +
terminal of the power supply, however each valve requires its own diode and NO relay terminal.

#### Usage
To initialize the script, run the command:
```
python -i ./rpi/burnin/RelayAPI.py
```
Enter any of the commands below to utilize the APIs.

#### Functionalities
To list all USB relays that are connected to the computer, use:
```
>>> p = get_all_device_paths()
[b'0001:0013:00']
```

To read channel states (currently only support 2 channel relays):
```
>>> get_relay_state(p[0])
{'CH1': 'OFF', 'CH2': 'OFF'}
```

Each channel can be turned on/off:
```
>>> set_relay_state(p[0], 1, ON)
>>> set_relay_state(p[0], 2, OFF)
```

To test, hook up a valve as shown above. Then call the `test_relay(t)` method,
where `t` is the number of seconds between each ON/OFF switch:
```
>>> test_relay(12)
```
which will initiate a loop where there is a 12 second pause between ON/OFF
switches. Use Ctrl+C to exit.


## Development
In NixOS, run `nix-shell` in the root folder of this project. All needed
dependencies should become available in that shell.

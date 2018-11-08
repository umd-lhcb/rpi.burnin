# rpi.burnin
This library provides an interface from the Rasperberry Pi GPIO to burn-in
related actvitities.


## Dependencies
The following Python packages need to be installed:
```
RPi.GPIO
hidapi
```


## `therm`
`ThermSensor.py` is a script that reads the output files made by the DS18B20
thermometers and runs a multithreaded process with each thread dedicated to
reading and outputting the data values from one thermometer. **To set a delay
on recording, run script in terminal with an integer to specify the delay in
seconds:**
```
python ThermSensor.py 4
```
will have a 4 second delay between each round of recording.

Written by Jorge Ramirez, improvements by Yipeng Sun.

### Setup
In `/boot/config.txt`, add the following line:
```
dtoverlay=w1-gpio,pullup=1
```


## `water`
`WaterAlarm.py` is a script that uses the LS2600 leak sensor in order to monitor
for leaks. If the LS2600 has both contacts in water, the sensor will close the
circuit and then the script will sense the High and track for how long in the
variable 'leak counter'.

Written by Jorge Ramirez, improvements by Yipeng Sun.


## `alarm`
Preliminary fire alarm detection by Yipeng Sun. Further improvements made by
Jorge Ramirez.


## `mux`
Preliminary voltage read-out from prototype mux boards is implemented by Rohan
Rajagopalan.


## `relay`
USB relay control for ` Van Ooijen Technische Informatica` USB relay by Yipeng
Sun. Currently only APIs are implemented, as they have not been wrapped into
worker classes that can be used directly in the burn-in system.

### Usage
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

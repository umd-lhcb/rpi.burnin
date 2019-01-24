# rpi.burnin
This library provides an interface from the Rasperberry Pi GPIO to burn-in
related activities.


## Dependencies
The following Python packages need to be installed:
```
RPi.GPIO
hidapi
```


## `therm`
`ThermSensor.py` is a script that reads the output files made by the DS18B20
thermometers and runs a multithreaded process with each thread dedicated to
reading and outputting the data values from one thermometer.  Written by Jorge
Ramirez, improvements by Yipeng Sun.

### Setup
In `/boot/config.txt`, add the following line:
```
dtoverlay=w1-gpio,pullup=1
```

### Usage
To set a delay on recording, run script in terminal with an integer to specify
the delay in seconds:
```
python ThermSensor.py 4
```
will have a 4 second delay between each round of recording.



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
Valves functionality has been confirmed by Jorge Ramirez. 



### Setup
Copy the udev rule in `relay/udev_rules/50-usb-relay-dct-tech.rules` under
`/etc/udev/rules.d/` directory, so that everyone (not just `root` user) has
read/write access to this type of USB relays.


### Usage
To initialize the script, use the command while in the ```relay``` directory:
```
python -i api.py
```

### Functionalities
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

To test, hook up a valve as shown in LHCb-Valve-Diagram.png. 
Call the TestRelay(x) method, where x is the number of seconds between each ON/OFF switch. 

```
>>>TestRelay(12)
```
Will initiate a loop where there is a 12 second pause between ON/OFF switches. Use Ctrl+C to exit.

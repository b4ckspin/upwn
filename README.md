# upwn
UPC/UBEE router default Wifi password generator and tester
based on work from yolosec, haxxin, .. 

## Demo:
![upwn usage](https://github.com/b4ckspin/upwn/blob/master/gif/tty.gif "upwn usage")

## Python:
Upwn is written in Python 2.7.6

## Download:
```
$ git clone https://github.com/b4ckspin/upwn.git
```

## Usage:
Start upwn
```
$ sudo python upwn.py
```

## Features:
### beta
- Scan Wifi Accesspoints for possible vulnerable UPC/UBEE router
- Select interface
- Select victim AP
- Select prefix for less keys to test
- If the router is a UBEE router, generate passkey and try it first
- Try the range of keys selected
- Auto connects to AP if key is found

  * UPC Admin interface:
  * 192.168.0.1
    * admin :: admin

### bugs
- upwn could report a false positive key (first key usually). This is because the networkmanager auto connected to a previously known wifi.
  * delete this connection and restart upwn.
- unexpected user input may crash upwn.
  * Wait for the next version
- No Wifi found
  * Restart your wifi interface or reconnect usb dongle

### next version
- Save which APs were tried, key (if found), state (which keys have we tried already? Leave them out)
- Add commandline support including minimal output (generated keys, key found/not found, maybe some more info)

## License:
This project is licensed under the ??? License 

## Acknowledgments:
* haxxin, deadcode, ...

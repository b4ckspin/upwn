# upwn
UPC/UBEE pwn tool

![upwn usage](https://github.com/b4ckspin/upwn/markdown/tty.gif "upwn usage")

Features

beta:
- Scan Wifi Accesspoints for possible vulnerable UPC/UBEE router
- Select interface
- Select victim AP
- Select prefix for less keys to test
- Select which band to test (ghz)
- If the router is a UBEE router, generate passkey and try it first
- Try the range of keys selected
- Auto connects to AP if key is found

Admin Interface of UPC router:
192.168.0.1admin::admin


next version:
- Auto select band of AP (delete band selection from tool)
- Save which APs were tried, key (if found), state (which keys have we tried already? Leave them out)
- Add commandline support including minimal output (generated keys, key found/not found, maybe some more info)
- some better coding :P
- better README (add credits, sources to repo)


Bugs:

- upwn could report a false positive key (first key usually). This is because you networkmanager auto connected to a previously known wifi.
-- delete this connection and restart upwn.
- The test output when trying keys has a counting error when testing UBEE key + others.
-- wait for next version
- unexpected user input may crash upwn.
-- wait for the next version
- No Wifi found
-- Restart your wifi interface or reconnect usb dongle

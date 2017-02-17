# upwn
UPC/UBEE pwn tool

Features

beta:	
	Scan Wifi Accesspoints for possible vulnerable UPC/UBEE router
	Select interface
	Select victim AP
	Select prefix for less keys to test
	Select which band to test (ghz)
	If the router is a UBEE router, generate passkey and try it first
	Try the range of keys selected
	Auto connects to AP if key is found

	Admin Interface of UPC router:
	192.168.0.1	admin::admin


next version:
	Auto select band of AP (delete band selection from tool)
	Save which APs were tried, key (if found), state (which keys have we tried already? Leave them out)	
	Add commandline support including minimal output (generated keys, key found/not found, maybe some more info)
	some better coding :P
	better README
	

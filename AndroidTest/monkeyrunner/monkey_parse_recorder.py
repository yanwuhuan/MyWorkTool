#!/usr/bin/env monkeyrunner
import sys

CMD_MAP = {
    'TOUCH': lambda arg: sys.stdout.write("    device.touch(" + str(arg["x"])+","+str(arg["y"]) \
                               +",\"" + arg["type"]+"\")\n"),
    #'DRAG': lambda arg: sys.stdout.write("device.drag(eval(\"" + str(arg) +"\"))\n"),
    'PRESS': lambda arg: sys.stdout.write("    device.press(\"" + arg["name"] + "\",\"" + arg["type"] + "\")\n"),
    'TYPE': lambda arg: sys.stdout.write("    device.type(\"" + arg["message"] + "\")\n"),
    'WAIT': lambda arg: sys.stdout.write("    mr.sleep(" + str(arg["seconds"]) +")\n"),
    'RUN'  : lambda arg: sys.stdout.write("    device.startActivity(component='" + arg["component"] + "')\n"),
    }


def parse_file(fname):
    fp = open(fname, 'r')
    for line in fp:
        (cmd, rest) = line.split('|')
        try:
            # Parse the pydict
            rest = eval(rest)
        except:
            print('unable to parse options')
            continue

        if cmd not in CMD_MAP:
            print('unknown command: ' + cmd + "|" + str(rest))
            continue

        CMD_MAP[cmd](rest)
    fp.close();


def main(fname="act.txt", cnt="1"):
    print("from com.android.monkeyrunner import MonkeyRunner as mr")
    #print("from com.android.monkeyrunner import MonkeyDevice as md")
    #print("from com.android.monkeyrunner import MonkeyImage as mi")
    print("\ndevice = mr.waitForConnection()\n")
    print("mr.sleep(2.0)\n")
    print("for i in range(0,%s):" % cnt)
    parse_file("act.txt")

if __name__ == '__main__':
    args = len(sys.argv)
    if  1 == args:
        print("Usage : " + sys.argv[0] + " filename_record.txt number_count")
        main()
    elif 2==args:
        main(sys.argv[1])
    else:
        main(sys.argv[1], sys.argv[2])

#!/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
# Time-stamp: <2012-06-04 14:17:32 Tanis Zhang>


import re

class Event3:
    """Other key"""
    def __init__(self):
        self.key_val = -1
        self.pressed = -1

    def feed(self, a1,a2,a3):
        if a1==0 and a2==0 and a3==0:
            print("Key: %d, press %d" % (self.key_val, self.pressed))
            self.key_val = -1
            self.pressed = -1
            #print("Key: sync signal")
        elif a1==1:
            if a3==1:
                self.key_val = a2
                self.pressed = 1
            elif a3==0:
                self.key_val = a2
                self.pressed = 0
    

class Event4:
    """Touch screen"""
    def __init__(self):
        self.x = -1
        self.y = -1
        self.pressed = 0

    def feed(self, a1,a2,a3):
        if a1==0 and a2==0 and a3==0:
            #print("Touch point : %d %d" % (self.x, self.y))
            print("Touch once, skip")
            return # one touch sync signal
        elif a1==0 and a2 == 2 and a3==0:
            if self.pressed == 1:
                print("Touch finger,down: %d %d" % (self.x, self.y))
            else:
                print("Touch finger,up: %d %d" % (self.x, self.y))
            return # on finger sync signal
        elif a1==3 and a2==0x35:
            self.x = a3
            #print("Touch x: %d" % a3)
        elif a1==3 and a2==0x36:
            self.y = a3
            #print("Touch y: %d" % a3)
        elif a1==3 and a2==0x30:
            if a3==1:
                self.pressed = a3
                #print("Touch down: %d %d" % (self.x, self.y))
            elif a3==0:
                self.pressed = a3
                #print("Touch up: %d %d" %(self.x, self.y))
            else:
                print("Touch unkonwn: 3 0030 %x" % a3)
        else:
            print("Touch: Unknow: %x %x %x" % (a1,a2,a3))

def evt5(a1,a2,a3):
    """Power key"""
    if a1==0 and a2==0 and a3==0:
        return # sync signal
    if (a1==1 and a3 == 1):
        print("Power key down: %d" % a2)
    elif (a1==1 and a3==0):
        print("Power key up: %d" % a2)
    else:
        print("Power key unknow: %d %d %d" % (a1,a2,a3))

        
        
        
        
def parse(io_file):
    tag_re = \
           re.compile("^(\d+)\-(\d+):\s*\/dev\/input\/event([345]):\s*([\da-fA-F]+)\s+([\da-fA-F]+)\s+([\da-fA-F]+)\s*$")
    io_file.seek(0)
    line = io_file.readline()
    sec_last = 0
    msec_last = 0
    evt3 = Event3()
    evt4 = Event4()
    while line:
        matchs = tag_re.match(line)
        if matchs :
            sec = int(matchs.group(1))
            msec = int(matchs.group(2))
            if sec_last ==0:
                sec_last = sec
                msec_last = msec
            else:
                sec_val = 0
                mdelta = msec - msec_last + (sec - sec_last)*1000000
                if mdelta >= 100000:
                    delta = mdelta/1000000.0
                    print("sleep %.1f" % delta)
                    #print("   sec: %d\n   last: %d\n" % (sec,sec_last))
                    #print("   msec: %d\n   last: %d\n" % (msec,msec_last))
                    #print("  mdelta %d" % mdelta)

                sec_last = sec
                msec_last = msec

            evt_idx = int(matchs.group(3),16)
            param1 = int(matchs.group(4),16)
            param2 = int(matchs.group(5),16)
            param3 = int(matchs.group(6),16)
            #print( "/dev/input/event%d %d %d %d" % (evt_idx,param1,param2,param3) )
            if evt_idx == 5:
                evt5(param1,param2,param3)
            elif evt_idx==4:
                evt4.feed(param1,param2,param3)
            elif evt_idx==3:
                evt3.feed(param1,param2,param3)
            else:
                print("evt %d: %d %d %d" % (evt_idx,param1,param2,param3) )
        else:
            pass
        line = io_file.readline()


def test(fname):
    fh = open(fname)
    parse(fh)
    fh.close()
    pass



if "__main__" == __name__:
    import io
    test_input_string = """180593-283470: /dev/input/event4: 0003 0035 0000008d
180593-283775: /dev/input/event4: 0003 0036 0000015e
180593-283897: /dev/input/event4: 0003 0030 00000001
180593-284019: /dev/input/event4: 0000 0002 00000000
180634-644092: /dev/input/event4: 0000 0000 00000000
"""
    #test_input = io.StringIO(test_input_string)
    #parse(test_input)
    test("output.txt")

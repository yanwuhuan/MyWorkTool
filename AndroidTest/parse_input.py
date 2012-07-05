#!/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
# Time-stamp: <2012-06-14 10:37:01 Tanis Zhang>


import re

def calc_time(sec,msec):
    res = (sec*1000000 + msec)/1000000.0
    val = "%.1f" % res
    return val

class Event3:
    """Other key"""
    def __init__(self):
        self.key_val = -1
        self.pressed = -1

    def feed(self, a1,a2,a3):
        """Affect event, return 1"""
        ret = 0
        if a1==0 and a2==0 and a3==0:
            print("Key: %d, press %d" % (self.key_val, self.pressed))
            self.key_val = -1
            self.pressed = -1
            ret = 0
            #print("Key: sync signal")
        elif a1==1:
            if a3==1:
                self.key_val = a2
                self.pressed = 1
                ret = 1
            elif a3==0:
                self.key_val = a2
                self.pressed = 0
                ret = 1
        return ret
    

class Event4:
    """Touch screen"""
    def __init__(self):
        self.x = -1
        self.y = -1
        self.pressed = 0

    def feed(self, a1,a2,a3):
        """Affect event, return 1"""
        ret = 0
        if a1==0 and a2==0 and a3==0:
            #print("Touch point : %d %d" % (self.x, self.y))
            #print("Touch once, skip")
            pass # one touch sync signal
        elif a1==0 and a2 == 2 and a3==0:
            if self.pressed == 1:
                print("Touch finger,down: %d %d" % (self.x, self.y))
            else:
                print("Touch finger,up: %d %d" % (self.x, self.y))
            ret = 1# on finger sync signal
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
        return ret

class Event5:
    """Power key"""
    def __init__(self):
        pass

    def feed(self,a1,a2,a3):
        """Affect event, return 1"""
        ret = 0
        if a1==0 and a2==0 and a3==0:
            return 0 # sync signal
        if (a1==1 and a3 == 1):
            print("Power key down: %d" % (a2))
            ret = 1
        elif (a1==1 and a3==0):
            print("Power key up: %d" % (a2))
            ret = 1
        else:
            print("Power key unknown: %d %d %d" % (a1,a2,a3))
        return ret


class EventMgr:
    """Manager event, for time"""
    def __init__(self):
        self.last_mtime=0
        self.evt3 = Event3()
        self.evt4 = Event4()
        self.evt5 = Event5()
        pass

    def dispatch(self,evt_idx,param1,param2,param3,sec,msec):
        is_valid = 0
        if evt_idx == 5:
            is_valid = self.evt5.feed(param1,param2,param3)
        elif evt_idx==4:
            is_valid = self.evt4.feed(param1,param2,param3)
        elif evt_idx==3:
            is_valid = self.evt3.feed(param1,param2,param3)
        else:
            print("evt %d: %d %d %d" % (evt_idx,param1,param2,param3) )

        if is_valid == 1:
            if self.last_mtime == 0:
                self.last_mtime = sec*10**6 + msec
            else:
                mtime = sec*10**6 + msec
                mdelta = mtime - self.last_mtime
                if mdelta >= 10**5:
                    delta = mdelta /1000000.0
                    print("sleep %.1f" % delta)
                self.last_mtime = mtime
                
    
def parse(io_file):
    tag_re = \
           re.compile("^(\d+)\-(\d+):\s*\/dev\/input\/event([345]):\s*([\da-fA-F]+)\s+([\da-fA-F]+)\s+([\da-fA-F]+)\s*$")
    io_file.seek(0)
    line = io_file.readline()
    sec_last = 0
    msec_last = 0
    evt3 = Event3()
    evt4 = Event4()
    evt5 = Event5()
    evt_mgr = EventMgr()
    while line:
        matchs = tag_re.match(line)
        if matchs :
            sec = int(matchs.group(1))
            msec = int(matchs.group(2))
            evt_idx = int(matchs.group(3),16)
            param1 = int(matchs.group(4),16)
            param2 = int(matchs.group(5),16)
            param3 = int(matchs.group(6),16)
            #print( "/dev/input/event%d %d %d %d" % (evt_idx,param1,param2,param3) )
            evt_mgr.dispatch(evt_idx, param1,param2,param3,sec,msec)
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

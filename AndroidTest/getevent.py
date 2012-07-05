#!/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
# Time-stamp: <2012-06-04 14:42:31 Tanis Zhang>

import os
import subprocess
import shlex
import re

class process_mgr:
    """ Python manager the process """
    def __init__(self, cmd):
        self.args = shlex.split(cmd)
        self.appPath = args[0]
        self.pid = None
        self.p = None

    def catch_run(self):
        fout = open("output.txt", "w")
        try:
            if(os.path.exists(self.appPath)):
                self.p = subprocess.Popen(self.args,0,None, 
                    None, fout, None)
                self.pid = self.p.pid
                if self.pid is None:  
                    return False  
                return True
            else:
                print('Path '+self.appPath+ "is NOT exists!")
        except KeyboardInterrupt as e:
            pass
        finally:
            fout.close()
    
    def start(self):
        self.catch_run()
        sts = self.p.wait()
        print("OK, catch the event, parsing ...")
        fh = open("output.txt", "r")
        self.parse(fh)
        fh.close()

    def parse(self,io_file):
        tag_re = \
               re.compile("^(\d+)\-(\d+):\s*\/dev\/input\/event([345]):\s*([\da-fA-F]+)\s+([\da-fA-F]+)\s+([\da-fA-F]+)\s*$")
        io_file.seek(0)
        line = io_file.readline()
        sec_last = 0
        msec_last = 0
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
                        delta = mdelta/1000000
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
                print( "/dev/input/event%d %d %d %d" % (evt_idx,param1,param2,param3) )
            else:
                pass
            line = io_file.readline()



if "__main__" == __name__:
    cmd = 'D:/MyHome/Apps/Phone/android_tools/adb.exe shell getevent -t'
    args = shlex.split(cmd)
    mgr = process_mgr(cmd)
    mgr.start()
    #popenData = subprocess.Popen(args,shell = False)
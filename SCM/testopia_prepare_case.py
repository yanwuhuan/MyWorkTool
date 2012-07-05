#!/bin/env python
# -- coding: utf-8 --

from win32com.client import Dispatch
import types
import re
from os import getcwd,system,sep

# for xml.sax.saxutils.escape(data)
try:
    import xml.sax.saxutils
except ImportError as e:
    raise ImportError("requires xml.sax.saxutils package!")





header = """<?xml version="1.0" encoding="UTF-8" ?>
<tr:testopia
 version="2.3"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:tr="http://www.mozilla.org/projects">

"""

footer = """
</tr:testopia>"""


case_template = """
    <tr:testcase>
            <tr:summary>%s</tr:summary>
            <tr:case_status>CONFIRMED</tr:case_status>
            <tr:priority>%s</tr:priority>
            <tr:category>
                <tr:name>%s</tr:name>
                <tr:product>%s</tr:product>
            </tr:category>
            <tr:author>
                <tr:login>%s</tr:login>
            </tr:author>
            <tr:isautomated>false</tr:isautomated>
            <tr:tag>BUGFIXED</tr:tag>
            <tr:linked_plans>%s</tr:linked_plans>
            <tr:text version="1">
                <tr:action><![CDATA[%s]]></tr:action>
                <tr:expected_result><![CDATA[%s]]></tr:expected_result>
                <tr:setup><![CDATA[<br>]]></tr:setup>
                <tr:breakdown><![CDATA[<br>]]></tr:breakdown>
            </tr:text>
        </tr:testcase>
"""

def use_temp(summary, \
             action, \
             result, \
             category, \
             plan_id=1, \
             pri="P3", \
             product="UP812B", \
             email="zhang.xiaojie@trigger.org"
             ):
    case = case_template % \
           (summary,pri,category,product,email,plan_id,action,result)
    return case

def pick_up_case(values, basepath, category="Release"):
    rr = re.compile('[\r\n]')
    length = len(values)

    curout = ""
    outpath = basepath
    fout = None
    
    fname = basepath + ".xml"
    fout = open(fname, 'wb')
    fout.write(header.encode('utf-8'))


    for row in range(1,length):
        summary = values[row][0]
        action = values[row][1]
        expect = values[row][2]
        
        if  summary == None \
           and action == None \
           and expect == None:
            continue
        if  summary == None \
           or action == None \
           or expect == None:
            err_row = row + 1
            print("-- %d --" % err_row)
            if summary != None :
                print("summary " + summary)
            if action != None :
                print("action " + action)
            if expect != None :
                print("expect " + expect)
            print("=====")
            continue

        summary = xml.sax.saxutils.escape(summary.strip())
        action = xml.sax.saxutils.escape(action.strip())
        expect = xml.sax.saxutils.escape(expect.strip())
        action = rr.sub("<br>\n", action)
        expect = rr.sub("<br>\n", expect)
        fout.write(use_temp(summary,action,expect,category, 5).encode('utf-8'))

    fout.write(footer.encode('utf-8'))
    fout.close()

if __name__ == '__main__':
    cur_path=getcwd()

    fname = "Stress.xls"
    filepath = cur_path + sep + fname
    
    #print("%s%s%s" % (header,case_template, footer))
    xlsApp = Dispatch("Excel.Application")
    xlsApp.Workbooks.Open(cur_path + sep + fname)
    xlsBook = xlsApp.Workbooks(fname)
    for i in range(500):
        try:
            sheet_name = xlsBook.Sheets[i].name
            allValue=xlsBook.Sheets[sheet_name].Range('A1:C900').Value
            category = sheet_name
            outpath = cur_path + sep + "Stress" + sep + category
            print(category)
            pick_up_case(allValue, outpath, category)
        except IndexError as e:
            break

    # sheet.name
    # Sheets['sheet_name']
    xlsBook.Close(SaveChanges = 0)
    del xlsApp

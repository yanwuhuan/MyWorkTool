#!/bin/env python
# -- encoding: utf-8 --



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
            <tr:summary>%SUMMARY%</tr:summary>
            <tr:case_status id="2">CONFIRMED</tr:case_status>
            <tr:priority id="1">P1</tr:priority>
            <tr:category id="14">
                <tr:name>%MODULE%</tr:name>
                <tr:product id="9">UP810</tr:product>
            </tr:category>
            <tr:author id="1">
                <tr:login>%EMAIL%</tr:login>
                <tr:name>%REALNAME%</tr:name>
            </tr:author>
            <tr:isautomated>false</tr:isautomated>
            <tr:tag>BUGFIXED</tr:tag>
            <tr:linked_plans>1</tr:linked_plans>
            <tr:text version="5">
                <tr:author>%REALNAME%</tr:author>
                <tr:action><![CDATA[%ACTIONS%]]></tr:action>
                <tr:expected_result><![CDATA[%RESULTS%]]></tr:expected_result>
                <tr:setup><![CDATA[%%PREPARE%]]></tr:setup>
                <tr:breakdown><![CDATA[]]></tr:breakdown>
            </tr:text>
        </tr:testcase>
"""

print("%s%s%s" % (header,case_template, footer))

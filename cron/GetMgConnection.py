#!/usr/bin/python

import requests
import re

class GetMgConnection():
    def __init__(self, lbtype, lbname, vip, timerange):
        self.average_connection = ""
        self.max_connection = ""
        if lbtype == "netscaler":
            virtualname = vip[0].replace(":", ".")    #multigraph does this
            url = "http://mg.vip.ebay.com/?target=%2F" + lbtype + "%2F" + lbname + "%2Fvirtualservers%2F" + virtualname + "%2F" + virtualname + ";view=Connections;ranges=" + timerange
            pattern = ".*open client connections</font></TD><TD align=right>(.*?) connections</TD><TD align=right>(.*?) connections</TD><TD align=right>(.*?) connections</TD>"
        if lbtype == "bigip":
            #url = "http://mg.vip.smf.ebay.com/?target=%2F" + lbtype + "%2F" + lbname + "%2Fvirtualserver%2F" + virtualname + ";view=Connections;ranges=" + timerange
            #pattern = ".*ltmvirtualservstatclientcurconns</font></TD><TD align=right>(.*?) </TD><TD align=right>(.*?) </TD><TD align=right>(.*?) </TD>"
            url = "http://mg.vip.smf.ebay.com/?target=%2F" + lbtype + "%2F" + lbname + "%2Fvirtualaddress%2F" + vip[1] + ";view=Connections;ranges=" + timerange
            url_ext = "http://mg.vip.smf.ebay.com/?target=%2F" + lbtype + "%2F" + lbname.replace(".", "-ext.", 1) + "%2Fvirtualaddress%2F" + vip[1] + ";view=Connections;ranges=" + timerange
            url_int = "http://mg.vip.smf.ebay.com/?target=%2F" + lbtype + "%2F" + lbname.replace(".", "-int.", 1) + "%2Fvirtualaddress%2F" + vip[1] + ";view=Connections;ranges=" + timerange
            pattern = ".*ltmvirtualaddrstatclientcurconns</font></TD><TD align=right>(.*?) </TD><TD align=right>(.*?) </TD><TD align=right>(.*?) </TD>"
        html = requests.get(url)
        text = html.text.replace("\n", "")
        m = re.match(pattern, text)
        if m is None:
            html = requests.get(url_ext)
            text = html.text.replace("\n", "")
            m = re.match(pattern, text)
            if m is None:
                html = requests.get(url_int)
                text = html.text.replace("\n", "")
                m = re.match(pattern, text)
        self.average_connection = m.group(2)
        self.max_connection = m.group(3)
            
#a = GetConnection("netscaler", "phxlb199.phx.ebay.com", "bir001-web-1-443", "w")
#a = GetMgConnection("bigip", "slclb05.slc.ebay.com", "edpn.ebay.com-443", "w")
#print a.max_connection

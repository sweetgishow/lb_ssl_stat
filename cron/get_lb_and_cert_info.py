#!/usr/bin/python

from glob import glob
import dns.resolver
import re

from Netscaler import Netscaler
from Bigip import Bigip
from GetCertInfo import GetCertInfo
from GetMgConnection import GetMgConnection
from OdbTool import OdbSearchByIp
from MultithreadRun import multithreadrun

from pprint import pprint

class GetLBAndCertInfo():
    def __init__(self):
        self.data = {"name": "", "lbtype": "", "model": "", "os": "", "ssl": []}
        self.name = ""
        self.lbtype = ""
        self.model = ""
        self.os = ""
        self.ssl = []
    def run_all(self, conf_file):
        re_match = re.match(".*ns.conf$", conf_file)
        if re_match is not None:
            lb = Netscaler()
            self.data["lbtype"] = "netscaler"
        else:
            lb = Bigip()
            self.data["lbtype"] = "bigip"
        lb.import_conf(conf_file)
        self.data["name"] = lb.name

        #get ssl info of the vips that are on this LB
        ssl_vip = lb.search_https_vip()
        ssl = []
        for vip in ssl_vip:
            try:
                cert_info = GetCertInfo(vip['address'])
                bit  = cert_info.bit
                not_after = cert_info.not_after
                days_to_expire = cert_info.days_to_expire
            except:
                bit  = "-"
                not_after = "-"
                days_to_expire = "-"

#            try:    
#                connection = GetMgConnection(self.data["lbtype"], self.data["name"], vip, "w")
#                max_conn = connection.max_connection
#                avg_conn = connection.average_connection
#            except:
            max_conn = "-"  #those will be updated by another script that runs like every 30 mins, not daily
            avg_conn = "-"
            ssl_info = {"vip_name": vip['name'], "vip_address": vip['address'], "bit": bit, "cert_expiration_date": not_after, "days_to_expire": days_to_expire, "average_connection": avg_conn, "max_connection": max_conn}
            ssl.append(ssl_info)
        self.data["ssl"] = ssl
        #get the LB model and os version
        fqdn = self.data["name"]
        if re.match("a\.|b\.", self.data["name"]) is None:
            fqdn = self.data["name"].replace(".", "a.", 1)  #get the ip of the LB a node
        try:
            ip = dns.resolver.query(fqdn, "A")[0].address
            odb = OdbSearchByIp(ip)
            self.data["model"] = odb.get_attribute("model")
            self.data["os"] = odb.get_attribute("osversion")
        except:
            self.data["model"] = "-"
            self.data["os"] = "-"

#def main():
def childthread(lbsslstat, conf_file):
    lbsslstat.run_all(conf_file)
    

def main():
    alllbsslstat = []
    arg = []
    for i in (glob("/var/tmp/current/*.ns.conf") + glob("/var/tmp/current/*.bigip.conf")):
        lbsslstat = GetLBAndCertInfo()
        alllbsslstat.append(lbsslstat)
        arg.append((lbsslstat, i))
        
    #a  = GetLBAndCertInfo()
    multithreadrun(childthread, arg, 40)
    
    alldata = []
    for i in alllbsslstat:
        if i.data["ssl"] != []:
            alldata.append(i.data)
    file = open("/var/tmp/sslstat", "w")
    print >>file, alldata

if __name__ == "__main__":
    main()

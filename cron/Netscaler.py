#!/usr/bin/python

import re

class Netscaler():

    def __init__(self, name = "unknown netscaler"):
        self.name = name
        self.server = {}
        self.service = {}
        self.lbv = {}
        self.csv = {}
        self.link_lbv_to_service = {}
        self.link_service_to_lbv = {}   #not necessary, to make programing easier and program run faster
        self.link_csv_to_lbv = {}
        self.link_lbv_to_csv = {}
        self.link_sslv = {}
        #data structure:
        #self.server = {"sjcwww01": "10.10.10.11",
        #               "sjcwww02": "10.10.10.12"}
        #self.service = {"sjcwww01-80": {"server_name": "sjcwww01", "port": "80"},
        #                "sjcwww02-80": {"server_name": "sjcwww02", "port": "80"}}
        #self.lbv = {"www.ebay.com-80": {"vip": "66.135.10.11", "port": "80"},
        #            "api.ebay.com": {"vip": "0.0.0.0", "port": "0"}}
        #self.csv = {"api.ebay.com-443": {"vip": "66.135.10.12", "port":"443"}
        #            "abc.sjc.ebay.com": {"vip": "10.10.11.11", "port": "8080"}}
        #"link" are considered many-to-many
        #All the "link":
        #self.link_lbv_to_service = {"www.ebay.com-80": ["sjcwww01-80", "sjcwww02-80],
        #                            "lbv1": ["service1", "service2", "service3"]}

    def import_conf(self, conf_file_or_conf_dir):   #"reset_name" allows to init the Netscaler object without hostname then set the hostname according to the config file's filename
        if self.name == "unknown netscaler":
            re_match = re.match("(.*/)?(.*).ns.conf", conf_file_or_conf_dir)
            self.name = re_match.group(2)
            conf = open(conf_file_or_conf_dir).readlines()
        else:
            conf = open(conf_file_or_conf_dir + "/" + self.name + ".ns.conf").readlines()

        add_server = "^add server (\S*) (\S*)"
        add_service = "^add service (\S*) (\S*) \S* (\d*)"
        add_lbv = "^add lb vserver (\S*) \S* (\S*) (\d*)"
        crazy_lbv = "^add lb vserver (\S*)" #to deal with like on sjclb112 "^add lb vserver kemmisc-app-1-8080 HTTP$"
        add_csv = "^add cs vserver (\S*) \S* (\S*) (\d*)"
        link_lbv = "^bind lb vserver (\S*) (\S*)"
        link_csv = "^bind cs vserver (\S*) (\S*)"
        link_sslv = "^bind ssl vserver (\S*)"

        for line in conf:
            re_match = re.match(add_server, line)
            if (re_match is not None):
                self.server[re_match.group(1)] = re_match.group(2)
                continue
            re_match = re.match(add_service, line)
            if (re_match is not None):
                self.service[re_match.group(1)] = {"server_name": re_match.group(2), "port": re_match.group(3)}
                self.link_service_to_lbv[re_match.group(1)] = []
                continue
            re_match = re.match("^add lb vserver (\S*) (\S*)$", line)
            if re_match is not None:
                line = line.strip() + " 0.0.0.0 0"  #to deal with "^add lb vserver NT_GB_app_dummy_pool HTTP$"
            re_match = re.match(add_lbv, line)
            if (re_match is not None):
                self.lbv[re_match.group(1)] = {"vip": re_match.group(2), "port": re_match.group(3)}
                self.link_lbv_to_service[re_match.group(1)] = []
                self.link_lbv_to_csv[re_match.group(1)] = []
                continue
            re_match = re.match(crazy_lbv, line)
            if (re_match is not None):
                self.lbv[re_match.group(1)] = {"vip": "0.0.0.0", "port": "0"}
                continue
            re_match = re.match(add_csv, line)
            if (re_match is not None):
                self.csv[re_match.group(1)] = {"vip": re_match.group(2), "port": re_match.group(3)}
                self.link_csv_to_lbv[re_match.group(1)] = []
                continue
            re_match = re.match(link_lbv, line)
            if (re_match is not None):
                if re_match.group(2) != "-policyName":  #to skip: "link lb vserver lbv_name -policyName policy_name"
                    if (not re_match.group(2) in self.link_lbv_to_service[re_match.group(1)]):
                        self.link_lbv_to_service[re_match.group(1)].append(re_match.group(2))
                        self.link_service_to_lbv[re_match.group(2)].append(re_match.group(1))
                continue
            re_match = re.match(link_csv, line)
            if (re_match is not None):
                if re_match.group(2) != "-policyName":
                    if (not re_match.group(2) in self.link_csv_to_lbv[re_match.group(1)]):
                        self.link_csv_to_lbv[re_match.group(1)].append(re_match.group(2))
                        self.link_lbv_to_csv[re_match.group(2)].append(re_match.group(1))
                       # print re_match.group(2), re_match.group(1)
                continue
            re_match = re.match(link_sslv, line)
            if (re_match is not None):
                self.link_sslv[re_match.group(1)] = ""

    def search(self, ip = None, port = None, scope = "all"): #search any IP and/or port that are configured on the netscaler, return the top level(lbv/csv) (even when a server is searched, the csv/lbv will be returned)
        if scope == "all":
            search_vip = True
            search_server = True
        if scope == "vip":
            search_vip = True
            search_server = False
        if scope == "server":
            search_vip = False
            search_server = True

        matched = []
        matched_unique = []
        if search_vip == True:
            for csv_name in self.csv:   #search in csv
                if ((self.csv[csv_name]["vip"] == ip or ip == None) and (self.csv[csv_name]["port"] == port or port == None)):
                    matched.append({'name': csv_name, 'address': self.csv[csv_name]["vip"], 'port': self.csv[csv_name]["port"], 'type': "csv"})
            for lbv_name in self.lbv:   #search in lbv
                if ((self.lbv[lbv_name]["vip"] == ip or ip == None) and (self.lbv[lbv_name]["port"] == port or port == None)):
                    if self.link_lbv_to_csv[lbv_name] != []:    #if the lbv is linked to csv, then retreive the csv
                        for csv_name in self.link_lbv_to_csv[lbv_name]:
                            matched.append({'name': csv_name, 'addess': self.csv[csv_name]["vip"], 'port': self.csv[csv_name]["port"], 'type': "csv"})
                    else:
                        matched.append({'name': lbv_name, 'address': self.lbv[lbv_name]["vip"], 'port': self.lbv[lbv_name]["port"], 'type': "lbv"})
        if search_server == True:
            for service_name in self.service:   #search in server
                if ((self.server[self.service[service_name]["server_name"]] == ip or ip == None) and (self.service[service_name]["port"] == port or port == None)):
                    if self.link_service_to_lbv[service_name] != []:
                        for lbv_name in self.link_service_to_lbv[service_name]:
                            if lbv_name in self.link_lbv_to_csv:
                                for csv_name in self.link_lbv_to_csv[lbv_name]:
                                    matched.append({'name': csv_name, 'address': self.csv[csv_name]["vip"], 'port': self.csv[csv_name]["port"], 'type': "csv"})
                            else:
                                matched.append({'name': lbv_name, 'address': self.lbv[lbv_name]["vip"], 'port': self.lbv[lbv_name]["port"], 'type': "lbv"})
        for i in matched:
            if not i in matched_unique:
                matched_unique.append(i)
        return matched_unique

    def search_https_vip(self):
        https_vip = []
        search = self.search(None, "443", "vip")
        for i in search:
            if i['name'] in self.link_sslv:  #ssl offload could be on the server side, not on lb, and those vips are ignored
                https_vip.append(i)
        return https_vip

                        
#a = Netscaler("phxlb93.phx.ebay.com")
#a.import_conf("current")
#b = a.search_https_vip()
#print b

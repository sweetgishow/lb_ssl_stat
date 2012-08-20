#!/usr/bin/python

import re
#from pprint import pprint

class Bigip():

    def __init__(self, name = "unknown bigip"):
        self.name = name
        self.virtual = {}
        self.link_virtual_to_pool = {}
        self.link_pool_to_virtual = {}
        self.link_pool_to_member = {}
        self.link_member_to_pool = {}
        self.sslprofile = {}
        #self.link_profile_to_virtual = {}
        self.link_virtual_to_profile = {}
        #data structure:
        #virtual = {"www.ebay.com-80": {"vip": 66.135.1.2", "port": "80"},
        #           "www.ebay.com-443": {"vip": 66.135.1.2", "port": "443"}}
        #link_virtual_to_pool = {"www.ebay.com-80": ["www_pool"],
        #                        "www.ebay.com-443": ["https_pool"]}
        #link_pool_to_virtual same as above
        #link_pool_to_member = {"www_pool": [{"node": "10.1.122.1", "port": "8080"},{}]}
        #link_member_to_pool = {"10.1.122.1": {"8080": ["pool1", "pool2"], "443": ["pool3", "pool4"]}, "10.2.2.2": {}}
    def import_conf(self, conf_file):
        if self.name == "unknown bigip":
            re_match = re.match("(.*/)?(.*).bigip.conf", conf_file)
            self.name = re_match.group(2)
            conf = open(conf_file).readlines()
        else:
            conf = open(conf_file_or_conf_dir + "/" + self.name + ".bigip.conf").readlines()

        new_pool = "^pool (\S*) {"
        new_virtual = "^virtual (\S*) {"
        new_clientssl_profile = "^profile clientssl (\S*) {"
        single_member_in_pool = "^ +members (\S*):(\S*)"
        multiple_member_in_pool = "^ +(\S*):(\S*)"
        single_profile_in_virtual = "^ +profiles (\S*) .+"
        multiple_profile_in_virtual = "^ +profiles {"
        pool_in_virtual = "^ +pool (\S*)"
        destination_in_virtual = "^ +destination (\S*):(\S*)"
        end_section = "^}"
        end_sub_section = "^ +}"

        in_pool_section_flag = False
        in_virtual_section_flag = False
        in_profile_section_of_virtual_section_flag = False
        pool_name = ""
        virtual_name = ""
        for line in conf:
            re_match = re.match(new_pool, line)
            if (re_match is not None):
                in_pool_section_flag = True
                pool_name = re_match.group(1)
                self.link_pool_to_member[pool_name] = []
                self.link_pool_to_virtual[pool_name] = []
                continue
            re_match = re.match(new_virtual, line)
            if (re_match is not None):
                in_virtual_section_flag = True
                virtual_name = re_match.group(1)
                self.virtual[virtual_name] = {}
                self.link_virtual_to_pool[virtual_name] = []
                self.link_virtual_to_profile[virtual_name] = []
                continue
            re_match = re.match(new_clientssl_profile, line)
            if re_match is not None:
                #in_profile_section = True
                profile_name = re_match.group(1)
                self.sslprofile[profile_name] = "clientssl"
                #self.link_profile_to_virtual[profile_name] = []
                continue
            re_match = re.match(end_section, line)
            if re_match is not None:
                #if (in_pool_section_flag == True or in_virtual_section_flag == True or in_profile_section_flag == True):
                in_pool_section_flag = False
                in_virtual_section_flag = False
                continue
            re_match = re.match(end_sub_section, line)
            if re_match is not None:
                #if (in_pool_section_flag == True or in_virtual_section_flag == True or in_profile_section_flag == True):
                in_profile_section_of_virtual_section_flag = False
                continue
                
            if in_pool_section_flag == True:
                re_match = re.match(single_member_in_pool, line)
                if (re_match is None):
                    re_match = re.match(multiple_member_in_pool, line)
                if (re_match is not None):
                    node = re_match.group(1)
                    port = re_match.group(2)    #could do something here to get rid of the port translation in /etc/services
                    self.link_pool_to_member[pool_name].append({"node": node, "port": port})
                    try:
                        self.link_member_to_pool[node][port].append(pool_name)  #self.link_member_to_pool[node] could not have been initialized yet
                    except:
                        self.link_member_to_pool[node] = {port: [pool_name]}    #initialize self.link_member_to_pool[node] as a dictionary
            if in_virtual_section_flag == True:
                re_match = re.match(pool_in_virtual, line)
                if (re_match is not None):
                    pool_name_in_virtual = re_match.group(1)
                    self.link_virtual_to_pool[virtual_name].append(pool_name_in_virtual)
                    self.link_pool_to_virtual[pool_name_in_virtual].append(virtual_name)
                    continue
                re_match = re.match(destination_in_virtual, line)
                if (re_match is not None):
                    self.virtual[virtual_name] = {"vip": re_match.group(1), "port": re_match.group(2)}
                    continue
                re_match = re.match(single_profile_in_virtual, line)
                if re_match is not None:
                    #print line,
                    profile_name = re_match.group(1)
                    if profile_name in self.sslprofile:
                        #self.link_profile_to_virtual[profile_name].append(virtual_name)
                        self.link_virtual_to_profile[virtual_name].append(profile_name)
                    continue
                re_match = re.match(multiple_profile_in_virtual, line)
                if re_match is not None:
                    in_profile_section_of_virtual_section_flag = True
                    continue
                if in_profile_section_of_virtual_section_flag == True:
                    re_match = re.match("^ +(\S+) .*{", line)
                    if re_match is not None:
                        profile_name = re_match.group(1)
                        #print profile_name
                        if profile_name in self.sslprofile:
                            #self.link_profile_to_virtual[profile_name].append(virtual_name)
                            self.link_virtual_to_profile[virtual_name].append(profile_name)
                    
    def search(self, ip = None, port = None, scope = "all"):    #search whatever, return the top level(virtual) that the searched searched string belongs to
        if port == "443":   #silly F5 doing port translation in config file
            port = "https"
        if scope == "all":
            search_vip = True
            search_node = True
        if scope == "vip":
            search_vip = True
            search_node = False
        if scope == "server":
            search_vip = False
            search_node = True
        matched = []
        matched_unique = []
        if search_vip == True:
            for virtual_name in self.virtual:
                if ((self.virtual[virtual_name]["vip"] == ip or ip == None) and (self.virtual[virtual_name]["port"] == port or port == None)):  #if the ip is 'None', then all ips will be matched, same as port
                    matched.append({'name': virtual_name, 'address': self.virtual[virtual_name]["vip"], 'port': self.virtual[virtual_name]["port"], 'type': "virtual"})
        if search_node == True: #if it's a node, then return all the virtuals that this node belongs to
            if ip in self.link_member_to_pool:
                if port in self.link_member_to_pool[ip]:
                    for pool in self.link_member_pool[ip][port]:
                        for virtual in self.link_pool_to_virtual[pool]:
                            matched.append({'name': virtual, 'address': self.virtual[virtual]["vip"], 'port': self.virtual[virtual]["port"], 'type': "virtual"})
                if port == None:    #if port is None, then all ports are matched
                    for port in self.link_member_to_pool[ip]:
                        for pool in self.link_member_to_pool[ip][port]:
                            for virtual in self.link_pool_to_virtual[pool]:
                                matched.append({'name': virtual, 'address': self.virtual[virtual_name]["vip"], 'port': self.virtual[virtual_name]["port"], 'type': "virtual"})
            if ip == None:
                for ip in self.link_member_to_pool:
                    if port in self.link_member_to_pool[ip]:
                        for pool in self.link_member_to_pool[ip][port]:
                            for virtual in self.link_pool_to_virtual[pool]:
                                matched.append({'name': virtual, 'address': self.virtual[virtual]["vip"], 'port': self.virtual[virtual]["port"], 'type': "virtual"})
                    if port == None:
                        for port in self.link_member_to_pool[ip]:
                            for pool in self.link_member_to_pool[ip][port]:
                                for virtual in self.link_pool_to_virtual[pool]:
                                    matched.append({'name': virtual, 'address': self.virtual[virtual]["vip"], 'port': self.virtual[virtual]["port"], 'type': "virtual"})
        for i in matched:
            if not i in matched_unique: #remove duplex virtuals in matched
                matched_unique.append(i)
        return matched_unique
    def search_https_vip(self):
        https_vip = []
        search = self.search(None, "443", "vip")
        #print self.sslprofile
        for i in search:
            if self.link_virtual_to_profile[i['name']] != []:   #sometimes even the LB has 443 vips, the cert is not on LB but on the server side, which means LB does not do any ssl offload, and those kind of vips will be ignored
                https_vip.append(i)
        return https_vip
        

#a = Bigip()
#a.import_conf("current/slclb42.slc.ebay.com.bigip.conf")
#b = a.search_https_vip()
#print b

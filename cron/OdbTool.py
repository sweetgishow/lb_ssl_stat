#!/usr/bin/python

import requests

class OdbSearchByIp():
    def __init__(self, ip):
        self.ip = ip
        self.result = {}
#    def search(self):
        search_url = "http://odb.vip.ebay.com:8080/jodbweb/odb.do?type=object&print=*&format=json&name=" + self.ip
        response = requests.get(search_url)
        attributes = response.json["objects"][0]["attributes"]
        for j in attributes:
            try:
                self.result[j["name"][0]] = j["value"][0]
            except:
                self.result[j["name"][0]] = ""
        
    def get_attribute(self, attribute):
        if attribute in self.result:
            return self.result[attribute]

#a = OdbSearchByIp("10.14.184.188")
#print a.get_attribute("hostname")

#!/usr/bin/python

from GetMgConnection import GetMgConnection
from MultithreadRun import multithreadrun

import ast

#read datafile generted by get_lb_and_cert_info.py that has everything but the connection data and fillin the connection data
class GetConnection():
    def __init__(self, datafile):
        self.datafile = datafile
        fh = open(self.datafile)
        content = fh.readlines()
        self.data = ast.literal_eval(content[0].strip())
        fh.close()
    def get_connection(self, lb_index, ssl_index, timerange):
        try:    
            connection = GetMgConnection(self.data[lb_index]["lbtype"], self.data[lb_index]["name"], self.data[lb_index]['ssl'][ssl_index]['vip_name'], self.data[lb_index]['ssl'][ssl_index]['vip_address'], timerange)
            self.data[lb_index]['ssl'][ssl_index]['max_connection'] = connection.max_connection
            self.data[lb_index]['ssl'][ssl_index]['average_connection'] = connection.average_connection
        except:
            self.data[lb_index]['ssl'][ssl_index]['max_connection'] = '-'
            self.data[lb_index]['ssl'][ssl_index]['average_connection'] = '-'
    def get_all_connection(self, timerange):
        arg = []
        for lb_index in range(len(self.data)):
            for ssl_index in range(len(self.data[lb_index]['ssl'])):
                arg.append((lb_index, ssl_index, timerange))
        multithreadrun(self.get_connection, arg, 30)

        datafile = open(self.datafile + "." + timerange, "w")
        print >>datafile, self.data
        datafile.close()

if __name__ == "__main__":
    get_connection = GetConnection('/var/tmp/sslstat')
    get_connection.get_all_connection('d')
    #get_connection.get_all_connection('w')
    #get_connection.get_all_connection('m')

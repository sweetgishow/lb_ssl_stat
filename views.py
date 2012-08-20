#!/usr/bin/python
import ast
from pprint import pprint

from django.http import HttpResponse
from django.utils import simplejson

def summary(request):

    default_cert_bit = 2048
    base = 2048.0

    max_capacity = {
    "10000 v1 1*CPU+4*BX+4*BZ": 10000,
    "10000 v1 1*CPU+4*BX+4*BZ+1*EZ": 10000,
    "9800 v2 1*BX+4*BX": 20000,
    "9950 v2 2CPU 1*BX+4*BX": 30000,
    "C103 deprecated": 20000,
    "C106 deprecated": 30000,
    "D106 deprecated": 40000,
    "D68 deprecated": 50000,
    "D88 deprecated": 8000,
    "NSMPX-10500 8*CPU+2*E1K+8*E1K+2*IX+8*CVM 1620": 10000
    }

    f = open("/var/www/html/ext/sslstat").readlines()
    data = ast.literal_eval(f[0].strip())
    return_data = []
    for i in data:
        accuracy = True
        avg_conn = 0
        max_conn = 0
        for j in i["ssl"]:
            if j["bit"] == "-":
                bit = default_cert_bit
                accuracy = False
            else:
                bit = int(j["bit"])
            if j["average_connection"] != '-':
                avg_conn += float(j["average_connection"]) * (bit/base) * (bit/base)
            else:
                accuracy = False
            if j["max_connection"] != "-":
                max_conn += float(j["max_connection"]) * (bit/base) * (bit/base)
            else:
                accuracy = False
        i["average_connection"] = str(avg_conn).split(".")[0]
        i["max_connection"] = str(max_conn).split(".")[0]
        i["average_load"] = str(avg_conn/max_capacity[i["model"]] * 100).split(".")[0] + "%"
        i["max_load"] = str(max_conn/max_capacity[i["model"]] * 100).split(".")[0] + "%"
        i["accuracy"] = str(accuracy)
        return_data.append(i)
    #return return_data
    return HttpResponse(simplejson.dumps(return_data))

        
                
    #return HttpResponse(simplejson.dumps(ast.literal_eval(f[0].strip())))

#pprint(summary())

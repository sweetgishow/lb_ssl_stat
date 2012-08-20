#!/usr/bin/python

import OpenSSL
import socket
import datetime

class GetCertInfo():    #do an handshake with the ssl address and get it's cert info
    def __init__(self, address, port = 443):
        self.address = address
        self.port = port
        self.not_after = ""
        self.days_to_expire = ""
        self.bit = ""
#    def get_cert_info(self):
        context = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        connection = OpenSSL.SSL.Connection(context,s)
        connection.connect((self.address, self.port))
        connection.setblocking(1)
        connection.do_handshake()
        cert = connection.get_peer_certificate()
        not_after = datetime.datetime.strptime(cert.get_notAfter()[0:8], "%Y%m%d")
        self.days_to_expire = (not_after - not_after.now()).days
        self.bit = str(cert.get_pubkey().bits())
        #self.expiration_date = not_after.strftime("%Y-%m-%d")
        self.not_after = not_after.strftime("%Y-%m-%d")

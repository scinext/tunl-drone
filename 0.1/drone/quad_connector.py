'''
Created on Jul 4, 2012

@author: Peter Hendriks
'''

import time
import socket
from threading import Thread

class quad_server(Thread):
    '''
    usage:
    qs = quad_server(port)
    qs.start()
    qs.send(data)
    '''
    
    def __init__(self, port):
        self.host = '192.168.0.36'
        self.port = port
        self.connected = 0
        Thread.__init__(self)
    
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        self.conn, addr = self.socket.accept()
        self.connected = 1
        print "connection opend from: " + str(addr)
        
    def send(self, data):
        if (self.connected):
            self.conn.send(data)

class quad_client(Thread):
    '''
    usage:
    qc = quad_client(host, port)
    qc.start()
    last_msg = qc.read_data()
    '''
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.last_msg = ''
        Thread.__init__(self)
    
    def run(self):
        self.running = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        while self.running:
            new_msg = self.socket.recv(1024)
            if (len(new_msg) > 0):
                self.last_msg = new_msg
                ## print self.last_msg
            
    def read_data(self):
        return self.last_msg
    
    def stop(self):
        self.running = 0
#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             DTNCarrier.py
    Create Date:      Mon 21 Mar 2011 09:18:20 AM CET

'''
import DTN

import socket
import threading
import time

class Carrier(threading.Thread, DTN.DTNConnection):
    def __init__(self):
        threading.Thread.__init__(self)
        DTN.DTNConnection.__init__(self, self.empty_cb)
        
        self.udp_listen = self._broadcat_server(8888)
        self.conn = None

        self.killed = False

        self.cmd = DTN.DTNQueue()
        self.data = DTN.DTNQueue()

    def __del__(self):
        self.killed = True

    def empty_cb(self, msg):
        pass

    def _broadcat_server(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', port))
        return s

    def work(self):

        send_thread = threading.Thread(target=self._send_thread)
        send_thread.start()
        recv_thread = threading.Thread(target=self._recv_thread)
        recv_thread.start()

        #ips = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]

        while True:
            if self.conn is None:

                self._log("UDP listening")
                message, address = self.udp_listen.recvfrom(1024)
                print 'message (%s) from : %s' % ( str(message), address[0])
                # Get mode and port from message
                mode = 'server'
                port = 4440

                if mode == 'server':
                    self.send_queue = self.data
                    self.recv_queue = self.cmd
                else:
                    self.send_queue = self.cmd
                    self.recv_queue = self.data

                # Get port from message
                try:
                    self.conn = self._tcp_connect(address[0], port)
                except socket.error, e:
                    continue

            time.sleep(DTN.TIMEOUT)

    def run(self):
        self.work()

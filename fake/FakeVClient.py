__author__ = 'kylewu'

import socket
import sys
import threading
import time
import DTN

class VClient(DTN.DTN, threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        DTN.DTN.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = None

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

        
    def run(self):
        while True:
            if self.conn is None:
                self.conn = self._tcp_connect(self.ip, self.port)
            if self.conn is not None:
                self.conn.send("PING\n")
            time.sleep(1)
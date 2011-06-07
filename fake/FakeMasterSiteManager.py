from _socket import socket, socket
import DTN

__author__ = 'kylewu'

import time
import DTN
import threading

import DTNDatabase
TIMEOUT = 2

class MasterSiteManager(DTN.DTN, threading.Thread):

    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        DTN.DTN.__init__(self)

        self.db = DTNDatabase.DTNDatabase()

        self.ip = ip
        self.port = port
        self._log("listening on port " + str(self.port))
        self.listen = self._tcp_listen(self.ip, self.port)
        self.conn = None
        self.killed = False

    def stop(self):
        self.killed = True
        self.conn = None


    def run(self):
        recv_thread = threading.Thread(target=self._recv_thread)
        recv_thread.start()
        #send_thread = threading.Thread(target=self._send_thread)
        #send_thread.start()
        while True:
            if self.killed:
                self._log('run is killed')
                break
            if self.conn is None:
                self.conn, addr = self.listen.accept()
                if self.conn is None:
                    continue
            time.sleep(TIMEOUT)
            
    def _send_thread(self):
        while True:
            if self.killed:
                self._log('send is killed')
                break

            if self.conn is None:
                time.sleep(TIMEOUT)
                continue

            # time out or queue is empty, then sleep and wait for connection again
            #time.sleep(TIMEOUT)
            self._log('Sending PONG')
            self.conn.send('PONG\n')

    def _recv_thread(self):
        print 'in recv  thread'
        buf = ''
        while True:

            if self.killed:
                self._log('recv is killed')
                break
            if self.conn is None:
                #self._log('connection is none')
                continue
            self._log('waiting')
            # receive from the other part

            try:
                buf += self.conn.recv(1024)
                while buf.find('\n') >= 0:
                    msg, buf = buf.split('\n', 1)
                    # pass msg to DTM
                    self._log(msg)
                    self._log(msg.split()[0])
                    self.conn.send('ACK %s\n' % msg.split()[0])
            except socket.timeout:
                self._log("no incoming data")
            self._log('done')

            time.sleep(TIMEOUT)
            #self._log(self.conn)

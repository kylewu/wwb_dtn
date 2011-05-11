#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Wed Feb 16 11:13:04 2011'
__version__ = '0.4'

import sys
import select
import socket 
import threading
import signal

import DTN
from DTN import logger
from DTNDatabase import DTNDatabase
from DTNConnection import DTNCarrier
from DTNConnection import DTNConnection
import DTNMsgHandler

"""
    Class inheritance

             -------------------
             |  BaseDTNDevice  |         BCast and DTN Ports
             -------------------
             ^                 ^
             |                 |
        ------------    -------------
        | MobileSM |    | BaseDTNSM |   Monitor and Vclient Ports
        ------------    -------------
                        ^           ^
                        |           |
                 ------------    ------------
                 | ServerSM |    | ClientSM |
                 ------------    ------------

"""
class BaseDTNDevice(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)

        # important when broadcasting
        self.mode = ''

        # FIXME find a better Database name
        self.db = DTNDatabase(self.__class__.__name__)

        # IP
        self.my_ip = kwargs.get('ip', socket.gethostbyname(socket.gethostname()))

        self.dtn_port = kwargs.get('dtn_port', 5555)
        self.dtn_listen = None

        self.bcast_port = kwargs.get('bcast_port', 6666)
        self.bcast_listen = None

        # DTN connection list
        self.dtn = list()

        # stop flag
        self.stop_flag = False

        # FIXME check if I need this
        self.bufs = dict()

        # FIXME seems does not work
        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        self.stop()

    def run(self):

        # open listener
        self.open_listener()

        while not self.stop_flag:
            try:
                self.work()
            except :
                logger.error( sys.exc_info()[0])
                break

    # FIXME
    def stop(self):
        self.stop_flag = True
        self.close_all_sockets()
        if self.isAlive():
            self.join()

    # FIXME remove?
    def quit(self):
        self.stop()
        self.close_listener()
        for s in self.monitor_sockets:
            DTN._cleanup_socket(s)
        for s in self.vclient_sockets:
            DTN._cleanup_socket(s)

    def open_listener(self):
        """ Open Listeners  
            @rewrite if implementing subclass
        """
        self.dtn_listen = DTN._tcp_listen(self.my_ip, self.dtn_port)
        self.bcast_listen = DTN._broadcast_listen(self.bcast_port)

    def close_all_sockets(self):
        """ Close all sockets """
        readers = self.get_sockets(self.f_map)

        for s in readers:
            if s is not None:
                DTN._cleanup_socket(s)

    def get_handle_map(self):
        """ Return new (variable, function) list
            f_map is a list of tuples
            [(socket, func), (socket, func)]
            @rewrite if implementing subclass which handles more sockets
            """
        f_map = [
                (self.dtn_listen    ,self.handle_dtn_listen),
                (self.bcast_listen  ,self.handle_bcast_listen),
                ]

        return f_map

    def get_sockets(self, l):
        """ return all the sockets
        """
        readers = list()
        for s in l:
            if isinstance(s[0], socket.socket):
                readers += [s[0]]
            elif isinstance(s[0], list):
                readers += s[0]

        return readers

    def work(self):

        # update f_map and readers
        f_map = self.get_handle_map()
        readers = self.get_sockets(f_map)

        try:
            ready_to_read, ready_to_write, in_error = select.select(readers, [], [], 30)
        except socket.timeout:
            return
        except:
            logger.error('error')
            return

        for r in ready_to_read:
            for s in f_map:
                if isinstance(s[0], socket.socket):
                    if r == s[0]:
                        s[1](r)
                        break
                elif isinstance(s[0], list):
                    if r in s[0]:
                        s[1](r)
                        break

    def handle_dtn_listen(self, s):
        """docstring for handle_dtn_listen"""
        logger.debug('new DTN connection')
        conn, remote = s.accept()
        # TODO check the arguments
        # check if conn from this ip already in dtn list
        dtnconn = DTNConnection(conn, self, 'SERVER', cb=self.notify_monitors)
        self.dtn.append(dtnconn)
        dtnconn.start()

    def handle_bcast_listen(self, s):
        """docstring for handle_bcast_listen"""

        msg , addr = s.recvfrom(65535)

        if self.mode == 'CLIENT_SM' and self.client.conn is not None:
            return
    
        if msg == CARRIER_PING:

            logger.debug('recv broadcast %s from %s' % (msg, addr))

            s.sendto(CARRIER_PONG + '%s %s' % (self.dtn_port, self.mode), (addr[0], addr[1]))

    # TODO
    def connect_to_sm(self, ip, port):
        """ connect to specific IP:PORT
        """
        conn = None
        conn = DTN._tcp_connect(ip, port)

        if conn is not None:
            self.client= DTNConnection(conn, self, 'CLIENT')
            self.client.start()
            return True

        return False

class BaseDTNSiteManager(BaseDTNDevice):
    """ Compare to BaseDTNDevice
        BaseDTNSiteManager supports Monitors and Vclients
    """

    def __init__(self, **kwargs):
        BaseDTNDevice.__init__(self, **kwargs)

        self.monitor_port = kwargs.get('monitor_port', 7777)
        self.monitor_listen = None
        self.monitor_sockets = list()

        self.vclient_port = kwargs.get('vclient_port', 8888)
        self.vclient_listen = None
        self.vclient_sockets = list()

    def get_handle_map(self):
        """docstring for get_map"""
        f_map = BaseDTNDevice.get_handle_map(self)
        f_map += [
                (self.monitor_listen,self.handle_monitor_listen),
                (self.vclient_listen,self.handle_vclient_listen),
                (self.monitor_sockets , self.handle_monitor_sockets),
                (self.vclient_sockets , self.handle_vclient_sockets),
            ]

        return f_map

    def open_listener(self):
        BaseDTNDevice.open_listener(self)
        self.monitor_listen = DTN._tcp_listen(self.my_ip, self.monitor_port)
        self.vclient_listen = DTN._udp_open(self.my_ip, self.vclient_port)

    def handle_vclient_sockets(self, r):
        """docstring for handle_vclient_sockets"""
        chunk = r.recv(1024)
        print self.name + ': receive data from vclient ->' + chunk
        if chunk == '':
            print self.name + ": Vclient disconnected", r
            self.vclient_sockets.remove(r)
            DTN._cleanup_socket(r)

        else:
            self.bufs[r] += chunk

            while self.bufs[r].find('\n') >= 0:
                msg, self.bufs[r] = self.bufs[r].split('\n', 1)
                self.db.insert(msg)

    def handle_monitor_listen(self, s):
        """docstring for handle_monitor_listen"""
        con, remote = s.accept()
        print "Monitor connected \n", remote
        self.bufs[con] = ''
        self.monitor_sockets.append(con)

    def handle_monitor_sockets(self, s):
        """docstring for handle_monitor_sockets"""
        pass

    def handle_vclient_listen(self, s):
        chunk = s.recv(1024)
        if chunk == '':
            print "UDP error", s
            sys.exit(1)
        else:
            logger.debug(chunk)
            msg = DTNMsgHandler.handle(chunk)
            if msg is not None:
                # Notify Monitors
                self.notify_monitors(chunk)
                # Save into database
                self.db.insert_tuple(msg[1:])
    
    def notify_monitors(self, msg):
        """ Notify Monitors when receiving a message """
        for m in self.monitor_sockets:
            logger.debug('sending to monitor %s'% msg)
            try:
                m.send(msg + '\n')
            except socket.error:
                print "Error sending to ", m
                self.monitor_sockets.remove(m)

class ServerSiteManager(BaseDTNSiteManager):
    def __init__(self, **kwargs):
        BaseDTNSiteManager.__init__(self, **kwargs)
        # MODE
        self.mode = 'SERVER'


class ClientSiteManager(BaseDTNSiteManager):
    def __init__(self, **kwargs):
        BaseDTNSiteManager.__init__(self, **kwargs)

        self.mode = 'CLIENT'
        # Server Info
        self.server_ip = kwargs.get('server_ip', '')
        self.server_port = kwargs.get('server_port', 0)

class MobileSiteManager(BaseDTNDevice):
    def __init__(self):
        self.db = DTNDatabase(self.__class__.__name__)
        #self.dtn = DTNConnection(bbbbbbbbbbb)

CARRIER_PING = "I'M CARRIER"
CARRIER_PONG = "DTN PORT "
class SiteManagerCarrier():

    def __init__(self):

        self.server_ip = ''
        self.server_port = 0

        self.db = DTNDatabase(self.name)

        self.carrier = DTNCarrier(self)

        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        self.stop()

    def bcast(self, bcast_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(CARRIER_PING, ('<broadcast>', bcast_port))

        s.settimeout(2)

        try:
            (buf, addr) = s.recvfrom(2048)
            print "Received from %s: %s" % (addr, buf)
            l = buf.split()
            if len(l) == 4:
                self.server_port = int(l[2])
                self.server_ip = addr[0]
                if l[3] == 'SERVER':
                    self.mode = 'client'
                elif l[3] == 'CLIENT':
                    self.mode = 'server'
                else:
                    s.close()
                    return False

                s.close()
                return True

        except:
            print 'no feedback'
            s.close()

        return False

    def connect_to_server(self):
        # try to connect to server
        conn = None
        conn = DTN._tcp_connect(self.server_ip, self.server_port)

        if conn is not None:
            if self.carrier is not None:
                self.carrier = None
            self.carrier = DTNCarrier(self)
            self.carrier.conn = conn
            self.carrier.mode = self.mode
            return True
        
        return False

    def start(self):
        self.carrier.start()

    def stop(self):
        self.carrier.stop()

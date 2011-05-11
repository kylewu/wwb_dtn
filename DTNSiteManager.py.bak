#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             SiteManager.py
    Create Date:      Wed Feb 16 11:13:04 2011

'''
import sys
import select
import socket 
import threading
import signal

import DTN
from DTN import logger
from DTNDatabase import DTNDatabase
#from DTNConnection import DTNClient
#from DTNConnection import DTNServer
from DTNConnection import DTNCarrier


CARRIER_PING = "I'M CARRIER"
CARRIER_PONG = "DTN PORT "

class SiteManager(threading.Thread):

    def __init__(self, ip):
        threading.Thread.__init__(self)
        
        if ip is None:
            self.my_ip = socket.gethostbyname(socket.gethostname())
        else:
            self.my_ip = ip

        # Database
        self.db = DTNDatabase(self.name)

        # Dst
        self.dst_ip = ""
        self.dst_id = ""

        # MODE
        self.mode = ""

        self.bufs = dict()
        self.started = False

    def open_listener(self):
        pass

    def close_listener(self):
        pass

    def work(self):
        pass

    def run(self):
        self.started = True
        while not self.killed:
            try:
                self.work()
            except:
                logger.error('error')
                break

class SiteManagerServer(SiteManager):
    """ Site Manager Server
        communicates with Monitors and has a list of DTNServer
    """

    def __init__(self, monitor_port, dtn_port, bcast_port, ip = None):
        SiteManager.__init__(self, ip)

        # ports
        self.monitor_port = monitor_port
        self.dtn_port = dtn_port
        self.bcast_port = bcast_port

        # Sockets Variables
        self.monitor_listen = None
        self.dtn_listen = None
        self.bcast_listen = None

        # monitors sockets
        self.monitor_sockets = list()
        # dtn connection list
        self.dtn = list()

        # cond
        self.killed = False

        # signal
        signal.signal(signal.SIGINT, self.sighandler)
        
        # open listener
        self.open_listener()

    def sighandler(self, signum, frame):
        self.stop()

    def stop(self):
        self.killed = True
        for s in self.dtn:
            s.stop()

        for d in self.dtn:
            d.join()

        if self.started:
            self.started = False
            self.join()

    def quit(self):
        self.stop()
        self.close_listener()
        for s in self.monitor_sockets:
            DTN._cleanup_socket(s)

    def open_listener(self):
        self.monitor_listen = DTN._tcp_listen(self.my_ip, self.monitor_port)
        self.dtn_listen = DTN._tcp_listen(self.my_ip, self.dtn_port)
        self.bcast_listen = DTN._broadcast_listen(self.bcast_port)

    def close_listener(self):
        for s in [self.monitor_listen, self.dtn_listen, self.bcast_listen]:
            if s is not None:
                DTN._cleanup_socket(s)

    def notify_monitors(self, msg):
        for m in self.monitor_sockets:
            logger.debug('sending to monitor %s'% msg)
            try:
                m.send(msg + '\n')
            except socket.error:
                print "Error sending to ", m
                self.monitor_sockets.remove(m)

    #def __del__(self):
        #self.close_listener()
        #for s in self.monitor_sockets:
            #DTN._cleanup_socket(s)

    def work(self):
        readers = self.monitor_sockets + [self.monitor_listen, self.dtn_listen, self.bcast_listen]

        try:
            ready_to_read, ready_to_write, in_error = select.select(readers, [], [], 2)
        except:
            return

        for r in ready_to_read:

            if self.killed:
                break

            if r == self.dtn_listen:
                logger.debug('new DTN connection')
                conn, remote = r.accept()

                server = DTNServer(conn, self)
                self.dtn.append(server)
                server.start()
                continue

            if r == self.monitor_listen:
                con, remote = r.accept()
                print "Monitor connected \n", remote
                self.bufs[con] = ''
                self.monitor_sockets.append(con)
                continue
            
            if r == self.bcast_listen:
                msg , addr = r.recvfrom(65535)

                if msg == CARRIER_PING:

                    logger.debug('recv broadcast %s from %s' % (msg, addr))

                    r.sendto(CARRIER_PONG + '%s SERVER' % self.dtn_port, (addr[0], addr[1]))
                continue

class SiteManagerClient(SiteManager):
    """ Site Manager Client
        gets data from VClients and send through DTConnection
    """

    def __init__(self, vclient_log_port, vclient_udp_port, dtn_port, bcast_port, server_ip, server_port, ip = None):
        
        SiteManager.__init__(self, ip)

        # socket variables
        self.vclient_udp_listen = None
        self.vclient_log_listen = None
        #self.vclient_cmd_listen = None
        self.dtn_listen         = None
        self.bcast_listen       = None

        # ports
        self.vclient_udp_port   = vclient_udp_port
        self.vclient_log_port   = vclient_log_port
        #self.vclient_cmd_port   = vclient_cmd_port
        self.dtn_port           = dtn_port
        self.bcast_port         = bcast_port

        # server info
        self.server_ip          = server_ip
        self.server_port        = server_port

        # vclient sockets
        self.vclient_sockets = list()
        #self.vclient_cmd_sockets = list()

        self.bufs[self.vclient_udp_listen] = ''
        
        # start DTN client
        self.client= DTNClient(self)

        # cond
        self.killed = False

        # signal
        signal.signal(signal.SIGINT, self.sighandler)
        
        # Open listeners
        self.open_listener()

    def sighandler(self, signum, frame):
        self.stop()

    def stop(self):
        self.client.stop()
        self.killed = True

        if self.started:
            self.started = False
            #self.client.join()
            self.join()
        print '~~~~~~~~~~~~~~~~~~``'

    def clean(self):
        self.close_listener()
        for s in self.vclient_sockets:
            DTN._cleanup_socket(s)
        print '*******************'

    #def __del__(self):

        #self.close_listener()
        #for s in self.vclient_sockets:
            #DTN._cleanup_socket(s)
        #for s in self.vclient_cmd_sockets:
            #DTN._cleanup_socket(s)
            
        #self.client.stop()
        #self.client.__del__()
        
    def open_listener(self):

        self.vclient_udp_listen = DTN._udp_open(self.my_ip, self.vclient_udp_port)
        self.vclient_log_listen = DTN._tcp_listen(self.my_ip, self.vclient_log_port)
        #self.vclient_cmd_listen = DTN._tcp_listen(self.my_ip, self.vclient_cmd_port)
        self.dtn_listen = DTN._tcp_listen(self.my_ip, self.dtn_port)
        self.bcast_listen = DTN._broadcast_listen(self.bcast_port)

        print 'vclient log : %d, udp : %d, dtn : %d, broadcast : %d server_ip : %s, server_port : %d, ip : %s' \
                % (self.vclient_log_port, self.vclient_udp_port, self.dtn_port, self.bcast_port, \
                   self.server_ip, self.server_port, self.my_ip)

    def close_listener(self):
        for s in [self.vclient_udp_listen, self.vclient_log_listen, self.dtn_listen, self.bcast_listen]:
            if s is not None:
                DTN._cleanup_socket(s)

    def distribute_cmd(self, msg):
        pass

    def connect_to_server(self):
        # try to connect to server
        conn = None
        print 'connecting'
        conn = DTN._tcp_connect(self.server_ip, self.server_port)

        if conn is not None:
            self.client= DTNClient(self)
            self.client.conn = conn
            self.client.start()
            return True

        return False

    def work(self):

        # FIXME do this in a thread
        if self.client.conn is None:
            self.connect_to_server()

        readers = self.vclient_sockets + [self.vclient_log_listen] + [self.dtn_listen] + [self.vclient_udp_listen] + [self.bcast_listen]
        
        try:
            ready_to_read, ready_to_write, in_error = select.select(readers, [], [], 2)
        except:
            return

        for r in ready_to_read:
            if self.killed:
                break

            # new vclient udp connection
            if r == self.vclient_udp_listen:
                
                chunk = r.recv(1024)
                if chunk == '':
                    print "UDP error", r
                    sys.exit(1)

                else:
                    self.db.insert(chunk)
                    
                continue

            if r in self.vclient_sockets:

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

                continue

            # new vclient log
            if r == self.vclient_log_listen:
                conn, remote = r.accept()
                print "DT: Vclient connected \n", remote
                self.bufs[conn] = ''
                self.vclient_sockets.append(conn)

                continue

            # new vclient cmd
            #if r == self.vclient_cmd_listen:
                ## TODO To get this feature, I need to change VClient Source Code
                #conn, remote = r.accept()
                #print "DT: Vclient cmd socket established \n"

                #chunk = r.recv(1024)
                #self.bufs[r] += chunk
                #while self.bufs[r].find('\n') >= 0:
                    #msg, self.bufs[r] = self.bufs[r].split('\n', 1)
                    ## TODO Get sensor information from msg, or distribute cmd to all sensors
                #self.vclient_cmd_sockets.append(("sensor_id", conn))

            if r == self.dtn_listen:
                print self.name + ': new DTN connection'
                conn, remote = r.accept()
                if self.client.killed:
                    self.client.join()
                elif self.client.conn is not None:
                    continue
                self.client= DTNClient(self)
                self.client.conn = conn
                self.client.start()

            if r == self.bcast_listen:
                msg , addr = r.recvfrom(65535)

                if self.client.conn is not None:
                    continue

                if msg == CARRIER_PING:

                    logger.debug('recv broadcast %s from %s' % (msg, addr))

                    r.sendto(CARRIER_PONG + '%s CLIENT' % self.dtn_port, (addr[0], addr[1]))


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

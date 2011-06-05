#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__date__    = 'Wed Feb 16 11:13:04 2011'
__version__ = '0.5'

import sys
import select
import socket 
import threading
import signal

import DTN
from DTN import logger
from DTNDatabase import DTNDatabase
from DTNConnection import DTNConnection
from DTNMessage import DTNMessage

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

MOBILE_SH_INFO = 'MOBILE'
SERVER_SH_INFO = 'SERVER'

EXIST_ERR = 'Already Exist'
SUCCESS_INFO = 'Success'

BCAST_MSG = 'FINDING'

class BaseDTNDevice(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)

        # FIXME find a better Database name
        self.db_name = kwargs.get('db_name', self.__class__.__name__)
        self.db = DTNDatabase(self.db_name)

        # IP
        self.my_ip = kwargs.get('ip', '127.0.0.1')#socket.gethostbyname(socket.gethostname()))

        self.dtn_port = kwargs.get('dtn_port', 5555)
        self.dtn_listen = None

        self.bcast_port = kwargs.get('bcast_port', 6666)
        self.bcast_listen = None

        # Sensor Host Information
        # = server if it is Server Site Manager
        # = mobile if it is Mobile Site Manager
        self.sh = kwargs.get('sh', '')

        # Target
        # * means all
        # or a list of SH
        # Normally, server needs *
        #           client needs data of its own sh
        self.target = kwargs.get('target', '*')

        # DTN connection dict
        # (SH, DTNConn)
        self.dtn = dict()
        # Dict which stores (SH, LastHash)
        self.last_hash = dict()

        # The last message received 
        # (SH, HASH)
        self.last_hash = dict()

        # flags
        self.stop_flag = False
        self.server_connected = False

        # FIXME check if I need this
        self.bufs = dict()

        # FIXME seems does not work
        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        self.stop()

    def sub_init(self):
        pass

    def run(self):

        self.sub_init()
        self.stop_flag = False

        # open listener
        self.open_listener()

        while not self.stop_flag:
            try:
                self.work()
            except :
                logger.error(sys.exc_info()[0])
                break

    # TODO 
    def stop(self):
        self.stop_flag = True
        for sh in self.dtn:
            if self.dtn[sh] is not None:
                self.dtn[sh].stop()
                self.dtn[sh] = None
        self.close_all_sockets()

    def open_listener(self):
        """ Open Listeners  
            @rewrite if implementing subclass
        """
        self.dtn_listen = DTN._tcp_listen(self.my_ip, self.dtn_port)
        self.bcast_listen = DTN._broadcast_listen(self.bcast_port)

    def close_all_sockets(self):
        """ Close all sockets """
        readers = self.get_sockets(self.get_handle_map())

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
            ready_to_read, ready_to_write, in_error = select.select(readers, [], [], 3)
        except socket.timeout:
            return
        except:
            logger.error('work error')
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


    def handle_bcast_listen(self, s):
        """docstring for handle_bcast_listen"""
        logger.debug('Recv bcast')

        msg, addr = s.recvfrom(65535)

        # send back DTN Port
        s.sendto('%d' % self.dtn_port, addr)

    def bcast(self, bcast_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(BCAST_MSG, ('<broadcast>', bcast_port))
        logger.debug('send broadcast')

        s.settimeout(2)

        try:
            buf, addr = s.recvfrom(2048)
            logger.info('Received from %s: %s' % (addr, buf))
            s.close()
            return addr[0], int(buf)

        except socket.timeout:
            logger.debug('no feedback')
        except :
            logger.debug('bcast socket error')

        s.close()
        return None

    def handle_dtn_listen(self, s):

        logger.info('DTN connection request')
        conn_recv, remote = s.accept()

        data = conn_recv.recv(1024)
        port = int(data.split()[0])
        sh = data.split()[1]
        tar = ' '.join(data.split()[2:])
        logger.debug('Port: %d, SH: %s, Target: %s' % (port, sh, tar))

        if self.dtn.has_key(sh):
            logger.debug(self.dtn[sh])
        if self.dtn.has_key(sh) and self.dtn[sh] is not None:
            conn_recv.send(EXIST_ERR)
            logger.debug('DTN connection already exists between these two Site Managers')
            return
        else:
            conn_recv.send(SUCCESS_INFO)

        # remote[0] is IP
        # remote[1] is PORT
        conn_send = DTN._tcp_connect(remote[0], port)

        if conn_send is not None:
            # send my SH info
            conn_send.send('%s %s' % (self.sh, self.target))

            data = conn_send.recv(1024) 
            if data == EXIST_ERR:
                logger.debug('DTN connection already exists between these two Site Managers')
                return 
            else:
                logger.debug('Good')

            # Ready

            dtn_conn = DTNConnection(conn_send, conn_recv, self.sh, sh, tar, self)
            self.dtn[sh] = dtn_conn
            if not self.last_hash.has_key(sh):
                self.last_hash[sh] = ''
            if sh == SERVER_SH_INFO:
                self.server_connected = True
            logger.info('New DTN connection established')
            dtn_conn.start()

    def connect_to_sm(self, ip, port):
        """ connect to specific IP:PORT
        """
        logger.debug('Try to connect to Site Manager and establish DTN connection')
        # Generate a random port for listening
        random_n = 1
        while True:
            try:
                listener = DTN._tcp_listen(self.my_ip, self.dtn_port+random_n)
            except:
                random_n += 1
                continue

            break
        conn_send = DTN._tcp_connect(ip, port)

        if conn_send is not None:

            # send port information
            conn_send.send('%d %s %s\n' % (self.dtn_port + random_n, self.sh, self.target))

            data = conn_send.recv(1024) 
            if data == EXIST_ERR:
                logger.debug('DTN connection already exists between these two Site Managers')
                return False
            else:
                logger.debug('Successed in sending port, sh and target info')

            # wait for connection
            listener.settimeout(5)
            try:
                conn_recv, remote = listener.accept()
            except socket.timeout:
                logger.debug('timeout')
                return False

            # Get SH info
            data = conn_recv.recv(1024)
            sh = data.split()[0]
            tar = ' '.join(data.split()[1:])
            logger.debug('SH: %s, Target: %s' % (sh, tar))
            
            # Check again
            if self.dtn.has_key(sh) and self.dtn[sh] is not None:
                conn_recv.send(EXIST_ERR)
                logger.debug('DTN connection already exists between these two Site Managers')
                return
            else:
                conn_recv.send(SUCCESS_INFO)

            # Ready
            dtn_conn = DTNConnection(conn_send, conn_recv, self.sh, sh, tar, self)
            self.dtn[sh] = dtn_conn
            if not self.last_hash.has_key(sh):
                self.last_hash[sh] = ''
            if sh == SERVER_SH_INFO:
                self.server_connected = True
            logger.info('New DTN connection established')
            dtn_conn.start()

            DTN._cleanup_socket(listener)
            return True

        DTN._cleanup_socket(listener)

        return False

    def stop_sh(self, sh):
        if self.dtn[sh].has_key(sh):
            self.dtn[sh].stop()
        else:
            logger.warning("no connection to %s" % sh)

    def list_connected_sh(self):
        return self.dtn.keys()

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

        # Server Info
        self.server_ip = kwargs.get('server_ip', 'SERVER')
        self.server_port = kwargs.get('server_port', 0)

        self.auto_connect = kwargs.get('auto_connect', False)
        self.server_connected = False

        self.conn_thread = threading.Thread(target=self._conn_thread)

    def sub_init(self):
        if self.auto_connect:
            self.conn_thread.start()

    def _conn_thread(self):
        if self.server_port is None:
            return
        while True:
            import time
            time.sleep(30)

            if self.server_connected:
                continue

            logger.debug('Client try to connect to server')
            if self.connect_to_sm(self.server_ip, self.server_port):
                self.server_connected = True

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

    # FIXME this function is not useful, but I would like keep it
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
            logger.debug('recv from vclient ' + chunk)
            msg = DTNMessage()
            msg.handle(chunk)
            msg.src = self.sh
            if msg.type == 'PING':
                # Notify Monitors
                self.notify_monitors(chunk)
                # Save into database
                self.db.insert_msg(msg)
    
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
        self.sh = SERVER_SH_INFO
        self.auto_connect = False

class ClientSiteManager(BaseDTNSiteManager):
    def __init__(self, **kwargs):
        BaseDTNSiteManager.__init__(self, **kwargs)

        import time
        self.sh = kwargs.get('sh', 'CLIENT %d'%int(time.time()))


class MobileSiteManager(BaseDTNDevice):
    def __init__(self, **kwargs):
        BaseDTNDevice.__init__(self, **kwargs)
        self.sh = kwargs.get('sh', MOBILE_SH_INFO)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Fri 11 Mar 2011 02:01:11 PM CET'
__version__ = '0.3'

import socket
import time
import threading

from DTN import logger
#from DTNMsgHandler import handle
from DTNMessage import DTNMessage

TIMEOUT = 5

class DTNConnection(threading.Thread):

    def __init__(self, conn_send, conn_recv, target, sm, cb=None):
        threading.Thread.__init__(self)

        #self.mode = mode
        self.conn_send = conn_send
        self.conn_recv = conn_recv

        self.sm = sm
        self.cb = cb

        self.target = target
        self.target_other = ''

        # Flags
        self.stop_flag = False
        self.keep_alive = False

        self.buf = ''
        
    def stop(self):
        self.stop_flag = True

        # Wait until all threads stop
        self.send_thread.join()
        self.recv_thread.join()
        self.daemon_thread.join()

        if self.conn_send is not None:
            self._cleanup_socket(self.conn_send)
        if self.conn_recv is not None:
            self._cleanup_socket(self.conn_recv)

        #remove from SM DTN list

    def _get_all(self):
        """
            NOT UPDATED
            MODE                                FUNC
            SERVER, MOBILE_SERVER           Look up all data to DST ID
            CLIENT, MOBILE_CLIENT           Look up all data to DST IP (server)

            create table data (id integer primary key, hash text, sent integer, ack integer, time text, src_ip text,
            src_port text, dst text, type text, node text, data text);
        """
        if self.dst == '*':
            return self.sm.db.select_all(where='sent=0')
        else:
            ids = self.dst.split()
            res = list()
            for id in ids:
                res += self.sm.db.select_all(where='sent=0 and dst={0}'.format(id))
            return res

    def _update_sent(self, id):
        return self.sm.db.update('sent=1', 'hash={0}'.format(id) )

    def _send(self, msg):

        data = msg.to_msg()
        try:
            self.conn_send.send(data)
            logger.debug("send %s" % data)
            res = self.conn_send_recv(1024)
            if res == 'ACK %s\n'%msg.hash:
                # update last hash
                self.sm.last_hash[self.sh] = msg.hash
                #FIXME
                self._update_sent(msg[0])
                return True
            elif res == 'ERROR':
                return False
        except socket.error:
            logger.warn("send_thread connection lost")
            return False
        return True

    def _send_thread(self):

        while True:
            if self.stop_flag:
                logger.debug('send_thread is killed')
                break

            # TODO
            if self.conn_send is None:
                logger.warn('No Connection')
                break

            # msg is instance of DTNMessage
            msgs = self._get_all()
            for msg in msgs:
                self._send(msg)

            if not self.keep_alive:
                break
            #logger.debug('message empty, waiting for more messages')
            time.sleep(TIMEOUT)

        logger.debug('send_thread exist')

    # TODO
    def _recv_handle(self, msg):
        dtn_msg = DTNMessage(msg)

        self.sm.db.insert(dtn_msg.to_tuple())

        if dtn_msg.re_type == 'PING_RECV':
            logger.debug('recv PING')
            logger.debug('Send ACK')
            self._send('ACK %s' % dtn_msg.hash)

        elif type.startswith('CMD_RECV'):
            logger.debug('recv CMD')
            logger.debug('Send ACK')
            self._send('ACK %s' % dtn_msg.hash)


            if self.mode == 'DTN_CLIENT':
                cmd = ' '.join(type.split()[1:])
                logger.debug('recv CMD : %s', cmd)
                import commands
                res = commands.getstatusoutput(cmd)
                logger.debug(res)

        elif dtn_msg.re_type == 'ACK':
            logger.debug('recv ACK')
        return True

    def _recv_thread(self):

        while True:
            if self.stop_flag:
                logger.debug('recv_thread is killed')
                break
                
            #TODO if one conn is lost, what should I do
            if self.conn_recv is None:
                logger.warn('No Connection')
                break

            is_finish = False
            try:
                self.buf += self.conn_recv.recv(65535)

                while self.buf.find('\n') >= 0:
                    msg, self.buf = self.buf.split('\n', 1)
                    logger.debug('recv ' + msg)
                    res = self._recv_handle(msg)
                    if self.cb is not None:
                        self.cb(msg)
                    if res == 'finish':
                        is_finish = True

            except socket.timeout:
                logger.debug("no incoming data")
            except socket.error:
                logger.warn("recv_thread connection lost")
                self.stop()
                break

            if is_finish:
                break

            #time.sleep(TIMEOUT)

        logger.debug('recv_thread exist')

    def _daemon_thread(self):
        while True:
            if not self.send_thread.isAlive() and not self.recv_thread.isAlive():
                if self.stop_flag:
                    logger.info('stop by user')
                else:
                    logger.info('asyn done')
                break
            time.sleep(5)

    def run(self):
        self.send_thread = threading.Thread(target=self._send_thread)
        self.recv_thread = threading.Thread(target=self._recv_thread)
        self.daemon_thread = threading.Thread(target=self._daemon_thread)

        self.send_thread.start()
        self.recv_thread.start()
        self.daemon_thread.start()


#class DTNServer(DTNConnection):
    #"""
        #DTNServer locates in the server part of DTN
        #It will not reconnect if the connection is lost
    #"""
    
    #def __init__(self, conn, sm):
        #DTNConnection.__init__(self)
        
        #self.conn = conn
        #self.sm = sm
        #self.mode = 'DTNSERVER'

    #def _cb(self, msg):
        #self.sm.notify_monitors(msg)

#class DTNClient(DTNConnection):
    #""" delay tolerate connection
        #connection maybe not available
        #all the messages are kept in a queue before sending
    #"""
    #def __init__(self, sm): 
        #DTNConnection.__init__(self)
        #self.sm = sm
        #self.mode = 'DTNCLIENT'

#class DTNCarrier(DTNConnection):
    #def __init__(self, sm):

        #DTNConnection.__init__(self)
        #self.sm = sm
        #self.mode = ''
        
    #def _get_all(self):
        #logger.debug('Get data from db')
        #if self.mode == 'client':
            #return self.sm.db.select_type('PING')
        #elif self.mode == 'server':
            #return self.sm.db.select_type('CMD')
        #else:
            #logger.error('Mode is not set')
            #return

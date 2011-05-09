#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             DTNConnection.py
    Create Date:      Fri 11 Mar 2011 02:01:11 PM CET

'''
import socket
import time
import threading

from DTN import logger
from DTNMsgHandler import handle

TIMEOUT = 5

class DTNConnection(threading.Thread):

    def __init__(self, conn, sm, mode, cb=None):
        threading.Thread.__init__(self)

        #self.mode = mode
        self.conn = conn
        self.sm = sm
        self.cb = cb

        self.dst = ''
        self.keep_alive = False

        # Exit flag
        self.stop_flag = False

        self.buf = ''
        
    def stop(self):
        self.stop_flag = True

        # Wait until all threads stop
        self.send_thread.join()
        self.recv_thread.join()
        self.daemon_thread.join()

        if self.conn is not None:
            self._cleanup_socket(self.conn)

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

        #if self.mode in ['SERVER', 'MOBILE_SERVER']:
            #if self.buf == '*':
                #return self.sm.db.select_all(where='sent=0 and dst_id={0}'.format(self.dst_id))
            #return self.sm.db.select_all(where='sent=0 and dst_id={0}'.format(self.dst_id))
        #if self.mode in ['CLIENT', 'MOBILE_CLIENT']:
            #return self.sm.db.select_all(where='sent=0 and dst_ip={0}'.format(self.dst_ip))

    def _update_sent(self, id):
        return self.sm.db.update('sent=1', 'hash={0}'.format(id) )

    def _recv_handle(self, msg):
        type, t = handle(msg)

        type = self.sm.db.insert(msg)
        if type == 'PING_RECV':
            logger.debug('recv PING')
            logger.debug('Send ACK')
            self._send('ACK %s' % msg.split()[0])
        elif type.startswith('CMD_RECV'):
            logger.debug('recv CMD')
            logger.debug('Send ACK')
            self._send('ACK %s' % msg.split()[0])
            if self.mode == 'DTN_CLIENT':
                cmd = ' '.join(type.split()[1:])
                logger.debug('recv CMD : %s', cmd)
                import commands
                res = commands.getstatusoutput(cmd)
                logger.debug(res)
        elif type == 'ACK':
            logger.debug('recv ACK')
        return True

    def _send(self, msgs):

        for msg in msgs:
            logger.debug('sending data') 
            data = ' '.join(msg)
            try:
                self.conn.send(data + '\n')
                logger.debug("send %s" % data)
                self._update_sent(msg[0])
            except socket.error:
                logger.warn("send_thread connection lost")
                return False
        return True

    def _send_thread(self):

        while True:
            if self.stop_flag:
                logger.debug('send_thread is killed')
                break

            if self.conn is None:
                logger.warn('No Connection')
                break

            is_succ = True
            # Get all messages
            msgs = self._get_all()
            while len(msgs) > 0:
                if not self._send(msgs[:10]):
                    is_succ = False
                    break
                msgs = msgs[10:]

            if not is_succ:
                logger.debug('connection lost')
                self.stop()
                break

            if not self.keep_alive:
                break

            #logger.debug('message empty, waiting for more messages')
            time.sleep(TIMEOUT)

        logger.debug('send_thread exist')

    def _recv_thread(self):

        while True:
            if self.stop_flag:
                logger.debug('recv_thread is killed')
                break
                
            if self.conn is None:
                logger.warn('No Connection')
                break

            is_finish = False
            try:
                self.buf += self.conn.recv(65535)

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

class DTNCarrier(DTNConnection):
    def __init__(self, sm):

        DTNConnection.__init__(self)
        self.sm = sm
        self.mode = ''
        
    def _get_all(self):
        logger.debug('Get data from db')
        if self.mode == 'client':
            return self.sm.db.select_type('PING')
        elif self.mode == 'server':
            return self.sm.db.select_type('CMD')
        else:
            logger.error('Mode is not set')
            return

#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Fri 11 Mar 2011 02:01:11 PM CET'
__version__ = '0.6'

import socket
import time
import threading

import DTN
from DTN import logger
from DTNMessage import DTNMessage

TIMEOUT = 5

SEND_DONE = 'FINISH'
UNKNOWN_MSG = 'UNKOWN'

class DTNConnection(threading.Thread):

    def __init__(self, conn_send, conn_recv, my_sh, sh, target, sm, cb=None, server_conn=False):
        threading.Thread.__init__(self)

        #self.mode = mode
        self.conn_send = conn_send
        self.conn_recv = conn_recv
        self.conn_recv.settimeout(4)

        self.sm = sm

        self.my_sh = my_sh
        self.sh = sh
        logger.debug('my_sh %s, sh %s' %(my_sh, sh))

        # FIXME need? Callback function
        self.cb = cb
        
        # Target the other Site Manager needs
        # * or list of ids
        self.target = target

        self.server_conn = server_conn

        self.msgs = list()

        # Flags
        self.stop_flag = False
        self.keep_alive = False
        self.send_done = False
        self.recv_done = False

        self.buf = ''
        

    def stop(self):
        self.stop_flag = True

        # Wait until all threads stop
        self.send_thread.join()
        self.recv_thread.join()
        self.daemon_thread.join()

        self.clean()

    def clean(self):
        if self.conn_send is not None:
            DTN._cleanup_socket(self.conn_send)
        if self.conn_recv is not None:
            DTN._cleanup_socket(self.conn_recv)

        # Set DTNConnection of this SH in Site Manager to None
        self.sm.dtn[self.sh] = None
        if self.server_conn:
            self.sm.server_connected = False

    def _get_last_key(self, hash):
        msgs = self.sm.db.select_msg("hash='%s'" % hash)
        if len(msgs) == 1:
            logger.debug('Last ID : %d' % msgs[0].id)
            return msgs[0].id
        return -1

    def _get_all(self):
        base_where = "dst!='%s' and src!='%s' and ack!=1 and %d<=time+ttl" % (self.my_sh, self.sh,
                int(time.time()*1000))

        # Start from last point
        if self.sm.last_hash[self.sh] != '':
            last_key = self._get_last_key(self.sm.last_hash[self.sh])
            if last_key != -1:
                base_where += ' and id>%s' % last_key

        if self.target == '*':
            return self.sm.db.select_msg(base_where)
        else:
            ids = self.target.split()
            res = list()
            for id in ids:
                res += self.sm.db.select_msg("%s and dst == '%s'" % (base_where, id))
            return res

    def _send(self, conn, data):
        conn.send(data + '\n')
 
    def _send_msg(self, msg, n=0):
        """ Send DTNMessage 
            If error occurs, message will be resent 3 times max
        """

        if n > 2:
            return False

        try:
            data = msg.to_msg()
            self._send(self.conn_send, data)

            logger.debug("send %s : %s" % (msg.type, data))

            # Waiting ACK
            res = self.conn_send.recv(1024)
            #logger.debug('waiting ack and recv ' + res)
            if res == 'ACK %s\n' % msg.hash:
                logger.debug('recv ACK')
                # update last hash
                self.sm.last_hash[self.sh] = msg.hash

                #reach destination, set ack=1
                #if msg.dst == self.sh:
                    #self.sm.db.update('ack=1', "hash='%s'"%msg.hash)

                return True
            elif res == UNKNOWN_MSG:
                return True
            else:
                logger.debug('not ACK, try to send again')
                # Error, try to send again
                time.sleep(TIMEOUT)
                return self._send_msg(msg, n+1)

        except socket.timeout:
            logger.debug('timeout, no ACK, try to send again')
            return self._send_msg(msg, n+1)

        except socket.error:
            self.stop_flag = True
            self.send_done = True
            logger.warn("send_thread connection lost")
            return False
        return True

    def _send_thread(self):

        # Get Messages from DB
        self.msgs.extend(self._get_all())
        logger.info('Total %d messages to send' % len(self.msgs))

        while True:
            if self.stop_flag: 
                self.send_done = True
                break

            while len(self.msgs) > 0:
                msg = self.msgs.pop(0)
                if not self._send_msg(msg):
                    # ERROR, exit thread
                    self.stop_flag = True
                    break

            time.sleep(TIMEOUT)

            if (not self.send_done) and len(self.msgs) == 0:
                # Send SEND_DONE when all messages are sent
                # Thread does not die until recv thread receives SEND_DONE
                logger.debug('SEND_DONE')
                self._send(self.conn_send, SEND_DONE) 
                self.send_done = True


        logger.debug('send_thread exist')

    def _recv_handle(self, msg):
        dtn_msg = DTNMessage()
        if not dtn_msg.handle(msg):
            logger.debug('cannot recognize message ' + msg)
            self._send(self.conn_recv, UNKNOWN_MSG)
            return 

        if dtn_msg.type == 'DST_ACK':
            self.sm.db.insert_dst_ack(dtn_msg)
            # set the match data ack=1
            self.sm.db.update('ack=1', "hash='%s'"%dtn_msg.data)
        else:
            self.sm.db.insert_msg(dtn_msg)

        logger.debug('recv %s : %s' % (dtn_msg.type, msg))

        # Any messages but ACK should send ACK
        if dtn_msg.type != 'ACK':
            self._send(self.conn_recv, 'ACK ' + dtn_msg.hash)
            logger.debug('send ACK ' + dtn_msg.hash)
        else: # ACK
            return

        # Message reaches destination
        if dtn_msg.dst == self.my_sh:
            self.sm.db.update('ack=1', "hash='%s'"%dtn_msg.hash)

            # New DST_ACK message
            if dtn_msg.type != 'DST_ACK':

                dst_msg = DTNMessage()
                dst_msg.time = int(time.time()*1000)
                dst_msg.ack = 1
                dst_msg.ip = self.sm.my_ip
                dst_msg.port = self.sm.dtn_port
                dst_msg.dst = dtn_msg.src
                dst_msg.src = self.my_sh
                dst_msg.type = 'DST_ACK'
                dst_msg.data = dtn_msg.hash
                dst_msg.hash = dst_msg.get_hash()

                self.sm.db.insert_dst_ack(dst_msg)

                self.msgs.append(dst_msg)

            # CMD 
            if dtn_msg.type == 'CMD':

                # Run
                cmd = dtn_msg.data
                logger.debug('recv CMD : %s', cmd)
                import commands
                res = commands.getstatusoutput(cmd)
                logger.debug('CMD result :' + str(res))

                # Send CMD_RES
                res_msg = DTNMessage()
                res_msg.time = int(time.time()*1000)
                res_msg.ack = 0
                res_msg.ip = self.sm.my_ip
                res_msg.port = self.sm.dtn_port
                res_msg.dst = dtn_msg.src
                res_msg.src = self.my_sh
                res_msg.type = 'CMD_RES'
                res_msg.data = str(res)
                res_msg.hash = res_msg.get_hash()

                self.sm.db.insert_msg(res_msg)

                self.msgs.append(res_msg)

        return True

    def _recv_thread(self):

        while True:
            if self.stop_flag:
                logger.debug('recv_thread is killed')
                self.recv_done = True
                break
                
            try:

                self.buf += self.conn_recv.recv(1024)

                while self.buf.find('\n') >= 0:
                    msg, self.buf = self.buf.split('\n', 1)

                    if msg == SEND_DONE:
                        logger.debug('recv SEND_DONE')
                        self.recv_done = True
                        continue

                    self._recv_handle(msg)
                    if self.cb is not None:
                        self.cb(msg)

            except socket.timeout:
                logger.debug("no incoming data")
            except socket.error:
                logger.warn("recv_thread connection lost")
                self.stop_flag = True
                self.recv_done = True
                break

        logger.debug('recv_thread exist')
        

    def _daemon_thread(self):
        while True:
            #if not self.send_thread.isAlive() and self.recv_done:#not self.recv_thread.isAlive():
            if (self.send_done and self.recv_done) or ((not self.send_thread.isAlive()) and (not
                    self.recv_thread.isAlive())):#not self.recv_thread.isAlive():
                if self.stop_flag:
                    logger.error('Error happended or stop by user')
                break

            time.sleep(5)

        # Work is done, this instance of DTNConnection could be removed
        self.stop_flag = True
        self.send_thread.join()
        self.recv_thread.join()
        self.clean()
        logger.debug('clean done')
        logger.info('job done')

    def run(self):
        self.send_thread = threading.Thread(target=self._send_thread)
        self.recv_thread = threading.Thread(target=self._recv_thread)
        self.daemon_thread = threading.Thread(target=self._daemon_thread)

        self.send_thread.start()
        self.recv_thread.start()
        self.daemon_thread.start()

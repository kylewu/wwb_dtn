#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Fri 11 Mar 2011 02:01:11 PM CET'
__version__ = '0.4'

import socket
import time
import threading

import DTN
from DTN import logger
from DTNMessage import DTNMessage

TIMEOUT = 5

SEND_DONE = 'FINISH'

class DTNConnection(threading.Thread):

    def __init__(self, conn_send, conn_recv, my_sh, sh, target, sm, cb=None):
        threading.Thread.__init__(self)

        #self.mode = mode
        self.conn_send = conn_send
        self.conn_recv = conn_recv

        self.sm = sm

        self.my_sh = my_sh
        self.sh = sh

        # FIXME need? Callback function
        self.cb = cb
        
        # Target the other Site Manager needs
        # * or list of ids
        self.target = target

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

        self.clean()

    def clean(self):
        if self.conn_send is not None:
            DTN._cleanup_socket(self.conn_send)
        if self.conn_recv is not None:
            DTN._cleanup_socket(self.conn_recv)

        # Set DTNConnection of this SH in Site Manager to None
        self.sm.dtn[self.sh] = None

    def _get_all(self):
        if self.target == '*':
            # FIXME
            return self.sm.db.select_msg('dst!=\'%s\'' % self.my_sh)
        else:
            ids = self.target.split()
            res = list()
            for id in ids:
                # FIXME
                res += self.sm.db.select_msg('dst!=\'%s\' and dst == \'%s\'' % (self.my_sh, id))
            return res

    # FIXME old, no need any more
    def _update_sent(self, id):
        return self.sm.db.update('sent=1', 'hash={0}'.format(id) )

    def _send_data(self, conn, data):
        conn.send(data + '\n')

    def _send(self, msg):

        try:
            data = msg.to_msg()

            self._send_data(self.conn_send, data)

            logger.debug("send %s" % data)

            res = self.conn_send.recv(1024)

            if res == 'ACK %s\n' % msg.hash:
                # update last hash
                self.sm.last_hash[self.sh] = msg.hash
                #FIXME
                #self._update_sent(msg[0])
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

            if self.conn_send is None:
                self.stop_flag = True
                logger.warn('No Connection')
                break

            # msg is instance of DTNMessage
            msgs = self._get_all()
            #logger.debug('LEN: %d' % len(msgs))
            res = True
            for msg in msgs:
                res = self._send(msg)
                if not res:
                    self.stop_flag = True
                    break

            if not res:
                break

            if not self.keep_alive:
                self._send_data(self.conn_send, SEND_DONE) 
                break

            time.sleep(TIMEOUT)

        logger.debug('send_thread exist')

    def _recv_handle(self, msg):
        dtn_msg = DTNMessage()
        dtn_msg.handle(msg)

        self.sm.db.insert_msg(dtn_msg)

        logger.debug('recv ' + dtn_msg.re_type)

        if dtn_msg.re_type != 'ACK':
            self._send_data(self.conn_recv, 'ACK ' + dtn_msg.hash)

        # FIXME
        if dtn_msg.dst == self.my_sh:
            dst_msg = DTNMessage()
            dst_msg.time = int(time.time()*1000)
            dst_msg.ip = self.sm.my_ip
            dst_msg.port = self.sm.dtn_port
            dst_msg.dst = dtn_msg.src
            dst_msg.src = self.my_sh
            dst_msg.data = dtn_msg.hash
            dst_msg.new_hash()

            self.sm.db.insert_msg(dst_msg)

            self._send(dst_msg)

        if dtn_msg.re_type == 'CMD' and self.my_sh == dtn_msg.dst:
            cmd = dtn_msg.data
            # TODO check this
            logger.debug('recv CMD : %s', cmd)
            import commands
            res = commands.getstatusoutput(cmd)
            logger.debug(res)

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

                    logger.debug(msg)

                    if msg == SEND_DONE:
                        is_finish = True
                        break

                    self._recv_handle(msg)
                    if self.cb is not None:
                        self.cb(msg)

            except socket.timeout:
                logger.debug("no incoming data")
            except socket.error:
                logger.warn("recv_thread connection lost")
                self.stop_flag = True
                break

            if is_finish:
                break

            #time.sleep(TIMEOUT)

        logger.debug('recv_thread exist')

    def _daemon_thread(self):
        while True:
            if not self.send_thread.isAlive() and not self.recv_thread.isAlive():
                if self.stop_flag:
                    logger.error('Error happended or stop by user')
                else:
                    logger.info('asyn done')
                break

            time.sleep(5)

        # Work is done, this instance of DTNConnection could be removed
        logger.debug('clean')
        self.clean()

    def run(self):
        self.send_thread = threading.Thread(target=self._send_thread)
        self.recv_thread = threading.Thread(target=self._recv_thread)
        self.daemon_thread = threading.Thread(target=self._daemon_thread)

        self.send_thread.start()
        self.recv_thread.start()
        self.daemon_thread.start()

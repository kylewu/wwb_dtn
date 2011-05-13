#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Wed May 01 23:03:51 2011'
__version__ = '0.1'

import hashlib
import re

# NOTE
# TIMESTAMP used in VClient is time.tv_sec*1000 + time.tv_usec/1000
# In python, we can get this by using int(time.time()*1000)

PING_RAW = 'PING_RAW'
PING = 'PING'
ACK = 'ACK'
CMD_RAW = 'CMD_RAW'
CMD = 'CMD'

# -----------------------------------------------------
# PING msg from VClient
PING_RAW_re = re.compile("(?P<time>\d+) (?P<ip>[\d+\.]+):(?P<port>\d+) PING (?P<src>[^ ]*) {(?P<attributes>[^}]+)}.*")
# PING msg in WSN
PING_re = re.compile("(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[\d+\.]+) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst>[^ ]*) PING {(?P<attributes>[^}]+)}.*")
# ACK msg in WSN
ACK_re = re.compile("ACK (?P<hash>[^ ]+)")
# CMD msg from Monitor
CMD_RAW_re = re.compile('(?P<time>\d+) (?P<dst>[^ ]*) CMD {(?P<cmd>[^}]+)}.*')
# CMD msg in WSN
CMD_re = re.compile("(?P<hash>[a-z0-9]+) (?P<time>\d+) SERVER PORT SERVER (?P<dst>[^ ]*) CMD {(?P<cmd>[^}]+)}.*")
# Reach DST
DST_re = re.compile("DST (?P<hash>[^ ]+)")


# -----------------------------------------------------

class DTNMessage():
    def __init__(self):
        # return value / re type
        self.re_type = None

        # keep a image of message
        self.msg = ''

        # DB attributes
        self.hash = ''
        self.sent = 0
        self.sent_time = ''
        self.ack  = 0
        self.ack_time = ''
        self.ttl = 2*24*60*60   # 2d
        self.time = ''
        self.ip   = ''
        self.port = ''
        self.src  = ''
        self.dst  = ''
        self.type = ''
        self.data = ''

        # get attributes from message
        #self.handle(msg)

    # FIXME not sure this function should be here
    def get_hash(self, msg):
        m = hashlib.md5()
        m.update(msg)
        return m.digest().encode('hex')

    def new_hash(self, msg):
        m = hashlib.md5()
        m.update('%d %s %s %s %s %s %s' \
                    % (self.time, self.ip, self.port, self.src, self.dst, self.type, self.data))
        self.hash = m.digest().encode('hex')

    def to_tuple(self):
        return None, self.hash, self.sent, self.ack, self.time, self.ip, self.port, self.src, self.dst, self.type, self.data 

    # TODO
    def to_msg(self):
        if self.re_type == PING_RAW:
            return '%s %d %s %s %s %s %s %s' \
                    % (self.hash, self.time, self.ip, self.port, self.src, self.dst, self.type, self.data)
        return '%s %d %s %s %s %s %s %s' \
                % (self.hash, self.time, self.ip, self.port, self.src, self.dst, self.type, self.data)



    ###########
    # HASH, SENT, ACK, TIME, IP, PORT, SRC, DST, TYPE, ATTR
    ###########
    def handle(self, msg):
        self.msg = msg

        m = PING_RAW_re.match(msg)
        if m is not None:
            self.re_type = PING_RAW 
            self.hash = self.get_hash(msg)
            self.time = int(m.group('time'))
            self.ip =  m.group('ip')
            self.port = m.group('port')
            self.src = m.group('src')
            self.dst = 'SERVER'
            self.type = 'PING'
            self.data = '{%s}' % m.group('attributes')
            return

        m = CMD_RAW_re.match(msg)
        if m is not None:
            self.re_type = CMD_RAW
            self.hash = self.get_hash(msg)
            self.time = m.group('time')
            self.ip = 'SERVER'
            self.port = 'PORT'
            self.src = 'SERVER'
            self.dst = m.group('dst')
            self.type = 'CMD'
            self.data = '{%s}' % m.group('cmd')
            return

        m = ACK_re.match(msg)
        if m is not None:
            self.re_type = ACK
            self.hash = m.group('hash')

        m = PING_re.match(msg)
        if m is not None:
            self.re_type = PING
            self.hash = m.group('hash')
            self.sent = -1
            self.time = m.group('time')
            self.ip = m.group('ip')
            self.port = m.group('port')
            self.src = m.group('src')
            self.dst = m.group('dst')
            self.type = 'PING'
            self.data = '{%s}' % m.group('attributes')

        # TODO
        m = CMD_re.match(msg)
        if m is not None:
            (None, m.group('hash'), -1, 0, m.group('time'), 'SERVER', 'PORT', 'SERVER', m.group('dst'), 'CMD', '{%s}' % m.group('cmd'))
            return 'CMD_RECV', m.group('cmd')

        return 

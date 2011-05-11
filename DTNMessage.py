#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Wed May 01 23:03:51 2011'
__version__ = '0.1'

import hashlib
import re

# -----------------------------------------------------
# PING msg from VClient
PING_SEND_re = re.compile("(?P<time>\d+) (?P<ip>[\d+\.]+):(?P<port>\d+) PING (?P<src>[^ ]*) {(?P<attributes>[^}]+)}.*")
# PING msg in WSN
PING_RECV_re = re.compile("(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[\d+\.]+) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst>[^ ]*) PING {(?P<attributes>[^}]+)}.*")
# ACK msg in WSN
ACK_re = re.compile("(?P<type>[A-Z]+) (?P<hash>[^ ]+)")
# CMD msg from Monitor
CMD_SEND_re = re.compile('(?P<time>\d+) (?P<dst>[^ ]*) CMD {(?P<cmd>[^}]+)}.*')
# CMD msg in WSN
CMD_RECV_re = re.compile("(?P<hash>[a-z0-9]+) (?P<time>\d+) SERVER PORT SERVER (?P<dst>[^ ]*) CMD {(?P<cmd>[^}]+)}.*")
# -----------------------------------------------------

class DTNMessage():
    def __init__(self, msg):
        # return value / re type
        self.re_type = None

        # keep a image of message
        self.msg = msg

        # DB attributes
        self.hash = ''
        self.sent = 0
        self.sent_time = ''
        self.ack  = 0
        self.ack_time = ''
        self.time = ''
        self.ip   = ''
        self.port = ''
        self.src  = ''
        self.dst  = ''
        self.type = ''
        self.data = ''

        # get attributes from message
        self.handle(msg)

    # FIXME not sure this function should be here
    def get_hash(self, msg):
        m = hashlib.md5()
        m.update(msg)
        return m.digest().encode('hex')

    def to_tuple(self):
        return None, self.hash, self.sent, self.ack, self.time, self.ip, self.port, self.src, self.dst, self.type, self.data 


    ###########
    # HASH, SENT, ACK, TIME, IP, PORT, SRC, DST, TYPE, ATTR
    ###########
    def handle(self, msg):

        m = PING_SEND_re.match(msg)
        if m is not None:
            self.re_type = 'PING_SEND'
            self.hash = self.get_hash(msg)
            self.time = m.group('time')
            self.ip =  m.group('ip')
            self.port = m.group('port')
            self.src = m.group('src')
            self.dst = 'SERVER'
            self.type = 'PING'
            self.data = '{%s}' % m.group('attributes')
            return

        m = CMD_SEND_re.match(msg)
        if m is not None:
            self.re_type = 'CMD_SEND'
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
            self.re_type = 'ACK'
            self.hash = m.group('hash')

        m = PING_RECV_re.match(msg)
        if m is not None:
            self.re_type = 'PING_RECV'
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
        m = CMD_RECV_re.match(msg)
        if m is not None:
            (None, m.group('hash'), -1, 0, m.group('time'), 'SERVER', 'PORT', 'SERVER', m.group('dst'), 'CMD', '{%s}' % m.group('cmd'))
            return 'CMD_RECV', m.group('cmd')

        return 

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

# TODO remove all these
PING_RAW = 'PING_RAW'
CMD_RAW = 'CMD_RAW'
PING = 'PING'
CMD = 'CMD'
ACK = 'ACK'
DST_ACK = 'DST_ACK'

# RAW MESSAGES  -----------------------------------------------------
# PING msg from VClient
PING_RAW_re = re.compile(
        "(?P<time>\d+) (?P<ip>[\d+\.]+):(?P<port>\d+) PING (?P<src>[^ ]*) {(?P<data>[^}]+)}.*"
        )
# CMD msg from Monitor
CMD_RAW_re = re.compile('(?P<time>\d+) (?P<dst>[^ ]*) CMD {(?P<cmd>[^}]+)}.*')

# ACK msg in WSN
ACK_re = re.compile("ACK (?P<hash>[^ ]+)")

# Message in WSN
MSG_re = re.compile(
        "(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[\d+\.]+) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst>[^ ]*) (?P<type>[^ ]*) {(?P<data>[^}]+)}.*"
        )

# MESSAGES in WSN -----------------------------------------------------
# TODO PING msg 
#PING_re = re.compile(
        #"(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[\d+\.]+) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst>[^ ]*) PING {(?P<data>[^}]+)}.*"
        #)
# TODO CMD msg 
#CMD_re = re.compile("(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[\d+\.]+) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst>[^ ]*) CMD {(?P<cmd>[^}]+)}.*")
# TODO CMS Result
#CMD_RES_re = re.compile("(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[^ ]*) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst[^ ]*) CMD_RES {(?P<cmd>[^}]+)}.*")

# TODO ACK from DST
#DST_ACK_re = re.compile(
        #"(?P<hash>[a-z0-9]+) (?P<time>\d+) (?P<ip>[\d+\.]+) (?P<port>\d+) (?P<src>[^ ]*) (?P<dst>[^ ]*) DST_ACK {(?P<data>[^}]+)}.*"
        #)

# -----------------------------------------------------

class DTNMessage():
    def __init__(self):
        # return value / re type
        #self.re_type = None

        # keep a image of message
        self.msg = ''

        # DB attributes
        self.hash = ''
        self.sent = 0
        #self.sent_time = ''
        self.ack  = 0
        #self.ack_time = ''
        self.ttl = 2*24*60*60   # 2d
        self.time = 0
        self.ip   = ''
        self.port = ''
        #self.pre = ''   # Only used in DB, cannot find this in messages
        self.src  = ''
        self.dst  = ''
        self.type = ''
        self.data = ''

    def get_hash(self):
        m = hashlib.md5()
        m.update(self._to_msg())
        return m.digest().encode('hex')
        

    def to_tuple(self):
        """ Generate tuple used in Database"""
        return None, self.hash, self.sent, self.ack, self.time, self.ip, self.port, self.src, self.dst, self.type, self.data 

    def _to_msg(self):
        """ Message without hash """
        return '%d %s %s %s %s %s {%s}' \
                % (self.time, self.ip, self.port, self.src, self.dst, self.type, self.data)

    def to_msg(self):
        """ Message with hash """
        return '%s %d %s %s %s %s %s {%s}' \
                % (self.hash, self.time, self.ip, self.port, self.src, self.dst, self.type, self.data)

    ###########
    # HASH, SENT, ACK, TIME, IP, PORT, SRC, DST, TYPE, ATTR
    ###########
    def handle(self, msg):
        self.msg = msg # keep a local copy of msg

        m = ACK_re.match(msg)
        if m is not None:
            #self.re_type = ACK
            self.type = ACK
            self.hash = m.group('hash')
            return True

        m = PING_RAW_re.match(msg)
        if m is not None:
            print 'PING_RAW'
            #self.re_type = PING_RAW 
            self.time = int(m.group('time'))
            self.ip =  m.group('ip')
            self.port = m.group('port')
            self.src = m.group('src')
            self.dst = 'SERVER'
            self.type = 'PING'
            self.data = m.group('data')
            self.hash = self.get_hash()
            return True

        m = CMD_RAW_re.match(msg)
        if m is not None:
            #self.re_type = CMD_RAW
            self.time = int(m.group('time'))
            self.ip = 'SERVER'
            self.port = 'PORT'
            self.src = 'SERVER'
            self.dst = m.group('dst')
            self.type = 'CMD'
            self.data = m.group('cmd')
            self.hash = self.get_hash()
            return True

        m = MSG_re.match(msg)
        if m is not None:
            #self.re_type = m.group('type')
            self.hash = m.group('hash')
            self.sent = 0
            self.ack = 0
            self.time = int(m.group('time'))
            self.ip = m.group('ip')
            self.port = m.group('port')
            self.src = m.group('src')
            self.dst = m.group('dst')
            self.type = m.group('type')
            self.data = m.group('data')
            return True

        # TODO remove the following
        #m = PING_re.match(msg)
        #if m is not None:
            #self.re_type = PING
            #self.hash = m.group('hash')
            #self.sent = -1
            #self.time = m.group('time')
            #self.ip = m.group('ip')
            #self.port = m.group('port')
            ##self.pre = pre
            #self.src = m.group('src')
            #self.dst = m.group('dst')
            #self.type = 'PING'
            #self.data = '{%s}' % m.group('data')
            #return

        #m = CMD_re.match(msg)
        #if m is not None:
            #self.re_type = CMD
            #self.hash = m.group('hash')
            #self.sent = -1
            #self.time = m.group('time')
            #self.ip = m.group('ip')
            #self.port = m.group('port')
            #self.src = m.group('src')
            #self.dst = m.group('dst')
            #self.type = 'CMD'
            #self.data = '{%s}' % m.group('cmd')
            #return
        
        #m = DST_ACK_re.match(msg)
        #if m is not None:
            #self.re_type = DST_ACK
            #self.hash = m.group('hash')
            #self.sent = -1
            #self.time = m.group('time')
            #self.ip = m.group('ip')
            #self.port = m.group('port')
            #self.src = m.group('src')
            #self.dst = m.group('dst')
            #self.type = 'DST_ACK'
            #self.data = '{%s}' % m.group('data')
            #return

        return False

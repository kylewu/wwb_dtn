#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon Apr 25 10:02:52 2011'
__version__ = '0.3'

import re
import hashlib

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

def hash(msg):
    """ Help function to compute hash
    """
    m = hashlib.md5()
    m.update(msg)
    return m.digest().encode('hex')

###########
# HASH, SENT, ACK, TIME, IP, PORT, SRC, DST, TYPE, ATTR
###########
def handle(msg):
    m = PING_SEND_re.match(msg)
    if m is not None:
        return 'PING_SEND', None, hash(msg), 0, 0, m.group('time'), m.group('ip'), m.group('port'), m.group('src'), 'SERVER', 'PING', '{%s}' % m.group('attributes')

    m = CMD_SEND_re.match(msg)
    if m is not None:
        return 'CMD_SEND', None, hash(msg), 0, 0, m.group('time'), 'SERVER', 'PORT', 'SERVER', m.group('dst'), 'CMD', '{%s}' % m.group('cmd')

    # recv ACK
    m = ACK_re.match(msg)
    if m is not None:
        #print m.group('hash')
        # TODO update_ack(m.group('hash'))
        #print m.group('hash')
        return 'ACK', m.group('hash')

    # recv PING
    m = PING_RECV_re.match(msg)
    if m is not None:
        return 'PING_RECV', None, m.group('hash'), -1, 0, m.group('time'), m.group('ip'), m.group('port'), m.group('src'), m.group('dst'), 'PING', '{%s}' % m.group('attributes')

    # recv CMD
    m = CMD_RECV_re.match(msg)
    if m is not None:
        (None, m.group('hash'), -1, 0, m.group('time'), 'SERVER', 'PORT', 'SERVER', m.group('dst'), 'CMD', '{%s}' % m.group('cmd'))
        #FIXME
        return 'CMD_RECV', m.group('cmd')

    return None

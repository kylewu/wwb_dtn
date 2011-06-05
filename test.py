#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sun 15 May 2011 04:51:57 PM CEST'
__version__ = '0.1'

import re
CMD_RAW_re = re.compile('(?P<time>\d+) (?P<dst>[^ ]*) (?P<ttl>\d+) CMD {(?P<cmd>[^}]+)}.*')
msg = '1305471087617 001E8C6C9172 86400000 CMD ls'

m = CMD_RAW_re.match(msg)
if m is not None:
    print 'good'

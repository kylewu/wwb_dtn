#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sun Apr  3 15:29:43 2011'
__version__ = '0.1'

import sys
import time

from DTNDatabase import DTNDatabase
from DTNMessage import DTNMessage

# dtncmd HOST NODE {CMD}

if len(sys.argv) < 3:
    sys.exit()
t = str(int(time.time()))

msg = '%s %s %d CMD %s' % (t, sys.argv[1], 24*60*60*1000, ' '.join(sys.argv[3:]))
m = DTNMessage(msg)
# TODO set message ip and port if possible

db = DTNDatabase('ServerSiteManager')
db.insert_msg(m)

print 'OK'
#for msg in db.select_all():
    #print msg

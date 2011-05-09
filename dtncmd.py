#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sun Apr  3 15:29:43 2011'
__version__ = '0.1'

import sys
import time

from DTNDatabase import DTNDatabase

# dtncmd HOST NODE {CMD}

if len(sys.argv) < 3:
    sys.exit()
t = str(int(time.time()))
msg = '%s %s CMD %s' % (t, sys.argv[1], ' '.join(sys.argv[3:]))

db = DTNDatabase('ServerSiteManager')
db.insert(msg)
print 'OK'

#for msg in db.select_all():
    #print msg

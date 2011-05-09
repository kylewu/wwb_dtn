#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sun 03 Apr 2011 08:00:05 PM CEST'
__version__ = '0.1'

from DTNSiteManager import SiteManagerCarrier

import time

carrier = SiteManagerCarrier()

while True:
    if carrier.bcast(5555) and carrier.connect_to_server():
        print 'successed'
        carrier.start()
        time.sleep(20)
        carrier.stop()
        break

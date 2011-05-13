#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 09 May 2011 09:59:04 AM CEST'
__version__ = '0.1'

from DTNSiteManager import ClientSiteManager

#ip='130.238.8.164'
#ip='127.0.0.1'
ip = '130.243.144.12'
sm = ClientSiteManager(server_ip='127.0.0.1', server_port=7777, vclient_port=4445, ip=ip, sh='client')
sm.start()

sm.connect_to_sm(ip, 15555)

#while True:
    #print 'send'
    #sm.bcast(16666)
    #print 'sent'
    #import time
    #time.sleep(5)

import sys
#sys.exit(1)

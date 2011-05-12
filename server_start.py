#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 09 May 2011 09:59:04 AM CEST'
__version__ = '0.1'

from DTNSiteManager import ServerSiteManager

#ip='130.238.8.164'
#ip='127.0.0.1'
ip = '130.243.144.12'
sm = ServerSiteManager(dtn_port=15555, bcast_port=16666, monitor_port=17777,vclient_port = 188888, ip=ip)
sm.start()

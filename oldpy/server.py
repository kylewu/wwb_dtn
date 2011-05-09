#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             server.py
    Create Date:      Wed Mar 23 12:02:08 2011

'''

from DTNSiteManager import SiteManagerServer 

ip = '130.238.8.164'
# m_port dtn_port, bcast_port
server = SiteManagerServer(4001, 4005, 5555, ip)
server.start()

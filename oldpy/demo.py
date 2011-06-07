#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 11 Apr 2011 10:16:37 PM CEST'
__version__ = '0.1'

import time
import sys

from DTNSiteManager import SiteManagerServer 
from DTNSiteManager import SiteManagerClient

ip = '130.238.8.164'

def test1():
    # m_port dtn_port, bcast_port
    server = SiteManagerServer(4001, 4005, 5555, ip)
    server.start()

    client1 = SiteManagerClient(4000, 4445, 4003, 5555, ip, 4005, '130.238.8.164')
    client1.start()
    time.sleep(3)
    client1.stop()
    #client1.join()
    client1.clean()

    time.sleep(3)

    #client2 = SiteManagerClient(4000, 4445, 4003, 5555, ip, 4005, '130.238.8.164')
    #client2.start()
    #time.sleep(3)
    #client2.stop()
    ##client2.join()
    #client2.clean()

    server.quit()

def test2():
    client = SiteManagerClient(4000, 4445, 4003, 5555, ip, 4005, '130.238.8.164')
    client.start()

    server1 = SiteManagerServer(4001, 4005, 5555, ip)
    server1.start()
    time.sleep(3)
    server1.stop()
    #server1.join()
    server1.quit()

    time.sleep(3)

    server2 = SiteManagerServer(4001, 4005, 5555, ip)
    server2.start()
    time.sleep(3)
    server2.stop()
    #server2.join()
    server2.quit()

    client.stop()
    #client.join()
    client.clean()

def test3():

    client = SiteManagerClient(4000, 4445, 4003, 5555, ip, 4005, '130.238.8.164')
    client.start()

    server = SiteManagerServer(4001, 4015, 5555, ip)
    server.start()

    time.sleep(60)

    client.stop()
    client.clean()
    server.stop()
    server.quit()

def test4():
    import commands
    print commands.getstatusoutput('python dtncmd.py vincent telosb_M4A7J5MB {python /home/wenbin/Dropbox/uu/echo.py}')

if __name__ == '__main__':
    if len(sys.argv)==1:
        sys.exit()

    try:
        locals()[sys.argv[1]]()
    except Exception, e:
        raise e

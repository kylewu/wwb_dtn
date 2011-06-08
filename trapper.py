#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sat May 14 10:48:06 2011'
__version__ = '0.3'

#from DTNSiteManager import ServerSiteManager
from DTNSiteManager import BaseDTNSiteManager

HELP = 'c : connect\nb : broadcast\ns : start\nq : quit'

mobile_ip = '192.168.100.126' # Mobile
ubuntu_ip = '130.238.8.164' # UBUNTU
vincent_ip = '130.238.8.154' # Vincent
trapper_ip = '130.238.8.166' # Trapper

ip = ubuntu_ip
server_ip = ubuntu_ip

dtn = None

while True:
    c = raw_input('Input cmd:')
    if c == 'c':
        if dtn is not None:
            print 'connect'
            i = raw_input('  Ip:')
            p = raw_input('  Port:')
            dtn.connect_to_sm(i,int(p))
    elif c == 'b':
        if dtn is not None:
            print 'braodcast'
            p = raw_input('  Port:')
            print dtn.bcast(int(p))
        else:
            print 'please start dtn first'
    elif c == 's':
        if dtn is None:
            print 'start'
            dtn = BaseDTNSiteManager(dtn_port=5555, 
                    bcast_port=6666, 
                    monitor_port=7777, 
                    vclient_port=4444, 
                    ip=ip,
                    sh='trapper', 
                    db_name='trapper')
            dtn.start()

    #DEMO
    elif c == '1':
        if dtn is None:
            print 'start'
            dtn = BaseDTNSiteManager(dtn_port=5555, 
                    bcast_port=6666, 
                    monitor_port=7777, 
                    vclient_port=4444, 
                    ip=ip,
                    sh='trapper', 
                    db_name='trapper')
            dtn.start()
    elif c == '2':
        if dtn is None:
            print 'start'
            dtn = BaseDTNSiteManager(dtn_port=5555, 
                    bcast_port=6666, 
                    monitor_port=7777, 
                    vclient_port=4444, 
                    ip=ip,
                    sh='trapper', 
                    db_name='trapper',
                    target='abc')
            dtn.start()

    elif c == 'q':
        print 'quit'
        if dtn is not None:
            dtn.stop()
        import sys
        sys.exit(0)
    else:
        print HELP

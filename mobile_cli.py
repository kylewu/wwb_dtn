#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sat May 14 10:48:06 2011'
__version__ = '0.1'

from DTNSiteManager import MobileSiteManager

HELP = 'c : connect\nb : broadcast\ns : start\nq : quit'

ip = '130.238.8.164' # UBUNTU
#ip = '130.238.8.154' # Vincent
#ip = '130.238.8.166' # Trapper

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
            dtn = MobileSiteManager(dtn_port=25555, bcast_port=26666, ip=ip)
            dtn.start()
    elif c == 'q':
        print 'quit'
        dtn.stop()
        import sys
        sys.exit(0)
    else:
        print HELP

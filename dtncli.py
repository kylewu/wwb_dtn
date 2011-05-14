#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sat May 14 10:48:06 2011'
__version__ = '0.1'

from DTNSiteManager import MobileSiteManager

HELP = 'c : connect\nb : broadcast\nk : stop\ns : start\nq : quit'

ip = '130.243.144.12'

mobile = None
while True:
    c = raw_input('Input cmd:')
    if c == 'c':
        print 'connect'
    elif c == 'b':
        if mobile is not None:
            print 'braodcast'
            p = raw_input('  Port:')
            print mobile.bcast(int(p))
        else:
            print 'please start mobile first'
    elif c == 'k':
        if mobile is not None:
            print 'stop'
            mobile.stop()
            mobile = None
    elif c == 's':
        if mobile is None:
            print 'start'
            mobile = MobileSiteManager(dtn_port=25555, bcast_port=26666, ip=ip)
            mobile.start()
    elif c == 'q':
        print 'quit'
    else:
        print HELP

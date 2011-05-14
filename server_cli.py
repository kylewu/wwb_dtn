#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sat May 14 10:48:06 2011'
__version__ = '0.1'

from DTNSiteManager import ServerSiteManager

HELP = 'c : connect\nb : broadcast\nk : stop\ns : start\nq : quit'

ip = '130.243.144.12'

server = None

while True:
    c = raw_input('Input cmd:')
    if c == 'c':
        print 'connect'
    elif c == 'b':
        if server is not None:
            print 'braodcast'
            p = raw_input('  Port:')
            print server.bcast(int(p))
        else:
            print 'please start server first'
    elif c == 'k':
        if server is not None:
            print 'stop'
            server.stop()
            server = None
    elif c == 's':
        if server is None:
            print 'start'
            server = ServerSiteManager(dtn_port=5555, bcast_port=6666, monitor_port=17777,vclient_port = 188888, ip=ip)
            server.start()
    elif c == 'q':
        print 'quit'
    else:
        print HELP

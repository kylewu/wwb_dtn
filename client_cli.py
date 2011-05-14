#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Sat May 14 10:48:06 2011'
__version__ = '0.1'

from DTNSiteManager import ClientSiteManager

HELP = 'c : connect\nb : broadcast\nk : stop\ns : start\nq : quit'

ip = '130.243.144.12'

client = None
while True:
    c = raw_input('Input cmd:')
    if c == 'c':
        print 'connect'
    elif c == 'b':
        if client is not None:
            print 'braodcast'
            p = raw_input('  Port:')
            print client.bcast(int(p))
        else:
            print 'please start client first'
    elif c == 'k':
        if client is not None:
            print 'stop'
            client.stop()
            client = None
    elif c == 's':
        if client is None:
            print 'start'
            client = ClientSiteManager(dtn_port=15555, bcast_port=16666, server_ip='127.0.0.1', server_port=7777, vclient_port=4445, ip=ip, sh='client')
            client.start()
    elif c == 'q':
        print 'quit'
    else:
        print HELP

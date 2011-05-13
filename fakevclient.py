#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Thu May 12 13:09:01 2011'
__version__ = '0.1'

import socket
import time

#UDP_IP='130.238.8.164'
#UDP_IP='127.0.0.1'
UDP_IP = '130.243.144.12'

UDP_PORT=4445
MESSAGE="%d 130.238.8.154:7000 PING 001E8C6C9172 {position=>wgs84,17.647102456850032,59.83816340033785,62.99983961507678;platform=>ASUS WL-500GP;type=>sensorhost;}" 


while True:
    print 'send msg'
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) 
    sock.sendto( MESSAGE % int(time.time()*1000), (UDP_IP, UDP_PORT) )
    time.sleep(2)


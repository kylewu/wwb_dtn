#!/usr/bin/env python

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             DTN.py
    Create Date:      Wed Feb 16 09:50:20 2011

'''
import socket
import sys
import logging

TIMEOUT = 0.5
SOCKET_TIMEOUT = 2

# Log Level, IMPORTANT
LOGLEVEL = logging.DEBUG

# global log variable
logger = None

def init_log(name):
    global logger
    if logger is not None:
        return 
    #create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOGLEVEL)

    #create file handler and set level to debug
    fh = logging.FileHandler("log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    #create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    #add formatter to ch and fh
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    #add ch and fh to logger
    logger.addHandler(fh)
    logger.addHandler(ch)

# INIT LOGGER
init_log('DTN')

def _tcp_listen(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error, e:
        logger.error("Error creating socket: %s" % e)
        sys.exit(1)

    try:
        s.bind((ip, port))
    except socket.error, e:
        logger.error("error binding socket to %s : %d" % (ip, port))
        sys.exit(1)

    try:
        s.listen(5)
    except socket.error, e:
        logger.error("error listening to socket")
        sys.exit(1)

    logger.debug('listening on port ' + str(port))
    return s

def _tcp_connect(ip, port):

    logger.debug("try to connect " + str(ip) + ":" + str(port))

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, e:
        logger.error("Error creating socket: %s" % e)
        sys.exit(1)

    s.settimeout(SOCKET_TIMEOUT)
    try:
        s.connect((ip, port))
    except socket.timeout:
        logger.debug("connect timeout")
        return None
    except socket.error, e:
        logger.debug("Error connecting TCP socket: %s" % e)
        return None

    return s

def _udp_open(ip, port):
    "Init the UDP socket"

    logger.debug("opening udp port %d" % port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((ip, port))

    except socket.error, e:
        logger.debug("Error creating socket: %s" % e)
        sys.exit(1)

    return s

def _broadcast_listen(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', port))
    return s

def _cleanup_socket(sock):
    if sock is None:
        return
    try:
        sock.close()
    except socket.error:
        logger.error("Error closing " + sock)
#class DTN():

    #def __init__(self):
        #self.name = self.__class__.__name__

    #def _log(self, log):
        #print '%s : %s' % (self.name, log)
        
    #def _tcp_listen(self, ip, port):
        #try:
            #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #except socket.error, e:
            #self._log("Error creating socket: %s" % e)
            #sys.exit(1)

        #try:
            #s.bind((ip, port))
        #except socket.error, e:
            #self._log("error binding socket to %s : %d" % (ip, port))
            #sys.exit(1)

        #try:
            #s.listen(5)
        #except socket.error, e:
            #self._log("error listening to socket")
            #sys.exit(1)

        #self._log('listening on port ' + str(port))
        #return s

    #def _tcp_connect(self, ip, port):

        #self._log("try to connect " + str(ip) + ":" + str(port))

        #try:
            #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #except socket.error, e:
            #self._log("Error creating socket: %s" % e)
            #sys.exit(1)

        #s.settimeout(SOCKET_TIMEOUT)
        #try:
            #s.connect((ip, port))
        #except socket.timeout:
            #self._log("connect timeout")
            #return None
        #except socket.error, e:
            ##self._log("Error connecting TCP socket: %s" % e)
            #return None

        #return s

    #def _udp_open(self, ip, port):
        #"Init the UDP socket"

        #self._log("opening udp port %d" % port)
        #try:
            #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #s.bind((ip, port))

        #except socket.error, e:
            #print "Error creating socket: %s" % e
            #sys.exit(1)

        #return s

    #def _broadcast_listen(self, port):
        #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #s.bind(('', port))

        #return s

    #def _cleanup_socket(self, sock):

        #try:
            #sock.close()
        #except socket.error:
            #self._log("Error closing " + sock)

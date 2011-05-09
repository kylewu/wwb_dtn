#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Tue Apr 19 09:14:39 2011'
__version__ = '0.1'


import threading 
import time

class A(threading.Thread):
    """docstring for A"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.f = False

    def run(self):
        """docstring for run"""
        while True:
            if self.f:
                time.sleep(5)
                print 'A die'
                break
            time.sleep(2)
    
    def stop(self):
        self.f = True
        
class B(threading.Thread):
    """docstring for B"""
    def __init__(self):
        threading.Thread.__init__(self)
        self.f = False
        
    def run(self):
        """docstring for run"""
        self.a = A()
        self.b = A()
        self.a.start()
        self.b.start()
        while True:
            if self.f:
                print 'B die'
                break


    def stop(self):
        self.f = True
        self.a.stop()
        self.b.stop()
        self.a.join()
        self.b.join()
        self.join()
        print 'B stop'

if __name__ == '__main__':
    x = B()
    x.start()
    time.sleep(2)
    x.stop()

import logging
LOGLEVEL = logging.INFO
name = 'test'
logger = None

def init_log():
    global logger
    #create logger
    logger = logging.getLogger("%s_%s" % (name, str(time.time())))
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

init_log()

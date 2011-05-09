#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon Apr 25 11:04:24 2011'
__version__ = '0.1'


class A():
    def __init__(self):
        self.a = 1
    def add(self):
        """docstring for add"""
        self.a += 1

class B(A):
    def __init__(self):
        A.__init__(self)
        self.a +=1
        print self.a
    def add(self):
        A.add(self)
        self.a+=1
        print self.a
        x=1

        for s in locals():
            print s
            print type(s)
        print self.a

b = B()
b.add()


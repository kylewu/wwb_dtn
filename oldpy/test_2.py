#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Tue Apr 19 10:38:48 2011'
__version__ = '0.1'

from test import logger
logger.info('test')

class TEST(object):
    """docstring for TEST"""
    def __init__(self):
        super(TEST, self).__init__()
        l = [('a', 'aa'), ('b',list()), ('c', None)]
        for x, y in l:
            setattr(self, x, y)
    def p(self):
        self.b.append('aaa')
        print locals()
        print self.a
        print self.b
        if self.c is None:
            print 'aaaa'
        
#t = TEST()
#t.p()
def test_var_args(farg, **args):
    x = args.get('abc', 'xxx')
    print x

test_var_args(1, bbc="two")

a=[1,2]
a+=[3,4]
print a

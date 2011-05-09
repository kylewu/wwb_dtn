#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 11 Apr 2011 02:41:13 PM CEST'
__version__ = '0.1'

from DTNDatabase import DTNDatabase
import sys

if len(sys.argv) == 1:
    sys.exit()

db = DTNDatabase(sys.argv[1])
for msg in db.select_all():
    print msg

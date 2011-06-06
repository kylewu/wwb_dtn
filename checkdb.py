#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 11 Apr 2011 02:41:13 PM CEST'
__version__ = '0.1'

import sys
import sqlite3

if len(sys.argv) == 1:
    sys.exit()

conn = sqlite3.connect(sys.argv[1])
s = 'select * from data where sent = 0'
cur = conn.execute(s)
msgs = cur.fetchall()
for msg in msgs:
    print msg
conn.commit()
conn.close()

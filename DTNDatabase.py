#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 21 Mar 2011 01:53:27 PM CET'
__version__ = '0.3'

import os
import sqlite3
import threading
from Queue import Queue

from DTNMessage import DTNMessage

CREATE_EXE = 'create table data (id integer primary key, hash text, sent integer, ack integer, ttl integer, time interger, ip text,\
                port text, src text, dst text, type text, data text);'
INSERT_EXE = 'insert into data (id, hash, sent, ack, ttl, time, ip, port, src, dst, type, data) SELECT ?, ?, ?, ?, ?,\
                ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM data WHERE hash = ?);'

INSERT_DST_EXE = 'insert into data (id, hash, sent, ack, ttl, time, ip, port, src, dst, type, data) SELECT ?, ?, ?, ?, ?,\
                ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM data WHERE data = ?);'

#CREATE_EXE = 'create table data (id integer primary key, hash text, sent integer, ack integer, ttl integer, time interger, ip text,\
                #port text, src text, dst text, type text, data text)'

#INSERT_EXE = "insert into data (id, hash, sent, ack, ttl, time, ip, port, src, dst, type, data) SELECT '%s', '%s', %d, %d, %d,\
                #%d, '%s', '%s', '%s', '%s', '%s', '%s' WHERE NOT EXISTS (SELECT 1 FROM data WHERE hash = '%s')"

#INSERT_DST_EXE = 'insert into data (id, hash, sent, ack, ttl, time, ip, port, src, dst, type, data) SELECT %s, %s, %s, %s, %s,\
                #%s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM data WHERE data = %s)'

"""
MultiThread support for SQLite access
http://code.activestate.com/recipes/526618/
"""
class DTNDatabase(threading.Thread):

    def __init__(self, name = 'DTN'):
        threading.Thread.__init__(self)
        self.db_name = name

        self.reqs = Queue()

        #print os.path.abspath(name)
        if not os.path.exists(os.path.abspath(name)):
            self._create_db()
            #os.remove(os.path.abspath(name))

        #self._create_db()

        self.start()

    def close(self):
        self.execute('--close--')

    def run(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        while True:
            req, arg, res = self.reqs.get()
            if req=='--close--': break
            cursor.execute(req, arg)
            if res:
                for rec in cursor:
                    res.put(rec)
                res.put('--no more--')
            conn.commit()
        conn.close()

    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))

    def select(self, req, arg=None):
        res = Queue()
        self.execute(req, arg, res)
        while True:
            rec=res.get()
            if rec=='--no more--': break
            yield rec

    def close(self):
        self.execute('--close--')

    def _create_db(self):
        self.execute(CREATE_EXE)
    def insert_msg(self, m):
        self.execute(INSERT_EXE, tuple(list(m.to_tuple())+[m.hash]))
    def insert_dst_ack(self, m):
        self.execute(INSERT_DST_EXE, tuple(list(m.to_tuple())+[m.data]))
    def update(self, set, where):
        self.execute('update data set %s where %s' % (set, where))

    def select_msg(self, where):
        msgs = self.select('select hash, time, ip, port, src, dst, type, data, ttl from data where %s' % where)

        res = list()
        for msg in msgs:
            m = DTNMessage()
            m.hash = msg[0]
            m.time = msg[1]
            m.ip = msg[2]
            m.port = msg[3]
            m.src = msg[4]
            m.dst = msg[5]
            m.type = msg[6]
            m.data = msg[7]
            m.ttl = msg[8]

            res.append(m)
        return res


    #def _create_db(self):
        #conn = sqlite3.connect(self.db_name, check_same_thread = False)
        #c = conn.cursor()
        #c.executescript(CREATE_EXE) 
        #conn.commit()
        #conn.close()
    #def insert_msg(self, m):
        #""" Insert DTNMessage """

        ##conn = sqlite3.connect(self.db_name, timeout=10)
        #conn = sqlite3.connect(self.db_name, check_same_thread = False)
        #conn.execute(INSERT_EXE, tuple(list(m.to_tuple())+[m.hash]))
        #conn.commit()
        #conn.close()
    #def insert_dst_ack(self, m):
        #""" Insert DST_ACK """

        ##conn = sqlite3.connect(self.db_name, timeout=10)
        #conn = sqlite3.connect(self.db_name, check_same_thread = False)
        #conn.execute(INSERT_DST_EXE, tuple(list(m.to_tuple())+[m.data]))
        #conn.commit()
        #conn.close()

    #def select_msg(self, where):
        #""" Return a list of DTNMessage
        #"""
        ##conn = sqlite3.connect(self.db_name, timeout=10)
        #conn = sqlite3.connect(self.db_name, check_same_thread = False)
        #cur = conn.execute('select hash, time, ip, port, src, dst, type, data, ttl from data where %s' % where)
        #msgs = cur.fetchall()
        #res = list()
        #for msg in msgs:
            #m = DTNMessage()
            #m.hash = msg[0]
            #m.time = msg[1]
            #m.ip = msg[2]
            #m.port = msg[3]
            #m.src = msg[4]
            #m.dst = msg[5]
            #m.type = msg[6]
            #m.data = msg[7]
            #m.ttl = msg[8]

            #res.append(m)

        #conn.close()
        #return res

    #def execute_(self, s):
        #""" A function for handling common script
        #"""
        ##conn = sqlite3.connect(self.db_name, timeout=10)
        #conn = sqlite3.connect(self.db_name, check_same_thread = False)
        #cur = conn.execute(s)
        #msgs = cur.fetchall()
        #conn.commit()
        #conn.close()
        #return msgs

    #def update(self, set, where):
        #conn = sqlite3.connect(self.db_name, timeout=10)
        #cla = 'update data set %s where %s' % (set, where)
        #conn.execute(cla)
        #conn.commit()
        #conn.close()
        #return True

    # FOR TEST
    #def select_all(self, where=None):
        #if where is None:
            #cla = 'select * from data where sent = 0'
        #else:
            #cla = 'select * from data where sent = 0 where ' + where
        #msgs = self.execute(cla)
        #return msgs

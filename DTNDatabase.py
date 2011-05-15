#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 21 Mar 2011 01:53:27 PM CET'
__version__ = '0.3'

import os
import sqlite3
from DTNMessage import DTNMessage

CREATE_EXE = 'create table data (id integer primary key, hash text, sent integer, ack integer, ttl integer, time interger, ip text,\
                port text, src text, dst text, type text, data text);'
INSERT_EXE = 'insert into data (id, hash, sent, ack, ttl, time, ip, port, src, dst, type, data) SELECT ?, ?, ?, ?, ?,\
                ?, ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM data WHERE hash = ?);'


class DTNDatabase():

    def __init__(self, name = 'DTN'):
        self.db_name = name

        #print os.path.abspath(name)
        if not os.path.exists(os.path.abspath(name)):
            self._create_db()
            #os.remove(os.path.abspath(name))

        #self._create_db()

    def _create_db(self):
        conn = sqlite3.connect(self.db_name, check_same_thread = False)
        c = conn.cursor()
        c.executescript(CREATE_EXE) 

    def insert_msg(self, m):
        """ Insert DTNMessage """

        conn = sqlite3.connect(self.db_name)
        conn.execute(INSERT_EXE, tuple(list(m.to_tuple())+[m.hash]))
        conn.commit()
        conn.close()

    def select_msg(self, where):
        """ Return a list of DTNMessage
        """
        conn = sqlite3.connect(self.db_name)
        cur = conn.execute('select hash, time, ip, port, src, dst, type, data, ttl from data where {0}'.format(where))
        msgs = cur.fetchall()
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

        conn.close()
        return res

    def execute(self, s):
        """ A function for handling common script
        """
        conn = sqlite3.connect(self.db_name)
        cur = conn.execute(s)
        msgs = cur.fetchall()
        conn.commit()
        conn.close()
        return msgs

    def update(self, set, where):
        conn = sqlite3.connect(self.db_name)
        cla = 'update data set {0} where {1}'.format(set, where)
        conn.execute(cla)
        conn.commit()
        conn.close()
        return True

    # FOR TEST
    def select_all(self, where=None):
        if where is None:
            cla = 'select * from data where sent = 0'
        else:
            cla = 'select * from data where sent = 0 where ' + where
        msgs = self.execute(cla)
        return msgs

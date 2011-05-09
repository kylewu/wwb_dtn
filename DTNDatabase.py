#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             DTNDatabase.py
    Create Date:      Mon 21 Mar 2011 01:53:27 PM CET

'''
import os
import sqlite3
import hashlib

class DTNDatabase():

    def __init__(self, name = 'DTN'):
        self.db_name = name

        #print os.path.abspath(name)
        if not os.path.exists(os.path.abspath(name)):
            self._create_db()
            #os.remove(os.path.abspath(name))

        #self._create_db()

    def _create_db(self):
        """ RECV
            data is received if sent == -1
            SEND
            data is sent but no ack    if sent == 1 and ack == 0
            data is sent and ack       if sent == 1 and ack == 1
            data is not sent if sent == 0
            """
            
        conn = sqlite3.connect(self.db_name, check_same_thread = False)
        c = conn.cursor()
        c.executescript('''
            create table data (id integer primary key, hash text, sent integer, ack integer, time text, ip text, port
            text, src text, dst text, type text, data text);
            ''')

    def insert_tuple(self, t):
        conn = sqlite3.connect(self.db_name)
        conn.execute('insert into data values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', t)
        conn.commit()
        conn.close()

    def update(self, set, where):
        conn = sqlite3.connect(self.db_name)
        cla = 'update data set {0} where {1}'.format(set, where)
        conn.execute(cla)
        conn.commit()
        conn.close()
        return True

    def update_ack(self, h):
        conn = sqlite3.connect(self.db_name)
        t = (h,)
        conn.execute('update data set ack=1 where hash = ?', t)
        conn.commit()
        conn.close()

    def select_all(self, where=None):
        if where is None:
            cla = 'select hash, time, ip, port, src, dst, type, data from data where sent = 0'
        else:
            cla = 'select hash, time, ip, port, src, dst, type, data from data where sent = 0 where ' + where
        msgs = self.execute(cla)
        return msgs

    def select_type(self, m):
        conn = sqlite3.connect(self.db_name)
        t = (m,)
        cur = conn.execute('select hash, time, ip, port, src, dst, type, data from data where type=? and sent = -1', t)
        msgs = cur.fetchall()
        conn.close()
        return msgs


    def execute(self, s):
        conn = sqlite3.connect(self.db_name)
        cur = conn.execute(s)
        msgs = cur.fetchall()
        conn.commit()
        conn.close()
        return msgs

    def hash(self, msg):
        m = hashlib.md5()
        m.update(msg)
        return m.digest().encode('hex')

if __name__ == '__main__':
    ##### FIXME #####
    ##### OLD TEST #####
    db = DTNDatabase('test')
    data = '2cc2f40e95db75de9d403449f9833e43 1300803228892 130.238.8.154 7000 PING 001E8C6C9172 {position=>wgs84,17.647102456850032,59.83816340033785,62.99983961507678;platform=>ASUS WL-500GP;type=>sensorhost;}'
    #data = '1299676566479 130.238.8.154:7000 PING 001E8C6C9172 {position=>wgs84,17.647102456850032,59.83816340033785,62.99983961507678;platform=>ASUSWL-500GP;type=>sensorhost;}'
    db.insert(data)
    db.update_ack('2cc2f40e95db75de9d403449f9833e43')

    for msg in db.select_all():
        print msg

    print db.execute("select * from data where sent = -1 and type='PING'")

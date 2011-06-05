#!/usr/bin/env python

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             TestDTNSiteManager.py
    Create Date:      Mon 21 Mar 2011 01:33:54 PM CET

'''

import unittest
import time

import DTNConnection
from FakeMasterSiteManager import MasterSiteManager
from DTNSiteManager import SiteManagerServer 
from DTNSiteManager import SiteManagerCarrier
from DTNSiteManager import SiteManagerClient

class DTNConnectionTestCase(unittest.TestCase):
    def setUp(self):
        pass

    #def test_client(self):
        #sm = MasterSiteManager('127.0.0.1', 4005)
        #client = SiteManagerClient(4001, 4445, 4002, 4003, 4004, '127.0.0.1', 4005, '130.238.8.164')
        #sm.start()
        #client.start()
        
        #time.sleep(5)
        #client.stop()
        #sm.stop()

        #for m in [msg for msg in client.db.select_all()]:
            #print m

    def test_server(self):
        client = SiteManagerClient(4001, 4445, 4002, 4003, 5555, '130.238.8.164', 4005, '130.238.8.164')
        client.start()

        #carrier = SiteManagerCarrier()
        #carrier.start()

        time.sleep(5)

        server = SiteManagerServer(4006, 4005, 4000, '130.238.8.164')
        server.start()

        time.sleep(5)
        server.quit()

        time.sleep(5)

        print 'ressssssssssssss'
        server = SiteManagerServer(4006, 4005, 4000, '130.238.8.164')
        server.start()

        time.sleep(5)

        print 'client'
        for m in [msg for msg in client.db.select_all()]:
            print m

        print 'server'
        for m in [msg for msg in server.db.select_all()]:
            print m

        server.stop()
        client.stop()
if __name__ == '__main__':
    unittest.main()


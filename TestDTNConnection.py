#!/usr/bin/env python

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             TestDTNConnection.py
    Create Date:      Mon 21 Mar 2011 09:18:20 AM CET

'''

import unittest
import time

import DTNConnection
from FakeMasterSiteManager import MasterSiteManager

class DTNConnectionTestCase(unittest.TestCase):
    def setUp(self):
        self.msm = MasterSiteManager('127.0.0.1', 5678)
        self.msm.start()

    def test_client(self):
        client = DTNConnection.DTNClient('127.0.0.1', 5678, sm = self.msm, ip = None)

        try:
            client.start()

            time.sleep(5)

            client.stop()
            self.msm.stop()
        except:
            client.stop()
            self.msm.stop()


if __name__ == '__main__':
    unittest.main()


__author__ = 'wenbin'

import unittest
import DTN
import FakeVClient

class DTNClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = DTN.DTNClient("127.0.0.1", 7000) # server_ip, server_port
        self.client.start()

    def test_send(self):

        self.client.send("Test Message")
        self.assertEqual(self.client.mq.empty(), False)


#class DTConnnectionManagerTestCase(unittest.TestCase):
#    def setUp(self):
#        self.cm = DTN.DTConnectionManager("127.0.0.1")
#
#    def test_add(self):
#        self.cm.add("sh", ["S1", "S2"], 7777)
#        self.assertEqual("sh", self.cm.getDTConnBySHName("sh").getSHName())
#
#    def test_send(self):
#        self.cm.add("sh", ["S1", "S2"], 8888)
#        self.assertEqual(True, self.cm.getDTConnBySHName("sh").mq.empty())
#        self.cm.send("HelloWorld")
#        self.assertEqual(False, self.cm.getDTConnBySHName("sh").mq.empty())

if __name__ == '__main__':
    unittest.main()

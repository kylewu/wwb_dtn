__author__ = 'wenbin'

import unittest
import Carrier
import SiteManager

class MyTestCase(unittest.TestCase):
    def test_something(self):
        c = Carrier.Carrier()
        c.start()

        a = SiteManager.SiteManagerClient(4444, 4445, 4442, 4440, "130.238.8.164", 8000, "130.238.8.164")
        a.start()

if __name__ == '__main__':
    unittest.main()

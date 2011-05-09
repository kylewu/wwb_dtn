#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             client.py
    Create Date:      Wed 23 Mar 2011 12:04:17 PM CET

'''

import time
from DTNSiteManager import SiteManagerClient

ip = '130.238.8.164'
client = SiteManagerClient(4000, 4445, 4003, 5555, ip, 4005, '130.238.8.164')
client.start()

#time.sleep(10)

#client.stop()
#client.join()
#client.clean()

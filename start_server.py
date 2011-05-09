#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Mon 09 May 2011 09:59:04 AM CEST'
__version__ = '0.1'

from newDTNSiteManager import SiteManager

sm = SiteManager('SERVER_SM')
sm.start()

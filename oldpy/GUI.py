#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Wenbin Wu <admin@wenbinwu.com>'
__credits__ = 'Python best'
__date__    = 'Thu 31 Mar 2011 03:41:15 PM CEST'
__version__ = '0.1'

#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx

from DTNSiteManager import MobileSiteManager

class Example(wx.Frame):
  
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(390, 350))
            
        self.InitUI()
        self.Centre()
        self.Show()     

        self.mobile = MobileSiteManager(ip = '130.243.144.12')
        
    def InitUI(self):
    
        panel = wx.Panel(self)

        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='IP ADDR')
        st1.SetFont(font)
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc1 = wx.TextCtrl(panel)
        hbox1.Add(self.tc1, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='PORT    ')
        st2.SetFont(font)
        hbox2.Add(st2, flag=wx.RIGHT, border=8)
        self.tc2 = wx.TextCtrl(panel)
        hbox2.Add(self.tc2, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st3 = wx.StaticText(panel, label='LOCAL  ')
        st3.SetFont(font)
        hbox3.Add(st3, flag=wx.RIGHT, border=8)
        self.tc3 = wx.TextCtrl(panel)
        hbox3.Add(self.tc3, proportion=1)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        st4 = wx.StaticText(panel, label='Info')
        st4.SetFont(font)
        hbox4.Add(st4)
        vbox.Add(hbox4, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc4 = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        hbox5.Add(self.tc4, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox5, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, 
            border=10)

        vbox.Add((-1, 25))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn1 = wx.Button(panel, label='Bcast', size=(70, 30))
        self.btn1.Bind(wx.EVT_BUTTON, self.btn1Click)
        hbox6.Add(self.btn1)
        self.btn2 = wx.Button(panel, label='Start', size=(70, 30))
        self.btn2.Bind(wx.EVT_BUTTON, self.btn2Click)
        hbox6.Add(self.btn2, flag=wx.LEFT|wx.BOTTOM, border=5)
        vbox.Add(hbox6, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)

        panel.SetSizer(vbox)

    def btn1Click(self, evt):
        self.btn1.Disable()
        res = self.mobile.bcast(16666)
        if res is not None:
            self.tc1.SetValue(res[0])
            self.tc2.SetValue(res[1])
            self.tc4.AppendText('Get reply\n')
        self.btn1.Enable()

    def btn2Click(self, evt):
        print self.tc4.GetValue()
        if self.btn2.LabelText == 'Start':
            self.tc4.AppendText('Start to work\n')
            #if not self.mobile.connect_to_server():
                #return
            self.tc4.AppendText('Successed in connecting to server, act as %s\n' % self.carrier.mode)
            self.btn2.SetLabel('Stop')
            #self.carrier.start()
        elif self.btn2.LabelText == 'Stop':
            self.tc4.AppendText('Stop\n')
            #self.carrier.stop()
            self.btn2.SetLabel('Start')

if __name__ == '__main__':
  
    app = wx.App()
    Example(None, title='I am a great mobile device :)')
    app.MainLoop()

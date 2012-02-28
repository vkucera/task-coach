'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx
import test
from taskcoachlib import gui, config, operating_system


class WindowTest(test.wxTestCase):
    def setUp(self):
        super(WindowTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.settings.setvalue('window', 'position', (50, 50))
        self.tracker = gui.windowdimensionstracker.WindowDimensionsTracker(self.frame, self.settings)
        self.section = 'window'
        
    def testInitialPosition(self):
        self.assertEqual(self.settings.getvalue(self.section, 'position'), 
                         self.frame.GetPositionTuple())
         
    def testInitialSize(self):
        # See MainWindowTest...
        w, h = self.frame.GetSizeTuple()
        if operating_system.isMac():
            h += 40 # pragma: no cover
        self.assertEqual((w, h), self.settings.getvalue(self.section, 'size'))
     
    def testMaximize(self):
        for maximized in [True, False]:
            self.frame.Maximize(maximized)
            self.assertEqual(maximized, self.frame.IsMaximized())
            self.assertEqual(maximized, self.settings.getboolean(self.section, 'maximized'))
            
    def testChangeSize(self):
        self.frame.Maximize(False)
        self.frame.ProcessEvent(wx.SizeEvent((123, 200)))
        self.assertEqual((123, 200), self.settings.getvalue(self.section, 'size'))
        
    def testMove(self):
        self.frame.Maximize(False)
        self.frame.Iconize(False)
        self.frame.ProcessEvent(wx.MoveEvent((200, 200)))
        self.assertEqual((200, 200), self.settings.getvalue(self.section, 'position'))


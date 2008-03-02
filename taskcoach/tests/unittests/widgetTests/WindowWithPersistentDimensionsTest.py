'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import test, gui, config, wx

class WindowWithPersistentDimensions(gui.mainwindow.WindowWithPersistentDimensions):
    def __init__(self, settings, shown=True):
        self._shown = shown
        super(WindowWithPersistentDimensions, self).__init__(settings)
        
    def IsShown(self):
        return self._shown
        
        
class WindowTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.settings.set('window', 'position', '(100, 100)')
        self.window = WindowWithPersistentDimensions(self.settings)
        self.section = self.window._section
        
    def testInitialPosition(self):
        self.assertEqual(eval(self.settings.get(self.section, 'position')), 
            self.window.GetPositionTuple())
         
    def testInitialSize(self):
        self.assertEqual(eval(self.settings.get(self.section, 'size')),
            self.window.GetSizeTuple())
     
    def testInitialIconizeState(self):
        self.assertEqual(self.settings.getboolean(self.section, 'iconized'),
            self.window.IsIconized())
            
    def testChangeSize(self):
        self.window.ProcessEvent(wx.SizeEvent((100, 100)))
        self.assertEqual((100, 100), 
            eval(self.settings.get(self.section, 'size')))
        
    def testMove(self):
        self.window.ProcessEvent(wx.MoveEvent((100, 100)))
        #The move is not processed, dunno why:
        self.assertEqual((100, 100), eval(self.settings.get(self.section, 'position')))


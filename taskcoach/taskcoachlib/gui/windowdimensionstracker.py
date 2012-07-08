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
from taskcoachlib import operating_system


class Tracker(object):
    def __init__(self, settings, section):
        super(Tracker, self).__init__()
        self.__settings = settings
        self.__section = section
               
    def setSetting(self, setting, value):
        self.__settings.setvalue(self.__section, setting, value)
        
    def getSetting(self, setting):
        return self.__settings.getvalue(self.__section, setting)
        

class WindowSizeAndPositionTracker(Tracker):
    ''' Track the size and position of a window in the settings. '''

    def __init__(self, window, settings, section):
        super(WindowSizeAndPositionTracker, self).__init__(settings, section)
        self._window = window
        self.setDimensions()
        self._window.Bind(wx.EVT_SIZE, self.onChangeSize)
        self._window.Bind(wx.EVT_MOVE, self.onChangePosition)
        self._window.Bind(wx.EVT_MAXIMIZE, self.onMaximize)

    def onChangeSize(self, event):
        # Ignore the EVT_SIZE when the window is maximized or iconized. 
        # Note how this depends on the EVT_MAXIMIZE being sent before the 
        # EVT_SIZE.
        maximized = self._window.IsMaximized()
        if not maximized and not self._window.IsIconized():
            self.setSetting('size', self._window.GetClientSize() \
                            if operating_system.isMac() else event.GetSize())
        # Jerome, 2008/07/12: On my system (KDE 3.5.7), EVT_MAXIMIZE
        # is not triggered, so set 'maximized' to True here as well as in 
        # onMaximize:
        self.setSetting('maximized', maximized)
        event.Skip()

    def onChangePosition(self, event):
        if not self._window.IsMaximized():
            self.setSetting('maximized', False)
            if not self._window.IsIconized():
                # Only save position when the window is not maximized 
                # *and* not minimized
                self.setSetting('position', event.GetPosition())
        event.Skip()

    def onMaximize(self, event):
        self.setSetting('maximized', True)
        event.Skip()

    def setDimensions(self):
        width, height = self.getSetting('size')
        if operating_system.isMac():
            # Under MacOS 10.5 and 10.4, when setting the size, the actual window height
            # is increased by 40 pixels. Dunno why, but it's highly annoying. This doesn't
            # hold for dialogs though. Sigh.
            if not isinstance(self._window, wx.Dialog):
                height += 18
        x, y = self.getSetting('position')
        self._window.SetDimensions(x, y, width, height)
        if operating_system.isMac():
            self._window.SetClientSize((width, height))
        if self.getSetting('maximized'):
            self._window.Maximize()
        # Check that the window is on a valid display and move if necessary:
        if wx.Display.GetFromWindow(self._window) == wx.NOT_FOUND:
            self._window.SetDimensions(0, 0, width, height)
            if operating_system.isMac():
                self._window.SetClientSize((width, height))

                
class WindowDimensionsTracker(WindowSizeAndPositionTracker):
    ''' Track the dimensions of a window in the settings. '''
    
    def __init__(self, window, settings):
        super(WindowDimensionsTracker, self).__init__(window, settings, 'window')
        self.__settings = settings
        if self.startIconized():
            if operating_system.isMac() or operating_system.isGTK():
                # Need to show the window on Mac OS X first, otherwise it   
                # won't be properly minimized. On wxGTK we need to show the
                # window first, otherwise clicking the task bar icon won't
                # show it.
                self._window.Show()
            self._window.Iconize(True)
            if not operating_system.isMac() and self.getSetting('hidewheniconized'):
                # Seems like hiding the window after it's been
                # iconized actually closes it on Mac OS...
                wx.CallAfter(self._window.Hide)                

    def startIconized(self):
        startIconized = self.__settings.get('window', 'starticonized')
        if startIconized == 'Always':
            return True
        if startIconized == 'Never':
            return False
        return self.getSetting('iconized')
     
    def savePosition(self):
        iconized = self._window.IsIconized()
        self.setSetting('iconized', iconized)
        if not iconized:
            self.setSetting('position', self._window.GetPosition())
                            
    

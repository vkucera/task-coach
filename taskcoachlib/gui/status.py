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

import wx
from taskcoachlib import patterns
from taskcoachlib.i18n import _


class StatusBar(wx.StatusBar):
    def __init__(self, parent, viewer):
        super(StatusBar, self).__init__(parent, -1)
        self.SetFieldsCount(2)
        self.parent = parent
        self.viewer = viewer
        patterns.Publisher().registerObserver(self.onSelect, 
            eventType=viewer.selectEventType(), eventSource=viewer)
        patterns.Publisher().registerObserver(self.onSelect, 
            eventType=viewer.viewerChangeEventType(), eventSource=viewer)
        self.scheduledStatusDisplay = None
        self.onSelect(None)
        parent.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, self.resetStatusBar)
        parent.Bind(wx.EVT_TOOL_ENTER, self.resetStatusBar)

    def resetStatusBar(self, event):
        ''' Unfortunately, the menu's and toolbar don't restore the
            previous statusbar text after they have displayed their help
            text, so we have to do it by hand. '''
        try:
            id = event.GetSelection() # for CommandEvent from the Toolbar
        except AttributeError:
            id = event.GetMenuId() # for MenuEvent
        if id == -1:
            self._displayStatus()
        event.Skip()

    def onSelect(self, *args, **kwargs):
        # Give viewer a chance to update first:
        wx.CallAfter(self._displayStatus)

    def _displayStatus(self):
        status1, status2 = self.viewer.statusMessages()
        super(StatusBar, self).SetStatusText(status1, 0)
        super(StatusBar, self).SetStatusText(status2, 1)

    def SetStatusText(self, message, pane=0, delay=3000):
        if self.scheduledStatusDisplay:
            self.scheduledStatusDisplay.Stop()
        super(StatusBar, self).SetStatusText(message, pane)
        self.scheduledStatusDisplay = wx.FutureCall(delay, self._displayStatus)

    def Destroy(self):
        patterns.Publisher().removeObserver(self.onSelect, 
            eventType=self.viewer.selectEventType())
        patterns.Publisher().removeObserver(self.onSelect, 
            eventType=self.viewer.viewerChangeEventType())
        self.parent.Unbind(wx.EVT_MENU_HIGHLIGHT_ALL)
        self.parent.Unbind(wx.EVT_TOOL_ENTER)
        if self.scheduledStatusDisplay:
            self.scheduledStatusDisplay.Stop()
        super(StatusBar, self).Destroy()


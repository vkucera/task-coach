'''
Task Coach - Your friendly task manager
Copyright (C) 2009 Frank Niessink <frank@niessink.com>

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
from taskcoachlib.thirdparty.timeline import timeline


class Timeline(timeline.TimeLine):
    def __init__(self, parent, rootNode, onSelect, onEdit):
        self.__selection = []
        super(Timeline, self).__init__(parent, model=rootNode, adapter=parent)
        self.selectCommand = onSelect
        self.Bind(timeline.EVT_TIMELINE_SELECTED, self.onSelect)
        self.editCommand = onEdit
        self.Bind(timeline.EVT_TIMELINE_ACTIVATED, self.onEdit)
        
    def refresh(self, count):
        self.Refresh()
        
    def RefreshItem(self, *args):
        self.Refresh()
        
    def onSelect(self, event):
        if event.node == self.model:
            self.__selection = []
        else:
            self.__selection = [event.node]
        wx.CallAfter(self.selectCommand)
        event.Skip()
        
    def select(self, index):
        pass
    
    def onEdit(self, event):
        self.editCommand(event.node)
        event.Skip()
        
    def onPopup(self, event):
        self.OnClickRelease(event) # Make sure the node is selected
        self.SetFocus()
        self.PopupMenu(self.popupMenu)
    
    def curselection(self):
        return self.__selection

    def GetItemCount(self):
        return 0

    def isAnyItemExpandable(self):
        return False

    isSelectionExpandable = isSelectionCollapsable = isAnyItemCollapsable =\
        isAnyItemExpandable

    def GetMainWindow(self):
        return self
    
    MainWindow = property(GetMainWindow)

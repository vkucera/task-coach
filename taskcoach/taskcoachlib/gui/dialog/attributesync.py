'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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


class AttributeSync(object):
    ''' Class used for keeping an attribute of a domain object synchronized with
        a control in a dialog. If the user edits the value using the control, 
        the domain object is changed, using the appropriate command. If the 
        attribute of the domain object is changed (e.g. in another dialog) the 
        value of the control is updated. '''
        
    def __init__(self, attributeName, entry, currentValue, items, commandClass, 
                 editedEventType, changedEventType):
        self._attributeName = attributeName
        self._entry = entry
        self._currentValue = currentValue
        self._items = items
        self._commandClass = commandClass
        entry.Bind(editedEventType, self.onAttributeEdited)
        if wx.Platform == '__WXMAC__':
            # On Mac OS X, the focused control does not receive
            # EVT_KILL_FOCUS when the containing window is closed.
            entry.TopLevelParent.Bind(wx.EVT_CLOSE, self.onAttributeEdited)
        if len(items) == 1:
            patterns.Publisher().registerObserver(self.onAttributeChanged,
                                                  eventType=changedEventType,
                                                  eventSource=items[0])
        
    def onAttributeEdited(self, event):
        event.Skip()
        newValue = self.getValue()
        if newValue != self._currentValue:
            self._currentValue = newValue
            commandKwArgs = self.commandKwArgs(newValue)
            self._commandClass(None, self._items, **commandKwArgs).do()
            
    def onAttributeChanged(self, event):
        newValue = event.value()
        if newValue != self._currentValue:
            self._currentValue = newValue
            self.setValue(newValue)

    def commandKwArgs(self, newValue):
        return {self._attributeName: newValue}
    
    def setValue(self, newValue):
        self._entry.SetValue(newValue)

    def getValue(self):
        return self._entry.GetValue()     


class FontColorSync(AttributeSync):
    def setValue(self, newValue):
        self._entry.SetColor(newValue)

    def getValue(self):
        return self._entry.GetColor()

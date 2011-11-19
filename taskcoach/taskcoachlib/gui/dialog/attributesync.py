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

from taskcoachlib import patterns


class AttributeSync(object):
    ''' Class used for keeping an attribute of a domain object synchronized with
        a control in a dialog. If the user edits the value using the control, 
        the domain object is changed, using the appropriate command. If the 
        attribute of the domain object is changed (e.g. in another dialog) the 
        value of the control is updated. '''
        
    def __init__(self, attributeName, entry, currentValue, items, commandClass, 
                 editedEventType, changedEventType, getter=None, **kwargs):
        self._attributeName = attributeName
        self._getter = getter or attributeName
        self._entry = entry
        self._currentValue = currentValue
        self._items = items
        self._commandClass = commandClass
        self.__commandKwArgs = kwargs
        entry.Bind(editedEventType, self.onAttributeEdited)
        if len(items) == 1:
            self.startObservingAttribute(changedEventType, items[0])
        
    def onAttributeEdited(self, event):
        event.Skip()
        newValue = self.getValue()
        if newValue != self._currentValue:
            self._currentValue = newValue
            commandKwArgs = self.commandKwArgs(newValue)
            self._commandClass(None, self._items, **commandKwArgs).do() # pylint: disable-msg=W0142
            
    def onAttributeChanged(self, event):
        if self._entry: 
            newValue = getattr(self._items[0], self._getter)()
            if newValue != self._currentValue:
                self._currentValue = newValue
                self.setValue(newValue)
        else:
            self.stopObservingAttribute()
            
    def commandKwArgs(self, newValue):
        self.__commandKwArgs[self._attributeName] = newValue
        return self.__commandKwArgs
    
    def setValue(self, newValue):
        self._entry.SetValue(newValue)
            
    def getValue(self):
        return self._entry.GetValue()
    
    def startObservingAttribute(self, eventType, eventSource):
        patterns.Publisher().registerObserver(self.onAttributeChanged,
                                                  eventType=eventType,
                                                  eventSource=eventSource)
    
    def stopObservingAttribute(self):
        patterns.Publisher().removeObserver(self.onAttributeChanged)


class FontColorSync(AttributeSync):
    def setValue(self, newValue):
        self._entry.SetColor(newValue)

    def getValue(self):
        return self._entry.GetColor()

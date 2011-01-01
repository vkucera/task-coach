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
from taskcoachlib.gui import artprovider


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
        if wx.Platform in ('__WXMAC__', '__WXGTK__'):
            # On some platforms, the focused control does not receive
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
    
    def getValue(self):
        return self.getValueFromEntry()
     
    def getValueFromEntry(self):
        return self._entry.GetValue()
    
    def setValue(self, newValue):
        self.setValueToEntry(newValue)
        
    def setValueToEntry(self, newValue):
        self._entry.SetValue(newValue)
            
            
class IconSync(AttributeSync):
    def commandKwArgs(self, newIcon):
        commandKwArgs = super(IconSync, self).commandKwArgs(newIcon)
        selectedIcon = newIcon[:-len('_icon')] + '_open_icon' \
            if (newIcon.startswith('folder') and newIcon.count('_') == 2) \
            else newIcon
        commandKwArgs['selectedIcon'] = selectedIcon
        return commandKwArgs
    
    def setValueToEntry(self, newIcon):
        imageNames = sorted(artprovider.chooseableItemImages.keys())
        self._entry.SetSelection(imageNames.index(newIcon))
        
    def getValueFromEntry(self):
        return self._entry.GetClientData(self._entry.GetSelection())


class OptionalAttributeSync(AttributeSync):
    ''' For attributes that can have no value, in which case a default value
        is shown in the control. The control has an accompanying checkbox that 
        indicates whether the value of the control is actually used. '''

    def __init__(self, *args, **kwargs):
        self._defaultValue = kwargs.pop('defaultValue')
        self._defaultCheckbox = kwargs.pop('defaultCheckbox')
        super(OptionalAttributeSync, self).__init__(*args, **kwargs)
        self._defaultCheckbox.Bind(wx.EVT_CHECKBOX, self.onAttributeChecked)

    def onAttributeChecked(self, event):
        super(OptionalAttributeSync, self).onAttributeEdited(event)

    def onAttributeEdited(self, event):
        self._defaultCheckbox.SetValue(True)
        super(OptionalAttributeSync, self).onAttributeEdited(event)

    def setValue(self, newValue):
        checked = newValue is not None
        self._defaultCheckbox.SetValue(checked)
        if checked:
            self.setValueToEntry(newValue)

    def getValue(self):
        return self.getValueFromEntry() if self._defaultCheckbox.IsChecked() \
            else None
        

class FontSync(OptionalAttributeSync):        
    def setValueToEntry(self, newValue):
        self._entry.SetSelectedFont(newValue)
        
    def getValueFromEntry(self):
        return self._entry.GetSelectedFont()
            
            
class FontColorSync(AttributeSync):
    def setValueToEntry(self, newValue):
        self._entry.SetSelectedColour(newValue)

    def getValueFromEntry(self):
        return self._entry.GetSelectedColour()
    
    
class ColorSync(OptionalAttributeSync):
    def setValueToEntry(self, newValue):
        self._entry.SetColour(newValue)
        
    def getValueFromEntry(self):
        return self._entry.GetColour()
    
    
class ChoiceSync(AttributeSync):
    def setValueToEntry(self, newValue):        
        for index in range(self._entry.GetCount()):
            if newValue == self._entry.GetClientData(index):
                self._entry.SetSelection(index)
                break
        
    def getValueFromEntry(self):
        return self._entry.GetClientData(self._entry.GetSelection())

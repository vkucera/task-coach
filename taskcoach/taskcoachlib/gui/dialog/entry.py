'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Carl Zmola <zmola@acm.org>

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

import wx, locale
from wx.lib import masked, newevent
from taskcoachlib import widgets
from taskcoachlib.domain import date
from taskcoachlib.thirdparty import combotreebox
 
 
DateTimeEntryEvent, EVT_DATETIMEENTRY = newevent.NewEvent()


class DateTimeEntry(widgets.PanelWithBoxSizer):
    defaultDateTime = date.DateTime()

    def __init__(self, parent, settings, initialDateTime=defaultDateTime, 
                 readonly=False, noneAllowed=True, showSeconds=False, 
                 *args, **kwargs):
        super(DateTimeEntry, self).__init__(parent, *args, **kwargs)
        starthour = settings.getint('view', 'efforthourstart')
        endhour = settings.getint('view', 'efforthourend')
        interval = settings.getint('view', 'effortminuteinterval')
        self._entry = widgets.DateTimeCtrl(self, noneAllowed=noneAllowed, 
                                           starthour=starthour, endhour=endhour, 
                                           interval=interval, 
                                           showSeconds=showSeconds)
        if readonly:
            self._entry.Disable()
        # First set the initial value and then set the callback so that the
        # callback is not triggered for the initial value
        self._entry.SetValue(initialDateTime)
        self._entry.setCallback(self.onDateTimeCtrlEdited)        
        self.add(self._entry)
        self.fit()

    def GetValue(self):
        return self._entry.GetValue()

    def SetValue(self, newValue=defaultDateTime):
        self._entry.SetValue(newValue)
        
    def onDateTimeCtrlEdited(self, *args, **kwargs):
        wx.PostEvent(self, DateTimeEntryEvent())            


class TimeDeltaEntry(widgets.PanelWithBoxSizer):
    defaultTimeDelta = date.TimeDelta()

    def __init__(self, parent, timeDelta=defaultTimeDelta, readonly=False, 
                 *args, **kwargs):
        super(TimeDeltaEntry, self).__init__(parent, *args, **kwargs)
        hours, minutes, seconds = timeDelta.hoursMinutesSeconds()
        if timeDelta < self.defaultTimeDelta:
            hours = -hours
        mask = 'X{8}:XX:XX' if readonly else '#{8}:##:##' # X is needed to allow for negative values 
        self._entry = widgets.masked.TextCtrl(self, mask=mask,
            formatcodes='FS',
            fields=[masked.Field(formatcodes='r', defaultValue='%8d'%hours),
                    masked.Field(defaultValue='%02d'%minutes),
                    masked.Field(defaultValue='%02d'%seconds)])
        if readonly:
            self._entry.Disable()
        self.add(self._entry, flag=wx.EXPAND|wx.ALL, proportion=1)
        self.fit()

    def GetValue(self):
        return date.parseTimeDelta(self._entry.GetValue())
    
    def SetValue(self, newTimeDelta):
        hours, minutes, seconds = newTimeDelta.hoursMinutesSeconds()
        if newTimeDelta < self.defaultTimeDelta:
            hours = -hours
        try:
            self._entry.SetValue('%8d:%02d:%02d'%(hours, minutes, seconds))
        except ValueError:            
            self._entry.SetValue('%8d:%02d:%02d'%(0, 0, 0))
            
    def Bind(self, *args, **kwargs): # pylint: disable-msg=W0221
        self._entry.Bind(*args, **kwargs)


class AmountEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, amount=0.0, readonly=False, *args, **kwargs):
        self.local_conventions = kwargs.pop('localeconv', locale.localeconv())
        super(AmountEntry, self).__init__(parent, *args, **kwargs)
        self._entry = self.createEntry(amount)
        if readonly:
            self._entry.Disable()
        self.add(self._entry)
        self.fit()

    def createEntry(self, amount):
        decimalChar = self.local_conventions['decimal_point'] or '.'
        groupChar = self.local_conventions['thousands_sep'] or ','
        groupDigits = len(self.local_conventions['grouping']) > 1
        # The thousands separator may come up as ISO-8859-1 character
        # 0xa0, which looks like a space but isn't ASCII, which
        # confuses NumCtrl... Play it safe and avoid any non-ASCII
        # character here, or groupChars that consist of multiple characters.
        if len(groupChar) > 1 or ord(groupChar) >= 128:
            groupChar = ' '
        # Prevent decimalChar and groupChar from being the same:
        if groupChar == decimalChar:
            groupChar = ' ' # Space is not allowed as decimal point
        return widgets.masked.NumCtrl(self, fractionWidth=2,
            decimalChar=decimalChar, groupChar=groupChar,
            groupDigits=groupDigits, 
            selectOnEntry=True, allowNegative=False, value=amount)
  
    def get(self):
        return self._entry.GetValue()

    def set(self, value):
        self._entry.SetValue(value)

    def Bind(self, *args, **kwargs): # pylint: disable-msg=W0221
        self._entry.Bind(*args, **kwargs)


PercentageEntryEvent, EVT_PERCENTAGEENTRY = newevent.NewEvent()
        
        
class PercentageEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, percentage=0, *args, **kwargs):
        kwargs['orientation'] = wx.HORIZONTAL
        super(PercentageEntry, self).__init__(parent, *args, **kwargs)
        self._slider = self._createSlider(percentage)
        self._entry = self._createSpinCtrl(percentage)
        self.add(self._slider, flag=wx.ALL, proportion=0)
        self.add(self._entry, flag=wx.ALL, proportion=0)
        self.fit()
        
    def _createSlider(self, percentage):
        slider = wx.Slider(self, value=percentage, style=wx.SL_AUTOTICKS,
                          minValue=0, maxValue=100, size=(150,-1))
        slider.SetTickFreq(25, 1)
        slider.Bind(wx.EVT_SCROLL, self.onSliderScroll)
        return slider
        
    def _createSpinCtrl(self, percentage):
        entry = widgets.SpinCtrl(self, value=str(percentage),
            initial=percentage, size=(50, -1), min=0, max=100)
        for eventType in wx.EVT_SPINCTRL, wx.EVT_KILL_FOCUS:
            entry.Bind(eventType, self.onSpin)
        return entry

    def GetValue(self):
        return self._entry.GetValue()

    def SetValue(self, value):
        self._entry.SetValue(value)
        self._slider.SetValue(value)
        
    def onSliderScroll(self, event): # pylint: disable-msg=W0613
        self.syncControl(self._entry, self._slider)
            
    def onSpin(self, event): # pylint: disable-msg=W0613
        self.syncControl(self._slider, self._entry)
            
    def syncControl(self, controlToWrite, controlToRead):
        value = controlToRead.GetValue()
        # Prevent potential endless loop by checking that we really need to set
        # the value:
        if controlToWrite.GetValue() != value:
            controlToWrite.SetValue(value)
        wx.PostEvent(self, PercentageEntryEvent())
        
    
class TaskComboTreeBox(wx.Panel):
    ''' A ComboTreeBox with tasks. This class does not inherit from the
        ComboTreeBox widget, because that widget is created using a
        factory function. '''

    def __init__(self, parent, rootTasks, selectedTask):
        ''' Initialize the ComboTreeBox, add the root tasks recursively and
            set the selection. '''
        super(TaskComboTreeBox, self).__init__(parent)
        self._createInterior()
        self._addTasks(rootTasks)
        self.SetSelection(selectedTask)

    def __getattr__(self, attr):
        ''' Delegate unknown attributes to the ComboTreeBox. This is needed
            since we cannot inherit from ComboTreeBox, but have to use
            delegation. '''
        return getattr(self._comboTreeBox, attr)

    def _createInterior(self):
        ''' Create the ComboTreebox widget. '''
        # pylint: disable-msg=W0201
        self._comboTreeBox = combotreebox.ComboTreeBox(self,
            style=wx.CB_READONLY|wx.CB_SORT|wx.TAB_TRAVERSAL)
        boxSizer = wx.BoxSizer()
        boxSizer.Add(self._comboTreeBox, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(boxSizer)
        
    def _addTasks(self, rootTasks):
        ''' Add the root tasks to the ComboTreeBox, including all their
            subtasks. '''
        for task in rootTasks:
            if not task.isDeleted():
                self._addTaskRecursively(task)

    def _addTaskRecursively(self, task, parentItem=None):
        ''' Add a task to the ComboTreeBox and then recursively add its
            subtasks. '''
        item = self._comboTreeBox.Append(task.subject(), parent=parentItem,
                                         clientData=task)
        for child in task.children():
            if not child.isDeleted():
                self._addTaskRecursively(child, item)

    def SetSelection(self, task):
        ''' Select the given task. '''
        self._comboTreeBox.SetClientDataSelection(task)

    def GetSelection(self):
        ''' Return the selected task. '''
        selection = self._comboTreeBox.GetSelection()
        return self._comboTreeBox.GetClientData(selection)


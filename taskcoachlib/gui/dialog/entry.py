'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
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
from wx.lib import masked, combotreebox
from taskcoachlib import widgets
from taskcoachlib.domain import date


class DateEntry(widgets.PanelWithBoxSizer):
    defaultDate = date.Date()

    def __init__(self, parent, date=defaultDate, readonly=False, callback=None,
                 *args, **kwargs):
        super(DateEntry, self).__init__(parent, *args, **kwargs)
        self._entry = widgets.DateCtrl(self, callback)
        if readonly:
            self._entry.Disable()
        self._entry.SetValue(date)
        self.add(self._entry)
        self.fit()

    def get(self, defaultDate=None):
        result = self._entry.GetValue()
        if result == date.Date() and defaultDate:
            result = defaultDate
        return result

    def set(self, date=defaultDate):
        self._entry.SetValue(date)

    def setToday(self):
        self._entry.SetValue(date.Today())


class TimeDeltaEntry(widgets.PanelWithBoxSizer):
    defaultTimeDelta=date.TimeDelta()

    def __init__(self, parent, timeDelta=defaultTimeDelta, readonly=False,
                 *args, **kwargs):
        super(TimeDeltaEntry, self).__init__(parent, *args, **kwargs)
        if readonly:
            self._entry = wx.StaticText(self, label=render.timeSpent(timeDelta))
        else:
            hours, minutes, seconds = timeDelta.hoursMinutesSeconds()
            self._entry = widgets.masked.TextCtrl(self, mask='#{6}:##:##',
                formatcodes='FS',
                fields=[masked.Field(formatcodes='r', defaultValue='%6d'%hours),
                        masked.Field(defaultValue='%02d'%minutes),
                        masked.Field(defaultValue='%02d'%seconds)])
        self.add(self._entry, flag=wx.EXPAND|wx.ALL, proportion=1)
        self.fit()

    def get(self):
        return date.parseTimeDelta(self._entry.GetValue())


class AmountEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, amount=0.0, readonly=False, *args, **kwargs):
        self.local_conventions = kwargs.pop('localeconv', locale.localeconv())
        super(AmountEntry, self).__init__(parent, *args, **kwargs)
        # Select factory for creating the entry:
        createEntry = self.createReadOnlyEntry if readonly else self.createEntry
        self._entry = createEntry(amount)
        self.add(self._entry)
        self.fit()

    def createReadOnlyEntry(self, amount):
        return wx.StaticText(self, label=render.monetaryAmount(amount))

    def createEntry(self, amount):
        decimalChar = self.local_conventions['decimal_point'] or '.'
        groupChar = self.local_conventions['thousands_sep'] or ','
        groupDigits = len(self.local_conventions['grouping']) > 1
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
        self._comboTreeBox = combotreebox.ComboTreeBox(self,
            style=wx.CB_READONLY|wx.CB_SORT|wx.TAB_TRAVERSAL)
        boxSizer = wx.BoxSizer()
        boxSizer.Add(self._comboTreeBox, flag=wx.EXPAND, proportion=1)
        self.SetSizerAndFit(boxSizer)

    def _addTasks(self, rootTasks):
        ''' Add the root tasks to the ComboTreeBox, including all their
            subtasks. '''
        for task in rootTasks:
            self._addTaskRecursively(task)

    def _addTaskRecursively(self, task, parentItem=None):
        ''' Add a task to the ComboTreeBox and then recursively add its
            subtasks. '''
        item = self._comboTreeBox.Append(task.subject(), parent=parentItem,
                                         clientData=task)
        for child in task.children():
            self._addTaskRecursively(child, item)

    def SetSelection(self, task):
        ''' Select the given task. '''
        self._comboTreeBox.SetClientDataSelection(task)

    def GetSelection(self):
        ''' Return the selected task. '''
        selection = self._comboTreeBox.GetSelection()
        return self._comboTreeBox.GetClientData(selection)


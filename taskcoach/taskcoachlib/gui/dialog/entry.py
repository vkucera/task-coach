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
from taskcoachlib.gui import artprovider
from taskcoachlib.domain import date
from taskcoachlib.thirdparty import combotreebox
from taskcoachlib.i18n import _

 
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
  
    def GetValue(self):
        return self._entry.GetValue()

    def SetValue(self, value):
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


FontEntryEvent, EVT_FONTENTRY = newevent.NewEvent()
        
class FontEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, currentFont, currentColor, *args, **kwargs):
        kwargs['orientation'] = wx.HORIZONTAL
        super(FontEntry, self).__init__(parent, *args, **kwargs)
        self._fontCheckBox = self._createCheckBox(currentFont)
        self._fontPicker = self._createFontPicker(currentFont, currentColor)
        self.add(self._fontCheckBox, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, proportion=0)
        self.add(self._fontPicker, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, proportion=1)
        self.fit()
        
    def _createCheckBox(self, currentFont):
        checkBox = wx.CheckBox(self, label=_('Use font:'))
        checkBox.SetValue(currentFont is not None)
        checkBox.Bind(wx.EVT_CHECKBOX, self.onChecked)
        return checkBox
    
    def _createFontPicker(self, currentFont, currentColor):
        defaultFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        picker = widgets.FontPickerCtrl(self,
            font=currentFont or defaultFont, colour=currentColor)
        picker.Bind(wx.EVT_FONTPICKER_CHANGED, self.onFontPicked)
        return picker
    
    def onChecked(self, event):
        event.Skip()
        wx.PostEvent(self, FontEntryEvent())
        
    def onFontPicked(self, event):
        event.Skip()
        self._fontCheckBox.SetValue(True)
        wx.PostEvent(self, FontEntryEvent())
    
    def GetValue(self):
        return self._fontPicker.GetSelectedFont() if self._fontCheckBox.IsChecked() \
            else None
            
    def SetValue(self, newFont):
        checked = newFont is not None
        self._fontCheckBox.SetValue(checked)
        if checked:
            self._fontPicker.SetSelectedFont(newFont)

    def GetColor(self):
        return self._fontPicker.GetSelectedColour()
            
    def SetColor(self, newColor):
        self._fontPicker.SetSelectedColour(newColor)


ColorEntryEvent, EVT_COLORENTRY = newevent.NewEvent()

class ColorEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, currentColor, defaultColor, *args, **kwargs):
        kwargs['orientation'] = wx.HORIZONTAL
        super(ColorEntry, self).__init__(parent, *args, **kwargs)
        self._colorCheckBox = self._createCheckBox(currentColor)
        self._colorPicker = self._createColorPicker(currentColor, defaultColor)
        self.add(self._colorCheckBox, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, proportion=0)
        self.add(self._colorPicker, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, proportion=1)
        self.fit()

    def _createCheckBox(self, currentColor):
        checkBox = wx.CheckBox(self, label=_('Use color:'))
        checkBox.SetValue(currentColor is not None)
        checkBox.Bind(wx.EVT_CHECKBOX, self.onChecked)
        return checkBox
    
    def _createColorPicker(self, currentColor, defaultColor):
        # wx.ColourPickerCtrl on Mac OS X expects a wx.Color and fails on tuples
        # so convert the tuples to a wx.Color:
        currentColor = wx.Color(*currentColor) if currentColor else defaultColor # pylint: disable-msg=W0142
        picker = wx.ColourPickerCtrl(self, col=currentColor)
        picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onColorPicked)
        return picker
    
    def onChecked(self, event):
        event.Skip()
        wx.PostEvent(self, ColorEntryEvent())
        
    def onColorPicked(self, event):
        event.Skip()
        self._colorCheckBox.SetValue(True)
        wx.PostEvent(self, ColorEntryEvent())

    def GetValue(self):
        return self._colorPicker.GetColour() if self._colorCheckBox.IsChecked() \
            else None
            
    def SetValue(self, newColor):
        checked = newColor is not None
        self._colorCheckBox.SetValue(checked)
        if checked:
            self._colorPicker.SetColour(newColor)


IconEntryEvent, EVT_ICONENTRY = newevent.NewEvent()

class IconEntry(wx.combo.BitmapComboBox):
    def __init__(self, parent, currentIcon, *args, **kwargs):
        kwargs['style'] = wx.CB_READONLY
        super(IconEntry, self).__init__(parent, *args, **kwargs)
        imageNames = sorted(artprovider.chooseableItemImages.keys())
        size = (16, 16)
        for imageName in imageNames:
            label = artprovider.chooseableItemImages[imageName]
            bitmap = wx.ArtProvider_GetBitmap(imageName, wx.ART_MENU, size)
            self.Append(label, bitmap, clientData=imageName)
        self.SetSelection(imageNames.index(currentIcon))
        self.Bind(wx.EVT_COMBOBOX, self.onIconPicked)
        
    def onIconPicked(self, event):
        event.Skip()
        wx.PostEvent(self, IconEntryEvent())

    def GetValue(self):
        return self.GetClientData(self.GetSelection())
    
    def SetValue(self, newValue):
        for index in range(self.GetCount()):
            if newValue == self.GetClientData(index):
                self.SetSelection(index)
                break


ChoiceEntryEvent, EVT_CHOICEENTRY = newevent.NewEvent()

class ChoiceEntry(wx.Choice):
    def __init__(self, parent, choices, currentChoiceValue, *args, **kwargs):
        super(ChoiceEntry, self).__init__(parent, *args, **kwargs)
        for choiceValue, choiceText in choices:
            self.Append(choiceText, choiceValue)
            if choiceValue == currentChoiceValue:
                self.SetSelection(self.GetCount()-1)
        if self.GetSelection() == wx.NOT_FOUND:
            # Force a selection if necessary:
            self.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.onChoice)

    def onChoice(self, event):
        event.Skip()
        wx.PostEvent(self, ChoiceEntryEvent())

    def GetValue(self):
        return self.GetClientData(self.GetSelection())

    def SetValue(self, newValue):
        for index in range(self.GetCount()):
            if newValue == self.GetClientData(index):
                self.SetSelection(index)
                break


TaskEntryEvent, EVT_TASKENTRY = newevent.NewEvent()

class TaskEntry(wx.Panel):
    ''' A ComboTreeBox with tasks. This class does not inherit from the
        ComboTreeBox widget, because that widget is created using a
        factory function. '''

    def __init__(self, parent, rootTasks, selectedTask):
        ''' Initialize the ComboTreeBox, add the root tasks recursively and
            set the selection. '''
        super(TaskEntry, self).__init__(parent)
        self._createInterior()
        self._addTasks(rootTasks)
        self.SetValue(selectedTask)

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
        self._comboTreeBox.Bind(wx.EVT_COMBOBOX, self.onTaskSelected)
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

    def onTaskSelected(self, event):
        wx.PostEvent(self, TaskEntryEvent())
        
    def SetValue(self, task):
        ''' Select the given task. '''
        self._comboTreeBox.SetClientDataSelection(task)

    def GetValue(self):
        ''' Return the selected task. '''
        selection = self._comboTreeBox.GetSelection()
        return self._comboTreeBox.GetClientData(selection)


RecurrenceEntryEvent, EVT_RECURRENCEENTRY = newevent.NewEvent()

class RecurrenceEntry(wx.Panel):
    horizontalSpace = (3, -1)
    verticalSpace = (-1, 3)

    def __init__(self, parent, recurrence, *args, **kwargs):
        super(RecurrenceEntry, self).__init__(parent, *args, **kwargs)
        recurrenceFrequencyPanel = wx.Panel(self)
        self._recurrencePeriodEntry = wx.Choice(recurrenceFrequencyPanel, 
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly'), _('Yearly')])        
        self._recurrencePeriodEntry.Bind(wx.EVT_CHOICE, self.onRecurrencePeriodEdited)
        self._recurrenceFrequencyEntry = widgets.SpinCtrl(recurrenceFrequencyPanel, 
                                                          size=(50,-1), 
                                                          initial=1, min=1)
        self._recurrenceFrequencyEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceEdited)
        self._recurrenceStaticText = wx.StaticText(recurrenceFrequencyPanel, 
                                                   label='reserve some space')
        self._recurrenceSameWeekdayCheckBox = wx.CheckBox(recurrenceFrequencyPanel, 
            label=_('keeping dates on the same weekday'))
        self._recurrenceSameWeekdayCheckBox.Bind(wx.EVT_CHECKBOX, self.onRecurrenceEdited)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(self._recurrencePeriodEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(wx.StaticText(recurrenceFrequencyPanel, label=_(', every')), 
                       flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(self._recurrenceFrequencyEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(self._recurrenceStaticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(self._recurrenceSameWeekdayCheckBox, proportion=1, 
                       flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        recurrenceFrequencyPanel.SetSizerAndFit(panelSizer)
        self._recurrenceSizer = panelSizer

        maxPanel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self._maxRecurrenceCheckBox = wx.CheckBox(maxPanel)
        self._maxRecurrenceCheckBox.Bind(wx.EVT_CHECKBOX, self.onMaxRecurrenceChecked)
        self._maxRecurrenceCountEntry = widgets.SpinCtrl(maxPanel, size=(50,-1), 
                                                         initial=1, min=1)
        self._maxRecurrenceCountEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceEdited)
        panelSizer.Add(self._maxRecurrenceCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(wx.StaticText(maxPanel, label=_('Stop after')),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(self._maxRecurrenceCountEntry,
                       flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add(self.horizontalSpace)
        panelSizer.Add(wx.StaticText(maxPanel, label=_('recurrences')),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        maxPanel.SetSizerAndFit(panelSizer)
        
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(recurrenceFrequencyPanel)
        panelSizer.Add(self.verticalSpace)
        panelSizer.Add(maxPanel)
        self.SetSizerAndFit(panelSizer)
        self.SetValue(recurrence)

    def updateRecurrenceLabel(self):
        recurrenceDict = {0: _('period,'), 1: _('day(s),'), 2: _('week(s),'),
                          3: _('month(s),'), 4: _('year(s),')}
        recurrenceLabel = recurrenceDict[self._recurrencePeriodEntry.Selection]
        self._recurrenceStaticText.SetLabel(recurrenceLabel)
        self._recurrenceSameWeekdayCheckBox.Enable(self._recurrencePeriodEntry.Selection in (3,4))
        self._recurrenceSizer.Layout()

    def onRecurrencePeriodEdited(self, event):
        recurrenceOn = event.String != _('None')
        self._maxRecurrenceCheckBox.Enable(recurrenceOn)
        self._recurrenceFrequencyEntry.Enable(recurrenceOn)
        self._maxRecurrenceCountEntry.Enable(recurrenceOn and \
            self._maxRecurrenceCheckBox.IsChecked())
        self.updateRecurrenceLabel()
        self.onRecurrenceEdited()

    def onMaxRecurrenceChecked(self, event):
        maxRecurrenceOn = event.IsChecked()
        self._maxRecurrenceCountEntry.Enable(maxRecurrenceOn)
        self.onRecurrenceEdited()

    def onRecurrenceEdited(self, event=None):
        wx.PostEvent(self, RecurrenceEntryEvent())
        
    def SetValue(self, recurrence):
        index = {'': 0, 'daily': 1, 'weekly': 2, 'monthly': 3, 'yearly': 4}[recurrence.unit]
        self._recurrencePeriodEntry.Selection = index
        self._maxRecurrenceCheckBox.Enable(bool(recurrence))
        self._maxRecurrenceCheckBox.SetValue(recurrence.max > 0)
        self._maxRecurrenceCountEntry.Enable(recurrence.max > 0)
        if recurrence.max > 0:
            self._maxRecurrenceCountEntry.Value = recurrence.max
        self._recurrenceFrequencyEntry.Enable(bool(recurrence))
        self._recurrenceFrequencyEntry.Value = recurrence.amount
        self._recurrenceSameWeekdayCheckBox.Value = recurrence.sameWeekday \
            if recurrence.unit in ('monthly', 'yearly') else False
        self.updateRecurrenceLabel()

    def GetValue(self):
        recurrenceDict = {0: '', 1: 'daily', 2: 'weekly', 3: 'monthly', 4: 'yearly'}
        kwargs = dict(unit=recurrenceDict[self._recurrencePeriodEntry.Selection])
        if self._maxRecurrenceCheckBox.IsChecked():
            kwargs['max'] = self._maxRecurrenceCountEntry.Value
        kwargs['amount'] = self._recurrenceFrequencyEntry.Value
        kwargs['sameWeekday'] = self._recurrenceSameWeekdayCheckBox.IsChecked()
        return date.Recurrence(**kwargs) # pylint: disable-msg=W0142

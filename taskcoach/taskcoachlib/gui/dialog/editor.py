# -*- coding: utf-8 -*-

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

import wx, os.path
from taskcoachlib import widgets, patterns, command
from taskcoachlib.gui import viewer, artprovider
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, date, note, attachment
from taskcoachlib.gui.dialog import entry


class Page(widgets.BookPage):
    columns = 2
    
    def __init__(self, items, *args, **kwargs):
        self.items = items
        super(Page, self).__init__(columns=self.columns, *args, **kwargs)
        self.addEntries()
        self.fit()
        
    def addEntries(self):
        raise NotImplementedError
        
    def entries(self):
        ''' A mapping of names of columns to entries on this editor page. '''
        return dict()
    
    def setFocusOnEntry(self, columnName):
        try:
            theEntry = self.entries()[columnName]
        except KeyError:
            theEntry = self.entries()['firstEntry']
        try:
            theEntry.SetSelection(-1, -1) # Select all text
        except (AttributeError, TypeError):
            pass # Not a TextCtrl
        theEntry.SetFocus()

    def ok(self, *args, **kwargs):
        pass

    def label(self, labelText, *entryControlsAndEvents):
        if len(self.items) > 1:
            label = wx.CheckBox(self, label=labelText)
            def onEntryEvent(event):
                label.SetValue(True)
                event.Skip()
            for entryControl, entryEvent in zip(entryControlsAndEvents[0::2], 
                                                entryControlsAndEvents[1::2]):
                entryControl.Bind(entryEvent, onEntryEvent)
        else:
            label = labelText
        return label

    def isAttributeChanged(self, currentValue, originalValue, label):
        return (len(self.items) == 1 or label.IsChecked()) and \
               currentValue != originalValue


class SubjectPage(Page):        
    pageName = 'subject'
    pageTitle = _('Description')
    pageIcon = 'pencil_icon'
    
    def addEntries(self):
        self.addSubjectEntry()
        self.addDescriptionEntry()
        
    def addSubjectEntry(self):
        # pylint: disable-msg=W0201
        self._originalSubject = self.items[0].subject() if len(self.items) == 1 else _('Edit to change all subjects')
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self._originalSubject)
        self._subjectEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingSubjectEntry)
        self._subjectLabel = self.label(_('Subject'), self._subjectEntry, wx.EVT_TEXT)
        self.addEntry(self._subjectLabel, self._subjectEntry)

    def onLeavingSubjectEntry(self, event):
        event.Skip()
        currentSubject = self._subjectEntry.GetValue()
        if self.isSubjectChanged(currentSubject):
            command.EditSubjectCommand(None, self.items, subject=currentSubject).do()
            self._originalSubject = currentSubject
            
    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        self._originalDescription = self.items[0].description() if len(self.items) == 1 else _('Edit to change all descriptions')
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, self._originalDescription)
        self._descriptionEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingDescriptionEntry)
        self._descriptionEntry.SetSizeHints(450, 150)
        self._descriptionLabel = self.label(_('Description'), self._descriptionEntry, wx.EVT_TEXT)
        self.addEntry(self._descriptionLabel, self._descriptionEntry, growable=True)
        
    def onLeavingDescriptionEntry(self, event):
        event.Skip()
        currentDescription = self._descriptionEntry.GetValue()
        if self.isDescriptionChanged(currentDescription):
            command.EditDescriptionCommand(None, self.items, description=currentDescription).do()
            self._originalDescription = currentDescription
            
    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)

    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)
        
    def isSubjectChanged(self, currentSubject):
        return self.isAttributeChanged(currentSubject, self._originalSubject, 
                                       self._subjectLabel)

    def isDescriptionChanged(self, currentDescription):
        return self.isAttributeChanged(currentDescription, 
                                       self._originalDescription, 
                                       self._descriptionLabel)
        
    def entries(self):
        return dict(firstEntry=self._subjectEntry,
                    subject=self._subjectEntry, 
                    description=self._descriptionEntry)

    
class TaskSubjectPage(SubjectPage):
    def addEntries(self):
        super(TaskSubjectPage, self).addEntries()
        self.addPriorityEntry()
         
    def addPriorityEntry(self):
        # pylint: disable-msg=W0201
        self._originalPriority = self.items[0].priority() if len(self.items) == 1 else 0
        self._priorityEntry = widgets.SpinCtrl(self, size=(100, -1),
            value=str(self._originalPriority), initial=self._originalPriority)
        self._priorityEntry.Bind(wx.EVT_SPINCTRL, self.onPriorityChanged)
        self._priorityLabel = self.label(_('Priority'), self._priorityEntry, wx.EVT_SPINCTRL)
        self.addEntry(self._priorityLabel, self._priorityEntry, flags=[None, wx.ALL])
    
    def onPriorityChanged(self, event):
        event.Skip()
        currentPriority = self._priorityEntry.GetValue()
        if self.isPriorityChanged(currentPriority):
            command.EditPriorityCommand(None, self.items, priority=currentPriority).do()
            self._originalPriority = currentPriority
            
    def isPriorityChanged(self, currentPriority):
        return self.isAttributeChanged(currentPriority, self._originalPriority, 
                                       self._priorityLabel)
        
    def entries(self):
        entries = super(TaskSubjectPage, self).entries()
        entries['priority'] = self._priorityEntry
        return entries
            

class CategorySubjectPage(SubjectPage):
    def addEntries(self):
        super(CategorySubjectPage, self).addEntries()
        self.addExclusiveSubcategoriesEntry()
       
    def addExclusiveSubcategoriesEntry(self):
        # pylint: disable-msg=W0201
        self._originalExclusivity = self.items[0].hasExclusiveSubcategories() if len(self.items) == 1 else False
        self._exclusiveSubcategoriesCheckBox = \
            wx.CheckBox(self, label=_('Mutually exclusive')) 
        self._exclusiveSubcategoriesCheckBox.SetValue(self._originalExclusivity)
        self._exclusiveSubcategoriesCheckBox.Bind(wx.EVT_CHECKBOX, 
                                                  self.onExclusivityChanged)
        self._exclusiveSubcategoriesLabel = self.label(_('Subcategories'), 
            self._exclusiveSubcategoriesCheckBox, wx.EVT_CHECKBOX)
        self.addEntry(self._exclusiveSubcategoriesLabel, 
                      self._exclusiveSubcategoriesCheckBox,
                      flags=[None, wx.ALL])
        
    def onExclusivityChanged(self, event):
        event.Skip()
        currentExclusivity = self._exclusiveSubcategoriesCheckBox.GetValue()
        if self.isExclusivityChanged(currentExclusivity):
            command.EditExclusiveSubcategoriesCommand(None, self.items, 
                                                      exclusivity=currentExclusivity).do()
            self._originalExclusivity = currentExclusivity
            
    def isExclusivityChanged(self, currentExclusivity):
        return self.isAttributeChanged(currentExclusivity, self._originalExclusivity, 
                                       self._exclusiveSubcategoriesLabel)        
                    

class AttachmentSubjectPage(SubjectPage):
    def __init__(self, attachments, parent, basePath, *args, **kwargs):
        super(AttachmentSubjectPage, self).__init__(attachments, parent, 
                                                    *args, **kwargs)
        self.basePath = basePath
        
    def addEntries(self):
        # Override addEntries to insert a location entry between the subject
        # and description entries 
        self.addSubjectEntry()
        self.addLocationEntry()
        self.addDescriptionEntry()

    def addLocationEntry(self):
        panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # pylint: disable-msg=W0201
        self._originalLocation = self.items[0].location() if len(self.items) == 1 else _('Edit to change location of all attachments')
        self._locationEntry = widgets.SingleLineTextCtrl(panel, self._originalLocation)
        self._locationEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingLocationEntry)
        sizer.Add(self._locationEntry, 1, wx.ALL, 3)
        if all(item.type_ == 'file' for item in self.items):
            button = wx.Button(panel, wx.ID_ANY, _('Browse'))
            sizer.Add(button, 0, wx.ALL, 3)
            wx.EVT_BUTTON(button, wx.ID_ANY, self.onSelectLocation)
        panel.SetSizer(sizer)
        self._locationLabel = self.label(_('Location'), self._locationEntry, wx.EVT_TEXT)
        self.addEntry(self._locationLabel, panel, flags=[None, wx.ALL|wx.EXPAND])
        
    def onLeavingLocationEntry(self, event):
        event.Skip()
        currentLocation = self._locationEntry.GetValue()
        if self.isLocationChanged(currentLocation):
            command.EditAttachmentLocationCommand(None, self.items, location=currentLocation).do()
            self._originalLocation = currentLocation

    def isLocationChanged(self, currentLocation):
        return self.isAttributeChanged(currentLocation, self._originalLocation, 
                                       self._locationLabel)

    def onSelectLocation(self, event): # pylint: disable-msg=W0613
        if self.items[0].type_ == 'file':
            basePath = os.path.split(self.items[0].normalizedLocation())[0]
        else:
            basePath = os.getcwd()

        filename = widgets.AttachmentSelector(default_path=basePath)

        if filename:
            if self.basePath:
                filename = attachment.getRelativePath(filename, self.basePath)
            self._subjectEntry.SetValue(os.path.split(filename)[-1])
            self._locationEntry.SetValue(filename)
            self.onLeavingSubjectEntry(event)
            self.onLeavingLocationEntry(event)


class AppearancePage(Page):
    pageName = 'appearance'
    pageTitle = _('Appearance')
    pageIcon = 'palette_icon'
    columns = 5
    
    def addEntries(self):
        self.addColorEntries()
        self.addFontEntry()
        self.addIconEntry()
        
    def addColorEntries(self):
        self.addFgColorEntry()
        self.addBgColorEntry()
        
    def addFgColorEntry(self):
        self.addColorEntry(_('Foreground color'), 'foreground', wx.BLACK)

    def addBgColorEntry(self):
        self.addColorEntry(_('Background color'), 'background', wx.WHITE)
        
    def addColorEntry(self, labelText, colorType, defaultColor):
        checkBox = wx.CheckBox(self, label=_('Use color:'))
        setattr(self, '_%sColorCheckBox'%colorType, checkBox)
        originalColor = getattr(self.items[0], '%sColor'%colorType)(recursive=False) if len(self.items) == 1 else None
        setattr(self, '_original%sColor'%colorType.capitalize(), originalColor)
        checkBox.SetValue(originalColor is not None)
        checkBoxHandlerName = 'on%sColourCheckBoxChecked'%colorType.capitalize()
        checkBoxHandler = getattr(self, checkBoxHandlerName)
        checkBox.Bind(wx.EVT_CHECKBOX, checkBoxHandler)
        # wx.ColourPickerCtrl on Mac OS X expects a wx.Color and fails on tuples
        # so convert the tuples to a wx.Color:
        originalColor = wx.Color(*originalColor) if originalColor else defaultColor # pylint: disable-msg=W0142
        button = wx.ColourPickerCtrl(self, col=originalColor)
        setattr(self, '_%sColorButton'%colorType, button)
        buttonHandler = getattr(self, 'on%sColourPicked'%colorType.capitalize())
        button.Bind(wx.EVT_COLOURPICKER_CHANGED, buttonHandler)
        label = self.label(labelText, button, wx.EVT_COLOURPICKER_CHANGED,
                           checkBox, wx.EVT_CHECKBOX)
        setattr(self, '_%sColorLabel'%colorType, label)
        self.addEntry(label, checkBox, button, flags=[None, None, wx.ALL])

    # pylint: disable-msg=E1101
    
    def onForegroundColourCheckBoxChecked(self, event):
        ''' User toggled the foreground colour check box. Update the colour
            of the font colour button. '''
        self._fontButton.SetColour(self._foregroundColorButton.GetColour() if \
                                   event.IsChecked() else wx.NullColour)
        self.onForegroundColorChanged(event)
        
    def onForegroundColourPicked(self, event): # pylint: disable-msg=W0613 
        ''' User picked a foreground colour. Check the foreground colour check
            box and update the font colour button. '''
        self._foregroundColorCheckBox.SetValue(True)
        self._fontButton.SetColour(self._foregroundColorButton.GetColour())
        self.onForegroundColorChanged(event)
        
    def onForegroundColorChanged(self, event):
        event.Skip()
        checked = self._foregroundColorCheckBox.GetValue()
        color = self._foregroundColorButton.GetColour() if checked else None
        if self.isForegroundColorChanged(color):
            command.EditForegroundColorCommand(None, self.items, color=color).do()
            self._originalForegroundColor = color # pylint: disable-msg=W0201

    def isForegroundColorChanged(self, currentColor):
        return self.isAttributeChanged(currentColor, self._originalForegroundColor, 
                                       self._foregroundColorLabel)

    def onBackgroundColourCheckBoxChecked(self, event):
        ''' User toggled the background colour check box. '''
        self.onBackgroundColorChanged(event)
        
    def onBackgroundColourPicked(self, event): # pylint: disable-msg=W0613 
        ''' User picked a background colour. Check the background colour check
            box. '''
        self._backgroundColorCheckBox.SetValue(True)
        self.onBackgroundColorChanged(event)
        
    def onBackgroundColorChanged(self, event):
        event.Skip()
        checked = self._backgroundColorCheckBox.GetValue()
        color = self._backgroundColorButton.GetColour() if checked else None
        if self.isBackgroundColorChanged(color):
            command.EditBackgroundColorCommand(None, self.items, color=color).do()
            self._originalBackgroundColor = color # pylint: disable-msg=W0201

    def isBackgroundColorChanged(self, currentColor):
        return self.isAttributeChanged(currentColor, self._originalBackgroundColor, 
                                       self._backgroundColorLabel)

    def addFontEntry(self):
        # pylint: disable-msg=W0201
        self._fontCheckBox = wx.CheckBox(self, label=_('Use font:'))
        self._originalFont = self.items[0].font() if len(self.items) == 1 else None
        currentColor = self._foregroundColorButton.GetColour()
        self._fontCheckBox.SetValue(self._originalFont is not None)
        self._fontCheckBox.Bind(wx.EVT_CHECKBOX, self.onFontChanged)
        self._defaultFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._fontButton = widgets.FontPickerCtrl(self,
            font=self._originalFont or self._defaultFont, colour=currentColor)
        self._fontButton.Bind(wx.EVT_FONTPICKER_CHANGED,
                              self.onFontPickerChanged)
        self._fontLabel = self.label(_('Font'), 
                                     self._fontButton, wx.EVT_FONTPICKER_CHANGED,
                                     self._fontCheckBox, wx.EVT_CHECKBOX)
        self.addEntry(self._fontLabel, self._fontCheckBox, self._fontButton,
                      flags=[None, None, wx.ALL])

    def onFontPickerChanged(self, event): # pylint: disable-msg=W0613 
        ''' User picked a font. Check the font check box and change the
            foreground color if needed. '''
        self._fontCheckBox.SetValue(True)
        if self._fontButton.GetSelectedColour() != self._foregroundColorButton.GetColour():
            self._foregroundColorCheckBox.SetValue(True)
            self._foregroundColorButton.SetColour(self._fontButton.GetSelectedColour())
        self.onFontChanged(event)
        
    def onFontChanged(self, event):
        event.Skip()
        checked = self._fontCheckBox.GetValue()
        font = self._fontButton.GetSelectedFont() if checked else self._defaultFont        
        if self.isFontChanged(font):
            command.EditFontCommand(None, self.items, font=font).do()
            self._originalFont = font
        
    def isFontChanged(self, currentFont):
        return self.isAttributeChanged(currentFont, self._originalFont, 
                                       self._fontLabel)
        
    def addIconEntry(self):
        # pylint: disable-msg=W0201
        self._iconEntry = wx.combo.BitmapComboBox(self, style=wx.CB_READONLY)
        self._iconEntry.Bind(wx.EVT_COMBOBOX, self.onIconChanged)
        size = (16, 16)
        imageNames = sorted(artprovider.chooseableItemImages.keys())
        for imageName in imageNames:
            label = artprovider.chooseableItemImages[imageName]
            bitmap = wx.ArtProvider_GetBitmap(imageName, wx.ART_MENU, size)
            self._iconEntry.Append(label, bitmap, clientData=imageName)
        self._originalIcon = self.items[0].icon() if len(self.items) == 1 else ''
        currentSelectionIndex = imageNames.index(self._originalIcon)
        self._iconEntry.SetSelection(currentSelectionIndex)
        self._iconLabel = self.label(_('Icon'), self._iconEntry, wx.EVT_COMBOBOX)
        self.addEntry(self._iconLabel, self._iconEntry, flags=[None, wx.ALL])
        
    def onIconChanged(self, event):
        event.Skip()
        icon = self._iconEntry.GetClientData(self._iconEntry.GetSelection())
        if self.isIconChanged(icon):
            selectedIcon = icon[:-len('_icon')] + '_open_icon' \
                if (icon.startswith('folder') and icon.count('_') == 2) \
                else icon
            command.EditIconCommand(None, self.items, icon=icon, selectedIcon=selectedIcon).do()
            self._originalIcon = icon
    
    def isIconChanged(self, currentIcon):
        return self.isAttributeChanged(currentIcon, self._originalIcon, 
                                       self._iconLabel)
                
    def entries(self):
        return dict(firstEntry=self._foregroundColorCheckBox)
    

class DatesPage(Page):
    pageName = 'dates'
    pageTitle = _('Dates') 
    pageIcon = 'calendar_icon'
    
    def __init__(self, theTask, parent, settings, *args, **kwargs):
        self.__settings = settings
        super(DatesPage, self).__init__(theTask, parent, *args, **kwargs)
        
    def addEntries(self):
        self.addDateEntries()
        self.addLine()
        self.addReminderEntry()
        self.addLine()
        self.addRecurrenceEntries()
        
    def addDateEntries(self):
        # pylint: disable-msg=W0201
        self._oldCompletionDateTime = dict([(item, item.completionDateTime()) for item in self.items]) 
        for label, taskMethodName, callback in [(_('Start date'), 'startDateTime', self.onStartDateTimeChanged),
                                                (_('Due date'), 'dueDateTime', self.onDueDateTimeChanged),
                                                (_('Completion date'), 'completionDateTime', self.onCompletionDateTimeChanged)]:
            label = self.label(label)
            setattr(self, '_%sLabel'%taskMethodName, label)
            dateTime = getattr(self.items[0], taskMethodName)() if len(self.items) == 1 else date.DateTime()
            setattr(self, '_original%s'%(taskMethodName[0].capitalize()+taskMethodName[1:]), dateTime)
            dateTimeEntry = entry.DateTimeEntry(self, self.__settings, dateTime,
                                                callback=callback)
            setattr(self, '_%sEntry'%taskMethodName, dateTimeEntry)
            self.addEntry(label, dateTimeEntry)
        
    def addReminderEntry(self):
        # pylint: disable-msg=W0201
        self._originalReminderDateTime = self.items[0].reminder() if len(self.items) == 1 else date.DateTime()
        self._reminderDateTimeLabel = self.label(_('Reminder'))
        self._reminderDateTimeEntry = entry.DateTimeEntry(self, self.__settings, 
                                                          self._originalReminderDateTime)
        # If the user has not set a reminder, make sure that the default 
        # date time in the reminder entry is a reasonable suggestion:
        if self._reminderDateTimeEntry.get() == date.DateTime():
            self.suggestReminder()
        self.addEntry(self._reminderDateTimeLabel, self._reminderDateTimeEntry)
        self._reminderDateTimeEntry.setCallback(self.onReminderChanged)
        
    def addRecurrenceEntries(self):
        # pylint: disable-msg=W0201
        recurrencePanel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._recurrenceEntry = wx.Choice(recurrencePanel, 
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly'), _('Yearly')])        
        self._recurrenceEntry.Bind(wx.EVT_CHOICE, self.onRecurrencePeriodChanged)
        panelSizer.Add(self._recurrenceEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        staticText = wx.StaticText(recurrencePanel, label=_(', every'))
        panelSizer.Add(staticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceFrequencyEntry = widgets.SpinCtrl(recurrencePanel, 
                                                          size=(50,-1), 
                                                          initial=1, min=1)
        self._recurrenceFrequencyEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceChanged)
        panelSizer.Add(self._recurrenceFrequencyEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceStaticText = wx.StaticText(recurrencePanel, 
                                                   label='reserve some space')
        panelSizer.Add(self._recurrenceStaticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3, -1))
        self._recurrenceSameWeekdayCheckBox = wx.CheckBox(recurrencePanel, 
            label=_('keeping dates on the same weekday'))
        self._recurrenceSameWeekdayCheckBox.Bind(wx.EVT_CHECKBOX, self.onRecurrenceChanged)
        panelSizer.Add(self._recurrenceSameWeekdayCheckBox, proportion=1, 
                       flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        recurrencePanel.SetSizerAndFit(panelSizer)
        self._recurrenceSizer = panelSizer

        maxPanel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._maxRecurrenceCheckBox = wx.CheckBox(maxPanel)
        self._maxRecurrenceCheckBox.Bind(wx.EVT_CHECKBOX, self.onMaxRecurrenceChecked)
        panelSizer.Add(self._maxRecurrenceCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._maxRecurrenceCountEntry = widgets.SpinCtrl(maxPanel, size=(50,-1), 
                                                         initial=1, min=1)
        self._maxRecurrenceCountEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceChanged)
        panelSizer.Add(self._maxRecurrenceCountEntry)
        maxPanel.SetSizerAndFit(panelSizer)
               
        self._recurrenceLabel = self.label(_('Recurrence'), 
                                           self._recurrenceEntry, wx.EVT_CHOICE,
                                           self._recurrenceFrequencyEntry, wx.EVT_SPINCTRL,
                                           self._recurrenceSameWeekdayCheckBox, wx.EVT_CHECKBOX,
                                           self._maxRecurrenceCheckBox, wx.EVT_CHECKBOX,
                                           self._maxRecurrenceCountEntry, wx.EVT_SPINCTRL)
        
        self.addEntry(self._recurrenceLabel, recurrencePanel)
        self.addEntry(_('Maximum number\nof recurrences'), maxPanel)
        
        self._originalRecurrence = self.items[0].recurrence() if len(self.items) == 1 else date.Recurrence()
        self.setRecurrence(self._originalRecurrence)
            
    def entries(self):
        # pylint: disable-msg=E1101
        return dict(startDateTime=self._startDateTimeEntry, 
                    dueDateTime=self._dueDateTimeEntry,
                    completionDateTime=self._completionDateTimeEntry, 
                    timeLeft=self._dueDateTimeEntry, 
                    reminder=self._reminderDateTimeEntry, 
                    recurrence=self._recurrenceEntry)
    
    def onRecurrencePeriodChanged(self, event):
        recurrenceOn = event.String != _('None')
        self._maxRecurrenceCheckBox.Enable(recurrenceOn)
        self._recurrenceFrequencyEntry.Enable(recurrenceOn)
        self._maxRecurrenceCountEntry.Enable(recurrenceOn and \
            self._maxRecurrenceCheckBox.IsChecked())
        self.updateRecurrenceLabel()
        self.onRecurrenceChanged(event)

    def onMaxRecurrenceChecked(self, event):
        maxRecurrenceOn = event.IsChecked()
        self._maxRecurrenceCountEntry.Enable(maxRecurrenceOn)
        self.onRecurrenceChanged(event)
        
    def onRecurrenceChanged(self, event):
        event.Skip()
        currentRecurrence = self.getRecurrence()
        if currentRecurrence != self._originalRecurrence:
            command.EditRecurrenceCommand(None, self.items, recurrence=currentRecurrence).do()
            self._originalRecurrence = currentRecurrence
            
    def getRecurrence(self):
        recurrenceDict = {0: '', 1: 'daily', 2: 'weekly', 3: 'monthly', 4: 'yearly'}
        kwargs = dict(unit=recurrenceDict[self._recurrenceEntry.Selection])
        if self._maxRecurrenceCheckBox.IsChecked():
            kwargs['max'] = self._maxRecurrenceCountEntry.Value
        kwargs['amount'] = self._recurrenceFrequencyEntry.Value
        kwargs['sameWeekday'] = self._recurrenceSameWeekdayCheckBox.IsChecked()
        return date.Recurrence(**kwargs) # pylint: disable-msg=W0142
    
    def onStartDateTimeChanged(self, event):
        # pylint: disable-msg=E1101,E0203,W0201
        event.Skip()
        currentStartDateTime = self._startDateTimeEntry.get()
        if currentStartDateTime != self._originalStartDateTime:
            command.EditStartDateTimeCommand(None, self.items, datetime=currentStartDateTime).do()
            self._originalStartDateTime = currentStartDateTime
        if len(self.items) > 1:
            self._startDateTimeLabel.SetValue(True) 
        else:
            self.onDateTimeChanged()
                    
    def onDueDateTimeChanged(self, event):
        # pylint: disable-msg=E1101,E0203,W0201
        event.Skip()
        currentDueDateTime = self._dueDateTimeEntry.get()
        if currentDueDateTime != self._originalDueDateTime:
            command.EditDueDateTimeCommand(None, self.items, datetime=currentDueDateTime).do()
            self._originalDueDateTime = currentDueDateTime
        if len(self.items) > 1:
            self._dueDateTimeLabel.SetValue(True)
        else:
            self.onDateTimeChanged()

    def onCompletionDateTimeChanged(self, event):
        # pylint: disable-msg=E1101,E0203,W0201
        event.Skip()
        currentCompletionDateTime = self._completionDateTimeEntry.get()
        if currentCompletionDateTime != self._originalCompletionDateTime:
            command.EditCompletionDateTimeCommand(None, self.items, datetime=currentCompletionDateTime).do()
            self._originalCompletionDateTime = currentCompletionDateTime
        if len(self.items) > 1:
            self._completionDateTimeLabel.SetValue(True)
        else:
            self.onDateTimeChanged()

    def onDateTimeChanged(self):
        ''' Called when one of the DateTimeEntries is changed by the user. 
            Update the suggested reminder if no reminder was set by the user. '''
        # Make sure the reminderDateTimeEntry has been created:
        if hasattr(self, '_reminderDateTimeEntry') and \
            self._reminderDateTimeEntry.get() == date.DateTime():
            self.suggestReminder()
            
    def onReminderChanged(self, event):
        event.Skip()
        currentReminderDatetime = self._reminderDateTimeEntry.get()
        if currentReminderDatetime != self._originalReminderDateTime:
            command.EditReminderDateTimeCommand(None, self.items, datetime=currentReminderDatetime).do()
            self._originalReminderDateTime = currentReminderDatetime
        if len(self.items) > 1:
            self._reminderDateTimeLabel.SetValue(True)
        
    def setReminder(self, reminder):
        self._reminderDateTimeEntry.set(reminder)

    def setRecurrence(self, recurrence):
        index = {'': 0, 'daily': 1, 'weekly': 2, 'monthly': 3, 'yearly': 4}[recurrence.unit]
        self._recurrenceEntry.Selection = index
        self._maxRecurrenceCheckBox.Enable(bool(recurrence))
        self._maxRecurrenceCheckBox.SetValue(recurrence.max > 0)
        self._maxRecurrenceCountEntry.Enable(recurrence.max > 0)
        if recurrence.max > 0:
            self._maxRecurrenceCountEntry.Value = recurrence.max
        self._recurrenceFrequencyEntry.Enable(bool(recurrence))
        if recurrence.amount > 1:
            self._recurrenceFrequencyEntry.Value = recurrence.amount
        if recurrence.unit in ('monthly', 'yearly'):
            self._recurrenceSameWeekdayCheckBox.Value = recurrence.sameWeekday
        else:
            # If recurrence is not monthly or yearly, set same week day to False
            self._recurrenceSameWeekdayCheckBox.Value = False
        self.updateRecurrenceLabel()

    def updateRecurrenceLabel(self):
        recurrenceDict = {0: _('period,'), 1: _('day(s),'), 2: _('week(s),'),
                          3: _('month(s),'), 4: _('year(s),')}
        recurrenceLabel = recurrenceDict[self._recurrenceEntry.Selection]
        self._recurrenceStaticText.SetLabel(recurrenceLabel)
        self._recurrenceSameWeekdayCheckBox.Enable(self._recurrenceEntry.Selection in (3,4))
        self._recurrenceSizer.Layout()

    def suggestReminder(self):
        ''' suggestReminder populates the reminder entry with a reasonable
            suggestion for a reminder date and time, but does not enable the
            reminder entry. '''
        # The suggested date for the reminder is the first date from the
        # list of candidates that is a real date:
        # pylint: disable-msg=E1101
        candidates = [self._dueDateTimeEntry.get(), self._startDateTimeEntry.get(),
                      date.Now() + date.oneDay]
        suggestedDateTime = [candidate for candidate in candidates \
                            if date.Now() <= candidate < date.DateTime()][0]
        # Now, make sure the suggested date time is set in the control
        self.setReminder(suggestedDateTime)
        # And then disable the control (because the SetValue in the
        # previous statement enables the control)
        self.setReminder(None)
        # Now, when the user clicks the check box to enable the
        # control it will show the suggested date time
        

class ProgressPage(Page):
    pageName = 'progress'
    pageTitle = _('Progress')
    pageIcon = 'progress'
    
    def addEntries(self):
        self.addProgressEntry()
        self.addBehaviorEntry()
        
    def addProgressEntry(self):
        # pylint: disable-msg=W0201
        self._originalPercentageComplete = self.items[0].percentageComplete() if len(self.items) == 1 else self.averagePercentageComplete(self.items)
        self._percentageCompleteEntry = entry.PercentageEntry(self, 
            self._originalPercentageComplete, 
            callback=self.onPercentageCompleteChanged)
        self._percentageCompleteLabel = self.label(_('Percentage complete'))
        self.addEntry(self._percentageCompleteLabel, self._percentageCompleteEntry)

    def averagePercentageComplete(self, items):
        return sum([item.percentageComplete() for item in items]) \
                    / float(len(items)) if items else 0

    def onPercentageCompleteChanged(self):
        currentPercentageComplete = self._percentageCompleteEntry.get()
        if currentPercentageComplete != self._originalPercentageComplete:
            command.EditPercentageCompleteCommand(None, self.items, 
                                                  percentage=currentPercentageComplete).do()
            self._originalPercentageComplete = currentPercentageComplete
        if len(self.items) > 1:
            self._percentageCompleteLabel.SetValue(True)
        
    def addBehaviorEntry(self):
        # pylint: disable-msg=W0201
        self._markTaskCompletedEntry = choice = wx.Choice(self)
        self._markTaskCompletedEntry.Bind(wx.EVT_CHOICE, self.onShouldMarkCompletedChanged)
        self._originalShouldMarkCompleted = self.items[0].shouldMarkCompletedWhenAllChildrenCompleted() if len(self.items) == 1 else None
        for choiceValue, choiceText in \
                [(None, _('Use application-wide setting')),
                 (False, _('No')), (True, _('Yes'))]:
            choice.Append(choiceText, choiceValue)
            if choiceValue == self._originalShouldMarkCompleted:
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND:
            # Force a selection if necessary:
            choice.SetSelection(0)
        self._markTaskCompletedLabel = self.label(_('Mark task completed when all children are completed?'),
                                                  self._markTaskCompletedEntry, 
                                                  wx.EVT_CHOICE)
        self.addEntry(self._markTaskCompletedLabel, choice, flags=[None, wx.ALL])
        
    def onShouldMarkCompletedChanged(self, event):
        event.Skip()
        currentShouldMarkCompleted = self._markTaskCompletedEntry.GetClientData( \
            self._markTaskCompletedEntry.GetSelection())
        if currentShouldMarkCompleted != self._originalShouldMarkCompleted:
            command.EditShouldMarkCompletedCommand(None, self.items, 
                                                   shouldMarkCompleted=currentShouldMarkCompleted).do()
            self._originalShouldMarkCompleted = currentShouldMarkCompleted
        
    def entries(self):
        return dict(percentageComplete=self._percentageCompleteEntry)
        

class BudgetPage(Page):
    pageName = 'budget'
    pageTitle = _('Budget')
    pageIcon = 'calculator_icon'
    
    def addEntries(self):
        self.addBudgetEntries()
        self.addLine()
        self.addRevenueEntries()
        
    def addBudgetEntries(self):
        self.addBudgetEntry()
        if len(self.items) == 1:
            self.addTimeSpentEntry()
            self.addBudgetLeftEntry()
            
    def addBudgetEntry(self):
        # pylint: disable-msg=W0201
        self._originalBudget = self.items[0].budget() if len(self.items) == 1 else date.TimeDelta()
        self._budgetEntry = entry.TimeDeltaEntry(self, self._originalBudget)
        self._budgetEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingBudgetEntry)
        self._budgetLabel = self.label(_('Budget'), self._budgetEntry._entry, wx.EVT_TEXT)
        self.addEntry(self._budgetLabel, self._budgetEntry, flags=[None, wx.ALL])
        
    def onLeavingBudgetEntry(self, event):
        event.Skip()
        currentBudget = self._budgetEntry.get()
        if self._originalBudget != currentBudget:
            command.EditBudgetCommand(None, self.items, budget=currentBudget).do()
            self._originalBudget = currentBudget
        
    def addTimeSpentEntry(self):
        timeSpent = self.items[0].timeSpent()
        timeSpentEntry = entry.TimeDeltaEntry(self, timeSpent, readonly=True)
        self.addEntry(_('Time spent'), timeSpentEntry, flags=[None, wx.ALL])
        
    def addBudgetLeftEntry(self):
        budgetLeft = self.items[0].budgetLeft()
        budgetLeftEntry = entry.TimeDeltaEntry(self, budgetLeft, readonly=True)
        self.addEntry(_('Budget left'), budgetLeftEntry, flags=[None, wx.ALL])
        
    def addRevenueEntries(self):
        self.addHourlyFeeEntry()
        self.addFixedFeeEntry()
        if len(self.items) == 1:
            self.addRevenueEntry()
            
    def addHourlyFeeEntry(self):
        # pylint: disable-msg=W0201
        self._originalHourlyFee = self.items[0].hourlyFee() if len(self.items) == 1 else 0
        self._hourlyFeeEntry = entry.AmountEntry(self, self._originalHourlyFee)
        self._hourlyFeeEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingHourlyFeeEntry)
        self._hourlyFeeLabel = self.label(_('Hourly fee'), self._hourlyFeeEntry._entry, wx.EVT_TEXT)
        self.addEntry(self._hourlyFeeLabel, self._hourlyFeeEntry, flags=[None, wx.ALL])
        
    def onLeavingHourlyFeeEntry(self, event):
        event.Skip()
        currentHourlyFee = self._hourlyFeeEntry.get()
        if currentHourlyFee != self._originalHourlyFee:
            command.EditHourlyFeeCommand(None, self.items, hourlyFee=currentHourlyFee).do()
            self._originalHourlyFee = currentHourlyFee
        
    def addFixedFeeEntry(self):
        # pylint: disable-msg=W0201
        self._originalFixedFee = self.items[0].fixedFee() if len(self.items) == 1 else 0
        self._fixedFeeEntry = entry.AmountEntry(self, self._originalFixedFee)
        self._fixedFeeEntry.Bind(wx.EVT_KILL_FOCUS, self.onLeavingFixedFeeEntry)
        self._fixedFeeLabel = self.label(_('Fixed fee'), self._fixedFeeEntry._entry, wx.EVT_TEXT)
        self.addEntry(self._fixedFeeLabel, self._fixedFeeEntry, flags=[None, wx.ALL])

    def onLeavingFixedFeeEntry(self, event):
        event.Skip()
        currentFixedFee = self._fixedFeeEntry.get()
        if currentFixedFee != self._originalFixedFee:
            command.EditFixedFeeCommand(None, self.items, fixedFee=currentFixedFee).do()
            self._originalFixedFee = currentFixedFee
        
    def addRevenueEntry(self):
        revenue = self.items[0].revenue()
        revenueEntry = entry.AmountEntry(self, revenue, readonly=True)
        self.addEntry(_('Revenue'), revenueEntry, flags=[None, wx.ALL])
        
    def entries(self):
        return dict(budget=self._budgetEntry, 
                    budgetLeft=self._budgetEntry,  
                    hourlyFee=self._hourlyFeeEntry, 
                    fixedFee=self._fixedFeeEntry,  
                    revenue=self._hourlyFeeEntry)


class PageWithViewer(Page):
    columns = 1
    
    def __init__(self, items, parent, taskFile, settings, settingsSection, *args, **kwargs):
        self.__taskFile = taskFile
        self.__settings = settings
        self.__settingsSection = settingsSection
        super(PageWithViewer, self).__init__(items, parent, *args, **kwargs)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        
    def addEntries(self):
        # pylint: disable-msg=W0201
        self.viewer = self.createViewer(self.__taskFile, self.__settings,
                                        self.__settingsSection) 
        self.addEntry(self.viewer, growable=True)
        
    def createViewer(self, taskFile, settings, settingsSection):
        raise NotImplementedError
        
    def onClose(self, event):
        # Don't notify the viewer about any changes anymore, it's about
        # to be deleted, but don't delete it soo soon.
        wx.CallAfter(self.detachAndDeleteViewer)
        event.Skip()        
        
    def detachAndDeleteViewer(self):
        if hasattr(self, 'viewer'):
            self.viewer.detach()
            del self.viewer


class EffortPage(PageWithViewer):
    pageName = 'effort'
    pageTitle = _('Effort')
    pageIcon = 'clock_icon'
            
    def createViewer(self, taskFile, settings, settingsSection):
        return viewer.EffortViewer(self, taskFile, settings, 
            settingsSection=settingsSection,
            tasksToShowEffortFor=task.TaskList(self.items))

    def entries(self):
        return dict(timeSpent=self.viewer)
        

class LocalCategoryViewer(viewer.BaseCategoryViewer):
    def __init__(self, items, *args, **kwargs):
        self.__items = items
        super(LocalCategoryViewer, self).__init__(*args, **kwargs)
        for item in self.domainObjectsToView():
            item.expand(context=self.settingsSection())

    def getIsItemChecked(self, category):
        for item in self.__items:
            if category in item.categories():
                return True
        return False

    def onCheck(self, event):
        ''' Here we keep track of the items checked by the user so that these 
            items remain checked when refreshing the viewer. ''' 
        category = self.widget.GetItemPyData(event.GetItem())
        command.ToggleCategoryCommand(None, self.__items, category=category).do()

    def createCategoryPopupMenu(self): # pylint: disable-msg=W0221
        return super(LocalCategoryViewer, self).createCategoryPopupMenu(True)            


class CategoriesPage(PageWithViewer):
    pageName = 'categories'
    pageTitle = _('Categories')
    pageIcon = 'folder_blue_arrow_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalCategoryViewer(self.items, self, taskFile, settings,
                                   settingsSection=settingsSection)
        
    def entries(self):
        return dict(categories=self.viewer) 


class LocalAttachmentViewer(viewer.AttachmentViewer):
    def __init__(self, *args, **kwargs):
        self.attachmentOwner = kwargs.pop('owner')
        attachments = attachment.AttachmentList(self.attachmentOwner.attachments())
        super(LocalAttachmentViewer, self).__init__(attachmentsToShow=attachments, *args, **kwargs)
        patterns.Publisher().registerObserver(self.onOriginalAttachmentsChanged, 
            eventType=self.attachmentOwner.attachmentsChangedEventType(), 
            eventSource=self.attachmentOwner)

    def onOriginalAttachmentsChanged(self, event): # pylint: disable-msg=W0613
        self.domainObjectsToView().clear()
        self.domainObjectsToView().extend(self.attachmentOwner.attachments())
        
    def newItemCommand(self, *args, **kwargs):
        return command.AddAttachmentCommand(None, [self.attachmentOwner])
    
    def deleteItemCommand(self):
        return command.RemoveAttachmentCommand(None, [self.attachmentOwner], attachments=self.curselection())


class AttachmentsPage(PageWithViewer):
    pageName = 'attachments'
    pageTitle = _('Attachments')
    pageIcon = 'paperclip_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalAttachmentViewer(self, taskFile, settings,
            settingsSection=settingsSection, owner=self.items[0])
        
    def entries(self):
        return dict(attachments=self.viewer)


class LocalNoteViewer(viewer.BaseNoteViewer):
    def __init__(self, *args, **kwargs):
        self.noteOwner = kwargs.pop('owner')
        notes = note.NoteContainer(self.noteOwner.notes())
        super(LocalNoteViewer, self).__init__(notesToShow=notes, *args, **kwargs)
        patterns.Publisher().registerObserver(self.onOriginalNotesChanged,
            eventType=self.noteOwner.notesChangedEventType(),
            eventSource=self.noteOwner)
        
    def onOriginalNotesChanged(self, event): # pylint: disable-msg=W0613
        self.domainObjectsToView().clear()
        self.domainObjectsToView().extend(self.noteOwner.notes())
        
    def newItemCommand(self, *args, **kwargs):
        return command.AddNoteCommand(None, [self.noteOwner])
    
    def newSubItemCommand(self):
        return command.AddSubNoteCommand(None, self.curselection(), owner=self.noteOwner)
    
    def deleteItemCommand(self):
        return command.RemoveNoteCommand(None, [self.noteOwner], notes=self.curselection())


class NotesPage(PageWithViewer):
    pageName = 'notes'
    pageTitle = _('Notes')
    pageIcon = 'note_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalNoteViewer(self, taskFile, settings, 
                                     settingsSection=settingsSection,
                                     owner=self.items[0])

    def entries(self):
        return dict(notes=self.viewer)
    

class LocalPrerequisiteViewer(viewer.CheckableTaskViewer):
    def __init__(self, items, *args, **kwargs):
        self.__items = items
        super(LocalPrerequisiteViewer, self).__init__(*args, **kwargs)
        for item in self.domainObjectsToView():
            item.expand(context=self.settingsSection())

    def getIsItemChecked(self, item):
        return item in self.__items[0].prerequisites()

    def getIsItemCheckable(self, item):
        return item not in self.__items
    
    def onCheck(self, event):
        item = self.widget.GetItemPyData(event.GetItem())
        isChecked = event.GetItem().IsChecked()
        if isChecked != self.getIsItemChecked(item):
            command.TogglePrerequisiteCommand(None, self.__items, checkedPrerequisites=[item],
                                              uncheckedPrerequisites=[]).do()
    
    
class PrerequisitesPage(PageWithViewer):
    pageName = 'prerequisites'
    pageTitle = _('Prerequisites')
    pageIcon = 'trafficlight_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        return LocalPrerequisiteViewer(self.items, self, taskFile, settings,
                                       settingsSection=settingsSection)
    
    def entries(self):
        return dict(prerequisites=self.viewer, dependencies=self.viewer)


class EditBook(widgets.Notebook):
    allPageNames = ['subclass responsibility']
    object = 'subclass responsibility'
    
    def __init__(self, parent, items, taskFile, settings):
        self.items = items
        self.settings = settings
        super(EditBook, self).__init__(parent)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self.addPages(taskFile)
        
    def addPages(self, taskFile):
        for pageName in self.allPageNamesInUserOrder():
            if self.shouldCreatePage(pageName):
                page = self.createPage(pageName, taskFile)
                self.AddPage(page, page.pageTitle, page.pageIcon)

    def allPageNamesInUserOrder(self):
        ''' Return all pages names in the order stored in the settings. The
            settings may not contain all pages (e.g. because a feature was
            turned off by the user) so we add the missing pages if necessary. '''
        pageNamesInUserOrder = self.settings.getlist('editor', '%spages'%self.object)
        remainingPageNames = self.allPageNames[:]
        for pageName in pageNamesInUserOrder:
            remainingPageNames.remove(pageName)
        return pageNamesInUserOrder + remainingPageNames
                    
    def shouldCreatePage(self, pageName):
        if self.pageFeatureDisabled(pageName):
            return False
        return self.pageSupportsMassEditing(pageName) if len(self.items) > 1 else True

    def pageFeatureDisabled(self, pageName):
        if pageName in ('budget', 'effort', 'notes'):
            feature = 'effort' if pageName == 'budget' else pageName
            return not self.settings.getboolean('feature', feature)
        else:
            return False
        
    def pageSupportsMassEditing(self, pageName):
        return pageName in ('subject', 'dates', 'progress', 'budget', 'appearance')

    def createPage(self, pageName, taskFile):
        if pageName == 'subject':
            return self.createSubjectPage()
        elif pageName == 'dates':
            return DatesPage(self.items, self, self.settings) 
        elif pageName == 'prerequisites':
            return PrerequisitesPage(self.items, self, taskFile, self.settings, 
                                     settingsSection='prerequisiteviewerin%seditor'%self.object)
        elif pageName == 'progress':    
            return ProgressPage(self.items, self)
        elif pageName == 'categories':
            return CategoriesPage(self.items, self, taskFile, self.settings, 
                                  settingsSection='categoryviewerin%seditor'%self.object)
        elif pageName == 'budget':                 
            return BudgetPage(self.items, self)
        elif pageName == 'effort':        
            return EffortPage(self.items, self, taskFile, self.settings,
                              settingsSection='effortviewerin%seditor'%self.object)
        elif pageName == 'notes':
            return NotesPage(self.items, self, taskFile, self.settings,
                             settingsSection='noteviewerin%seditor'%self.object)
        elif pageName == 'attachments':
            return AttachmentsPage(self.items, self, taskFile, self.settings, 
                                   settingsSection='attachmentviewerin%seditor'%self.object)
        elif pageName == 'appearance':
            return AppearancePage(self.items, self)
        
    def createSubjectPage(self):
        return SubjectPage(self.items, self)
    
    def setFocus(self, columnName):
        ''' Select the correct page of the editor and correct control on a page
            based on the column that the user double clicked. '''
        page = 0
        for pageIndex in range(self.GetPageCount()):
            if columnName in self[pageIndex].entries():
                page = pageIndex
                break
        self.SetSelection(page)
        self[page].setFocusOnEntry(columnName)

    def isDisplayingItemOrChildOfItem(self, targetItem):
        ancestors = []
        for item in self.items:
            ancestors.extend(item.ancestors())
        return targetItem in self.items + ancestors
    
    def onClose(self, event):
        event.Skip()
        pageNames = [self[index].pageName for index in range(self.GetPageCount())]
        self.settings.setlist('editor', '%spages'%self.object, pageNames)


class TaskEditBook(EditBook):
    allPageNames = ['subject', 'dates', 'prerequisites', 'progress', 
                    'categories', 'budget', 'effort', 'notes', 'attachments', 
                    'appearance']
    object = 'task'

    def createSubjectPage(self):    
        return TaskSubjectPage(self.items, self)


class CategoryEditBook(EditBook):
    allPageNames = ['subject', 'notes', 'attachments', 'appearance']
    object = 'category'

    def createSubjectPage(self):
        return CategorySubjectPage(self.items, self)


class NoteEditBook(EditBook):
    allPageNames = ['subject', 'categories', 'attachments', 'appearance']
    object = 'note'
    

class AttachmentEditBook(EditBook):
    allPageNames = ['subject', 'notes', 'appearance']
    object = 'attachment'
            
    def createSubjectPage(self):
        return AttachmentSubjectPage(self.items, self,
                                     self.settings.get('file', 'attachmentbase'))
    
    def isDisplayingItemOrChildOfItem(self, targetItem):
        return targetItem in self.items
    
        
class EffortEditBook(Page):
    columns = 3
    
    def __init__(self, parent, efforts, taskFile, settings, *args, **kwargs):
        self._effortList = taskFile.efforts()
        taskList = taskFile.tasks()
        self._taskList = task.TaskList(taskList)
        self._taskList.extend([effort.task() for effort in efforts if effort.task() not in taskList])
        self._settings = settings
        super(EffortEditBook, self).__init__(efforts, parent, *args, **kwargs)
        
    def addEntries(self):
        self.addTaskEntry()
        self.addStartAndStopEntries()
        self.addDescriptionEntry()

    def addTaskEntry(self):
        ''' Add an entry for changing the task that this effort record
            belongs to. '''
        # pylint: disable-msg=W0201
        self._taskEntry = entry.TaskComboTreeBox(self,
            rootTasks=self._taskList.rootItems(),
            selectedTask=self.items[0].task())
        self._taskLabel = self.label(_('Task'), self._taskEntry._comboTreeBox, wx.EVT_COMBOBOX)
        self.addEntry(self._taskLabel, self._taskEntry, flags=[None, wx.ALL|wx.EXPAND])

    def addStartAndStopEntries(self):
        # pylint: disable-msg=W0201,W0142
        dateTimeEntryKwArgs = dict(showSeconds=True) 
        self._startEntry = entry.DateTimeEntry(self, self._settings,
            self.items[0].getStart(), noneAllowed=False, 
            callback=self.onStartChanged, **dateTimeEntryKwArgs)
        self._startLabel = self.label(_('Start'))
        startFromLastEffortButton = wx.Button(self,
            label=_('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort,
            startFromLastEffortButton)
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()

        self._stopEntry = entry.DateTimeEntry(self, self._settings, 
            self.items[0].getStop(), noneAllowed=True, 
            callback=self.onStopChanged, **dateTimeEntryKwArgs)
        self._stopLabel = self.label(_('Stop'))
        flags = [None, wx.ALIGN_RIGHT|wx.ALL, wx.ALIGN_LEFT|wx.ALL, None]
        self.addEntry(self._startLabel, self._startEntry,
            startFromLastEffortButton,  flags=flags)
        self.addEntry(self._stopLabel, self._stopEntry, '', flags=flags)

    def onStartFromLastEffort(self, event): # pylint: disable-msg=W0613
        self._startEntry.set(self._effortList.maxDateTime())
        self.preventNegativeEffortDuration()

    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        self._descriptionEntry = widgets.MultiLineTextCtrl(self,
            self.items[0].description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self._descriptionLabel = self.label(_('Description'), 
                                            self._descriptionEntry, wx.EVT_TEXT)
        self.addEntry(self._descriptionLabel, self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)

    @patterns.eventSource
    def ok(self, event=None): # pylint: disable-msg=W0221
        for item in self.items:
            if len(self.items) == 1 or self._taskLabel.IsChecked():
                item.setTask(self._taskEntry.GetSelection(), event=event)
            if len(self.items) == 1 or self._startLabel.IsChecked():
                item.setStart(self._startEntry.get(), event=event)
            if len(self.items) == 1 or self._stopLabel.IsChecked():
                item.setStop(self._stopEntry.get(), event=event)
            if len(self.items) == 1 or self._descriptionLabel.IsChecked():
                item.setDescription(self._descriptionEntry.GetValue(), event=event)

    def onStartChanged(self, *args, **kwargs):
        if len(self.items) > 1:
            self._startLabel.SetValue(True)
        self.onPeriodChanged(*args, **kwargs)
        
    def onStopChanged(self, *args, **kwargs):
        if len(self.items) > 1:
            self._stopLabel.SetValue(True)
        self.onPeriodChanged(*args, **kwargs)
        
    def onPeriodChanged(self, *args, **kwargs): # pylint: disable-msg=W0613
        if not hasattr(self, '_stopEntry'): # Check that both entries exist
            return
        # We use CallAfter to give the DatePickerCtrl widgets a chance
        # to update themselves
        wx.CallAfter(self.preventNegativeEffortDuration)

    def preventNegativeEffortDuration(self):
        if self._startEntry.get() > self._stopEntry.get():
            self.TopLevelParent.disableOK()
        else:
            self.TopLevelParent.enableOK()

    def setFocus(self, columnName):
        self.setFocusOnEntry(columnName)
        
    def isDisplayingItemOrChildOfItem(self, item):
        if hasattr(item, 'setTask'):
            return self.items[0] == item # Regular effort
        else:
            return item.mayContain(self.items[0]) # Composite effort
    
    def entries(self):
        return dict(period=self._stopEntry, task=self._taskEntry,
                    firstEntry=self._taskEntry,
                    description=self._descriptionEntry,
                    timeSpent=self._stopEntry,
                    revenue=self._taskEntry)
    
    
class EditorWithCommand(widgets.Dialog):
    EditBookClass = lambda: 'Subclass responsibility'
    
    def __init__(self, parent, command, settings, container, taskFile, *args, **kwargs):
        self._command = command
        self._settings = settings
        self._taskFile = taskFile
        super(EditorWithCommand, self).__init__(parent, command.name(), 
                                                *args, **kwargs)
        columnName = kwargs.get('columnName', '')
        self._interior.setFocus(columnName)
        patterns.Publisher().registerObserver(self.onItemRemoved, 
            eventType=container.removeItemEventType(), eventSource=container)

        if '__WXMAC__' in wx.PlatformInfo:
            # The window manager does this automatically on other
            # platforms but on Mac OS X it opens by default in the
            # top-left corner of the first display. This gets annoying
            # on a 2560x1440 27" + 1920x1200 24" dual screen...
            self.CentreOnParent()
        
    def cancel(self, *args, **kwargs): # pylint: disable-msg=W0221
        patterns.Publisher().removeObserver(self.onItemRemoved)
        super(EditorWithCommand, self).cancel(*args, **kwargs)
        
    def ok(self, *args, **kwargs):
        patterns.Publisher().removeObserver(self.onItemRemoved)
        self.okInterior()
        self._command.do()
        super(EditorWithCommand, self).ok(*args, **kwargs)
        
    def createInterior(self):
        return self.EditBookClass(self._panel, self._command.items, 
                                  self._taskFile, self._settings)
        
    @patterns.eventSource
    def okInterior(self, event=None):
        self._interior.ok(event=event)
                
    def onItemRemoved(self, event):
        ''' The item we're editing or one of its ancestors has been removed or 
            is hidden by a filter. If the item is really removed, close the tab 
            of the item involved and close the whole editor if there are no 
            tabs left. '''
        if not self:
            return # Prevent _wxPyDeadObject TypeError
        for item in event.values():
            if self._interior.isDisplayingItemOrChildOfItem(item) and not item in self._taskFile:
                self.cancel()
                break            


class TaskEditor(EditorWithCommand):
    EditBookClass = TaskEditBook


class CategoryEditor(EditorWithCommand):
    EditBookClass = CategoryEditBook


class NoteEditor(EditorWithCommand):
    EditBookClass = NoteEditBook


class AttachmentEditor(EditorWithCommand):
    EditBookClass = AttachmentEditBook


class EffortEditor(EditorWithCommand):
    EditBookClass = EffortEditBook

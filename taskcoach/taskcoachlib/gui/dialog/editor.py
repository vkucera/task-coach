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
from taskcoachlib.gui.dialog import entry, attributesync


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

                        
class SubjectPage(Page):
    pageName = 'subject'
    pageTitle = _('Description')
    pageIcon = 'pencil_icon'
    
    def addEntries(self):
        self.addSubjectEntry()
        self.addDescriptionEntry()
        
    def addSubjectEntry(self):
        # pylint: disable-msg=W0201
        currentSubject = self.items[0].subject() if len(self.items) == 1 else _('Edit to change all subjects')
        self._subjectEntry = widgets.SingleLineTextCtrl(self, currentSubject)
        self._subjectSync = attributesync.AttributeSync('subject', 
            self._subjectEntry, currentSubject, self.items,
            command.EditSubjectCommand, wx.EVT_KILL_FOCUS,
            self.items[0].subjectChangedEventType())
        self.addEntry(_('Subject'), self._subjectEntry)

    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        currentDescription = self.items[0].description() if len(self.items) == 1 else _('Edit to change all descriptions')
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, currentDescription)
        self._descriptionEntry.SetSizeHints(450, 150)
        self._descriptionSync = attributesync.AttributeSync('description', 
            self._descriptionEntry, currentDescription, self.items,
            command.EditDescriptionCommand, wx.EVT_KILL_FOCUS,
            self.items[0].descriptionChangedEventType())
        self.addEntry(_('Description'), self._descriptionEntry, growable=True)
                        
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
        currentPriority = self.items[0].priority() if len(self.items) == 1 else 0
        self._priorityEntry = widgets.SpinCtrl(self, size=(100, -1),
            value=str(currentPriority), initial=currentPriority)
        self._prioritySync = attributesync.AttributeSync('priority', 
            self._priorityEntry, currentPriority, self.items,
            command.EditPriorityCommand, wx.EVT_SPINCTRL, 'task.priority')
        self.addEntry(_('Priority'), self._priorityEntry, flags=[None, wx.ALL])
            
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
        currentExclusivity = self.items[0].hasExclusiveSubcategories() if len(self.items) == 1 else False
        self._exclusiveSubcategoriesCheckBox = wx.CheckBox(self, label=_('Mutually exclusive')) 
        self._exclusiveSubcategoriesCheckBox.SetValue(currentExclusivity)
        self._exclusiveSubcategoriesSync = attributesync.AttributeSync( \
            'exclusivity', self._exclusiveSubcategoriesCheckBox, 
            currentExclusivity, self.items, 
            command.EditExclusiveSubcategoriesCommand, wx.EVT_CHECKBOX,
            self.items[0].exclusiveSubcategoriesChangedEventType())
        self.addEntry(_('Subcategories'), self._exclusiveSubcategoriesCheckBox,
                      flags=[None, wx.ALL])
            

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
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # pylint: disable-msg=W0201
        currentLocation = self.items[0].location() if len(self.items) == 1 else _('Edit to change location of all attachments')
        self._locationEntry = widgets.SingleLineTextCtrl(panel, currentLocation)
        self._locationSync = attributesync.AttributeSync('location', 
            self._locationEntry, currentLocation, self.items,
            command.EditAttachmentLocationCommand, wx.EVT_KILL_FOCUS, 
            self.items[0].locationChangedEventType())
        sizer.Add(self._locationEntry, 1, wx.ALL, 3)
        if all(item.type_ == 'file' for item in self.items):
            button = wx.Button(panel, wx.ID_ANY, _('Browse'))
            sizer.Add(button, 0, wx.ALL, 3)
            wx.EVT_BUTTON(button, wx.ID_ANY, self.onSelectLocation)
        panel.SetSizer(sizer)
        self.addEntry(_('Location'), panel, flags=[None, wx.ALL|wx.EXPAND])

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
            self._subjectSync.onAttributeEdited(event)
            self._locationSync.onAttributeEdited(event)
        

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
        currentColor = getattr(self.items[0], '%sColor'%colorType)(recursive=False) if len(self.items) == 1 else None
        checkBox.SetValue(currentColor is not None)
        # wx.ColourPickerCtrl on Mac OS X expects a wx.Color and fails on tuples
        # so convert the tuples to a wx.Color:
        currentColor = wx.Color(*currentColor) if currentColor else defaultColor # pylint: disable-msg=W0142
        button = wx.ColourPickerCtrl(self, col=currentColor)
        setattr(self, '_%sColorButton'%colorType, button)
        commandClass = getattr(command, 'Edit%sColorCommand'%colorType.capitalize())
        eventType = getattr(self.items[0], '%sColorChangedEventType'%colorType)()
        colorSync = attributesync.ColorSync('color', button, currentColor, 
            self.items, commandClass, wx.EVT_COLOURPICKER_CHANGED, eventType, 
            defaultValue=defaultColor, defaultCheckbox=checkBox)
        setattr(self, '_%sColorSync'%colorType, colorSync)
        self.addEntry(labelText, checkBox, button, flags=[None, None, wx.ALL])
            
    def addFontEntry(self):
        # pylint: disable-msg=W0201
        fontCheckBox = wx.CheckBox(self, label=_('Use font:'))
        currentFont = self.items[0].font() if len(self.items) == 1 else None
        currentColor = self._foregroundColorButton.GetColour()
        fontCheckBox.SetValue(currentFont is not None)
        defaultFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._fontButton = widgets.FontPickerCtrl(self,
            font=currentFont or defaultFont, colour=currentColor)
        self._fontSync = attributesync.FontSync('font', self._fontButton, 
            currentFont, self.items, command.EditFontCommand, 
            wx.EVT_FONTPICKER_CHANGED, self.items[0].fontChangedEventType(),
            defaultValue=defaultFont, defaultCheckbox=fontCheckBox)
        self._fontColorSync = attributesync.FontColorSync('color', 
            self._fontButton, currentColor, self.items, 
            command.EditForegroundColorCommand, wx.EVT_FONTPICKER_CHANGED,
            self.items[0].foregroundColorChangedEventType())
        self.addEntry(_('Font'), fontCheckBox, self._fontButton,
                      flags=[None, None, wx.ALL])
                    
    def addIconEntry(self):
        # pylint: disable-msg=W0201
        self._iconEntry = wx.combo.BitmapComboBox(self, style=wx.CB_READONLY)
        size = (16, 16)
        imageNames = sorted(artprovider.chooseableItemImages.keys())
        for imageName in imageNames:
            label = artprovider.chooseableItemImages[imageName]
            bitmap = wx.ArtProvider_GetBitmap(imageName, wx.ART_MENU, size)
            self._iconEntry.Append(label, bitmap, clientData=imageName)
        currentIcon = self.items[0].icon() if len(self.items) == 1 else ''
        currentSelectionIndex = imageNames.index(currentIcon)
        self._iconEntry.SetSelection(currentSelectionIndex)
        self._iconSync = attributesync.IconSync('icon', self._iconEntry, 
            currentIcon, self.items, command.EditIconCommand, wx.EVT_COMBOBOX, 
            self.items[0].iconChangedEventType())
        self.addEntry(_('Icon'), self._iconEntry, flags=[None, wx.ALL])
    
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
        for label, taskMethodName in [(_('Start date'), 'startDateTime'),
                                      (_('Due date'), 'dueDateTime'),
                                      (_('Completion date'), 'completionDateTime')]:
            self.addDateEntry(label, taskMethodName)
            
    def addDateEntry(self, label, taskMethodName):
        TaskMethodName = taskMethodName[0].capitalize() + taskMethodName[1:]
        dateTime = getattr(self.items[0], taskMethodName)() if len(self.items) == 1 else date.DateTime()
        setattr(self, '_current%s'%TaskMethodName, dateTime)
        dateTimeEntry = entry.DateTimeEntry(self, self.__settings, dateTime)
        setattr(self, '_%sEntry'%taskMethodName, dateTimeEntry)
        commandClass = getattr(command, 'Edit%sCommand'%TaskMethodName)
        eventType = 'task.%s'%taskMethodName
        datetimeSync = attributesync.AttributeSync('datetime', dateTimeEntry, 
            dateTime, self.items, commandClass, entry.EVT_DATETIMEENTRY, 
            eventType)
        setattr(self, '_%sSync'%taskMethodName, datetimeSync) 
        self.addEntry(label, dateTimeEntry)
        dateTimeEntry.Bind(entry.EVT_DATETIMEENTRY, self.onDateTimeEdited)
        
    def addReminderEntry(self):
        # pylint: disable-msg=W0201
        currentReminderDateTime = self.items[0].reminder() if len(self.items) == 1 else date.DateTime()
        self._reminderDateTimeEntry = entry.DateTimeEntry(self, self.__settings, 
                                                          currentReminderDateTime)
        # If the user has not set a reminder, make sure that the default 
        # date time in the reminder entry is a reasonable suggestion:
        if self._reminderDateTimeEntry.GetValue() == date.DateTime():
            self.suggestReminder()
        self._reminderDateTimeSync = attributesync.AttributeSync('datetime', 
            self._reminderDateTimeEntry, currentReminderDateTime, self.items, 
            command.EditReminderDateTimeCommand, entry.EVT_DATETIMEENTRY, 
            'task.reminder')
        self.addEntry(_('Reminder'), self._reminderDateTimeEntry)
        
    def addRecurrenceEntries(self):
        # pylint: disable-msg=W0201
        recurrencePanel = wx.Panel(self)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._recurrenceEntry = wx.Choice(recurrencePanel, 
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly'), _('Yearly')])        
        self._recurrenceEntry.Bind(wx.EVT_CHOICE, self.onRecurrencePeriodEdited)
        panelSizer.Add(self._recurrenceEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        staticText = wx.StaticText(recurrencePanel, label=_(', every'))
        panelSizer.Add(staticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceFrequencyEntry = widgets.SpinCtrl(recurrencePanel, 
                                                          size=(50,-1), 
                                                          initial=1, min=1)
        self._recurrenceFrequencyEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceEdited)
        panelSizer.Add(self._recurrenceFrequencyEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceStaticText = wx.StaticText(recurrencePanel, 
                                                   label='reserve some space')
        panelSizer.Add(self._recurrenceStaticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3, -1))
        self._recurrenceSameWeekdayCheckBox = wx.CheckBox(recurrencePanel, 
            label=_('keeping dates on the same weekday'))
        self._recurrenceSameWeekdayCheckBox.Bind(wx.EVT_CHECKBOX, self.onRecurrenceEdited)
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
        self._maxRecurrenceCountEntry.Bind(wx.EVT_SPINCTRL, self.onRecurrenceEdited)
        panelSizer.Add(self._maxRecurrenceCountEntry)
        maxPanel.SetSizerAndFit(panelSizer)
        self.addEntry(_('Recurrence'), recurrencePanel)
        self.addEntry(_('Maximum number\nof recurrences'), maxPanel)
        self._currentRecurrence = self.items[0].recurrence() if len(self.items) == 1 else date.Recurrence()
        self.setRecurrence(self._currentRecurrence)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onRecurrenceChanged, 
                                                  eventType='task.recurrence', 
                                                  eventSource=self.items[0])
            
    def entries(self):
        # pylint: disable-msg=E1101
        return dict(firstEntry=self._startDateTimeEntry,
                    startDateTime=self._startDateTimeEntry, 
                    dueDateTime=self._dueDateTimeEntry,
                    completionDateTime=self._completionDateTimeEntry, 
                    timeLeft=self._dueDateTimeEntry, 
                    reminder=self._reminderDateTimeEntry, 
                    recurrence=self._recurrenceEntry)
    
    def onRecurrencePeriodEdited(self, event):
        recurrenceOn = event.String != _('None')
        self._maxRecurrenceCheckBox.Enable(recurrenceOn)
        self._recurrenceFrequencyEntry.Enable(recurrenceOn)
        self._maxRecurrenceCountEntry.Enable(recurrenceOn and \
            self._maxRecurrenceCheckBox.IsChecked())
        self.updateRecurrenceLabel()
        self.onRecurrenceEdited(event)

    def onMaxRecurrenceChecked(self, event):
        maxRecurrenceOn = event.IsChecked()
        self._maxRecurrenceCountEntry.Enable(maxRecurrenceOn)
        self.onRecurrenceEdited(event)
        
    def onRecurrenceEdited(self, event):
        event.Skip()
        newRecurrence = self.getRecurrence()
        if newRecurrence != self._currentRecurrence:
            command.EditRecurrenceCommand(None, self.items, recurrence=newRecurrence).do()
            self._currentRecurrence = newRecurrence
            
    def onRecurrenceChanged(self, event):
        newRecurrence = event.value()
        if newRecurrence != self._currentRecurrence:
            self._currentRecurrence = newRecurrence
            self.setRecurrence(newRecurrence)
            
    def getRecurrence(self):
        recurrenceDict = {0: '', 1: 'daily', 2: 'weekly', 3: 'monthly', 4: 'yearly'}
        kwargs = dict(unit=recurrenceDict[self._recurrenceEntry.Selection])
        if self._maxRecurrenceCheckBox.IsChecked():
            kwargs['max'] = self._maxRecurrenceCountEntry.Value
        kwargs['amount'] = self._recurrenceFrequencyEntry.Value
        kwargs['sameWeekday'] = self._recurrenceSameWeekdayCheckBox.IsChecked()
        return date.Recurrence(**kwargs) # pylint: disable-msg=W0142
    
    def onDateTimeEdited(self, event):
        ''' Called when one of the DateTimeEntries is changed by the user. 
            Update the suggested reminder if no reminder was set by the user. '''
        # Make sure the reminderDateTimeEntry has been created:
        event.Skip()
        if hasattr(self, '_reminderDateTimeEntry') and \
            self._reminderDateTimeEntry.GetValue() == date.DateTime():
            self.suggestReminder()
            
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
        candidates = [self._dueDateTimeEntry.GetValue(), self._startDateTimeEntry.GetValue(),
                      date.Now() + date.oneDay]
        suggestedDateTime = [candidate for candidate in candidates \
                            if date.Now() <= candidate < date.DateTime()][0]
        # Now, make sure the suggested date time is set in the control
        self._reminderDateTimeEntry.SetValue(suggestedDateTime)
        # And then disable the control (because the SetValue in the
        # previous statement enables the control)
        self._reminderDateTimeEntry.SetValue(None)
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
        currentPercentageComplete = self.items[0].percentageComplete() if len(self.items) == 1 else self.averagePercentageComplete(self.items)
        self._percentageCompleteEntry = entry.PercentageEntry(self, 
            currentPercentageComplete)
        self._percentageCompleteSync = attributesync.AttributeSync('percentage', 
            self._percentageCompleteEntry, currentPercentageComplete, 
            self.items, command.EditPercentageCompleteCommand, 
            entry.EVT_PERCENTAGEENTRY, 
            self.items[0].percentageCompleteChangedEventType())
        self.addEntry(_('Percentage complete'), self._percentageCompleteEntry)

    @staticmethod
    def averagePercentageComplete(items):
        return sum([item.percentageComplete() for item in items]) \
                    / float(len(items)) if items else 0
        
    def addBehaviorEntry(self):
        # pylint: disable-msg=W0201
        self._shouldMarkCompletedEntry = choice = wx.Choice(self)
        currentShouldMarkCompleted = self.items[0].shouldMarkCompletedWhenAllChildrenCompleted() if len(self.items) == 1 else None
        for choiceValue, choiceText in \
                [(None, _('Use application-wide setting')),
                 (False, _('No')), (True, _('Yes'))]:
            choice.Append(choiceText, choiceValue)
            if choiceValue == currentShouldMarkCompleted:
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND:
            # Force a selection if necessary:
            choice.SetSelection(0)
        self._shouldMarkCompletedSync = attributesync.ChoiceSync( \
            'shouldMarkCompleted', choice, currentShouldMarkCompleted, 
            self.items, command.EditShouldMarkCompletedCommand, wx.EVT_CHOICE,
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted')                                                       
        self.addEntry(_('Mark task completed when all children are completed?'), 
                      choice, flags=[None, wx.ALL])
        
    def entries(self):
        return dict(firstEntry=self._percentageCompleteEntry,
                    percentageComplete=self._percentageCompleteEntry)
        

class BudgetPage(Page):
    pageName = 'budget'
    pageTitle = _('Budget')
    pageIcon = 'calculator_icon'
    
    def addEntries(self):
        self.addBudgetEntries()
        self.addLine()
        self.addRevenueEntries()
        self.observeTracking()
        
    def addBudgetEntries(self):
        self.addBudgetEntry()
        if len(self.items) == 1:
            self.addTimeSpentEntry()
            self.addBudgetLeftEntry()
            
    def addBudgetEntry(self):
        # pylint: disable-msg=W0201
        currentBudget = self.items[0].budget() if len(self.items) == 1 else date.TimeDelta()
        self._budgetEntry = entry.TimeDeltaEntry(self, currentBudget)
        self._budgetSync = attributesync.AttributeSync('budget', 
            self._budgetEntry, currentBudget, self.items,                                         
            command.EditBudgetCommand, wx.EVT_KILL_FOCUS, 'task.budget')
        self.addEntry(_('Budget'), self._budgetEntry, flags=[None, wx.ALL])
                    
    def addTimeSpentEntry(self):
        assert len(self.items) == 1
        # pylint: disable-msg=W0201 
        self._timeSpentEntry = entry.TimeDeltaEntry(self, 
                                                    self.items[0].timeSpent(), 
                                                    readonly=True)
        self.addEntry(_('Time spent'), self._timeSpentEntry, 
                      flags=[None, wx.ALL])
        patterns.Publisher().registerObserver(self.onTimeSpentChanged, 
                                              eventType='task.timeSpent', 
                                              eventSource=self.items[0])
        
    def onTimeSpentChanged(self, event): # pylint: disable-msg=W0613
        newTimeSpent = self.items[0].timeSpent()
        if newTimeSpent != self._timeSpentEntry.GetValue():
            self._timeSpentEntry.SetValue(newTimeSpent)
            
    def addBudgetLeftEntry(self):
        assert len(self.items) == 1
        # pylint: disable-msg=W0201
        self._budgetLeftEntry = entry.TimeDeltaEntry(self, 
                                                     self.items[0].budgetLeft(), 
                                                     readonly=True)
        self.addEntry(_('Budget left'), self._budgetLeftEntry, 
                      flags=[None, wx.ALL])
        patterns.Publisher().registerObserver(self.onBudgetLeftChanged,
                                              eventType='task.budgetLeft',
                                              eventSource=self.items[0])
        
    def onBudgetLeftChanged(self, event): # pylint: disable-msg=W0613
        newBudgetLeft = self.items[0].budgetLeft()
        if newBudgetLeft != self._budgetLeftEntry.GetValue():
            self._budgetLeftEntry.SetValue(newBudgetLeft)
            
    def addRevenueEntries(self):
        self.addHourlyFeeEntry()
        self.addFixedFeeEntry()
        if len(self.items) == 1:
            self.addRevenueEntry()
            
    def addHourlyFeeEntry(self):
        # pylint: disable-msg=W0201
        currentHourlyFee = self.items[0].hourlyFee() if len(self.items) == 1 else 0
        self._hourlyFeeEntry = entry.AmountEntry(self, currentHourlyFee)
        self._hourlyFeeSync = attributesync.AttributeSync('hourlyFee',
            self._hourlyFeeEntry, currentHourlyFee, self.items,
            command.EditHourlyFeeCommand, wx.EVT_KILL_FOCUS, 
            self.items[0].hourlyFeeChangedEventType())
        self.addEntry(_('Hourly fee'), self._hourlyFeeEntry, flags=[None, wx.ALL])
        
    def addFixedFeeEntry(self):
        # pylint: disable-msg=W0201
        currentFixedFee = self.items[0].fixedFee() if len(self.items) == 1 else 0
        self._fixedFeeEntry = entry.AmountEntry(self, currentFixedFee)
        self._fixedFeeSync = attributesync.AttributeSync('fixedFee',
            self._fixedFeeEntry, currentFixedFee, self.items,
            command.EditFixedFeeCommand, wx.EVT_KILL_FOCUS, 'task.fixedFee')
        self.addEntry(_('Fixed fee'), self._fixedFeeEntry, flags=[None, wx.ALL])

    def addRevenueEntry(self):
        assert len(self.items) == 1
        revenue = self.items[0].revenue()
        self._revenueEntry = entry.AmountEntry(self, revenue, readonly=True) # pylint: disable-msg=W0201
        self.addEntry(_('Revenue'), self._revenueEntry, flags=[None, wx.ALL])
        patterns.Publisher().registerObserver(self.onRevenueChanged,
                                              eventType='task.revenue',
                                              eventSource=self.items[0])

    def onRevenueChanged(self, event): # pylint: disable-msg=W0613
        newRevenue = self.items[0].revenue()
        if newRevenue != self._revenueEntry.GetValue():
            self._revenueEntry.SetValue(newRevenue)
            
    def observeTracking(self):
        if len(self.items) != 1:
            return
        registerObserver = patterns.Publisher().registerObserver
        item = self.items[0]
        registerObserver(self.onStartTracking, 
                         eventType=item.trackStartEventType(), 
                         eventSource=item)
        registerObserver(self.onStopTracking, 
                         eventType=item.trackStopEventType(), 
                         eventSource=item)
        if item.isBeingTracked():
            self.onStartTracking(None)
        
    def onStartTracking(self, event): # pylint: disable-msg=W0613
        # We might already be observing the clock if the user is tracking this
        # task with multiple effort records simultaneously
        if self.onEverySecond not in patterns.Publisher().observers('clock.second'):
            patterns.Publisher().registerObserver(self.onEverySecond, eventType='clock.second')
        
    def onStopTracking(self, event): # pylint: disable-msg=W0613
        # We might need to keep tracking the clock if the user was tracking this
        # task with multiple effort records simultaneously
        if not self.items[0].isBeingTracked():
            patterns.Publisher().removeObserver(self.onEverySecond, eventType='clock.second')
    
    def onEverySecond(self, event):
        self.onTimeSpentChanged(event)
        self.onBudgetLeftChanged(event)
        self.onRevenueChanged(event)
        
    def entries(self):
        return dict(firstEntry=self._budgetEntry,
                    budget=self._budgetEntry, 
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
        return dict(firstEntry=self.viewer,
                    timeSpent=self.viewer)
        

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
        assert len(self.items) == 1
        item = self.items[0]
        registerObserver = patterns.Publisher().registerObserver
        for eventType in (item.categoryAddedEventType(), 
                         item.categoryRemovedEventType()):
            registerObserver(self.onCategoryChanged, eventType=eventType,
                            eventSource=item)
        return LocalCategoryViewer(self.items, self, taskFile, settings,
                                   settingsSection=settingsSection)
        
    def onCategoryChanged(self, event):
        self.viewer.refreshItems(*event.values())
        
    def entries(self):
        return dict(firstEntry=self.viewer, categories=self.viewer) 


class LocalAttachmentViewer(viewer.AttachmentViewer):
    def __init__(self, *args, **kwargs):
        self.attachmentOwner = kwargs.pop('owner')
        attachments = attachment.AttachmentList(self.attachmentOwner.attachments())
        super(LocalAttachmentViewer, self).__init__(attachmentsToShow=attachments, *args, **kwargs)

    def newItemCommand(self, *args, **kwargs):
        return command.AddAttachmentCommand(None, [self.attachmentOwner])
    
    def deleteItemCommand(self):
        return command.RemoveAttachmentCommand(None, [self.attachmentOwner], attachments=self.curselection())


class AttachmentsPage(PageWithViewer):
    pageName = 'attachments'
    pageTitle = _('Attachments')
    pageIcon = 'paperclip_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        assert len(self.items) == 1
        item = self.items[0]
        patterns.Publisher().registerObserver(self.onAttachmentsChanged, 
            eventType=item.attachmentsChangedEventType(), 
            eventSource=item)    
        return LocalAttachmentViewer(self, taskFile, settings,
            settingsSection=settingsSection, owner=item)

    def onAttachmentsChanged(self, event): # pylint: disable-msg=W0613
        self.viewer.domainObjectsToView().clear()
        self.viewer.domainObjectsToView().extend(self.items[0].attachments())
        
    def entries(self):
        return dict(firstEntry=self.viewer, attachments=self.viewer)


class LocalNoteViewer(viewer.BaseNoteViewer):
    def __init__(self, *args, **kwargs):
        self.noteOwner = kwargs.pop('owner')
        notes = note.NoteContainer(self.noteOwner.notes())
        super(LocalNoteViewer, self).__init__(notesToShow=notes, *args, **kwargs)

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
        assert len(self.items) == 1
        item = self.items[0]
        patterns.Publisher().registerObserver(self.onNotesChanged,
                                              eventType=item.notesChangedEventType(),
                                              eventSource=item)
        return LocalNoteViewer(self, taskFile, settings, 
                               settingsSection=settingsSection, owner=item)

    def onNotesChanged(self, event): # pylint: disable-msg=W0613
        self.viewer.domainObjectsToView().clear()
        self.viewer.domainObjectsToView().extend(self.items[0].notes())

    def entries(self):
        return dict(firstEntry=self.viewer, notes=self.viewer)
    

class LocalPrerequisiteViewer(viewer.CheckableTaskViewer):
    def __init__(self, items, *args, **kwargs):
        self.__items = items
        super(LocalPrerequisiteViewer, self).__init__(*args, **kwargs)

    def getIsItemChecked(self, item):
        return item in self.__items[0].prerequisites()

    def getIsItemCheckable(self, item):
        return item not in self.__items
    
    def onCheck(self, event):
        item = self.widget.GetItemPyData(event.GetItem())
        isChecked = event.GetItem().IsChecked()
        if isChecked != self.getIsItemChecked(item):
            checked, unchecked = ([item], []) if isChecked else ([], [item])            
            command.TogglePrerequisiteCommand(None, self.__items, 
                checkedPrerequisites=checked, uncheckedPrerequisites=unchecked).do()
    
    
class PrerequisitesPage(PageWithViewer):
    pageName = 'prerequisites'
    pageTitle = _('Prerequisites')
    pageIcon = 'trafficlight_icon'
    
    def createViewer(self, taskFile, settings, settingsSection):
        assert len(self.items) == 1
        patterns.Publisher().registerObserver(self.onPrerequisitesChanged, 
                                              eventType='task.prerequisites', 
                                              eventSource=self.items[0])
        return LocalPrerequisiteViewer(self.items, self, taskFile, settings,
                                       settingsSection=settingsSection)
        
    def onPrerequisitesChanged(self, event):
        self.viewer.refreshItems(*event.values())
    
    def entries(self):
        return dict(firstEntry=self.viewer, prerequisites=self.viewer, 
                    dependencies=self.viewer)


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
        removeInstance = patterns.Publisher().removeInstance
        for page in self:
            removeInstance(page)
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
        self._currentTask = self.items[0].task()
        self._taskEntry = entry.TaskComboTreeBox(self,
            rootTasks=self._taskList.rootItems(),
            selectedTask=self._currentTask)
        self._taskEntry._comboTreeBox.Bind(wx.EVT_COMBOBOX, self.onTaskEdited)
        self.addEntry(_('Task'), self._taskEntry, flags=[None, wx.ALL|wx.EXPAND])
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onTaskChanged,
                                                  eventType=self.items[0].taskChangedEventType(),
                                                  eventSource=self.items[0])
            
    def onTaskEdited(self, event): # pylint: disable-msg=W0613
        event.Skip()
        newTask = self._taskEntry.GetSelection()
        if newTask != self._currentTask:
            self._currentTask = newTask
            command.ChangeTaskCommand(None, self.items, task=newTask).do()
            
    def onTaskChanged(self, event):
        newTask = event.value()
        if newTask != self._currentTask:
            self._currentTask = newTask
            self._taskEntry.SetSelection(newTask)
            
    def addStartAndStopEntries(self):
        # pylint: disable-msg=W0201,W0142
        dateTimeEntryKwArgs = dict(showSeconds=True)
        self._currentStartDateTime = self.items[0].getStart() 
        self._startDateTimeEntry = entry.DateTimeEntry(self, self._settings,
            self._currentStartDateTime, noneAllowed=False, **dateTimeEntryKwArgs)
        self._startDateTimeEntry.Bind(entry.EVT_DATETIMEENTRY, self.onStartDateTimeEdited)
        startFromLastEffortButton = wx.Button(self,
            label=_('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort,
            startFromLastEffortButton)
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()

        self._currentStopDateTime = self.items[0].getStop()
        self._stopDateTimeEntry = entry.DateTimeEntry(self, self._settings, 
            self._currentStopDateTime, noneAllowed=True, **dateTimeEntryKwArgs)
        self._stopDateTimeEntry.Bind(entry.EVT_DATETIMEENTRY, self.onStopDateTimeEdited)
        self.invalidPeriodMessage = wx.StaticText(self, label='')
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD )
        self.invalidPeriodMessage.SetFont(font)
        
        flags = [None, wx.ALIGN_RIGHT|wx.ALL, wx.ALIGN_LEFT|wx.ALL, None]
        self.addEntry(_('Start'), self._startDateTimeEntry,
            startFromLastEffortButton, flags=flags)
        self.addEntry(_('Stop'), self._stopDateTimeEntry, self.invalidPeriodMessage, flags=flags)
        if len(self.items) == 1:
            registerObserver = patterns.Publisher().registerObserver
            registerObserver(self.onStartDateTimeChanged, 
                             eventType='effort.start', eventSource=self.items[0])
            registerObserver(self.onStopDateTimeChanged, 
                             eventType='effort.stop', eventSource=self.items[0])
            
    def onStartDateTimeEdited(self, *args, **kwargs):
        newStartDateTime = self._startDateTimeEntry.GetValue()
        if newStartDateTime != self._currentStartDateTime and self.validPeriod():
            self._currentStartDateTime = newStartDateTime
            command.ChangeEffortStartDateTimeCommand(None, self.items, datetime=newStartDateTime).do()
        self.updateInvalidPeriodMessage()
        
    def onStartDateTimeChanged(self, event):
        newStartDateTime = event.value()
        if newStartDateTime != self._currentStartDateTime:
            self._currentStartDateTime = newStartDateTime
            self._startDateTimeEntry.SetValue(newStartDateTime)
        
    def onStopDateTimeEdited(self, *args, **kwargs): 
        newStopDateTime = self._stopDateTimeEntry.GetValue()
        if newStopDateTime != self._currentStopDateTime and self.validPeriod():
            self._currentStopDateTime = newStopDateTime
            command.ChangeEffortStopDateTimeCommand(None, self.items, datetime=newStopDateTime).do()
        self.updateInvalidPeriodMessage()

    def onStopDateTimeChanged(self, event):
        newStopDateTime = event.value()
        if newStopDateTime != self._currentStopDateTime:
            self._currentStopDateTime = newStopDateTime
            self._stopDateTimeEntry.SetValue(newStopDateTime)
        
    def updateInvalidPeriodMessage(self):
        self.invalidPeriodMessage.SetLabel('' if self.validPeriod() else \
                                           _('Warning: start must be earlier than stop'))
                
    def onStartFromLastEffort(self, event): # pylint: disable-msg=W0613
        self._startDateTimeEntry.SetValue(self._effortList.maxDateTime())
        
    def validPeriod(self):
        if not hasattr(self, '_stopDateTimeEntry'):
            return True
        else:
            return self._startDateTimeEntry.GetValue() < self._stopDateTimeEntry.GetValue()
        
    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        self._currentDescription = self.items[0].description() if len(self.items) == 1 else _('Edit to change all descriptions')
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, self._currentDescription)
        self._descriptionEntry.Bind(wx.EVT_KILL_FOCUS, self.onDescriptionEdited)
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry, growable=True)
        if len(self.items) == 1:
            patterns.Publisher().registerObserver(self.onDescriptionChanged, 
                                                  eventType=self.items[0].descriptionChangedEventType(), 
                                                  eventSource=self.items[0])
        
    def onDescriptionEdited(self, event):
        event.Skip()
        newDescription = self._descriptionEntry.GetValue()
        if newDescription != self._currentDescription:
            self._currentDescription = newDescription
            command.EditDescriptionCommand(None, self.items, description=newDescription).do()

    def onDescriptionChanged(self, event):
        newDescription = event.value()
        if newDescription != self._currentDescription:
            self._currentDescription = newDescription
            self._descriptionEntry.SetValue(newDescription)

    def setFocus(self, columnName):
        self.setFocusOnEntry(columnName)
        
    def isDisplayingItemOrChildOfItem(self, item):
        if hasattr(item, 'setTask'):
            return self.items[0] == item # Regular effort
        else:
            return item.mayContain(self.items[0]) # Composite effort
    
    def entries(self):
        return dict(firstEntry=self._taskEntry, task=self._taskEntry,
                    period=self._stopDateTimeEntry,
                    description=self._descriptionEntry,
                    timeSpent=self._stopDateTimeEntry,
                    revenue=self._taskEntry)
    
    
class Editor(widgets.ButtonLessDialog):
    EditBookClass = lambda: 'Subclass responsibility'
    singular_title = 'Subclass responsibility %s'
    plural_title = 'Subclass responsibility'
    
    def __init__(self, parent, items, settings, container, taskFile, *args, **kwargs):
        self._items = items
        self._settings = settings
        self._taskFile = taskFile
        super(Editor, self).__init__(parent, self.title(), *args, **kwargs)
        columnName = kwargs.get('columnName', '')
        self._interior.setFocus(columnName)
        patterns.Publisher().registerObserver(self.onItemRemoved, 
            eventType=container.removeItemEventType(), eventSource=container)
        if len(self._items) == 1:
            patterns.Publisher().registerObserver(self.onSubjectChanged,
                                                  eventType=self._items[0].subjectChangedEventType(),
                                                  eventSource=self._items[0])
        self.Bind(wx.EVT_CLOSE, self.onClose)

        if '__WXMAC__' in wx.PlatformInfo:
            # The window manager does this automatically on other
            # platforms but on Mac OS X it opens by default in the
            # top-left corner of the first display. This gets annoying
            # on a 2560x1440 27" + 1920x1200 24" dual screen...
            self.CentreOnParent()
                
    def createInterior(self):
        return self.EditBookClass(self._panel, self._items, 
                                  self._taskFile, self._settings)

    def onClose(self, event):
        event.Skip()
        patterns.Publisher().removeInstance(self)
                        
    def onItemRemoved(self, event):
        ''' The item we're editing or one of its ancestors has been removed or 
            is hidden by a filter. If the item is really removed, close the tab 
            of the item involved and close the whole editor if there are no 
            tabs left. '''
        if not self:
            return # Prevent _wxPyDeadObject TypeError
        for item in event.values():
            if self._interior.isDisplayingItemOrChildOfItem(item) and not item in self._taskFile:
                self.Close()
                break            

    def onSubjectChanged(self, event): # pylint: disable-msg=W0613
        self.SetTitle(self.title())
        
    def title(self):
        return self.plural_title if len(self._items) > 1 else \
               self.singular_title%self._items[0].subject()
    
    
class TaskEditor(Editor):
    plural_title = _('Multiple tasks')
    singular_title = _('%s (task)')
    EditBookClass = TaskEditBook


class CategoryEditor(Editor):
    plural_title = _('Multiple categories')
    singular_title = _('%s (category)')
    EditBookClass = CategoryEditBook


class NoteEditor(Editor):
    plural_title = _('Multiple notes')
    singular_title = _('%s (note)')
    EditBookClass = NoteEditBook


class AttachmentEditor(Editor):
    plural_title = _('Multiple attachments')
    singular_title = _('%s (attachment)')
    EditBookClass = AttachmentEditBook


class EffortEditor(Editor):
    plural_title = _('Multiple efforts')
    singular_title = _('%s (effort)')
    EditBookClass = EffortEditBook

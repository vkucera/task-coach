# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
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

import wx.combo, os.path
from taskcoachlib import widgets, patterns, command, operating_system
from taskcoachlib.gui import viewer, uicommand, windowdimensionstracker
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
            value=currentPriority)
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
            self.items[0].exclusiveSubcategoriesChangedEventType(),
            'hasExclusiveSubcategories')
        self.addEntry(_('Subcategories'), self._exclusiveSubcategoriesCheckBox,
                      flags=[None, wx.ALL])
            

class AttachmentSubjectPage(SubjectPage):
    def __init__(self, attachments, parent, settings, *args, **kwargs):
        super(AttachmentSubjectPage, self).__init__(attachments, parent,
                                                    *args, **kwargs)
        self.settings = settings
        
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
        basePath = self.settings.get('file', 'lastattachmentpath')
        if not basePath:
            basePath = os.getcwd()

        filename = widgets.AttachmentSelector(default_path=basePath)

        if filename:
            self.settings.set('file', 'lastattachmentpath', os.path.abspath(os.path.split(filename)[0]))
            if self.settings.get('file', 'attachmentbase'):
                filename = attachment.getRelativePath(filename, self.settings.get('file', 'attachmentbase'))
            self._subjectEntry.SetValue(os.path.split(filename)[-1])
            self._locationEntry.SetValue(filename)
            self._subjectSync.onAttributeEdited(event)
            self._locationSync.onAttributeEdited(event)
        

class TaskAppearancePage(Page):
    pageName = 'appearance'
    pageTitle = _('Appearance')
    pageIcon = 'palette_icon'
    columns = 5
    
    def addEntries(self):
        self.addColorEntries()
        self.addFontEntry()
        self.addIconEntry()
        
    def addColorEntries(self):
        self.addColorEntry(_('Foreground color'), 'foreground', wx.BLACK)
        self.addColorEntry(_('Background color'), 'background', wx.WHITE)
        
    def addColorEntry(self, labelText, colorType, defaultColor):
        currentColor = getattr(self.items[0], '%sColor'%colorType)(recursive=False) if len(self.items) == 1 else None
        colorEntry = entry.ColorEntry(self, currentColor, defaultColor)
        setattr(self, '_%sColorEntry'%colorType, colorEntry)        
        commandClass = getattr(command, 'Edit%sColorCommand'%colorType.capitalize())
        colorSync = attributesync.AttributeSync('color', colorEntry, currentColor, 
            self.items, commandClass, entry.EVT_COLORENTRY, 
            self.items[0].appearanceChangedEventType(), '%sColor'%colorType)
        setattr(self, '_%sColorSync'%colorType, colorSync)
        self.addEntry(labelText, colorEntry, flags=[None, wx.ALL])
            
    def addFontEntry(self):
        # pylint: disable-msg=W0201,E1101
        currentFont = self.items[0].font() if len(self.items) == 1 else None
        currentColor = self._foregroundColorEntry.GetValue()
        self._fontEntry = entry.FontEntry(self, currentFont, currentColor)
        self._fontSync = attributesync.AttributeSync('font', self._fontEntry, 
            currentFont, self.items, command.EditFontCommand, 
            entry.EVT_FONTENTRY, self.items[0].appearanceChangedEventType())
        self._fontColorSync = attributesync.FontColorSync('color', 
            self._fontEntry, currentColor, self.items, 
            command.EditForegroundColorCommand, entry.EVT_FONTENTRY,
            self.items[0].appearanceChangedEventType(), 'foregroundColor')
        self.addEntry(_('Font'), self._fontEntry, flags=[None, wx.ALL])
                    
    def addIconEntry(self):
        # pylint: disable-msg=W0201,E1101
        currentIcon = self.items[0].icon() if len(self.items) == 1 else ''
        self._iconEntry = entry.IconEntry(self, currentIcon)
        self._iconSync = attributesync.AttributeSync('icon', self._iconEntry, 
            currentIcon, self.items, command.EditIconCommand, 
            entry.EVT_ICONENTRY, self.items[0].appearanceChangedEventType())
        self.addEntry(_('Icon'), self._iconEntry, flags=[None, wx.ALL])

    def entries(self):
        return dict(firstEntry=self._foregroundColorEntry) # pylint: disable-msg=E1101
    

class DatesPage(Page):
    pageName = 'dates'
    pageTitle = _('Dates') 
    pageIcon = 'calendar_icon'
    
    def __init__(self, theTask, parent, settings, itemsAreNew, *args, **kwargs):
        self.__settings = settings
        self._duration = None
        self.__itemsAreNew = itemsAreNew
        super(DatesPage, self).__init__(theTask, parent, *args, **kwargs)
        
    def addEntries(self):
        self.addDateEntries()
        self.addLine()
        self.addReminderEntry()
        self.addLine()
        self.addRecurrenceEntry()

    def addDateEntries(self):
        for label, taskMethodName in [(_('Start date'), 'startDateTime'),
                                                (_('Due date'), 'dueDateTime'),
                                                (_('Completion date'), 'completionDateTime')]:
            self.addDateEntry(label, taskMethodName)

    def addDateEntry(self, label, taskMethodName):
        TaskMethodName = taskMethodName[0].capitalize() + taskMethodName[1:]
        dateTime = getattr(self.items[0], taskMethodName)() if len(self.items) == 1 else date.DateTime()
        setattr(self, '_current%s'%TaskMethodName, dateTime)
        suggestedDateTimeMethodName = 'suggested' + TaskMethodName
        suggestedDateTime = getattr(self.items[0], suggestedDateTimeMethodName)()
        if self.__shouldPresetDateTime(taskMethodName, dateTime):
            self.__presetDateTime(TaskMethodName, suggestedDateTime)
            dateTime = suggestedDateTime
        dateTimeEntry = entry.DateTimeEntry(self, self.__settings, dateTime,
                                            suggestedDateTime=suggestedDateTime)
        setattr(self, '_%sEntry'%taskMethodName, dateTimeEntry)
        commandClass = getattr(command, 'Edit%sCommand'%TaskMethodName)
        eventType = 'task.%s'%taskMethodName
        keep_delta = self.__keep_delta(taskMethodName)
        datetimeSync = attributesync.AttributeSync('datetime', dateTimeEntry, 
            dateTime, self.items, commandClass, entry.EVT_DATETIMEENTRY, 
            eventType, taskMethodName, keep_delta=keep_delta)
        setattr(self, '_%sSync'%taskMethodName, datetimeSync) 
        self.addEntry(label, dateTimeEntry)

    def __shouldPresetDateTime(self, taskMethodName, dateTime):
        return self.__itemsAreNew and dateTime == date.DateTime() and \
            self.__settings.get('view', 'default%s'%taskMethodName.lower()).startswith('preset')
            
    @patterns.eventSource
    def __presetDateTime(self, TaskMethodName, dateTime, event=None):
        for item in self.items:
            getattr(item, 'set%s'%TaskMethodName)(dateTime, event=event)
            
    def __keep_delta(self, taskMethodName):
        datesTied = self.__settings.get('view', 'datestied')
        return (datesTied == 'startdue' and taskMethodName == 'startDateTime') or \
               (datesTied == 'duestart' and taskMethodName == 'dueDateTime')
               
    def addReminderEntry(self):
        # pylint: disable-msg=W0201
        reminderDateTime = self.items[0].reminder() if len(self.items) == 1 else date.DateTime()
        suggestedDateTime = self.items[0].suggestedReminderDateTime()
        if self.__shouldPresetDateTime('reminderdatetime', reminderDateTime):
            self.__presetDateTime('Reminder', suggestedDateTime)
            reminderDateTime = suggestedDateTime
        self._reminderDateTimeEntry = entry.DateTimeEntry(self, self.__settings,
                                                          reminderDateTime, 
                                                          suggestedDateTime=suggestedDateTime)
        self._reminderDateTimeSync = attributesync.AttributeSync('datetime', 
            self._reminderDateTimeEntry, reminderDateTime, self.items, 
            command.EditReminderDateTimeCommand, entry.EVT_DATETIMEENTRY, 
            'task.reminder', 'reminder')
        self.addEntry(_('Reminder'), self._reminderDateTimeEntry)
        
    def addRecurrenceEntry(self):
        currentRecurrence = self.items[0].recurrence() if len(self.items) == 1 else date.Recurrence()
        self._recurrenceEntry = entry.RecurrenceEntry(self, currentRecurrence)
        self._recurrenceSync = attributesync.AttributeSync('recurrence',
            self._recurrenceEntry, currentRecurrence, self.items,
            command.EditRecurrenceCommand, entry.EVT_RECURRENCEENTRY,
            'task.recurrence')
        self.addEntry(_('Recurrence'), self._recurrenceEntry)
            
    def entries(self):
        # pylint: disable-msg=E1101
        return dict(firstEntry=self._startDateTimeEntry,
                    startDateTime=self._startDateTimeEntry,
                    dueDateTime=self._dueDateTimeEntry,
                    completionDateTime=self._completionDateTimeEntry,
                    timeLeft=self._dueDateTimeEntry,
                    reminder=self._reminderDateTimeEntry,
                    recurrence=self._recurrenceEntry)


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
            self.items[0].percentageCompleteChangedEventType(), 
            'percentageComplete')
        self.addEntry(_('Percentage complete'), self._percentageCompleteEntry)

    @staticmethod
    def averagePercentageComplete(items):
        return sum([item.percentageComplete() for item in items]) \
                    / float(len(items)) if items else 0
        
    def addBehaviorEntry(self):
        # pylint: disable-msg=W0201
        choices = [(None, _('Use application-wide setting')),
                   (False, _('No')), (True, _('Yes'))]
        currentChoice = self.items[0].shouldMarkCompletedWhenAllChildrenCompleted() \
            if len(self.items) == 1 else None
        self._shouldMarkCompletedEntry = entry.ChoiceEntry(self, choices,
                                                           currentChoice)
        self._shouldMarkCompletedSync = attributesync.AttributeSync( \
            'shouldMarkCompleted', self._shouldMarkCompletedEntry, 
            currentChoice, self.items, command.EditShouldMarkCompletedCommand, 
            entry.EVT_CHOICEENTRY,
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
            'shouldMarkCompletedWhenAllChildrenCompleted')                                                       
        self.addEntry(_('Mark task completed when all children are completed?'), 
                      self._shouldMarkCompletedEntry, flags=[None, wx.ALL])
        
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
        # pylint: disable-msg=W0201,W0212
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
        # pylint: disable-msg=W0201,W0212
        currentHourlyFee = self.items[0].hourlyFee() if len(self.items) == 1 else 0
        self._hourlyFeeEntry = entry.AmountEntry(self, currentHourlyFee)
        self._hourlyFeeSync = attributesync.AttributeSync('hourlyFee',
            self._hourlyFeeEntry, currentHourlyFee, self.items,
            command.EditHourlyFeeCommand, wx.EVT_KILL_FOCUS, 
            self.items[0].hourlyFeeChangedEventType())
        self.addEntry(_('Hourly fee'), self._hourlyFeeEntry, flags=[None, wx.ALL])
        
    def addFixedFeeEntry(self):
        # pylint: disable-msg=W0201,W0212
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
        self.viewer.detach()
        # Don't notify the viewer about any changes anymore, it's about
        # to be deleted, but don't delete it too soon.
        wx.CallAfter(self.deleteViewer)
        event.Skip()        
        
    def deleteViewer(self):
        if hasattr(self, 'viewer'):
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

    def getIsItemChecked(self, category): # pylint: disable-msg=W0621
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
        return command.AddAttachmentCommand(None, [self.attachmentOwner], *args, **kwargs)
    
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
    
    def __init__(self, parent, items, taskFile, settings, itemsAreNew):
        self.items = items
        self.settings = settings
        super(EditBook, self).__init__(parent)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        pageNames = self.addPages(taskFile, itemsAreNew)
        self.loadPerspective(pageNames)
        
    def addPages(self, taskFile, itemsAreNew):
        pageNames = []
        for pageName in self.allPageNamesInUserOrder():
            if self.shouldCreatePage(pageName):
                page = self.createPage(pageName, taskFile, itemsAreNew)
                self.AddPage(page, page.pageTitle, page.pageIcon)
                pageNames.append(pageName)
        return pageNames

    def getPage(self, pageName):
        for index in range(self.GetPageCount()):
            if pageName == self[index].pageName:
                return self[index]
        return None
        
    def allPageNamesInUserOrder(self):
        ''' Return all pages names in the order stored in the settings. The
            settings may not contain all pages (e.g. because a feature was
            turned off by the user) so we add the missing pages if necessary. '''
        pageNamesInUserOrder = self.settings.getlist('editor', '%spages' % self.object)
        remainingPageNames = self.allPageNames[:]
        for pageName in pageNamesInUserOrder:
            try:
                remainingPageNames.remove(pageName)
            except ValueError:
                pass # Page doesn't exist anymore
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

    def createPage(self, pageName, taskFile, itemsAreNew):
        if pageName == 'subject':
            return self.createSubjectPage()
        elif pageName == 'dates':
            return DatesPage(self.items, self, self.settings, itemsAreNew) 
        elif pageName == 'prerequisites':
            return PrerequisitesPage(self.items, self, taskFile, self.settings,
                                     settingsSection='prerequisiteviewerin%seditor' % self.object)
        elif pageName == 'progress':    
            return ProgressPage(self.items, self)
        elif pageName == 'categories':
            return CategoriesPage(self.items, self, taskFile, self.settings,
                                  settingsSection='categoryviewerin%seditor' % self.object)
        elif pageName == 'budget':                 
            return BudgetPage(self.items, self)
        elif pageName == 'effort':        
            return EffortPage(self.items, self, taskFile, self.settings,
                              settingsSection='effortviewerin%seditor' % self.object)
        elif pageName == 'notes':
            return NotesPage(self.items, self, taskFile, self.settings,
                             settingsSection='noteviewerin%seditor' % self.object)
        elif pageName == 'attachments':
            return AttachmentsPage(self.items, self, taskFile, self.settings,
                                   settingsSection='attachmentviewerin%seditor' % self.object)
        elif pageName == 'appearance':
            return TaskAppearancePage(self.items, self)
        
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
    
    def loadPerspective(self, pageNames):
        perspectiveKey = self.perspectiveKey(pageNames) 
        perspective = self.settings.getdict('%sdialog'%self.object, 'perspectives').get(perspectiveKey, '')
        if perspective:
            try:
                self.LoadPerspective(perspective)
            except:
                pass # pylint: disable-msg=W0702

    def savePerspective(self, pageNames):
        perspectives = self.settings.getdict('%sdialog'%self.object, 'perspectives')
        perspectiveKey = self.perspectiveKey(pageNames)
        perspectives[perspectiveKey] = self.SavePerspective() 
        self.settings.setdict('%sdialog'%self.object, 'perspectives', perspectives)
        
    @staticmethod
    def perspectiveKey(pageNames):
        return '_'.join(pageNames + ['perspective'])
    
    def onClose(self, event):
        event.Skip()
        removeInstance = patterns.Publisher().removeInstance
        for page in self:
            removeInstance(page)
        pageNames = [self[index].pageName for index in range(self.GetPageCount())]
        self.settings.setlist('editor', '%spages'%self.object, pageNames)
        self.savePerspective(pageNames)


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
        return AttachmentSubjectPage(self.items, self, self.settings)
    
    def isDisplayingItemOrChildOfItem(self, targetItem):
        return targetItem in self.items
    
        
class EffortEditBook(Page):
    object = 'effort'
    columns = 3
    
    def __init__(self, parent, efforts, taskFile, settings, itemsAreNew, *args, **kwargs): # pylint: disable-msg=W0613
        self._effortList = taskFile.efforts()
        taskList = taskFile.tasks()
        self._taskList = task.TaskList(taskList)
        self._taskList.extend([effort.task() for effort in efforts if effort.task() not in taskList])
        self._settings = settings
        self._taskFile = taskFile
        super(EffortEditBook, self).__init__(efforts, parent, *args, **kwargs)
        
    def getPage(self, pageName): # pylint: disable-msg=W0613
        return None # An EffortEditBook is not really a notebook...
        
    def addEntries(self):
        self.addTaskEntry()
        self.addStartAndStopEntries()
        self.addDescriptionEntry()

    def addTaskEntry(self):
        ''' Add an entry for changing the task that this effort record
            belongs to. '''
        # pylint: disable-msg=W0201,W0212
        panel = wx.Panel(self)
        currentTask = self.items[0].task()
        self._taskEntry = entry.TaskEntry(panel,
            rootTasks=self._taskList.rootItems(), selectedTask=currentTask)
        self._taskSync = attributesync.AttributeSync('task', self._taskEntry,
            currentTask, self.items, command.ChangeTaskCommand,
            entry.EVT_TASKENTRY, self.items[0].taskChangedEventType())
        editTaskButton = wx.Button(panel, label=_('Edit task'))
        editTaskButton.Bind(wx.EVT_BUTTON, self.onEditTask)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(self._taskEntry, proportion=1,
                       flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3, -1))
        panelSizer.Add(editTaskButton, proportion=0,
                       flag=wx.ALIGN_CENTER_VERTICAL)
        panel.SetSizerAndFit(panelSizer)
        self.addEntry(_('Task'), panel, flags=[None, wx.ALL|wx.EXPAND])

    def addStartAndStopEntries(self):
        # pylint: disable-msg=W0201,W0142
        dateTimeEntryKwArgs = dict(showSeconds=True)
        flags = [None, wx.ALIGN_RIGHT | wx.ALL, wx.ALIGN_LEFT | wx.ALL, None]
        
        currentStartDateTime = self.items[0].getStart()
        self._startDateTimeEntry = entry.DateTimeEntry(self, self._settings,
            currentStartDateTime, noneAllowed=False, **dateTimeEntryKwArgs)
        self._startDateTimeSync = attributesync.AttributeSync('datetime',
            self._startDateTimeEntry, currentStartDateTime, self.items,
            command.ChangeEffortStartDateTimeCommand, entry.EVT_DATETIMEENTRY,
            'effort.start', 'getStart')
        self._startDateTimeEntry.Bind(entry.EVT_DATETIMEENTRY, self.onDateTimeChanged)        
        startFromLastEffortButton = self._createStartFromLastEffortButton()
        self.addEntry(_('Start'), self._startDateTimeEntry,
            startFromLastEffortButton, flags=flags)

        self._previousStopDateTime = currentStopDateTime = self.items[0].getStop()
        self._stopDateTimeEntry = entry.DateTimeEntry(self, self._settings, 
            currentStopDateTime, noneAllowed=True, **dateTimeEntryKwArgs)
        self._stopDateTimeSync = attributesync.AttributeSync('datetime',
            self._stopDateTimeEntry, currentStopDateTime, self.items,
            command.ChangeEffortStopDateTimeCommand, entry.EVT_DATETIMEENTRY,
            'effort.stop', 'getStop')
        self._stopDateTimeEntry.Bind(entry.EVT_DATETIMEENTRY, self.onStopDateTimeChanged)
        self._invalidPeriodMessage = self._createInvalidPeriodMessage()
        self.addEntry(_('Stop'), self._stopDateTimeEntry, 
                      self._invalidPeriodMessage, flags=flags)
            
    def _createStartFromLastEffortButton(self):
        button = wx.Button(self, label=_('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort, button)
        if self._effortList.maxDateTime() is None:
            button.Disable()
        return button
            
    def _createInvalidPeriodMessage(self):
        text = wx.StaticText(self, label='')
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(font)
        return text

    def onStartFromLastEffort(self, event): # pylint: disable-msg=W0613
        maxDateTime = self._effortList.maxDateTime()
        if self._startDateTimeEntry.GetValue() != maxDateTime:
            self._startDateTimeEntry.SetValue(self._effortList.maxDateTime())
            self._startDateTimeSync.onAttributeEdited(event)
        self.onDateTimeChanged(event)

    def onStopDateTimeChanged(self, *args, **kwargs):
        # When the user checks the stop datetime, enter the current datetime
        if self._stopDateTimeEntry.GetValue() != date.DateTime() and self._previousStopDateTime == date.DateTime():
            self._stopDateTimeEntry.SetValue(date.Now())
        self._previousStopDateTime = self._stopDateTimeEntry.GetValue() # pylint: disable-msg=W0201
        self.onDateTimeChanged(*args, **kwargs)

    def onDateTimeChanged(self, event):
        event.Skip()
        self.updateInvalidPeriodMessage()
                    
    def updateInvalidPeriodMessage(self):
        message = '' if self.validPeriod() else _('Warning: start must be earlier than stop')
        self._invalidPeriodMessage.SetLabel(message)
                
    def validPeriod(self):
        try:
            return self._startDateTimeEntry.GetValue() < self._stopDateTimeEntry.GetValue()
        except AttributeError:
            return True # Entries not created yet

    def onEditTask(self, event): # pylint: disable-msg=W0613
        taskToEdit = self._taskEntry.GetValue()
        TaskEditor(None, [taskToEdit], self._settings, self._taskFile.tasks(), 
            self._taskFile).Show()

    def addDescriptionEntry(self):
        # pylint: disable-msg=W0201
        currentDescription = self.items[0].description() if len(self.items) == 1 else _('Edit to change all descriptions')
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, currentDescription)
        self._descriptionEntry.SetSizeHints(300, 150)
        self._descriptionSync = attributesync.AttributeSync('description', 
            self._descriptionEntry, currentDescription, self.items,
            command.EditDescriptionCommand, wx.EVT_KILL_FOCUS,
            self.items[0].descriptionChangedEventType())
        self.addEntry(_('Description'), self._descriptionEntry, growable=True)
        
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
    
    
class Editor(widgets.Dialog):
    EditBookClass = lambda *args: 'Subclass responsibility'
    singular_title = 'Subclass responsibility %s'
    plural_title = 'Subclass responsibility'
    
    def __init__(self, parent, items, settings, container, taskFile, *args, **kwargs):
        self._items = items
        self._settings = settings
        self._taskFile = taskFile
        self.__itemsAreNew = kwargs.get('itemsAreNew', False)
        self._callAfter = kwargs.get('callAfter', wx.CallAfter)
        super(Editor, self).__init__(parent, self.title(), buttonTypes=wx.ID_CLOSE, *args, **kwargs)
        columnName = kwargs.get('columnName', '')
        self._interior.setFocus(columnName)
        patterns.Publisher().registerObserver(self.onItemRemoved,
            eventType=container.removeItemEventType(), eventSource=container)
        if len(self._items) == 1:
            patterns.Publisher().registerObserver(self.onSubjectChanged,
                                                  eventType=self._items[0].subjectChangedEventType(),
                                                  eventSource=self._items[0])
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # On Mac OS X, the frame opens by default in the top-left
        # corner of the first display. This gets annoying on a
        # 2560x1440 27" + 1920x1200 24" dual screen...

        # On Windows, for some reason, the Python 2.5 and 2.6 versions
        # of wxPython 2.8.11.0 behave differently; on Python 2.5 the
        # frame opens centered on its parent but on 2.6 it opens on
        # the first display!

        # On Linux this is not needed but doesn't do any harm.
        self.CentreOnParent()
        self.createUICommands()
        self._dimensionsTracker = windowdimensionstracker.WindowSizeAndPositionTracker(self, settings, '%sdialog' % self.EditBookClass.object)
        
    def createUICommands(self):
        # FIXME: keyboard shortcuts are hardcoded here, but they can be 
        # changed in the translations
        # FIXME: there are more keyboard shortcuts that don't work in dialogs atm 
        newEffortId = wx.NewId()
        table = wx.AcceleratorTable([(wx.ACCEL_CMD, ord('Z'), wx.ID_UNDO),
                                     (wx.ACCEL_CMD, ord('Y'), wx.ID_REDO),
                                     (wx.ACCEL_CMD, ord('E'), newEffortId)])
        self._interior.SetAcceleratorTable(table)
        # pylint: disable-msg=W0201
        self.undoCommand = uicommand.EditUndo()
        self.redoCommand = uicommand.EditRedo()
        effortPage = self._interior.getPage('effort') 
        effortViewer = effortPage.viewer if effortPage else None 
        self.newEffortCommand = uicommand.EffortNew(viewer=effortViewer,
                                                    taskList=self._taskFile.tasks(),
                                                    effortList=self._taskFile.efforts(),
                                                    settings=self._settings)
        self.undoCommand.bind(self._interior, wx.ID_UNDO)
        self.redoCommand.bind(self._interior, wx.ID_REDO)
        self.newEffortCommand.bind(self._interior, newEffortId)

    def createInterior(self):
        return self.EditBookClass(self._panel, self._items, 
                                  self._taskFile, self._settings, self.__itemsAreNew)

    def onClose(self, event):
        event.Skip()
        patterns.Publisher().removeInstance(self)
        # On Mac OS X, the text control does not lose focus when
        # destroyed...
        if operating_system.isMac():
            self._interior.SetFocusIgnoringChildren()
                        
    def onItemRemoved(self, event):
        ''' The item we're editing or one of its ancestors has been removed or 
            is hidden by a filter. If the item is really removed, close the tab 
            of the item involved and close the whole editor if there are no 
            tabs left. '''
        if self: # Prevent _wxPyDeadObject TypeError
            self._callAfter(self.closeIfItemIsDeleted, event.values())
        
    def closeIfItemIsDeleted(self, items):
        for item in items:
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

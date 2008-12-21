'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
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

import wx, datetime, os.path, sys
from taskcoachlib import widgets, patterns
from taskcoachlib.gui import render, viewer, uicommand
from taskcoachlib.widgets import draganddrop
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, category, date, note, attachment
from taskcoachlib.thirdparty import desktop
import entry


class Page(object):
    def entries(self):
        ''' A mapping of names of columns to entries on this editor page. '''
        return dict()
    
    def setFocusOnEntry(self, columnName):
        try:
            theEntry = self.entries()[columnName]
        except KeyError:
            return
        try:
            theEntry.SetSelection(-1, -1) # Select all text
        except (AttributeError, TypeError):
            pass # Not a TextCtrl
        theEntry.SetFocus()

    def ok(self):
        pass
       
        
class PageWithHeaders(Page, widgets.PanelWithBoxSizer):
    def __init__(self, parent, item, *args, **kwargs):
        super(PageWithHeaders, self).__init__(parent, *args, **kwargs) 
        self.item = item

    def addHeaders(self, box):
        headers = ['', self.headerForNonRecursiveAttributes]
        if self.item.children():
            headers.append(self.headerForRecursiveAttributes)
        else:
            headers.append('')
        for header in headers:
            box.add(header)
    


class TaskHeaders(object):
    headerForNonRecursiveAttributes = _('For this task')
    headerForRecursiveAttributes = _('For this task including all subtasks')
    

class NoteHeaders(object):
    headerForNonRecursiveAttributes = _('For this note')
    headerForRecursiveAttributes = _('For this note including all subnotes')


class SubjectPage(Page, widgets.BookPage):
    def addSubjectEntry(self):
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self.item.subject())
        self.addEntry(_('Subject'), self._subjectEntry, 
                      flags=[None, wx.ALL|wx.EXPAND])

    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, 
            self.item.description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)

    def addColorEntry(self):
        currentColor = self.item.color(recursive=False)
        self._colorCheckBox = wx.CheckBox(self, label=_('Use this color:'))
        self._colorCheckBox.SetValue(currentColor is not None)
        self._colorButton = wx.ColourPickerCtrl(self, -1,
            currentColor or wx.WHITE, size=(40,-1))
        self._colorButton.Bind(wx.EVT_COLOURPICKER_CHANGED,
            lambda event: self._colorCheckBox.SetValue(True))
        self.addEntry(_('Color'), self._colorCheckBox, self._colorButton)

    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)

    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)

    def ok(self):
        self.item.setSubject(self._subjectEntry.GetValue())
        self.item.setDescription(self._descriptionEntry.GetValue())
        if self._colorCheckBox.IsChecked():
            color = self._colorButton.GetColour()
        else:
            color = None
        self.item.setColor(color)
        super(SubjectPage, self).ok()
                        
    def entries(self):
        return dict(subject=self._subjectEntry, 
                    description=self._descriptionEntry)

    
class TaskSubjectPage(SubjectPage):
    def __init__(self, parent, task, *args, **kwargs):
        self.item = task
        super(TaskSubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.addSubjectEntry()
        self.addDescriptionEntry()
        self.addPriorityEntry()
        self.addColorEntry()
        self.fit()
         
    def addPriorityEntry(self):
        self._prioritySpinner = widgets.SpinCtrl(self,
            initial=self.item.priority())
        self.addEntry(_('Priority'), self._prioritySpinner, 
            flags=[None, wx.ALL|wx.EXPAND])
    
    def ok(self):
        self.item.setPriority(self._prioritySpinner.GetValue())
        super(TaskSubjectPage, self).ok()
 
    def entries(self):
        entries = super(TaskSubjectPage, self).entries()
        entries['priority'] = entries['totalPriority'] = self._prioritySpinner
        return entries
            

class CategorySubjectPage(SubjectPage):
    def __init__(self, parent, category, *args, **kwargs):
        self.item = self._category = category
        super(CategorySubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.addSubjectEntry()
        self.addDescriptionEntry()
        self.addColorEntry()
        self.fit()


class NoteSubjectPage(SubjectPage):
    def __init__(self, parent, theNote, *args, **kwargs):
        super(NoteSubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.item = self._note = theNote
        self.addSubjectEntry()
        self.addDescriptionEntry()
        self.addColorEntry()
        self.fit()
            

class AttachmentSubjectPage(SubjectPage):
    def __init__(self, parent, theAttachment, basePath, *args, **kwargs):
        super(AttachmentSubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.item = self._attachment = theAttachment
        self.basePath = basePath
        self.addSubjectEntry()
        self.addLocationEntry()
        self.addDescriptionEntry()
        self.addColorEntry()
        self.fit()

    def addLocationEntry(self):
        panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._locationEntry = widgets.SingleLineTextCtrl(panel,
                                                         self._attachment.location())
        sizer.Add(self._locationEntry, 1, wx.ALL, 3)
        if self._attachment.type_ == 'file':
            button = wx.Button(panel, wx.ID_ANY, _('Browse'))
            sizer.Add(button, 0, wx.ALL, 3)
            wx.EVT_BUTTON(button, wx.ID_ANY, self.OnSelectLocation)
        panel.SetSizer(sizer)
        self.addEntry(_('Location'), panel, flags=[None, wx.ALL|wx.EXPAND])

    def ok(self):
        self._attachment.setLocation(self._locationEntry.GetValue())
        super(AttachmentSubjectPage, self).ok()

    def OnSelectLocation(self, evt):
        filename = widgets.AttachmentSelector()
        if filename:
            if self.basePath:
                filename = attachment.getRelativePath(filename, self.basePath)
            self._subjectEntry.SetValue(os.path.split(filename)[-1])
            self._locationEntry.SetValue(filename)


class DatesPage(PageWithHeaders, TaskHeaders):
    def __init__(self, parent, task, *args, **kwargs):
        super(DatesPage, self).__init__(parent, task, *args, **kwargs)
        datesBox = self.addDatesBox(task)
        reminderBox = self.addReminderBox(task)
        recurrenceBox = self.addRecurrenceBox(task)

        for box in datesBox, reminderBox, recurrenceBox:
            box.fit()
            self.add(box, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
    
    def addDatesBox(self, task):
        datesBox = widgets.BoxWithFlexGridSizer(self, label=_('Dates'), cols=3)
        self.addHeaders(datesBox)
        for label, taskMethodName in [(_('Start date'), 'startDate'),
                                      (_('Due date'), 'dueDate'),
                                      (_('Completion date'), 'completionDate')]:
            datesBox.add(label)
            taskMethod = getattr(task, taskMethodName)
            dateEntry = entry.DateEntry(datesBox, taskMethod(),
                                        callback=self.onDateChanged)
            setattr(self, '_%sEntry'%taskMethodName, dateEntry)
            datesBox.add(dateEntry)
            if task.children():
                recursiveDateEntry = entry.DateEntry(datesBox,
                    taskMethod(recursive=True), readonly=True)
            else:
                recursiveDateEntry = (0, 0)
            datesBox.add(recursiveDateEntry)
        return datesBox
        
    def addReminderBox(self, task):
        reminderBox = widgets.BoxWithFlexGridSizer(self, label=_('Reminder'), 
                                                   cols=2)
        reminderBox.add(_('Reminder'))
        self._reminderDateTimeEntry = widgets.DateTimeCtrl(reminderBox,
            task.reminder())
        # If the user has not set a reminder, make sure that the default 
        # date time in the reminder entry is a reasonable suggestion:
        if self._reminderDateTimeEntry.GetValue() == date.DateTime.max:
            self.suggestReminder()
        reminderBox.add(self._reminderDateTimeEntry)
        return reminderBox
        
    def addRecurrenceBox(self, task):
        recurrenceBox = widgets.BoxWithFlexGridSizer(self,
            label=_('Recurrence'), cols=2)
        recurrenceBox.add(_('Recurrence'))
        panel = wx.Panel(recurrenceBox)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._recurrenceEntry = wx.Choice(panel,
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly'), _('Yearly')])        
        self._recurrenceEntry.Bind(wx.EVT_CHOICE, self.onRecurrenceChanged)
        panelSizer.Add(self._recurrenceEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        staticText = wx.StaticText(panel, label=_(', every'))
        panelSizer.Add(staticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceFrequencyEntry = widgets.SpinCtrl(panel, size=(50,-1), 
                                                          min=1)
        panelSizer.Add(self._recurrenceFrequencyEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceStaticText = wx.StaticText(panel, label='reserve some space')
        panelSizer.Add(self._recurrenceStaticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3, -1))
        self._recurrenceSameWeekdayCheckBox = wx.CheckBox(panel, 
            label=_('keeping dates on the same weekday'))
        panelSizer.Add(self._recurrenceSameWeekdayCheckBox, proportion=1, 
                       flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        panel.SetSizerAndFit(panelSizer)
        self._recurrenceSizer = panelSizer

        recurrenceBox.add(panel)
        recurrenceBox.add(_('Maximum number of recurrences'))
        panel = wx.Panel(recurrenceBox)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._maxRecurrenceCheckBox = wx.CheckBox(panel)
        self._maxRecurrenceCheckBox.Bind(wx.EVT_CHECKBOX, self.onMaxRecurrenceChecked)
        panelSizer.Add(self._maxRecurrenceCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._maxRecurrenceCountEntry = widgets.SpinCtrl(panel, size=(50,-1), 
                                                         min=1)
        panelSizer.Add(self._maxRecurrenceCountEntry)
        panel.SetSizerAndFit(panelSizer)
        recurrenceBox.add(panel)

        self.setRecurrence(task.recurrence())
        return recurrenceBox
    
    def entries(self):
        return dict(startDate=self._startDateEntry, dueDate=self._dueDateEntry,
                    completionDate=self._completionDateEntry, 
                    timeLeft=self._dueDateEntry, 
                    reminder=self._reminderDateTimeEntry, 
                    recurrence=self._recurrenceEntry)
    
    def onRecurrenceChanged(self, event):
        event.Skip()
        recurrenceOn = event.String != _('None')
        self._maxRecurrenceCheckBox.Enable(recurrenceOn)
        self._recurrenceFrequencyEntry.Enable(recurrenceOn)
        self._maxRecurrenceCountEntry.Enable(recurrenceOn and \
            self._maxRecurrenceCheckBox.IsChecked())
        self.updateRecurrenceLabel()

    def onMaxRecurrenceChecked(self, event):
        event.Skip()
        maxRecurrenceOn = event.IsChecked()
        self._maxRecurrenceCountEntry.Enable(maxRecurrenceOn)

    def onDateChanged(self, event):
        ''' Called when one of the DateEntries is changed by the user. Update
            the suggested reminder if no reminder was set by the user. '''
        event.Skip()
        if self._reminderDateTimeEntry.GetValue() == date.DateTime.max:
            self.suggestReminder()

    def ok(self):
        recurrenceDict = {0: '', 1: 'daily', 2: 'weekly', 3: 'monthly', 4: 'yearly'}
        kwargs = dict(unit=recurrenceDict[self._recurrenceEntry.Selection])
        if self._maxRecurrenceCheckBox.IsChecked():
            kwargs['max'] =self._maxRecurrenceCountEntry.Value
        kwargs['amount'] = self._recurrenceFrequencyEntry.Value
        kwargs['sameWeekday'] = self._recurrenceSameWeekdayCheckBox.IsChecked()
        self.item.setRecurrence(date.Recurrence(**kwargs))
        self.item.setStartDate(self._startDateEntry.get())
        self.item.setDueDate(self._dueDateEntry.get())
        self.item.setCompletionDate(self._completionDateEntry.get())
        self.item.setReminder(self._reminderDateTimeEntry.GetValue())

    def setReminder(self, reminder):
        self._reminderDateTimeEntry.SetValue(reminder)

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
        if recurrence.unit == 'monthly':
            self._recurrenceSameWeekdayCheckBox.Value = recurrence.sameWeekday
        else:
            # If recurrence is not monthly, set same week day to False
            self._recurrenceSameWeekdayCheckBox.Value = False
        self.updateRecurrenceLabel()

    def updateRecurrenceLabel(self):
        recurrenceDict = {0: _('period,'), 1: _('day(s),'), 2: _('week(s),'),
                          3: _('month(s),'), 4: _('year(s),')}
        recurrenceLabel = recurrenceDict[self._recurrenceEntry.Selection]
        self._recurrenceStaticText.SetLabel(recurrenceLabel)
        self._recurrenceSameWeekdayCheckBox.Enable(self._recurrenceEntry.Selection == 3)
        self._recurrenceSizer.Layout()

    def suggestReminder(self):
        ''' suggestReminder populates the reminder entry with a reasonable
            suggestion for a reminder date and time, but does not enable the
            reminder entry. '''
        # The suggested date for the reminder is the first date from the
        # list of candidates that is a real date:
        candidates = [self._dueDateEntry.get(), self._startDateEntry.get(),
                      date.Tomorrow()]
        suggestedDate = [candidate for candidate in candidates \
                         if date.Today() <= candidate < date.Date()][0]
        # Add a suggested time of 8:00 AM:
        suggestedDateTime = date.DateTime(suggestedDate.year,
                                          suggestedDate.month,
                                          suggestedDate.day, 8, 0, 0)
        # Now, make sure the suggested date time is set in the control
        self.setReminder(suggestedDateTime)
        # And then disable the control (because the SetValue in the
        # previous statement enables the control)
        self.setReminder(None)
        # Now, when the user clicks the check box to enable the
        # control it will show the suggested date time


class BudgetPage(PageWithHeaders, TaskHeaders):
    def __init__(self, parent, task, *args, **kwargs):
        super(BudgetPage, self).__init__(parent, task, *args, **kwargs)
        # Boxes:
        budgetBox = widgets.BoxWithFlexGridSizer(self, label=_('Budget'), cols=3)
        revenueBox = widgets.BoxWithFlexGridSizer(self, label=_('Revenue'), cols=3)
        # Editable entries:
        self._budgetEntry = entry.TimeDeltaEntry(budgetBox, task.budget())
        self._hourlyFeeEntry = entry.AmountEntry(revenueBox, task.hourlyFee())
        self._fixedFeeEntry = entry.AmountEntry(revenueBox, task.fixedFee())
        # Readonly entries:
        if task.children():
            recursiveBudget = render.budget(task.budget(recursive=True))
            recursiveTimeSpent = render.timeSpent(task.timeSpent(recursive=True))
            recursiveBudgetLeft = render.budget(task.budgetLeft(recursive=True))
            recursiveFixedFee = render.amount(task.fixedFee(recursive=True))
            recursiveRevenue = render.amount(task.revenue(recursive=True))
        else:
            recursiveBudget = recursiveTimeSpent = recursiveBudgetLeft = \
            recursiveFixedFee = recursiveRevenue = ''
        # Fill the boxes:
        self.addHeaders(budgetBox)
        for eachEntry in [_('Budget'), self._budgetEntry, recursiveBudget,
                          _('Time spent'), render.budget(task.timeSpent()), 
                          recursiveTimeSpent, _('Budget left'), 
                          render.budget(task.budgetLeft()),
                          recursiveBudgetLeft]:
            budgetBox.add(eachEntry, flag=wx.ALIGN_RIGHT)

        self.addHeaders(revenueBox)
        for eachEntry in [_('Hourly fee'), self._hourlyFeeEntry, '',
                          _('Fixed fee'), self._fixedFeeEntry, 
                          recursiveFixedFee, _('Revenue'), 
                          render.amount(task.revenue()), recursiveRevenue]:
            revenueBox.add(eachEntry, flag=wx.ALIGN_RIGHT)
        for box in budgetBox, revenueBox:
            box.fit()
            self.add(box, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
        
    def entries(self):
        return dict(budget=self._budgetEntry, 
                    totalBudget=self._budgetEntry,
                    budgetLeft=self._budgetEntry, 
                    totalBudgetLeft=self._budgetEntry, 
                    hourlyFee=self._hourlyFeeEntry, 
                    fixedFee=self._fixedFeeEntry, 
                    totalFixedFee=self._fixedFeeEntry, 
                    revenue=self._hourlyFeeEntry, 
                    totalRevenue=self._hourlyFeeEntry)
        
    def ok(self):
        self.item.setBudget(self._budgetEntry.get())
        self.item.setHourlyFee(self._hourlyFeeEntry.get())
        self.item.setFixedFee(self._fixedFeeEntry.get())


class EffortPage(PageWithHeaders, TaskHeaders):
    def __init__(self, parent, theTask, taskFile, settings, *args, **kwargs):
        super(EffortPage, self).__init__(parent, theTask, *args, **kwargs)
        self.effortViewer = viewer.EffortViewer(self, taskFile,
            settings, settingsSection='effortviewerintaskeditor',
            tasksToShowEffortFor=task.TaskList([theTask]))
        self.add(self.effortViewer, proportion=1, flag=wx.EXPAND|wx.ALL, 
                 border=5)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self.fit()

    def entries(self):
        return dict(timeSpent=self.effortViewer, 
                    totalTimeSpent=self.effortViewer)
        
    def onClose(self, event):
        # Don't notify the viewer about any changes anymore, it's about
        # to be deleted.
        self.effortViewer.detach()
        event.Skip()


class LocalDragAndDropFix(object):
    def __init__(self, *args, **kwargs):
        super(LocalDragAndDropFix, self).__init__(*args, **kwargs)

        # For  a reason  that completely  escapes me,  under  MSW, the
        # viewers don't act  as drop targets in the  notebook. So make
        # the containing panel do.

        if '__WXMSW__' in wx.PlatformInfo:
            dropTarget = draganddrop.DropTarget(self.onDropURL,
                                                self.onDropFiles,
                                                self.onDropMail)
            self.SetDropTarget(dropTarget)


class LocalCategoryViewer(LocalDragAndDropFix, viewer.BaseCategoryViewer):
    def __init__(self, item, *args, **kwargs):
        self.item = item
        super(LocalCategoryViewer, self).__init__(*args, **kwargs)
        self.widget.ExpandAll()
    
    def getIsItemChecked(self, index):
        item = self.getItemWithIndex(index)
        if isinstance(item, category.Category):
            return item in self.item.categories()
        return False

    def createCategoryPopupMenu(self):
        return super(LocalCategoryViewer, self).createCategoryPopupMenu(True)

    def onCheck(self, event):
        # We don't want the 'main' category viewer to be affected by
        # what's happening here.
        pass


class CategoriesPage(PageWithHeaders):
    def __init__(self, parent, item, taskFile, settings, *args, **kwargs):
        super(CategoriesPage, self).__init__(parent, item, *args, **kwargs)
        self.__categories = category.CategorySorter(taskFile.categories())
        categoriesBox = widgets.BoxWithBoxSizer(self, label=_('Categories'))
        self._categoryViewer = LocalCategoryViewer(item, categoriesBox,
                                       taskFile, settings,
                                       settingsSection=self.settingsSection())
        categoriesBox.add(self._categoryViewer, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.fit()
        self.add(categoriesBox)
        self.fit()
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self._categoryViewer.detach()
        event.Skip()

    def entries(self):
        return dict(categories=self._categoryViewer,
                    totalCategories=self._categoryViewer) 

    def ok(self):
        treeCtrl = self._categoryViewer.widget
        treeCtrl.ExpandAll()
        for categoryNode in treeCtrl.GetItemChildren(recursively=True):
            categoryIndex = treeCtrl.GetIndexOfItem(categoryNode)
            category = self._categoryViewer.getItemWithIndex(categoryIndex)
            if categoryNode.IsChecked():
                category.addCategorizable(self.item)
                self.item.addCategory(category)
            else:
                category.removeCategorizable(self.item)
                self.item.removeCategory(category)


class TaskCategoriesPage(CategoriesPage, TaskHeaders):
    def settingsSection(self):
        return 'categoryviewerintaskeditor'


class NoteCategoriesPage(CategoriesPage, NoteHeaders):
    def settingsSection(self):
        return 'categoryviewerinnoteeditor'


class LocalAttachmentViewer(LocalDragAndDropFix, viewer.AttachmentViewer):
    pass


class AttachmentsPage(PageWithHeaders):
    def __init__(self, parent, item, settings, taskFile, *args, **kwargs):
        settingsSection = kwargs.pop('settingsSection')
        super(AttachmentsPage, self).__init__(parent, item, *args, **kwargs)
        self.attachmentsList = attachment.AttachmentList(item.attachments())
        attachmentsBox = widgets.BoxWithBoxSizer(self, label=_('Attachments'))
        self._attachmentViewer = LocalAttachmentViewer(attachmentsBox,
                                                       taskFile, settings,
                                                       settingsSection=settingsSection,
                                                       attachmentsToShow=self.attachmentsList)
        attachmentsBox.add(self._attachmentViewer, proportion=1, flag=wx.EXPAND|wx.ALL)
        attachmentsBox.fit()
        self.add(attachmentsBox)
        self.fit()
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)

    def entries(self):
        return dict(attachments=self._attachmentViewer)

    def ok(self):
        self.item.setAttachments(self.attachmentsList)
        super(AttachmentsPage, self).ok()

    def onClose(self, event):
        self._attachmentViewer.detach()
        event.Skip()


class LocalNoteViewer(LocalDragAndDropFix, viewer.BaseNoteViewer):
    pass


class NotesPage(PageWithHeaders):
    def __init__(self, parent, item, settings, taskFile, *args, **kwargs):
        super(NotesPage, self).__init__(parent, item, *args, **kwargs)
        notesBox = widgets.BoxWithBoxSizer(self, label=_('Notes'))
        self.notes = note.NoteContainer(item.notes())
        self.noteViewer = LocalNoteViewer(notesBox, taskFile, settings, 
            settingsSection='noteviewerintaskeditor',
            notesToShow=self.notes)
        notesBox.add(self.noteViewer, flag=wx.EXPAND|wx.ALL, proportion=1)
        notesBox.fit()
        self.add(notesBox, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self.fit()
    
    def entries(self):
        return dict(notes=self.noteViewer)
        
    def onClose(self, event):
        # Don't notify the viewer about any changes anymore, it is about
        # to be deleted.
        self.noteViewer.detach()
        event.Skip()
        
    def ok(self):
        self.item.setNotes(list(self.notes.rootItems()))


class BehaviorPage(PageWithHeaders, TaskHeaders):
    def __init__(self, parent, task, *args, **kwargs):
        super(BehaviorPage, self).__init__(parent, task, *args, **kwargs)
        behaviorBox = widgets.BoxWithFlexGridSizer(self,
            label=_('Task behavior'), cols=2)
        choice = self._markTaskCompletedEntry = wx.Choice(behaviorBox)
        for choiceValue, choiceText in \
                [(None, _('Use application-wide setting')),
                 (False, _('No')), (True, _('Yes'))]:
            choice.Append(choiceText, choiceValue)
            if choiceValue == task.shouldMarkCompletedWhenAllChildrenCompleted:
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND:
            # Force a selection if necessary:
            choice.SetSelection(0)
        behaviorBox.add(_('Mark task completed when all children are'
                          ' completed?'))
        behaviorBox.add(choice)
        behaviorBox.fit()
        self.add(behaviorBox, border=5)
        self.fit()

    def ok(self):
        self.item.shouldMarkCompletedWhenAllChildrenCompleted = \
            self._markTaskCompletedEntry.GetClientData( \
                self._markTaskCompletedEntry.GetSelection())


class TaskEditBook(widgets.Listbook):
    def __init__(self, parent, task, taskFile, settings, *args, **kwargs):
        super(TaskEditBook, self).__init__(parent)
        self.AddPage(TaskSubjectPage(self, task), _('Description'), 'description')
        self.AddPage(DatesPage(self, task), _('Dates'), 'date')
        self.AddPage(TaskCategoriesPage(self, task, taskFile, settings), 
                     _('Categories'), 'category')
        if settings.getboolean('feature', 'effort'):
            self.AddPage(BudgetPage(self, task),
                         _('Budget'), 'budget')
            self.AddPage(EffortPage(self, task, taskFile, settings), 
                         _('Effort'), 'start')
        if settings.getboolean('feature', 'notes'):
            self.AddPage(NotesPage(self, task, settings, taskFile), 
                         _('Notes'), 'note')
        self.AddPage(AttachmentsPage(self, task, settings, taskFile, 
                                     settingsSection='attachmentviewerintaskeditor'), 
                     _('Attachments'), 'attachment')
        self.AddPage(BehaviorPage(self, task), _('Behavior'), 'behavior')
        self.item = task


class EffortEditBook(Page, widgets.BookPage):
    def __init__(self, parent, effort, editor, effortList, taskList, settings,
                 *args, **kwargs):
        super(EffortEditBook, self).__init__(parent, columns=3, *args, **kwargs)
        self._editor = editor
        self.item = self._effort = effort
        self._effortList = effortList
        self._taskList = taskList
        self._settings = settings
        self.addTaskEntry()
        self.addStartAndStopEntries()
        self.addDescriptionEntry()
        self.fit()

    def addTaskEntry(self):
        ''' Add an entry for changing the task that this effort record
            belongs to. '''
        self._taskEntry = entry.TaskComboTreeBox(self,
            rootTasks=self._taskList.rootItems(),
            selectedTask=self._effort.task())
        self.addEntry(_('Task'), self._taskEntry,
                      flags=[None, wx.ALL|wx.EXPAND])

    def addStartAndStopEntries(self):
        starthour = self._settings.getint('view', 'efforthourstart')
        endhour = self._settings.getint('view', 'efforthourend')
        interval = self._settings.getint('view', 'effortminuteinterval')
        self._startEntry = widgets.DateTimeCtrl(self, self._effort.getStart(),
            self.onPeriodChanged, noneAllowed=False,
            starthour=starthour, endhour=endhour, interval=interval)
        startFromLastEffortButton = wx.Button(self,
            label=_('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort,
            startFromLastEffortButton)
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()

        self._stopEntry = widgets.DateTimeCtrl(self, self._effort.getStop(),
            self.onPeriodChanged, noneAllowed=True,
            starthour=starthour, endhour=endhour, interval=interval)

        flags = [None, wx.ALIGN_RIGHT|wx.ALL, wx.ALIGN_LEFT|wx.ALL, None]
        self.addEntry(_('Start'), self._startEntry,
            startFromLastEffortButton,  flags=flags)
        self.addEntry(_('Stop'), self._stopEntry, '', flags=flags)

    def onStartFromLastEffort(self, event):
        self._startEntry.SetValue(self._effortList.maxDateTime())
        self.preventNegativeEffortDuration()

    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self,
            self._effort.description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)

    def ok(self):
        self._effort.setTask(self._taskEntry.GetSelection())
        self._effort.setStart(self._startEntry.GetValue())
        self._effort.setStop(self._stopEntry.GetValue())
        self._effort.setDescription(self._descriptionEntry.GetValue())

    def onPeriodChanged(self, *args, **kwargs):
        if not hasattr(self, '_stopEntry'): # Check that both entries exist
            return
        # We use CallAfter to give the DatePickerCtrl widgets a chance
        # to update themselves
        wx.CallAfter(self.preventNegativeEffortDuration)

    def preventNegativeEffortDuration(self):
        if self._startEntry.GetValue() > self._stopEntry.GetValue():
            self._editor.disableOK()
        else:
            self._editor.enableOK()

    # Fake a Book interface:
    
    def GetPageCount(self):
        return 1 # EffortEditBook has no pages.
    
    def ChangeSelection(self, pageIndex):
        pass
    
    def __getitem__(self, index):
        return self
    
    def entries(self):
        return dict(period=self._stopEntry, task=self._taskEntry,
                    description=self._descriptionEntry,
                    timeSpent=self._stopEntry, totalTimeSpent=self._stopEntry,
                    revenue=self._taskEntry, totalRevenue=self._taskEntry)
    
    
class CategoryEditBook(widgets.Listbook):
    def __init__(self, parent, theCategory, settings, taskFile, *args, **kwargs):
        self.item = theCategory
        super(CategoryEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(CategorySubjectPage(self, theCategory), 
                     _('Description'), 'description')
        if settings.getboolean('feature', 'notes'):
            self.AddPage(NotesPage(self, theCategory, settings, taskFile), 
                         _('Notes'), 'note')
        self.AddPage(AttachmentsPage(self, theCategory, settings, taskFile, 
                                     settingsSection='attachmentviewerincategoryeditor'), 
                     _('Attachments'), 'attachment')


class NoteEditBook(widgets.Listbook):
    def __init__(self, parent, theNote, settings, categories, taskFile, *args, **kwargs):
        self.item = theNote
        super(NoteEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(NoteSubjectPage(self, theNote), _('Description'), 'description')
        self.AddPage(NoteCategoriesPage(self, theNote, taskFile, settings), 
                     _('Categories'), 'category')
        self.AddPage(AttachmentsPage(self, theNote, settings, taskFile, 
                                     settingsSection='attachmentviewerinnoteeditor'),
                     _('Attachments'), 'attachment')


class AttachmentEditBook(widgets.Listbook):
    def __init__(self, parent, theAttachment, settings, taskFile,
                 *args, **kwargs):
        self.item = theAttachment
        super(AttachmentEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(AttachmentSubjectPage(self, theAttachment,
                                           settings.get('file', 'attachmentbase')), 
                     _('Description'), 'description')
        if settings.getboolean('feature', 'notes'):
            self.AddPage(NotesPage(self, theAttachment, settings, taskFile), 
                         _('Notes'), 'note')


class EditorWithCommand(widgets.NotebookDialog):
    def __init__(self, parent, command, container, *args, **kwargs):
        self._command = command
        super(EditorWithCommand, self).__init__(parent, command.name(), 
                                                *args, **kwargs)
        columnName = kwargs.get('columnName', '')
        if columnName:
            self.setFocus(columnName)
        else:
            self.setFocusOnFirstEntry()
        patterns.Publisher().registerObserver(self.onItemRemoved, 
            eventType=container.removeItemEventType())

    def setFocus(self, columnName):
        ''' Select the correct page of the editor and correct control on a page
            based on the column that the user double clicked. '''
        page = 0
        for pageIndex in range(self[0].GetPageCount()):
            if columnName in self[0][pageIndex].entries():
                page = pageIndex
                break
        self[0].ChangeSelection(page)
        self[0][page].setFocusOnEntry(columnName)
        
    def setFocusOnFirstEntry(self):
        firstEntry = self[0][0]._subjectEntry
        firstEntry.SetSelection(-1, -1) # Select all text
        firstEntry.SetFocus()

    def addPages(self):
        for item in self._command.items:
            self.addPage(item)

    def cancel(self, *args, **kwargs):
        patterns.Publisher().removeObserver(self.onItemRemoved)
        super(EditorWithCommand, self).cancel(*args, **kwargs)
        
    def ok(self, *args, **kwargs):
        patterns.Publisher().removeObserver(self.onItemRemoved)
        self._command.do()
        super(EditorWithCommand, self).ok(*args, **kwargs)

    def onItemRemoved(self, event):
        ''' The item we're editing has been removed. Close the tab of the item
            involved and close the whole editor if there are no tabs left. '''
        if not self:
            return # Prevent _wxPyDeadObject TypeError
        pagesToCancel = [] # Collect the pages to cancel so we don't modify the 
                           # book widget while we iterate over it
        for item in event.values():
            pagesToCancel.extend([page for page in self \
                                  if self.isPageDisplayingItem(page, item)])
        self.cancelPages(pagesToCancel)
        if len(list(self)) == 0:
            self.cancel()
            
    def isPageDisplayingItem(self, page, item):
        return page.item == item


class TaskEditor(EditorWithCommand):
    def __init__(self, parent, command, taskFile, settings, bitmap='edit', 
                 *args, **kwargs):
        self._settings = settings
        self._taskFile = taskFile
        super(TaskEditor, self).__init__(parent, command, taskFile.tasks(), 
                                         bitmap, *args, **kwargs)

    def addPage(self, task):
        page = TaskEditBook(self._interior, task, self._taskFile, self._settings)
        self._interior.AddPage(page, task.subject())
        

class EffortEditor(EditorWithCommand):
    def __init__(self, parent, command, taskFile, settings, *args, **kwargs):
        self._taskFile = taskFile
        self._settings = settings
        super(EffortEditor, self).__init__(parent, command, taskFile.efforts(), 
                                           *args, **kwargs)

    def setFocusOnFirstEntry(self):
        pass
        
    def addPages(self):
        # Override this method to make sure we use the efforts, not the task
        for effort in self._command.efforts:
            self.addPage(effort)

    def addPage(self, effort):
        page = EffortEditBook(self._interior, effort, self, self._taskFile.efforts(),
            self._taskFile.tasks(), self._settings)
        self._interior.AddPage(page, effort.task().subject())

    def isPageDisplayingItem(self, page, item):
        if hasattr(item, 'setTask'):
            return page.item == item # Regular effort
        else:
            return item.mayContain(page.item) # Composite effort


class CategoryEditor(EditorWithCommand):
    def __init__(self, parent, command, settings, taskFile, *args, **kwargs):
        self._settings = settings
        self._taskFile = taskFile
        super(CategoryEditor, self).__init__(parent, command, taskFile.categories(), 
                                             *args, **kwargs)

    def addPage(self, category):
        page = CategoryEditBook(self._interior, category,
                                self._settings, self._taskFile)
        self._interior.AddPage(page, category.subject())


class NoteEditor(EditorWithCommand):
    def __init__(self, parent, command, settings, notes, taskFile, *args, **kwargs):
        self._settings = settings
        self._taskFile = taskFile
        super(NoteEditor, self).__init__(parent, command, notes, *args, **kwargs)

    def addPages(self):
        # Override this method to make sure we use the notes, not the note owner
        for note in self._command.notes:
            self.addPage(note)

    def addPage(self, note):
        page = NoteEditBook(self._interior, note, self._settings, 
                            self._taskFile.categories(), self._taskFile)
        self._interior.AddPage(page, note.subject())


class AttachmentEditor(EditorWithCommand):
    def __init__(self, parent, command, settings, attachments, taskFile, *args, **kwargs):
        self._settings = settings
        self._taskFile = taskFile
        super(AttachmentEditor, self).__init__(parent, command, attachments, *args, **kwargs)

    def addPage(self, attachment):
        page = AttachmentEditBook(self._interior, attachment, self._settings,
                                  self._taskFile)
        self._interior.AddPage(page, attachment.subject())

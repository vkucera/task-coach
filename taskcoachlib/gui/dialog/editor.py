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
from wx.lib import masked
import wx.lib.customtreectrl as customtree
from taskcoachlib import widgets, patterns
from taskcoachlib.gui import render, viewer, uicommand
from taskcoachlib.widgets import draganddrop
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, category, date, note, attachment
from taskcoachlib.thirdparty import desktop, combotreebox


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
            self._entry = masked.TextCtrl(self, mask='#{6}:##:##',
                fields=[masked.Field(formatcodes='rRFS'),
                        masked.Field(formatcodes='RFS'),
                        masked.Field(formatcodes='RFS')])
            hours, minutes, seconds = timeDelta.hoursMinutesSeconds()
            self._entry.SetFieldParameters(0, defaultValue='%6d'%hours)
            self._entry.SetFieldParameters(1, defaultValue='%02d'%minutes)
            self._entry.SetFieldParameters(2, defaultValue='%02d'%seconds)
        self.add(self._entry, flag=wx.EXPAND|wx.ALL, proportion=1)
        self.fit()

    def get(self):
        return date.parseTimeDelta(self._entry.GetValue())


class AmountEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, amount=0.0, readonly=False, *args, **kwargs):
        super(AmountEntry, self).__init__(parent, *args, **kwargs)
        if readonly:
            self._entry = wx.StaticText(self, label=render.amount(amount))
        else:
            self._entry = masked.NumCtrl(self, fractionWidth=2,
                                         allowNegative=False, value=amount)
        self.add(self._entry)
        self.fit()

    def get(self):
        return self._entry.GetValue()

    def set(self, value):
        self._entry.SetValue(value)


class ColorEntryMixin(object):
    def addColorEntry(self):
        currentColor = self.item.color(recursive=False)
        self._colorCheckBox = wx.CheckBox(self, label=_('Use this color:'))
        self._colorCheckBox.SetValue(currentColor is not None)
        self._colorButton = wx.ColourPickerCtrl(self, -1,
            currentColor or wx.WHITE, size=(40,-1))
        self._colorButton.Bind(wx.EVT_COLOURPICKER_CHANGED,
            lambda event: self._colorCheckBox.SetValue(True))
        self.addEntry(_('Color'), self._colorCheckBox, self._colorButton)

    def ok(self):
        super(ColorEntryMixin, self).ok()
        if self._colorCheckBox.IsChecked():
            color = self._colorButton.GetColour()
        else:
            color = None
        self.item.setColor(color)


class EditorPage(widgets.PanelWithBoxSizer):
    def __init__(self, parent, item, *args, **kwargs):
        super(EditorPage, self).__init__(parent, *args, **kwargs)
        self._defaultControl=None
        self._fieldMap={}   
        self.item = item

    def addHeaders(self, box):
        headers = ['', self.headerForNonRecursiveAttributes]
        if self.item.children():
            headers.append(self.headerForRecursiveAttributes)
        else:
            headers.append('')
        for header in headers:
            box.add(header)

    def containsField(self,fieldname):
        return fieldname in self._fieldMap.keys()

    def setFocusForField(self, fieldname):        
        ''' if a field has an associated control, set focus on that control.
            if not, set focus to the default control.
        '''
        if self.containsField(fieldname):
            self._fieldMap[fieldname].SetFocus()
        else:
            self._defaultControl.SetFocus()

    def ok(self):
        pass


class TaskHeaders(object):
    headerForNonRecursiveAttributes = _('For this task')
    headerForRecursiveAttributes = _('For this task including all subtasks')
    

class NoteHeaders(object):
    headerForNonRecursiveAttributes = _('For this note')
    headerForRecursiveAttributes = _('For this note including all subnotes')

    
class SubjectPage(ColorEntryMixin, widgets.BookPage):
    def __init__(self, parent, task, *args, **kwargs):
        self.item = task
        super(SubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.addSubjectEntry()
        self.addDescriptionEntry()
        self.addPriorityEntry()
        self.addColorEntry()
        self.fit()
        self._defaultControl=self._subjectEntry
        self._fieldMap={}   #FIXME: cz: remove when subject page is an editor page
        self._fieldMap['subject']    = self._subjectEntry
        self._fieldMap['description']= self._descriptionEntry
        self._fieldMap['priority']   = self._prioritySpinner

    def containsField(self,fieldname):
        #FIXME: cz: remove when subject page is an editor page
        # print fieldname , "  ",fieldname in self._fieldMap.keys(),' ',self
        return fieldname in self._fieldMap.keys()
            
    def setFocusForField(self, fieldname):        
        #FIXME: cz: remove when subject page is an editor page
        ''' if a field has an associated control, set focus on that control.
            if not, set focus to the default control.
        '''
        if self.containsField(fieldname):
            self._fieldMap[fieldname].SetFocus()
        else:
            self._defaultControl.SetFocus()

    def addSubjectEntry(self):
        self._subjectEntry = widgets.SingleLineTextCtrl(self, 
            self.item.subject())
        self.addEntry(_('Subject'), self._subjectEntry, 
            flags=[None, wx.ALL|wx.EXPAND])

    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, 
            self.item.description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)
          
    def addPriorityEntry(self):
        self._prioritySpinner = widgets.SpinCtrl(self,
            value=render.priority(self.item.priority()))
        self.addEntry(_('Priority'), self._prioritySpinner, 
            flags=[None, wx.ALL|wx.EXPAND])
    
    def ok(self):
        self.item.setSubject(self._subjectEntry.GetValue())
        self.item.setDescription(self._descriptionEntry.GetValue())
        self.item.setPriority(self._prioritySpinner.GetValue())
        super(SubjectPage, self).ok()
        
    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)

    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)


class DatesPage(EditorPage, TaskHeaders):
    def __init__(self, parent, task, *args, **kwargs):
        super(DatesPage, self).__init__(parent, task, *args, **kwargs)
        datesBox = widgets.BoxWithFlexGridSizer(self, label=_('Dates'), cols=3)
        self.addHeaders(datesBox)
        for label, taskMethodName in [(_('Start date'), 'startDate'),
                                      (_('Due date'), 'dueDate'),
                                      (_('Completion date'), 'completionDate')]:
            datesBox.add(label)
            taskMethod = getattr(task, taskMethodName)
            entry = DateEntry(datesBox, taskMethod(),
                              callback=self.onDateChanged)
            setattr(self, '_%sEntry'%taskMethodName, entry)
            self._fieldMap[taskMethodName]= entry
            datesBox.add(entry)
            if task.children():
                recursiveEntry = DateEntry(datesBox,
                    taskMethod(recursive=True), readonly=True)
            else:
                recursiveEntry = (0, 0)
            datesBox.add(recursiveEntry)

        reminderBox = widgets.BoxWithFlexGridSizer(self, label=_('Reminder'),
            cols=2)
        reminderBox.add(_('Reminder'))
        self._reminderDateTimeEntry = widgets.DateTimeCtrl(reminderBox,
            task.reminder())
        self._fieldMap['reminder']= self._reminderDateTimeEntry
        # If the user has not set a reminder, make sure that the default 
        # date time in the reminder entry is a reasonable suggestion:
        if self._reminderDateTimeEntry.GetValue() == date.DateTime.max:
            self.suggestReminder()
        reminderBox.add(self._reminderDateTimeEntry)

        self._recurrenceBox = recurrenceBox = widgets.BoxWithFlexGridSizer(self,
            label=_('Recurrence'), cols=2)
        recurrenceBox.add(_('Recurrence'))
        panel = wx.Panel(recurrenceBox)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._recurrenceEntry = wx.Choice(panel,
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly'), _('Yearly')])
        self._fieldMap['recurrence']= self._recurrenceEntry        
        self._recurrenceEntry.Bind(wx.EVT_CHOICE, self.onRecurrenceChanged)
        panelSizer.Add(self._recurrenceEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        staticText = wx.StaticText(panel, label=_(', every'))
        panelSizer.Add(staticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceFrequencyEntry = wx.SpinCtrl(panel, size=(50,-1),
            style=wx.SP_ARROW_KEYS)
        # Can't use sys.maxint because Python and wxPython disagree on what the
        # maximum integer is on Suse 10.0 x86_64. Using sys.maxint will cause
        # an Overflow exception, so we use a constant:
        maxint = 2147483647
        self._recurrenceFrequencyEntry.SetRange(1, maxint)
        panelSizer.Add(self._recurrenceFrequencyEntry, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._recurrenceStaticText = wx.StaticText(panel, label='reserve some space')
        panelSizer.Add(self._recurrenceStaticText, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3, -1))
        self._recurrenceSameWeekdayCheckBox = wx.CheckBox(panel, label=_('keeping dates on the same weekday'))
        panelSizer.Add(self._recurrenceSameWeekdayCheckBox, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        #panelSizer.Add((3, -1))
        #staticText = wx.StaticText(panel, label=_('keeping dates on the same weekday'))
        #panelSizer.Add(staticText, flag=wx.ALIGN_CENTER_VERTICAL)
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
        self._maxRecurrenceCountEntry = wx.SpinCtrl(panel, size=(50,-1),
            style=wx.SP_ARROW_KEYS)
        self._maxRecurrenceCountEntry.SetRange(1, maxint)
        panelSizer.Add(self._maxRecurrenceCountEntry)
        panel.SetSizerAndFit(panelSizer)
        recurrenceBox.add(panel)

        self.setRecurrence(task.recurrence())

        for box in datesBox, reminderBox, recurrenceBox:
            box.fit()
            self.add(box, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
        self._defaultControl=self._reminderDateTimeEntry  #  need to confirm this is the right box

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


class BudgetPage(EditorPage, TaskHeaders):
    def __init__(self, parent, task, *args, **kwargs):
        super(BudgetPage, self).__init__(parent, task, *args, **kwargs)
        # Boxes:
        budgetBox = widgets.BoxWithFlexGridSizer(self, label=_('Budget'), cols=3)
        revenueBox = widgets.BoxWithFlexGridSizer(self, label=_('Revenue'), cols=3)
        # Editable entries:
        self._budgetEntry = TimeDeltaEntry(budgetBox, task.budget())
        self._hourlyFeeEntry = AmountEntry(revenueBox, task.hourlyFee())
        self._fixedFeeEntry = AmountEntry(revenueBox, task.fixedFee())
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
        for entry in [_('Budget'), self._budgetEntry, recursiveBudget,
                      _('Time spent'), render.budget(task.timeSpent()), recursiveTimeSpent,
                      _('Budget left'), render.budget(task.budgetLeft()), recursiveBudgetLeft]:
            budgetBox.add(entry, flag=wx.ALIGN_RIGHT)

        self.addHeaders(revenueBox)
        for entry in [_('Hourly fee'), self._hourlyFeeEntry, '',
                      _('Fixed fee'), self._fixedFeeEntry, recursiveFixedFee,
                      _('Revenue'), render.amount(task.revenue()), recursiveRevenue]:
            revenueBox.add(entry, flag=wx.ALIGN_RIGHT)
        for box in budgetBox, revenueBox:
            box.fit()
            self.add(box, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
        self._fieldMap['budget']=self._budgetEntry
        #FIXME: cz: ?  The calculated fields now actually set focus on budget entry
        # behavior can be chaned by adding a separate map, that can be checked in containsField
        # or changing the setFocusForField method to recognize NONE for field
        # this behavior will be OK for now.         
        self._fieldMap['timeSpent']=self._budgetEntry
        self._fieldMap['totalTimeSpent']=self._budgetEntry
        self._fieldMap['totalBudget']=self._budgetEntry
        self._fieldMap['timeLeft']=self._budgetEntry
        self._fieldMap['budgetLeft']=self._budgetEntry
        self._fieldMap['totalTimeLeft']=self._budgetEntry
        self._fieldMap['hourlyFee']=self._hourlyFeeEntry
        self._fieldMap['revenue']=self._hourlyFeeEntry
        self._fieldMap['totalRevenue']=self._hourlyFeeEntry
        self._defaultControl = self._budgetEntry

    def ok(self):
        self.item.setBudget(self._budgetEntry.get())
        self.item.setHourlyFee(self._hourlyFeeEntry.get())
        self.item.setFixedFee(self._fixedFeeEntry.get())


class EffortPage(EditorPage, TaskHeaders):
    def __init__(self, parent, theTask, taskList, settings, *args, **kwargs):
        super(EffortPage, self).__init__(parent, theTask, *args, **kwargs)
        singleTaskList = task.SingleTaskList()
        self.effortViewer = viewer.EffortViewer(self, taskList, 
            settings, settingsSection='effortviewerintaskeditor',
            tasksToShowEffortFor=singleTaskList)
        self.add(self.effortViewer, proportion=1, flag=wx.EXPAND|wx.ALL, 
                 border=5)
        singleTaskList.append(theTask)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self.fit()

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
        # tasks and notes are only used for the 2 commands that we'll
        # suppress anyway.
        kwargs['tasks'] = []
        kwargs['notes'] = []

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


class CategoriesPage(EditorPage):
    def __init__(self, parent, item, categories, settings, *args, **kwargs):
        super(CategoriesPage, self).__init__(parent, item, *args, **kwargs)
        self.__categories = category.CategorySorter(categories)
        categoriesBox = widgets.BoxWithBoxSizer(self, label=_('Categories'))
        self._categoryViewer = LocalCategoryViewer(item, categoriesBox, categories,
                                       tasks=[], notes=[], settings=settings,
                                       settingsSection=self.settingsSection())
        categoriesBox.add(self._categoryViewer, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.fit()
        self.add(categoriesBox)
        self.fit()
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self._fieldMap['categories']=self._categoryViewer
        self._fieldMap['totalCategories']=self._categoryViewer # readOnlyField maps to base 

    def onClose(self, event):
        self._categoryViewer.detach()
        event.Skip()

    def getCategoryWithIndex(self, index):
        children = self.__categories.rootItems()
        for i in index:
            category = children[i]
            childIndices = [self.__categories.index(child) for child in \
                            category.children() if child in self.__categories]
            childIndices.sort()
            children = [self.__categories[childIndex] for childIndex \
                        in childIndices]
        return category

    def ok(self):
        treeCtrl = self._categoryViewer.widget
        treeCtrl.ExpandAll()
        for categoryNode in treeCtrl.GetItemChildren(recursively=True):
            categoryIndex = treeCtrl.GetIndexOfItem(categoryNode)
            category = self.getCategoryWithIndex(categoryIndex)
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


class AttachmentsPage(EditorPage):
    def __init__(self, parent, item, settings, categories, *args, **kwargs):
        super(AttachmentsPage, self).__init__(parent, item, *args, **kwargs)

        self.attachmentsList = attachment.AttachmentList(item.attachments())
        attachmentsBox = widgets.BoxWithBoxSizer(self, label=_('Attachments'))
        self._attachmentViewer = LocalAttachmentViewer(attachmentsBox,
                                                       self.attachmentsList,
                                                       settings,
                                                       categories=categories,
                                                       settingsSection=self.settingsSection())
        attachmentsBox.add(self._attachmentViewer, proportion=1, flag=wx.EXPAND|wx.ALL)
        attachmentsBox.fit()
        self.add(attachmentsBox)
        self.fit()
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self._fieldMap['attachments']=self._attachmentViewer

    def ok(self):
        self.item.setAttachments(self.attachmentsList)
        super(AttachmentsPage, self).ok()

    def onClose(self, event):
        self._attachmentViewer.detach()
        event.Skip()


class TaskAttachmentsPage(AttachmentsPage):
    def settingsSection(self):
        return 'attachmentviewerintaskeditor'


class NoteAttachmentsPage(AttachmentsPage):
    def settingsSection(self):
        return 'attachmentviewerinnoteeditor'


class CategoryAttachmentsPage(AttachmentsPage):
    def settingsSection(self):
        return 'attachmentviewerincategoryeditor'


class LocalNoteViewer(LocalDragAndDropFix, viewer.NoteViewer):
    def createFilter(self, notes):
        # Inside the editor, all notes should be shown.
        categories = self.categories
        self.categories = category.CategoryList()
        notes = super(LocalNoteViewer, self).createFilter(notes)
        self.categories = categories
        return notes


class NotesPage(EditorPage):
    def __init__(self, parent, item, settings, categories, 
                 *args, **kwargs):
        super(NotesPage, self).__init__(parent, item, *args, **kwargs)
        notesBox = widgets.BoxWithBoxSizer(self, label=_('Notes'))
        self.noteContainer = note.NoteContainer(item.notes())
        self.noteViewer = LocalNoteViewer(notesBox, self.noteContainer, 
            settings, settingsSection='noteviewerintaskeditor', 
            categories=categories)
        notesBox.add(self.noteViewer, flag=wx.EXPAND|wx.ALL, proportion=1)
        notesBox.fit()
        self.add(notesBox, proportion=1, flag=wx.EXPAND|wx.ALL,
                 border=5)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self._fieldMap['note']=self.noteViewer # not sure of the fieldname
        self._defaultControl=self.noteViewer # not sure of the fieldname
        self.fit()
        
    def onClose(self, event):
        # Don't notify the viewer about any changes anymore, it is about
        # to be deleted.
        self.noteViewer.detach()
        event.Skip()
        
    def ok(self):
        self.item.setNotes(list(self.noteContainer.rootItems()))


class BehaviorPage(EditorPage, TaskHeaders):
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
        self._defaultControl=choice
        self._fieldMap['behavior']=choice

    def ok(self):
        self.item.shouldMarkCompletedWhenAllChildrenCompleted = \
            self._markTaskCompletedEntry.GetClientData( \
                self._markTaskCompletedEntry.GetSelection())


class TaskEditBook(widgets.Listbook):
    def __init__(self, parent, task, taskList, settings, categories, 
                 *args, **kwargs):
        super(TaskEditBook, self).__init__(parent)
        self.AddPage(SubjectPage(self, task), _('Description'), 'description')
        self.AddPage(DatesPage(self, task), _('Dates'), 'date')
        self.AddPage(TaskCategoriesPage(self, task, categories, settings), 
                     _('Categories'), 'category')
        effortOn = settings.getboolean('feature', 'effort')
        if effortOn:
            self.AddPage(BudgetPage(self, task), _('Budget'), 'budget')
        if effortOn and task.timeSpent(recursive=True):
            effortPage = EffortPage(self, task, taskList, settings)
            self.AddPage(effortPage, _('Effort'), 'start')
        if settings.getboolean('feature', 'notes'):
            self.AddPage(NotesPage(self, task, settings, categories), 
                         _('Notes'), 'note')
        self.AddPage(TaskAttachmentsPage(self, task, settings, categories), 
                     _('Attachments'), 'attachment')
        self.AddPage(BehaviorPage(self, task), _('Behavior'), 'behavior')
        self.item = task


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
            style=wx.CB_READONLY|wx.CB_SORT)
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


class EffortEditBook(widgets.BookPage):
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
        self._taskEntry = TaskComboTreeBox(self,
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



class CategorySubjectPage(ColorEntryMixin, widgets.BookPage):
    def __init__(self, parent, category, *args, **kwargs):
        self.item = self._category = category
        super(CategorySubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.addSubjectEntry()
        self.addDescriptionEntry()
        self.addColorEntry()
        self.fit()

    def addSubjectEntry(self):
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self._category.subject())
        self.addEntry(_('Subject'), self._subjectEntry, flags=[None, wx.ALL|wx.EXPAND])

    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self,
            self._category.description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)

    def ok(self):
        self._category.setSubject(self._subjectEntry.GetValue())
        self._category.setDescription(self._descriptionEntry.GetValue())
        super(CategorySubjectPage, self).ok()
        
        
class CategoryEditBook(widgets.Listbook):
    def __init__(self, parent, theCategory, settings, categories,
                 *args, **kwargs):
        self.item = theCategory
        super(CategoryEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(CategorySubjectPage(self, theCategory), 
                     _('Description'), 'description')
        if settings.getboolean('feature', 'notes'):
            self.AddPage(NotesPage(self, theCategory, settings, categories), 
                         _('Notes'), 'note')
        self.AddPage(CategoryAttachmentsPage(self, theCategory, settings, 
                                             categories), 
                     _('Attachments'), 'attachment')


class NoteSubjectPage(ColorEntryMixin, widgets.BookPage):
    def __init__(self, parent, theNote, *args, **kwargs):
        super(NoteSubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.item = self._note = theNote
        self.addSubjectEntry()
        self.addDescriptionEntry()
        self.addColorEntry()
        self.fit()

    def addSubjectEntry(self):
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self._note.subject())
        self.addEntry(_('Subject'), self._subjectEntry, flags=[None, wx.ALL|wx.EXPAND])

    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self,
            self._note.description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)

    def ok(self):
        self._note.setSubject(self._subjectEntry.GetValue())
        self._note.setDescription(self._descriptionEntry.GetValue())
        super(NoteSubjectPage, self).ok()
        

class NoteEditBook(widgets.Listbook):
    def __init__(self, parent, theNote, settings, categories, *args, **kwargs):
        self.item = theNote
        super(NoteEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(NoteSubjectPage(self, theNote), _('Description'), 'description')
        self.AddPage(NoteCategoriesPage(self, theNote, categories, settings), _('Categories'),
                     'category')
        self.AddPage(NoteAttachmentsPage(self, theNote, settings, categories),
                     _('Attachments'), 'attachment')


class AttachmentSubjectPage(ColorEntryMixin, widgets.BookPage):
    def __init__(self, parent, theAttachment, basePath, *args, **kwargs):
        super(AttachmentSubjectPage, self).__init__(parent, columns=3, *args, **kwargs)
        self.item = self._attachment = theAttachment
        self.basePath = basePath
        self.addSubjectEntry()
        self.addLocationEntry()
        self.addDescriptionEntry()
        self.addColorEntry()
        self.fit()

    def addSubjectEntry(self):
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self._attachment.subject())
        self.addEntry(_('Subject'), self._subjectEntry, flags=[None, wx.ALL|wx.EXPAND])

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

    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self,
            self._attachment.description())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry,
            flags=[None, wx.ALL|wx.EXPAND], growable=True)

    def ok(self):
        self._attachment.setSubject(self._subjectEntry.GetValue())
        self._attachment.setLocation(self._locationEntry.GetValue())
        self._attachment.setDescription(self._descriptionEntry.GetValue())
        super(AttachmentSubjectPage, self).ok()

    def OnSelectLocation(self, evt):
        filename = widgets.AttachmentSelector()
        if filename:
            if self.basePath:
                filename = attachment.getRelativePath(filename, self.basePath)
            self._subjectEntry.SetValue(os.path.split(filename)[-1])
            self._locationEntry.SetValue(filename)


class AttachmentEditBook(widgets.Listbook):
    def __init__(self, parent, theAttachment, settings, categories,
                 *args, **kwargs):
        super(AttachmentEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(AttachmentSubjectPage(self, theAttachment,
                                           settings.get('file', 'attachmentbase')), 
                     _('Description'), 'description')
        if settings.getboolean('feature', 'notes'):
            self.AddPage(NotesPage(self, theAttachment, settings, 
                                   categories), _('Notes'), 'note')


class EditorWithCommand(widgets.NotebookDialog):
    def __init__(self, parent, command, container, *args, **kwargs):
        self._command = command
        super(EditorWithCommand, self).__init__(parent, command.name(), 
                                                *args, **kwargs)
        self.setFocusOnFirstEntry()
        patterns.Publisher().registerObserver(self.onItemRemoved, 
            eventType=container.removeItemEventType())

    def setFocusOnFirstEntry(self):
        firstEntry = self[0][0]._subjectEntry
        firstEntry.SetSelection(-1, -1) # Select all text
        firstEntry.SetFocus()
        wx.CallAfter(firstEntry.SetFocus) # FIXME: Is this really needed on MSW? GTK works without CallAfter

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
    def __init__(self, parent, command, taskList, settings, categories, 
                 bitmap='edit', *args, **kwargs):
        self._settings = settings
        self._taskList = taskList
        self._categories = categories
        super(TaskEditor, self).__init__(parent, command, taskList, bitmap, 
                                         *args, **kwargs)
        self[0][0]._subjectEntry.SetSelection(-1, -1)
        # This works on Linux Ubuntu 5.10, but fails silently on Windows XP:
        self.setFocus(*args,**kwargs) 
        # This works on Windows XP, but fails silently on Linux Ubuntu 5.10:
        wx.CallAfter(self.setFocus,*args,**kwargs) 
        # So we did just do it twice, guess it doesn't hurt
        
    def setFocus(self, *args, **kwargs):
        ''' select the correct page and correct control on a page
            kwargs include:
            Page --  index of page to select
            Task --  index of task (in tabbed notebook)
            Field -- field to highlight (overrides page)
            '''
        tsk=0
        page=0
        fieldname=''
        #print args
        #print kwargs
        if kwargs.has_key('Task'):
            tsk=kwargs['Task']
            self.ChangeSelection(kwargs['Task'])    # always go to the first tab
        if kwargs.has_key('Page'):
            page=kwargs['Page']
            selectCtrl= self[tsk][page]._defaultControl
        if kwargs.has_key('Field'):
            # lookup the what page the field is edite on.
            fieldname=kwargs['Field']    
            page=self.getFieldPage(fieldname)
            self[tsk].ChangeSelection(page) # go to the second tab,  try by name.
        self[tsk].ChangeSelection(page) # go to the second tab,  try by name.
        self[tsk][page].setFocusForField(fieldname)

    def getFieldPage(self,fieldname,task=0):
        ''' return the page on which the field should be edited'''
        page=0 #hard code the second page for sample
        for  p in range((self[task]).GetPageCount()):
            if self[task][p].containsField(fieldname):
                return p
        return page
        
    def addPage(self, task):
        page = TaskEditBook(self._interior, task, self._taskList,
            self._settings, self._categories)
        self._interior.AddPage(page, task.subject())
        


class EffortEditor(EditorWithCommand):
    def __init__(self, parent, command, effortList, taskList,
                 settings, *args, **kwargs):
        self._effortList = effortList
        self._taskList = taskList
        self._settings = settings
        super(EffortEditor, self).__init__(parent, command, effortList, 
                                           *args, **kwargs)

    def setFocusOnFirstEntry(self):
        pass
        
    def addPages(self):
        for effort in self._command.efforts: # FIXME: use getter
            self.addPage(effort)

    def addPage(self, effort):
        page = EffortEditBook(self._interior, effort, self, self._effortList,
            self._taskList, self._settings)
        self._interior.AddPage(page, effort.task().subject())

    def isPageDisplayingItem(self, page, item):
        if hasattr(item, 'setTask'):
            return page.item == item # Regular effort
        else:
            return item.mayContain(page.item) # Composite effort


class CategoryEditor(EditorWithCommand):
    def __init__(self, parent, command, settings, categories, *args, **kwargs):
        self._settings = settings
        self._categories = categories
        super(CategoryEditor, self).__init__(parent, command, categories, 
                                             *args, **kwargs)

    def addPage(self, category):
        page = CategoryEditBook(self._interior, category,
                                self._settings, self._categories)
        self._interior.AddPage(page, category.subject())


class NoteEditor(EditorWithCommand):
    def __init__(self, parent, command, settings, notes, categories, *args, **kwargs):
        self._settings = settings
        self._categories = categories
        super(NoteEditor, self).__init__(parent, command, notes, *args, **kwargs)

    def addPages(self):
        for note in self._command.notes: # FIXME: use getter
            self.addPage(note)
            
    def addPage(self, note):
        page = NoteEditBook(self._interior, note, self._settings, 
                            self._categories)
        self._interior.AddPage(page, note.subject())


class AttachmentEditor(EditorWithCommand):
    def __init__(self, parent, command, settings, categories, *args, **kwargs):
        self._settings = settings
        self._categories = categories
        super(AttachmentEditor, self).__init__(parent, command, categories, *args, **kwargs)

    def addPages(self):
        for attachment in self._command.attachments: # FIXME: use getter
            self.addPage(attachment)

    def addPage(self, attachment):
        page = AttachmentEditBook(self._interior, attachment, self._settings,
                                  self._categories)
        self._interior.AddPage(page, attachment.subject())

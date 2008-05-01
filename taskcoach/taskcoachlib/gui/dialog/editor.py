'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

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

import wx, datetime, os.path
from wx.lib import masked, combotreebox
import wx.lib.customtreectrl as customtree
from taskcoachlib import widgets
from taskcoachlib.gui import render, viewercontainer, viewer
from taskcoachlib.widgets import draganddrop
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, category, date, note, attachment
from taskcoachlib.thirdparty import desktop


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


class TaskEditorPage(widgets.PanelWithBoxSizer):
    def __init__(self, parent, task, *args, **kwargs):
        super(TaskEditorPage, self).__init__(parent, *args, **kwargs)
        self._task = task
                
    def addHeaders(self, box):
        headers = ['', _('For this task')]
        if self._task.children():
            headers.append(_('For this task including all subtasks'))
        else:
            headers.append('')
        for header in headers:
            box.add(header)
        
    def ok(self):
        pass


class PrioritySpinCtrl(wx.SpinCtrl):
    def __init__(self, *args, **kwargs):
        kwargs['style'] = wx.SP_ARROW_KEYS
        super(PrioritySpinCtrl, self).__init__(*args, **kwargs)
        # Can't use sys.maxint because Python and wxPython disagree on what the 
        # maximum integer is on Suse 10.0 x86_64. Using sys.maxint will cause
        # an Overflow exception, so we use a constant:
        maxint = 2147483647
        self.SetRange(-maxint, maxint)
        self.Bind(wx.EVT_SPINCTRL, self.onValueChanged)

    def onValueChanged(self, event):
        ''' wx.SpinCtrl resets invalid values (e.g. text or an empty string)
            to wx.SpinCtrl.GetMin(). The minimum priority value is a large
            (negative) number. It makes more sense to reset the SpinCtrl to 0 
            in case of invalid input. '''
        if self.GetValue() == self.GetMin():
            wx.CallAfter(self.SetValue, 0)
        event.Skip()
            
        
class SubjectPage(TaskEditorPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(SubjectPage, self).__init__(parent, task, *args, **kwargs)
        descriptionBox = widgets.BoxWithFlexGridSizer(self, _('Description'), cols=2, growableRow=1, growableCol=1)
        descriptionBox.add(_('Subject'))
        self._subjectEntry = widgets.SingleLineTextCtrl(descriptionBox, task.subject())
        descriptionBox.add(self._subjectEntry, proportion=1, flag=wx.EXPAND)
        descriptionBox.add(_('Description'))
        self._descriptionEntry = widgets.MultiLineTextCtrl(descriptionBox, task.description())
        descriptionBox.add(self._descriptionEntry, proportion=1, flag=wx.EXPAND)
        
        priorityBox = widgets.BoxWithFlexGridSizer(self, _('Priority'), cols=2)
        priorityBox.add(_('Priority'))
        self._prioritySpinner = PrioritySpinCtrl(priorityBox, 
            value=render.priority(task.priority()))
        priorityBox.add(self._prioritySpinner)

        for box, proportion in [(descriptionBox, 1), (priorityBox, 0)]:
            box.fit()
            self.add(box, proportion=proportion, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
        
    def ok(self):
        self._task.setSubject(self._subjectEntry.GetValue())
        self._task.setDescription(self._descriptionEntry.GetValue())
        self._task.setPriority(self._prioritySpinner.GetValue())
        
    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)

    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)        


class DatesPage(TaskEditorPage):
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
        # If the users has not set a reminder, make sure that the default 
        # date time in the reminder entry is a reasonable suggestion:
        if self._reminderDateTimeEntry.GetValue() == date.DateTime.max:
            self.suggestReminder()
        reminderBox.add(self._reminderDateTimeEntry)

        recurrenceBox = widgets.BoxWithFlexGridSizer(self, 
            label=_('Recurrence'), cols=2)
        recurrenceBox.add(_('Recurrence'))
        self._recurrenceEntry = wx.Choice(recurrenceBox, 
            choices=[_('None'), _('Daily'), _('Weekly'), _('Monthly')])
        self._recurrenceEntry.Bind(wx.EVT_CHOICE, self.onRecurrenceChanged)
        recurrenceBox.add(self._recurrenceEntry)
        recurrenceBox.add(_('Maximum number of recurrences'))
        panel = wx.Panel(recurrenceBox)
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._maxRecurrenceCheckBox = wx.CheckBox(panel)
        self._maxRecurrenceCheckBox.Bind(wx.EVT_CHECKBOX, self.onMaxRecurrenceChecked)
        panelSizer.Add(self._maxRecurrenceCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
        panelSizer.Add((3,-1))
        self._maxRecurrenceCountEntry = wx.SpinCtrl(panel, size=(50,-1),
            value=str(task.maxRecurrenceCount()), style=wx.SP_ARROW_KEYS)
        # Can't use sys.maxint because Python and wxPython disagree on what the 
        # maximum integer is on Suse 10.0 x86_64. Using sys.maxint will cause
        # an Overflow exception, so we use a constant:
        maxint = 2147483647
        self._maxRecurrenceCountEntry.SetRange(1, maxint)
        self.setRecurrence(task.recurrence())
        panelSizer.Add(self._maxRecurrenceCountEntry)
        panel.SetSizerAndFit(panelSizer)
        recurrenceBox.add(panel)
        
        for box in datesBox, reminderBox, recurrenceBox:
            box.fit()
            self.add(box, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
        
    def onRecurrenceChanged(self, event):
        event.Skip()
        recurrenceOn = event.String != _('None')
        self._maxRecurrenceCheckBox.Enable(recurrenceOn)
        self._maxRecurrenceCountEntry.Enable(recurrenceOn and \
            self._maxRecurrenceCheckBox.IsChecked())
        
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
        recurrenceDict = {0: '', 1: 'daily', 2: 'weekly', 3: 'monthly'}
        recurrence = recurrenceDict[self._recurrenceEntry.Selection]
        self._task.setRecurrence(recurrence)
        if self._maxRecurrenceCheckBox.IsChecked():
            self._task.setMaxRecurrenceCount(self._maxRecurrenceCountEntry.Value)
        self._task.setStartDate(self._startDateEntry.get())
        self._task.setDueDate(self._dueDateEntry.get())
        self._task.setCompletionDate(self._completionDateEntry.get())
        self._task.setReminder(self._reminderDateTimeEntry.GetValue())
        
    def setReminder(self, reminder):
        self._reminderDateTimeEntry.SetValue(reminder)
        
    def setRecurrence(self, recurrence):
        index = {'': 0, 'daily': 1, 'weekly': 2, 'monthly': 3}[recurrence]
        self._recurrenceEntry.Selection = index
        self._maxRecurrenceCheckBox.Enable(bool(recurrence))
        self._maxRecurrenceCountEntry.Enable(bool(recurrence) and \
            self._maxRecurrenceCheckBox.IsChecked())

    def setMaxRecurrenceCount(self, maxRecurrence):
        self._maxRecurrenceCountEntry.Value = maxRecurrence
        self._maxRecurrenceCheckBox.Enable(self._recurrenceEntry.Selection != 0)
        self._maxRecurrenceCheckBox.SetValue(maxRecurrence > 0)

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
    

class BudgetPage(TaskEditorPage):
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
        
    def ok(self):
        self._task.setBudget(self._budgetEntry.get())           
        self._task.setHourlyFee(self._hourlyFeeEntry.get())   
        self._task.setFixedFee(self._fixedFeeEntry.get())   


class EffortPage(TaskEditorPage):        
    def __init__(self, parent, theTask, taskList, settings, uiCommands, 
                 *args, **kwargs):
        super(EffortPage, self).__init__(parent, theTask, *args, **kwargs)
        self.containerWidget = widgets.Choicebook(self)
        self._viewerContainer = viewercontainer.ViewerContainer(self.containerWidget, 
            settings, 'effortviewerintaskeditor')
        singleTaskList = task.SingleTaskList()
        self.addEffortViewers(singleTaskList, uiCommands, settings)       
        self.add(self.containerWidget, proportion=1, flag=wx.EXPAND|wx.ALL, 
                 border=5)
        singleTaskList.append(theTask)
        self.TopLevelParent.Bind(wx.EVT_CLOSE, self.onClose)
        self.fit()
        
    def onClose(self, event):
        # Don't notify the viewers about any changes anymore, they are about
        # to be deleted.
        for viewer in self._viewerContainer:
            viewer.detach()
        event.Skip()
    
    def addEffortViewers(self, taskList, uiCommands, settings):
        effortViewer = viewer.EffortListViewer(self.containerWidget, taskList, 
            uiCommands, settings, 
            settingsSection='effortlistviewerintaskeditor')
        self._viewerContainer.addViewer(effortViewer, _('Effort details')) 
        effortPerDayViewer = viewer.EffortPerDayViewer(self.containerWidget,
            taskList, uiCommands, settings, 
            settingsSection='effortperdayviewerintaskeditor')
        self._viewerContainer.addViewer(effortPerDayViewer, _('Effort per day'))
        effortPerWeekViewer = viewer.EffortPerWeekViewer(self.containerWidget,
            taskList, uiCommands, settings, 
            settingsSection='effortperweekviewerintaskeditor')
        self._viewerContainer.addViewer(effortPerWeekViewer, 
            _('Effort per week'))
        effortPerMonthViewer = viewer.EffortPerMonthViewer(self.containerWidget,
            taskList, uiCommands, settings, 
            settingsSection='effortpermonthviewerintaskeditor')
        self._viewerContainer.addViewer(effortPerMonthViewer, 
            _('Effort per month'))    


class CategoriesPage(TaskEditorPage):
    def __init__(self, parent, task, categories, *args, **kwargs):
        super(CategoriesPage, self).__init__(parent, task, *args, **kwargs)
        self.__categories = category.CategorySorter(categories)
        categoriesBox = widgets.BoxWithBoxSizer(self, label=_('Categories'))
        self._treeCtrl = widgets.CheckTreeCtrl(categoriesBox, 
            lambda index: self.getCategoryWithIndex(index).subject(),
            lambda *args: None,
            lambda index, expanded=False: -1, 
            lambda index: customtree.TreeItemAttr(),
            self.getChildrenCount, 
            lambda index: 'Undetermined', 
            lambda index: self.getCategoryWithIndex(index) in task.categories(),
            lambda *args: None, lambda *args: None, lambda *args: None,
            lambda *args: None)
        self._treeCtrl.expandAllItems()
        categoriesBox.add(self._treeCtrl, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.fit()
        self.add(categoriesBox)
        self.fit()

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
    
    def getChildrenCount(self, index): # FIXME: duplication with viewers
        if index == ():
            return len(self.__categories.rootItems())
        else:
            category = self.getCategoryWithIndex(index)
            return len(category.children())
        
    def ok(self):
        self._treeCtrl.ExpandAll()
        for item in self._treeCtrl.GetItemChildren(recursively=True):
            index = self._treeCtrl.GetIndexOfItem(item)
            category = self.getCategoryWithIndex(index)
            if item.IsChecked():
                category.addCategorizable(self._task)
                self._task.addCategory(category)
            else:
                category.removeCategorizable(self._task)
                self._task.removeCategory(category)
    

class AttachmentPage(TaskEditorPage):
    def __init__(self, parent, task, settings, *args, **kwargs):
        super(AttachmentPage, self).__init__(parent, task, *args, **kwargs)
        self.settings = settings
        attachmentBox = widgets.BoxWithBoxSizer(self, label=_('Attachments'))
        self._listCtrl = wx.ListCtrl(attachmentBox, style=wx.LC_REPORT)
        self._listCtrl.InsertColumn(0, _('Attachment filenames'))
        self._listCtrl.SetColumnWidth(0, 500)
        attachmentBox.add(self._listCtrl, flag=wx.EXPAND|wx.ALL, proportion=1)
        self._listData = {}

        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._buttonBox = widgets.ButtonBox(attachmentBox, 
            (_('Open attachment'), self.onOpen),
            (_('Remove attachment'), self.onRemove),
            (_('Edit filename'), self.onEdit), 
            orientation=wx.HORIZONTAL)        
        boxSizer.Add(self._buttonBox)
        buttonBox2 = widgets.ButtonBox(attachmentBox, 
            (_('Browse for new attachment...'), self.onBrowse),
            orientation=wx.HORIZONTAL)
        boxSizer.Add(buttonBox2)
        attachmentBox.add(boxSizer)
        attachmentBox.fit()

        filenameBox = widgets.BoxWithBoxSizer(self, 
            label=_('Attachment filename'), orientation=wx.HORIZONTAL)
        self._urlEntry = widgets.SingleLineTextCtrlWithEnterButton(filenameBox, 
            label=_('Add attachment'), onEnter=self.onAdd)
        filenameBox.add(self._urlEntry, proportion=1)
        filenameBox.fit()

        self.add(attachmentBox, proportion=1, border=5)
        self.add(filenameBox, proportion=0, border=5)
        self.fit()
        self.bindEventHandlers()
        for att in task.attachments():
            self.addAttachmentToListCtrl(att)
        if task.attachments():
            self._listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED, 
                                        wx.LIST_STATE_SELECTED)
        else:
            self.onDeselectItem()

    def bindEventHandlers(self):
        self._listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectItem)
        self._listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselectItem)
        self._listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOpen)
        dropTarget = draganddrop.DropTarget(self.onURLDrop, self.onFileDrop,
            self.onMailDrop)
        self._listCtrl.SetDropTarget(dropTarget)
            
    def addAttachmentToListCtrl(self, att):
        item = wx.ListItem()
        item.SetData(wx.NewId())
        item.SetText(unicode(att))
        index = self._listCtrl.InsertItem(item)
        self._listCtrl.Select(index)
        self._listData[item.GetData()] = att
            
    def onAdd(self, *args, **kwargs):
        att = self._urlEntry.GetData()
        if att is None:
            att = attachment.URIAttachment(self._urlEntry.GetValue())
        else:
            att.setDescription(self._urlEntry.GetValue())
        self.addAttachmentToListCtrl(att)
        
    def onFileDrop(self, x, y, filenames):
        base = self.settings.get('file', 'attachmentbase')
        for filename in filenames:
            if base:
                path = attachment.getRelativePath(filename, base)
            else:
                path = filename

            self.addAttachmentToListCtrl(attachment.FileAttachment(path))
            
    def onURLDrop(self, x, y, url):
        self.addAttachmentToListCtrl(attachment.URIAttachment(url))

    def onMailDrop(self, x, y, mail):
        self.addAttachmentToListCtrl(attachment.MailAttachment(mail))

    def onBrowse(self, *args, **kwargs):
        filename = widgets.AttachmentSelector()
        if filename:
            base = self.settings.get('file', 'attachmentbase')
            if base:
                path = attachment.getRelativePath(filename, base)
            else:
                path = filename

            self.addAttachmentToListCtrl(attachment.FileAttachment(path))
        
    def onOpen(self, event, showerror=wx.MessageBox):
        index = -1
        while True:
            index = self._listCtrl.GetNextItem(index, 
                state=wx.LIST_STATE_SELECTED)
            if index == -1:
                break
            attachment = self._listData[self._listCtrl.GetItemData(index)]
            try:    
                attachment.open(self.settings.get('file', 'attachmentbase'))
            except Exception, instance:
                showerror(str(instance), 
                    caption=_('Error opening attachment'), style=wx.ICON_ERROR)
    
    def onRemove(self, *args, **kwargs):
        index = -1
        while True:
            index = self._listCtrl.GetNextItem(index, 
                state=wx.LIST_STATE_SELECTED)
            if index == -1:
                break
            del self._listData[self._listCtrl.GetItemData(index)]
            self._listCtrl.DeleteItem(index)
            
    def onEdit(self, *args, **kwargs):
        index = self._listCtrl.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)
        attachment = self._listData[self._listCtrl.GetItemData(index)]
        self._listCtrl.DeleteItem(index)
        self._urlEntry.SetValue(unicode(attachment))
        self._urlEntry.SetData(attachment)
        self._urlEntry.SetFocus()
    
    def onSelectItem(self, *args, **kwargs):
        for button in self._buttonBox.buttonLabels():
            self._buttonBox.enable(button)
        
    def onDeselectItem(self, *args, **kwargs):
        if self._listCtrl.GetSelectedItemCount() == 0:
            for button in self._buttonBox.buttonLabels():
                self._buttonBox.disable(button)

    def ok(self):
        self._task.removeAllAttachments()
        ids = [ self._listCtrl.GetItemData(i) for i in xrange(self._listCtrl.GetItemCount()) ]
        attachments = [v for id_, v in self._listData.items() if id_ in ids]
        self._task.addAttachments(*attachments)
                                     
            
class BehaviorPage(TaskEditorPage):
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
        self._task.shouldMarkCompletedWhenAllChildrenCompleted = \
            self._markTaskCompletedEntry.GetClientData( \
                self._markTaskCompletedEntry.GetSelection())


class TaskEditBook(widgets.Listbook):
    def __init__(self, parent, task, taskList, uiCommands, settings, 
                 categories, *args, **kwargs):
        super(TaskEditBook, self).__init__(parent)
        self.AddPage(SubjectPage(self, task), _('Description'), 'description')
        self.AddPage(DatesPage(self, task), _('Dates'), 'date')
        self.AddPage(CategoriesPage(self, task, categories), _('Categories'), 
                     'category')
        self.AddPage(BudgetPage(self, task), _('Budget'), 'budget')
        if task.timeSpent(recursive=True):
            effortPage = EffortPage(self, task, taskList, settings, uiCommands)
            self.AddPage(effortPage, _('Effort'), 'start')
        self.AddPage(AttachmentPage(self, task, settings), _('Attachments'), 'attachment')
        self.AddPage(BehaviorPage(self, task), _('Behavior'), 'behavior') 


class EffortEditBook(widgets.BookPage):
    def __init__(self, parent, effort, editor, effortList, taskList, 
                 *args, **kwargs):
        super(EffortEditBook, self).__init__(parent, columns=3, *args, **kwargs)
        self._editor = editor
        self._effort = effort
        self._effortList = effortList
        self._taskList = taskList
        self.addTaskEntry()
        self.addStartAndStopEntries()
        self.addDescriptionEntry()
        self.fit()

    def addTaskEntry(self):
        self._taskEntry = combotreebox.ComboTreeBox(self, 
            style=wx.CB_READONLY|wx.CB_SORT)

        def addTaskRecursively(task, parentItem=None):
            item = self._taskEntry.Append(task.subject(), 
                parent=parentItem, clientData=task)
            for child in task.children():
                addTaskRecursively(child, item)

        for task in self._taskList.rootItems():
            addTaskRecursively(task)
        self._taskEntry.SetClientDataSelection(self._effort.task())
        self.addEntry(_('Task'), self._taskEntry, flags=[None, wx.ALL|wx.EXPAND])

    def addStartAndStopEntries(self):
        self._startEntry = widgets.DateTimeCtrl(self, self._effort.getStart(),
            self.onPeriodChanged, noneAllowed=False)
        startFromLastEffortButton = wx.Button(self, 
            label=_('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort, 
            startFromLastEffortButton) 
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()
        
        self._stopEntry = widgets.DateTimeCtrl(self, self._effort.getStop(),
            self.onPeriodChanged, noneAllowed=True)
        
        flags = [None, wx.ALIGN_RIGHT|wx.ALL, wx.ALIGN_LEFT|wx.ALL, None]
        self.addEntry(_('Start'), self._startEntry, 
            startFromLastEffortButton,  flags=flags)
        self.addEntry(_('Stop'), self._stopEntry, '', flags=flags)
            
    def onStartFromLastEffort(self, event):
        self._startEntry.SetValue(self._effortList.maxDateTime())
        self.preventNegativeEffortDuration()
            
    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, 
            self._effort.getDescription())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry, 
            flags=[None, wx.ALL|wx.EXPAND], growable=True)
        
    def ok(self):
        self._effort.setTask(self._taskEntry.GetClientData(self._taskEntry.GetSelection()))
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


class CategoryEditBook(widgets.BookPage):
    def __init__(self, parent, category, *args, **kwargs):
        super(CategoryEditBook, self).__init__(parent, columns=3, *args, **kwargs)
        self._category = category
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
        
    def addColorEntry(self):
        currentColor = self._category.color(recursive=False)
        self._checkBox = wx.CheckBox(self, label=_('Use this color:'))
        self._checkBox.SetValue(currentColor is not None)
        self._colorButton = wx.ColourPickerCtrl(self, -1, 
            currentColor or wx.WHITE, size=(40,-1))
        self._colorButton.Bind(wx.EVT_COLOURPICKER_CHANGED, 
            lambda event: self._checkBox.SetValue(True))
        self.addEntry(_('Color'), self._checkBox, self._colorButton)

    def ok(self):
        self._category.setSubject(self._subjectEntry.GetValue())
        self._category.setDescription(self._descriptionEntry.GetValue())
        if self._checkBox.IsChecked():
            color = self._colorButton.GetColour()
        else:
            color = None
        self._category.setColor(color)


class NoteSubjectPage(widgets.BookPage):
    def __init__(self, parent, theNote, *args, **kwargs):
        super(NoteSubjectPage, self).__init__(parent, columns=2, *args, **kwargs)
        self._note = theNote
        self.addSubjectEntry()
        self.addDescriptionEntry()
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


class NoteCategoriesPage(widgets.BookPage): # FIXME: duplication with (Task)CategoriesPage
    def __init__(self, parent, theNote, categories, *args, **kwargs):
        super(NoteCategoriesPage, self).__init__(parent, columns=1, *args, **kwargs)
        self._note = theNote
        self.__categories = category.CategorySorter(categories)
        categoriesBox = widgets.BoxWithBoxSizer(self, label=_('Categories'))
        self._treeCtrl = widgets.CheckTreeCtrl(categoriesBox, 
            lambda index: self.getCategoryWithIndex(index).subject(),
            lambda *args: None,
            lambda index, expanded=False: -1, 
            lambda index: customtree.TreeItemAttr(),
            self.getChildrenCount, 
            lambda index: 'Undetermined', 
            lambda index: self.getCategoryWithIndex(index) in theNote.categories(),
            lambda *args: None, lambda *args: None, lambda *args: None,
            lambda *args: None)
        self._treeCtrl.expandAllItems()
        categoriesBox.add(self._treeCtrl, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.fit()
        self.addEntry(categoriesBox, growable=True)
        self.fit()

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
    
    def getChildrenCount(self, index): # FIXME: duplication with viewers
        if index == ():
            return len(self.__categories.rootItems())
        else:
            category = self.getCategoryWithIndex(index)
            return len(category.children())
        
    def ok(self):
        self._treeCtrl.ExpandAll()
        for item in self._treeCtrl.GetItemChildren(recursively=True):
            index = self._treeCtrl.GetIndexOfItem(item)
            category = self.getCategoryWithIndex(index)
            if item.IsChecked():
                category.addCategorizable(self._note)
                self._note.addCategory(category)
            else:
                category.removeCategorizable(self._note)
                self._note.removeCategory(category)


class NoteEditBook(widgets.Listbook):
    def __init__(self, parent, theNote, categories, *args, **kwargs):
        super(NoteEditBook, self).__init__(parent, *args, **kwargs)
        self.AddPage(NoteSubjectPage(self, theNote), _('Description'), 'description')
        self.AddPage(NoteCategoriesPage(self, theNote, categories), _('Categories'), 
                     'category')


class EditorWithCommand(widgets.NotebookDialog):
    def __init__(self, parent, command, uiCommands, *args, **kwargs):
        self._uiCommands = uiCommands
        self._command = command
        super(EditorWithCommand, self).__init__(parent, command.name(), *args, **kwargs)
        
    def ok(self, *args, **kwargs):
        self._command.do()
        super(EditorWithCommand, self).ok(*args, **kwargs)

            
class TaskEditor(EditorWithCommand):
    def __init__(self, parent, command, taskList, uiCommands, settings, categories, bitmap='edit', *args, **kwargs):
        self._settings = settings
        self._taskList = taskList
        self._categories = categories
        super(TaskEditor, self).__init__(parent, command, uiCommands, bitmap, *args, **kwargs)
        self[0][0]._subjectEntry.SetSelection(-1, -1)
        # This works on Linux Ubuntu 5.10, but fails silently on Windows XP:
        self.setFocus() 
        # This works on Windows XP, but fails silently on Linux Ubuntu 5.10:
        wx.CallAfter(self.setFocus) 
        # So we did just do it twice, guess it doesn't hurt

    def setFocus(self, *args, **kwargs):
        self[0][0]._subjectEntry.SetFocus()
        
    def addPages(self):
        for task in self._command.items:
            self.addPage(task)

    def addPage(self, task):
        page = TaskEditBook(self._interior, task, self._taskList, 
            self._uiCommands, self._settings, self._categories)
        self._interior.AddPage(page, task.subject())
        
    
class EffortEditor(EditorWithCommand):
    def __init__(self, parent, command, uiCommands, effortList, taskList, 
                 *args, **kwargs):
        self._effortList = effortList
        self._taskList = taskList
        super(EffortEditor, self).__init__(parent, command, uiCommands, 
                                           *args, **kwargs)
        
    def addPages(self):
        for effort in self._command.efforts: # FIXME: use getter
            self.addPage(effort)

    def addPage(self, effort):
        page = EffortEditBook(self._interior, effort, self, self._effortList, 
            self._taskList)
        self._interior.AddPage(page, effort.task().subject())


class CategoryEditor(EditorWithCommand):
    def __init__(self, parent, command, uiCommands, categories, *args, **kwargs):
        self._categories = categories
        super(CategoryEditor, self).__init__(parent, command, uiCommands, 
                                             *args, **kwargs)
        self[0]._subjectEntry.SetSelection(-1, -1)
        # This works on Linux Ubuntu 5.10, but fails silently on Windows XP:
        self.setFocus() 
        # This works on Windows XP, but fails silently on Linux Ubuntu 5.10:
        wx.CallAfter(self.setFocus) 
        # So we did just do it twice, guess it doesn't hurt

    def setFocus(self, *args, **kwargs):
        self[0]._subjectEntry.SetFocus()
        
    def addPages(self):
        for category in self._command.items:
            self.addPage(category)
            
    def addPage(self, category):
        page = CategoryEditBook(self._interior, category)
        self._interior.AddPage(page, category.subject())


class NoteEditor(EditorWithCommand):
    def __init__(self, parent, command, categories, *args, **kwargs):
        self._categories = categories
        super(NoteEditor, self).__init__(parent, command, None, *args, **kwargs)
        self[0][0]._subjectEntry.SetSelection(-1, -1)
        # This works on Linux Ubuntu 5.10, but fails silently on Windows XP:
        self.setFocus() 
        # This works on Windows XP, but fails silently on Linux Ubuntu 5.10:
        wx.CallAfter(self.setFocus) 
        # So we did just do it twice, guess it doesn't hurt

    def setFocus(self, *args, **kwargs):
        self[0][0]._subjectEntry.SetFocus()
        
    def addPages(self):
        for note in self._command.items:
            self.addPage(note)
            
    def addPage(self, note):
        page = NoteEditBook(self._interior, note, self._categories)
        self._interior.AddPage(page, note.subject())

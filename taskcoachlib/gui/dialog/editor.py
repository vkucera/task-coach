import widgets
from gui import render
import widgets.draganddrop as draganddrop
import wx, datetime
import wx.lib.masked as masked
from i18n import _
import domain.date as date
import thirdparty.desktop as desktop


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
                formatcodes='RrFS')
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
        self._prioritySpinner = wx.SpinCtrl(priorityBox, value=render.priority(task.priority()), 
            style=wx.SP_ARROW_KEYS)
        # Can't use sys.maxint because Python and wxPython disagree on what the 
        # maximum integer is on Suse 10.0 x86_64. Using sys.maxint will cause
        # an Overflow exception, so we use a constant:
        maxint = 2147483647
        self._prioritySpinner.SetRange(-maxint, maxint)
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
            entry = DateEntry(datesBox, taskMethod())
            setattr(self, '_%sEntry'%taskMethodName, entry)
            datesBox.add(entry)
            if task.children():
                recursiveEntry = DateEntry(datesBox, taskMethod(recursive=True), readonly=True)
            else:
                recursiveEntry = (0, 0)
            datesBox.add(recursiveEntry)
        
        reminderBox = widgets.BoxWithFlexGridSizer(self, label=_('Reminder'), cols=2)
        reminderBox.add(_('Reminder'))
        self._reminderDateTimeEntry = widgets.DateTimeCtrl(reminderBox, task.reminder())
        reminderBox.add(self._reminderDateTimeEntry)
        for box in datesBox, reminderBox:
            box.fit()
            self.add(box, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()

    def ok(self):                   
        self._task.setStartDate(self._startDateEntry.get())
        self._task.setDueDate(self._dueDateEntry.get())
        self._task.setCompletionDate(self._completionDateEntry.get())
        self._task.setReminder(self._reminderDateTimeEntry.GetValue())

    def setReminder(self, newReminder):
        self._reminderDateTimeEntry.SetValue(newReminder)
        

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
            self.add(box, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()
        
    def ok(self):
        self._task.setBudget(self._budgetEntry.get())           
        self._task.setHourlyFee(self._hourlyFeeEntry.get())   
        self._task.setFixedFee(self._fixedFeeEntry.get())   


class EffortPage(TaskEditorPage):        
    def __init__(self, parent, task, taskList, settings, uiCommands, *args, **kwargs):
        super(EffortPage, self).__init__(parent, task, *args, **kwargs)
        from gui import viewercontainer, viewerfactory
        import domain.effort as effort
        viewerContainer = viewercontainer.ViewerChoicebook(self, settings, 
            'effortviewerineditor')
        myEffortList = effort.SingleTaskEffortList(task)
        viewerfactory._addEffortViewers(viewerContainer, myEffortList, 
            taskList, uiCommands, settings)
        self.add(viewerContainer, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        self.fit()


class CategoriesPage(TaskEditorPage):
    def __init__(self, parent, task, categories, *args, **kwargs):
        super(CategoriesPage, self).__init__(parent, task, *args, **kwargs)
        categoriesBox = widgets.BoxWithFlexGridSizer(self, label=_('Categories'), cols=2, growableCol=1, growableRow=0)
        self._checkListBox = wx.CheckListBox(categoriesBox)
        self._checkListBox.InsertItems(categories, 0)
        for index in range(self._checkListBox.GetCount()):
            if self._checkListBox.GetString(index) in task.categories():
                self._checkListBox.Check(index)
        categoriesBox.add(_('Categories'))
        categoriesBox.add(self._checkListBox, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.add(_('New category'))
        self._textEntry = widgets.SingleLineTextCtrlWithEnterButton(categoriesBox, 
            label=_('New category'), onEnter=self.onNewCategory)
        categoriesBox.add(self._textEntry, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.fit()
        self.add(categoriesBox, border=5)
        self.fit()
        
    def ok(self):
        for index in range(self._checkListBox.GetCount()):
            category = self._checkListBox.GetString(index)
            if self._checkListBox.IsChecked(index):
                self._task.addCategory(category)
            else:
                self._task.removeCategory(category)
                    
    def onNewCategory(self, newCategory):
        self._checkListBox.InsertItems([newCategory], 0)
        self._checkListBox.Check(0)


class AttachmentPage(TaskEditorPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(AttachmentPage, self).__init__(parent, task, *args, **kwargs)
        attachmentBox = widgets.BoxWithFlexGridSizer(self, 
            label=_('Attachments'), cols=2, growableCol=1, growableRow=0)
        self._buttonBox = widgets.ButtonBox(attachmentBox, 
            (_('Open attachment'), self.onOpen),
            (_('Remove attachment'), self.onRemove),
            (_('Edit attachment'), self.onEdit), orientation=wx.HORIZONTAL)        
        self._listCtrl = wx.ListCtrl(attachmentBox, style=wx.LC_LIST)
        self._listCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectItem)
        self._listCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselectItem)
        self._listCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOpen)
        dropTarget = draganddrop.FileDropTarget(self.onFileDrop)
        self._listCtrl.SetDropTarget(dropTarget)
        self.onFileDrop(0, 0, task.attachments())
        attachmentBox.add(_('Attachments'))
        attachmentBox.add(self._listCtrl, flag=wx.EXPAND|wx.ALL, proportion=1)
        attachmentBox.add('')
        attachmentBox.add(self._buttonBox)
        self._urlEntry = widgets.SingleLineTextCtrlWithEnterButton(attachmentBox, 
            label=_('Add attachment'), onEnter=self.onAdd)
        attachmentBox.add(_('New attachment'))
        attachmentBox.add(self._urlEntry, flag=wx.EXPAND|wx.ALL, proportion=1)
        attachmentBox.add('')
        browseButton = wx.Button(attachmentBox, label=_('Browse for attachment...'))
        browseButton.Bind(wx.EVT_BUTTON, self.onBrowse)
        attachmentBox.add(browseButton)
        if task.attachments():
            self._listCtrl.SetItemState(0, wx.LIST_STATE_SELECTED, 
                                        wx.LIST_STATE_SELECTED)
        else:
            self.onDeselectItem()
        attachmentBox.fit()
        self.add(attachmentBox, border=5)
        self.fit()
            
    def addAttachmentToListCtrl(self, filename):
        item = wx.ListItem()
        item.SetText(filename)
        index = self._listCtrl.InsertItem(item)
        self._listCtrl.Select(index)
            
    def onAdd(self, *args, **kwargs):
        self.addAttachmentToListCtrl(self._urlEntry.GetValue())
        
    def onFileDrop(self, x, y, filenames):
        for filename in filenames:
            self.addAttachmentToListCtrl(filename)
        
    def onBrowse(self, *args, **kwargs):
        filename = widgets.AttachmentSelector()
        if filename:
            self.addAttachmentToListCtrl(filename)
        
    def onOpen(self, *args, **kwargs):
        index = -1
        while True:
            index = self._listCtrl.GetNextItem(index, state=wx.LIST_STATE_SELECTED)
            if index == -1:
                break
            try:
                desktop.open(self._listCtrl.GetItemText(index))
            except Exception, instance:
                wx.MessageBox(str(instance), caption=_('Error opening attachment'), 
                              style=wx.ICON_ERROR)
    
    def onRemove(self, *args, **kwargs):
        index = -1
        while True:
            index = self._listCtrl.GetNextItem(index, state=wx.LIST_STATE_SELECTED)
            if index == -1:
                break
            self._listCtrl.DeleteItem(index)
            
    def onEdit(self, *args, **kwargs):
        index = self._listCtrl.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)
        attachment = self._listCtrl.GetItem(index).GetText()
        self._listCtrl.DeleteItem(index)
        self._urlEntry.SetValue(attachment)
    
    def onSelectItem(self, *args, **kwargs):
        for button in self._buttonBox.buttonLabels():
            self._buttonBox.enable(button)
        
    def onDeselectItem(self, *args, **kwargs):
        if self._listCtrl.GetSelectedItemCount() == 0:
            for button in self._buttonBox.buttonLabels():
                self._buttonBox.disable(button)
        
    def ok(self):
        self._task.removeAllAttachments()
        attachments = [self._listCtrl.GetItem(index).GetText() for index in range(self._listCtrl.GetItemCount())]
        self._task.addAttachments(*attachments)
                                     
            
class BehaviorPage(TaskEditorPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(BehaviorPage, self).__init__(parent, task, *args, **kwargs)
        behaviorBox = widgets.BoxWithFlexGridSizer(self,
            label=_('Task behavior'), cols=2)                                           
        choice = self._markTaskCompletedEntry = wx.Choice(behaviorBox)
        for choiceValue, choiceText in [(None, _('Use application-wide setting')), 
                                        (False, _('No')), (True, _('Yes'))]:
            choice.Append(choiceText, choiceValue)
            if choiceValue == task.shouldMarkCompletedWhenAllChildrenCompleted:
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND: # force a selection if necessary
            choice.SetSelection(0)
        behaviorBox.add(_('Mark task completed when all children are completed?'))
        behaviorBox.add(choice)
        behaviorBox.fit()
        self.add(behaviorBox, border=5)
        self.fit()
            
    def ok(self):
        self._task.shouldMarkCompletedWhenAllChildrenCompleted = \
            self._markTaskCompletedEntry.GetClientData(self._markTaskCompletedEntry.GetSelection())


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
        self.AddPage(AttachmentPage(self, task), _('Attachments'), 'attachment')
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
        
    def addTaskEntry(self):
        self._taskEntry = wx.ComboBox(self, style=wx.CB_READONLY|wx.CB_SORT)
        for task in self._taskList:
            self._taskEntry.Append(render.subject(task, recursively=True), task)
        self._taskEntry.SetStringSelection(render.subject(self._effort.task(),
            recursively=True))
        self.addEntry(_('Task'), self._taskEntry)

    def addStartAndStopEntries(self):
        self._startEntry = widgets.DateTimeCtrl(self, self._effort.getStart(),
            self.preventNegativeEffortDuration, noneAllowed=False)
        startFromLastEffortButton = wx.Button(self, -1, 
            _('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort, 
            startFromLastEffortButton) 
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()
        
        self._stopEntry = widgets.DateTimeCtrl(self, self._effort.getStop(),
            self.preventNegativeEffortDuration, noneAllowed=True)
        
        self.addEntry(_('Start'), self._startEntry, startFromLastEffortButton)
        self.addEntry(_('Stop'), self._stopEntry, '')
            
    def onStartFromLastEffort(self, event):
        self._startEntry.SetValue(self._effortList.maxDateTime())
        self.preventNegativeEffortDuration()
            
    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.MultiLineTextCtrl(self, 
            self._effort.getDescription())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry)
        
    def ok(self):
        self._effort.setTask(self._taskEntry.GetClientData(self._taskEntry.GetSelection()))
        self._effort.setStart(self._startEntry.GetValue())
        self._effort.setStop(self._stopEntry.GetValue())
        self._effort.setDescription(self._descriptionEntry.GetValue())

    def preventNegativeEffortDuration(self, *args, **kwargs):
        if not hasattr(self, '_stopEntry'): # check that both entries have been created
            return
        if self._startEntry.GetValue() > self._stopEntry.GetValue():
            self._editor.disableOK()
        else:
            self._editor.enableOK()


class EditorWithCommand(widgets.NotebookDialog):
    def __init__(self, parent, command, uiCommands, *args, **kwargs):
        self._uiCommands = uiCommands
        self._command = command
        super(EditorWithCommand, self).__init__(parent, command.name(), *args, **kwargs)
        
    def ok(self, *args, **kwargs):
        super(EditorWithCommand, self).ok(*args, **kwargs)
        self._command.do()

            
class TaskEditor(EditorWithCommand):
    def __init__(self, parent, command, taskList, uiCommands, settings, categories=None, bitmap='edit', *args, **kwargs):
        self._settings = settings
        self._taskList = taskList
        self._categories = list(categories or [])
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


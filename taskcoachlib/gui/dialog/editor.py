import widgets
from gui import render, viewercontainer, viewer
import widgets.draganddrop as draganddrop
import domain.attachment as attachment
import wx, datetime
import wx.lib.masked as masked
import wx.lib.customtreectrl as customtree
import wx.lib.combotreebox as combotreebox
from i18n import _
from domain import task, category, date, note
from thirdparty import desktop
from mailer import outlook, thunderbird
import os.path


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
    def __init__(self, parent, theTask, taskList, settings, uiCommands, 
                 *args, **kwargs):
        super(EffortPage, self).__init__(parent, theTask, *args, **kwargs)
        self._viewerContainer = viewercontainer.ViewerChoicebook(self, settings, 
            'effortviewerineditor')
        singleTaskList = task.SingleTaskList()
        self.addEffortViewers(singleTaskList, uiCommands, settings)
        self.add(self._viewerContainer, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        singleTaskList.append(theTask)
        self.fit()
    
    def addEffortViewers(self, taskList, uiCommands, settings):
        effortViewer = viewer.EffortListViewer(self._viewerContainer, taskList, 
            uiCommands, settings)
        self._viewerContainer.addViewer(effortViewer, _('Effort details'), 'start')
        effortPerDayViewer = viewer.EffortPerDayViewer(self._viewerContainer,
            taskList, uiCommands, settings)
        self._viewerContainer.addViewer(effortPerDayViewer, _('Effort per day'), 'date')
        effortPerWeekViewer = viewer.EffortPerWeekViewer(self._viewerContainer,
            taskList, uiCommands, settings)
        self._viewerContainer.addViewer(effortPerWeekViewer, _('Effort per week'), 
            'date')
        effortPerMonthViewer = viewer.EffortPerMonthViewer(self._viewerContainer,
            taskList, uiCommands, settings)
        self._viewerContainer.addViewer(effortPerMonthViewer, _('Effort per month'), 
            'date')    


class CategoriesPage(TaskEditorPage):
    def __init__(self, parent, task, categories, *args, **kwargs):
        super(CategoriesPage, self).__init__(parent, task, *args, **kwargs)
        self.__categories = category.CategorySorter(categories)
        categoriesBox = widgets.BoxWithBoxSizer(self, label=_('Categories'))
        self._treeCtrl = widgets.CheckTreeCtrl(categoriesBox, 
            lambda index: self.getCategoryWithIndex(index).subject(),
            lambda index, expanded=False: -1, lambda index: customtree.TreeItemAttr(),
            self.getChildrenCount,
            lambda index: task in self.getCategoryWithIndex(index).tasks(),
            lambda *args: None, lambda *args: None, lambda *args: None,
            lambda *args: None)
        categoriesBox.add(self._treeCtrl, proportion=1, flag=wx.EXPAND|wx.ALL)
        categoriesBox.fit()
        self.add(categoriesBox)
        self.fit()

    def getCategoryWithIndex(self, index):
        children = self.__categories.rootItems()
        for i in index:
            category = children[i]
            children = [child for child in category.children() \
                        if child in self.__categories]
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
                category.addTask(self._task)
            else:
                category.removeTask(self._task)
    

class AttachmentPage(TaskEditorPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(AttachmentPage, self).__init__(parent, task, *args, **kwargs)
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
        #dropTarget = draganddrop.FileDropTarget(self.onFileDrop)
        dropTarget = draganddrop.DropTarget(self.onURLDrop, self.onFileDrop,
            self.onThunderbirdMailDrop, self.onOutlookMailDrop)
        self._listCtrl.SetDropTarget(dropTarget)
            
    def addAttachmentToListCtrl(self, att):
        item = wx.ListItem()
        item.SetData(wx.NewId())
        item.SetText(unicode(att))
        index = self._listCtrl.InsertItem(item)
        self._listCtrl.Select(index)
        self._listData[item.GetData()] = att
            
    def onAdd(self, *args, **kwargs):
        self.addAttachmentToListCtrl(attachment.URIAttachment(self._urlEntry.GetValue()))
        
    def onFileDrop(self, filenames):
        for filename in filenames:
            self.addAttachmentToListCtrl(attachment.FileAttachment(filename))
            
    def onURLDrop(self, url):
        self.addAttachmentToListCtrl(attachment.URIAttachment(url))

    def onThunderbirdMailDrop(self, id_):
        self.addAttachmentToListCtrl(attachment.MailAttachment(thunderbird.getMail(id_)))

    def onOutlookMailDrop(self):
        for filename in outlook.getCurrentSelection():
            self.addAttachmentToListCtrl(attachment.MailAttachment(filename))

    def onBrowse(self, *args, **kwargs):
        filename = widgets.AttachmentSelector()
        if filename:
            self.addAttachmentToListCtrl(attachment.FileAttachment(filename))
        
    def onOpen(self, event, showerror=wx.MessageBox):
        index = -1
        while True:
            index = self._listCtrl.GetNextItem(index, 
                state=wx.LIST_STATE_SELECTED)
            if index == -1:
                break
            attachment = self._listData[self._listCtrl.GetItemData(index)]
            try:    
                attachment.open()
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
        # FIXME: disable editing for certain types of attachment, fix this
        index = self._listCtrl.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)
        attachment = self._listCtrl.GetItem(index).GetText()
        self._listCtrl.DeleteItem(index)
        self._urlEntry.SetValue(attachment)
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
    def __init__(self, parent, category, editor, *args, **kwargs):
        super(CategoryEditBook, self).__init__(parent, columns=2, *args, **kwargs)
        self._editor = editor
        self._category = category
        self.addSubjectEntry()
        self.fit()

    def addSubjectEntry(self):
        self._subjectEntry = widgets.SingleLineTextCtrl(self, self._category.subject())
        self.addEntry(_('Subject'), self._subjectEntry, flags=[None, wx.ALL|wx.EXPAND])

    def ok(self):
        self._category.setSubject(self._subjectEntry.GetValue())


class NoteEditBook(widgets.BookPage):
    def __init__(self, parent, theNote, editor, *args, **kwargs):
        super(NoteEditBook, self).__init__(parent, columns=2, *args, **kwargs)
        self._editor = editor
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
        

class EditorWithCommand(widgets.NotebookDialog):
    def __init__(self, parent, command, uiCommands, *args, **kwargs):
        self._uiCommands = uiCommands
        self._command = command
        super(EditorWithCommand, self).__init__(parent, command.name(), *args, **kwargs)
        
    def ok(self, *args, **kwargs):
        super(EditorWithCommand, self).ok(*args, **kwargs)
        self._command.do()

            
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
        page = CategoryEditBook(self._interior, category, self)
        self._interior.AddPage(page, category.subject())


class NoteEditor(EditorWithCommand):
    def __init__(self, parent, command, uiCommands, notes, *args, **kwargs):
        self._notes = notes
        super(NoteEditor, self).__init__(parent, command, uiCommands, 
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
        for note in self._command.items:
            self.addPage(note)
            
    def addPage(self, note):
        page = NoteEditBook(self._interior, note, self)
        self._interior.AddPage(page, note.subject())

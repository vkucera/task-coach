import date, widgets
from gui import render
import wx, datetime
import wx.lib.masked as masked
from i18n import _

class DateEntry(wx.Panel):
    defaultDate = date.Date()

    def __init__(self, parent, date=defaultDate, readonly=False, callback=None, *args, **kwargs):
        super(DateEntry, self).__init__(parent, -1, *args, **kwargs)
        self._entry = widgets.DateCtrl(self, callback, size=(100, -1))
        if readonly:
            self._entry.Disable()
        self._entry.SetValue(date)

    def get(self, defaultDate=None):
        result = self._entry.GetValue()
        if result == date.Date() and defaultDate:
            result = defaultDate
        return result

    def set(self, date=defaultDate):
        self._entry.SetValue(date)

    def setToday(self):
        self._entry.SetValue(date.Today())


class TimeDeltaEntry(wx.Panel):
    defaultTimeDelta=date.TimeDelta()
    
    def __init__(self, parent, timeDelta=defaultTimeDelta, readonly=False, *args, **kwargs):
        super(TimeDeltaEntry, self).__init__(parent, -1, *args, **kwargs)
        if readonly:
            self._entry = wx.StaticText(self, -1, render.timeSpent(timeDelta))
        else:
            self._entry = masked.TextCtrl(self, -1, mask='#{6}:##:##',
                formatcodes='RrFS')
            hours, minutes, seconds = timeDelta.hoursMinutesSeconds()
            self._entry.SetFieldParameters(0, defaultValue='%6d'%hours)
            self._entry.SetFieldParameters(1, defaultValue='%02d'%minutes)
            self._entry.SetFieldParameters(2, defaultValue='%02d'%seconds)

    def get(self):
        return date.parseTimeDelta(self._entry.GetValue())


class SubjectPage(widgets.BookPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(SubjectPage, self).__init__(parent, columns=2, *args, **kwargs)
        self._subjectEntry = wx.TextCtrl(self, -1, task.subject())
        self._descriptionEntry = widgets.TextCtrl(self, task.description())
        self._descriptionEntry.SetSizeHints(500, 260)
        self.addEntry(_('Subject'), self._subjectEntry)    
        self.addEntry(_('Description'), self._descriptionEntry, growable=True)    
        self._task = task
        
    def ok(self):
        self._task.setSubject(self._subjectEntry.GetValue())
        self._task.setDescription(self._descriptionEntry.GetValue())

    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)

    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)        


class DatesPage(widgets.BookPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(DatesPage, self).__init__(parent, columns=3, *args, **kwargs)
        self._task = task
        self._startDateEntry = DateEntry(self, task.startDate())
        self._dueDateEntry = DateEntry(self, task.dueDate())
        self._completionDateEntry = DateEntry(self, task.completionDate())        
        entriesArgs = [['', _('For this task')],
                       [_('Start date'), self._startDateEntry],
                       [_('Due date'), self._dueDateEntry],
                       [_('Completion date'), self._completionDateEntry]]    
        if task.children():
            entriesArgs[0].append(_('For this task including all subtasks'))
            entriesArgs[1].append(DateEntry(self, task.startDate(recursive=True), readonly=True))
            entriesArgs[2].append(DateEntry(self, task.dueDate(recursive=True), readonly=True))
            entriesArgs[3].append(DateEntry(self, task.completionDate(recursive=True), readonly=True))
        for entryArgs in entriesArgs:
            self.addEntry(*entryArgs)

    def ok(self):                   
        self._task.setStartDate(self._startDateEntry.get())
        self._task.setDueDate(self._dueDateEntry.get())
        self._task.setCompletionDate(self._completionDateEntry.get())


class BudgetPage(widgets.BookPage):
    def __init__(self, parent, task, *args, **kwargs):
        super(BudgetPage, self).__init__(parent, columns=3, *args, **kwargs)
        self._task = task
        self._budgetEntry = TimeDeltaEntry(self, task.budget())
        entriesArgs = [['', _('For this task')],
                       [_('Budget'), self._budgetEntry],
                       [_('Time spent'), render.timeSpent(task.timeSpent())],
                       [_('Budget left'), render.budget(task.budgetLeft())]]
        if task.children():
            entriesArgs[0].append(_('For this task including all subtasks'))
            entriesArgs[1].append(render.budget(task.budget(recursive=True)))
            entriesArgs[2].append(render.timeSpent(task.timeSpent(recursive=True)))
            entriesArgs[3].append(render.budget(task.budgetLeft(recursive=True)))
        for entryArgs in entriesArgs:
            self.addEntry(*entryArgs)

    def ok(self):
        self._task.setBudget(self._budgetEntry.get())              


class EffortPage(widgets.BookPage):        
    def __init__(self, parent, task, settings, uiCommands, *args, **kwargs):
        super(EffortPage, self).__init__(parent, columns=1, *args, **kwargs)
        from gui import viewercontainer, viewerfactory
        import effort
        viewerContainer = viewercontainer.ViewerChoicebook(self, settings, 'effortviewerineditor')
        myEffortList = effort.SingleTaskEffortList(task)
        viewerfactory._addEffortViewers(viewerContainer, myEffortList, uiCommands)
        self.addEntry(None, viewerContainer, growable=True)


class CategoriesPage(widgets.BookPage):
    def __init__(self, parent, task, categories, *args, **kwargs):
        super(CategoriesPage, self).__init__(parent, columns=3, growableColumn=1, *args, **kwargs)
        self._prioritySpinner = wx.SpinCtrl(self, -1, render.priority(task.priority()), 
            style=wx.SP_ARROW_KEYS)
        self.addEntry(_('Priority'), self._prioritySpinner)
        self._checkListBox = wx.CheckListBox(self, -1)
        self._checkListBox.InsertItems(categories, 0)
        for index in range(self._checkListBox.GetCount()):
            if self._checkListBox.GetString(index) in task.categories():
                self._checkListBox.Check(index)
        self.addEntry(_('Categories'), self._checkListBox, growable=True)
        self._textEntry = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        addButton = wx.Button(self, -1, 'Add category')
        addButton.Bind(wx.EVT_BUTTON, self.onNewCategory)
        self.addEntry(_('New category'), self._textEntry, addButton)
        self.Bind(wx.EVT_TEXT_ENTER, self.onNewCategory, self._textEntry)
        self._task = task
        
    def ok(self):
        self._task.setPriority(self._prioritySpinner.GetValue())
        for index in range(self._checkListBox.GetCount()):
            category = self._checkListBox.GetString(index)
            if self._checkListBox.IsChecked(index):
                self._task.addCategory(category)
            else:
                self._task.removeCategory(category)

    def onNewCategory(self, event):
        self._checkListBox.InsertItems([self._textEntry.GetValue()], 0)
        self._checkListBox.Check(0)
        self._textEntry.Clear()


class TaskEditBook(widgets.Listbook):
    def __init__(self, parent, task, uiCommands, settings, categories, *args, **kwargs):
        super(TaskEditBook, self).__init__(parent)
        self.AddPage(SubjectPage(self, task), _('Description'), 'description')
        self.AddPage(DatesPage(self, task), _('Dates'), 'date')
        self.AddPage(CategoriesPage(self, task, categories), _('Categories'), 'category')
        self.AddPage(BudgetPage(self, task), _('Budget'), 'budget')        
        if task.timeSpent(recursive=True):
            effortPage = EffortPage(self, task, settings, uiCommands)
            self.AddPage(effortPage, _('Effort'), 'start')
                  

class EffortEditBook(widgets.BookPage):
    def __init__(self, parent, effort, editor, effortList, *args, **kwargs):
        super(EffortEditBook, self).__init__(parent, columns=3, *args, **kwargs)
        self._editor = editor
        self._effort = effort
        self._effortList = effortList
        self.addStartAndStopEntries()
        self.addDescriptionEntry()
        
    def addStartAndStopEntries(self):
        self._startEntry = widgets.DateTimeCtrl(self, self._effort.getStart(),
            self.preventNegativeEffortDuration, noneAllowed=False)
        startFromLastEffortButton = wx.Button(self, -1, _('Start tracking from last stop time'))
        self.Bind(wx.EVT_BUTTON, self.onStartFromLastEffort, startFromLastEffortButton) 
        if self._effortList.maxDateTime() is None:
            startFromLastEffortButton.Disable()
        
        self._stopEntry = widgets.DateTimeCtrl(self, self._effort.getStop(),
            self.preventNegativeEffortDuration)
        
        self.addEntry(_('Start'), self._startEntry, startFromLastEffortButton)
        self.addEntry(_('Stop'), self._stopEntry, '')
            
    def onStartFromLastEffort(self, event):
        self._startEntry.SetValue(self._effortList.maxDateTime())
        self.preventNegativeEffortDuration()
            
    def addDescriptionEntry(self):
        self._descriptionEntry = widgets.TextCtrl(self, self._effort.getDescription())
        self._descriptionEntry.SetSizeHints(300, 150)
        self.addEntry(_('Description'), self._descriptionEntry)
        
    def ok(self):
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
    def __init__(self, parent, command, uiCommands, settings, categories=None, bitmap='edit', *args, **kwargs):
        self._settings = settings
        self._categories = list(categories or [])
        super(TaskEditor, self).__init__(parent, command, uiCommands, bitmap, *args, **kwargs)
        self[0][0]._subjectEntry.SetSelection(-1, -1)
        wx.CallAfter(self[0][0]._subjectEntry.SetFocus)
        
    def addPages(self):
        for task in self._command.items:
            self.addPage(task)

    def addPage(self, task):
        page = TaskEditBook(self._interior, task, self._uiCommands, self._settings, self._categories)
        self._interior.AddPage(page, task.subject())
        
    
class EffortEditor(EditorWithCommand):
    def __init__(self, parent, command, uiCommands, effortList, *args, **kwargs):
        self._effortList = effortList
        super(EffortEditor, self).__init__(parent, command, uiCommands, *args, **kwargs)
        
    def addPages(self):
        for effort in self._command.efforts: # FIXME: use getter
            self.addPage(effort)

    def addPage(self, effort):
        page = EffortEditBook(self._interior, effort, self, self._effortList)
        self._interior.AddPage(page, effort.task().subject())


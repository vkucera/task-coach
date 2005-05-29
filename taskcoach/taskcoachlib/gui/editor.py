import date, widgets, render
import wx, datetime
import wx.lib.masked as masked
from i18n import _

class DateEntry(wx.Panel):
    defaultDate = date.Date()

    def __init__(self, parent, date=defaultDate, readonly=False, callback=None, *args, **kwargs):
        super(DateEntry, self).__init__(parent, -1, *args, **kwargs)
        size = (100, -1)
        if readonly:
            self._entry = widgets.StaticDateCtrl(self, size=size)
        else:
            self._entry = widgets.DateCtrl(self, callback, size=size)
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


class TaskEditBook(widgets.Listbook):
    def __init__(self, parent, task, uiCommands, settings, *args, **kwargs):
        super(TaskEditBook, self).__init__(parent)
        self._task = task
        self._uiCommands = uiCommands
        self._settings = settings
        self.addSubjectPage()
        self.addDatesPage()
        self.addBudgetPage()
        self.addEffortPage()
        
    def addSubjectPage(self):
        subjectPage = widgets.BookPage(self, columns=2)
        self._subjectEntry = wx.TextCtrl(subjectPage, -1, self._task.subject())
        self._descriptionEntry = wx.TextCtrl(subjectPage, -1, 
            self._task.description(), style=wx.TE_MULTILINE)
        self._descriptionEntry.SetSizeHints(500, 220)
        subjectPage.addEntry(_('Subject'), self._subjectEntry)
        subjectPage.addEntry(_('Description'), self._descriptionEntry, growable=True)
        self.AddPage(subjectPage, _('Description'), 'description')
        
    def addDatesPage(self):
        datesPage = widgets.BookPage(self, columns=3)
        self._startDateEntry = DateEntry(datesPage, self._task.startDate())
        self._dueDateEntry = DateEntry(datesPage, self._task.dueDate())
        self._completionDateEntry = DateEntry(datesPage, self._task.completionDate())        
        entriesArgs = [['', _('For this task')],
                       [_('Start date'), self._startDateEntry],
                       [_('Due date'), self._dueDateEntry],
                       [_('Completion date'), self._completionDateEntry]]    
        if self._task.children():
            entriesArgs[0].append(_('For this task including all subtasks'))
            entriesArgs[1].append(DateEntry(datesPage, self._task.startDate(recursive=True), readonly=True))
            entriesArgs[2].append(DateEntry(datesPage, self._task.dueDate(recursive=True), readonly=True))
            entriesArgs[3].append(DateEntry(datesPage, self._task.completionDate(recursive=True), readonly=True))
        for entryArgs in entriesArgs:
            datesPage.addEntry(*entryArgs)
        self.AddPage(datesPage, _('Dates'), 'date')
    
    def addBudgetPage(self):
        budgetPage = widgets.BookPage(self, columns=3)
        self._budgetEntry = TimeDeltaEntry(budgetPage, self._task.budget())
        entriesArgs = [['', _('For this task')],
                       [_('Budget'), self._budgetEntry],
                       [_('Time spent'), render.timeSpent(self._task.duration())],
                       [_('Budget left'), render.budget(self._task.budgetLeft())]]
        if self._task.children():
            entriesArgs[0].append(_('For this task including all subtasks'))
            entriesArgs[1].append(render.budget(self._task.budget(recursive=True)))
            entriesArgs[2].append(render.timeSpent(self._task.duration(recursive=True)))
            entriesArgs[3].append(render.budget(self._task.budgetLeft(recursive=True)))
        for entryArgs in entriesArgs:
            budgetPage.addEntry(*entryArgs)
        self.AddPage(budgetPage, _('Budget'), 'budget')
                
    def addEffortPage(self):
        if not self._task.duration(recursive=True):
            return
        effortPage = widgets.BookPage(self, columns=1)
        import viewercontainer, viewerfactory, effort
        viewerContainer = viewercontainer.ViewerChoicebook(effortPage, self._settings, 'effortviewerineditor')
        myEffortList = effort.SingleTaskEffortList(self._task)
        viewerfactory._addEffortViewers(viewerContainer, myEffortList, self._uiCommands)
        effortPage.addEntry(None, viewerContainer, growable=True)
        self.AddPage(effortPage, _('Effort'), 'start')
            
    def ok(self):
        self._task.setSubject(self._subjectEntry.GetValue())
        self._task.setDescription(self._descriptionEntry.GetValue())
        self._task.setStartDate(self._startDateEntry.get(date.Today()))
        self._task.setDueDate(self._dueDateEntry.get())
        self._task.setCompletionDate(self._completionDateEntry.get())
        self._task.setBudget(self._budgetEntry.get())     
        
    def setSubject(self, subject):
        self._subjectEntry.SetValue(subject)

    def setDescription(self, description):
        self._descriptionEntry.SetValue(description)        


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
        self._descriptionEntry = wx.TextCtrl(self, -1, 
            self._effort.getDescription(), style=wx.TE_MULTILINE)
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
    def __init__(self, parent, command, uiCommands, settings, bitmap='edit', *args, **kwargs):
        self._settings = settings
        super(TaskEditor, self).__init__(parent, command, uiCommands, bitmap, *args, **kwargs)
        self[0]._subjectEntry.SetSelection(-1, -1)
        wx.CallAfter(self[0]._subjectEntry.SetFocus)
        
    def addPages(self):
        for task in self._command.items:
            self.addPage(task)

    def addPage(self, task):
        page = TaskEditBook(self._book, task, self._uiCommands, self._settings)
        self._book.AddPage(page, task.subject())
        
    
class EffortEditor(EditorWithCommand):
    def __init__(self, parent, command, uiCommands, effortList, *args, **kwargs):
        self._effortList = effortList
        super(EffortEditor, self).__init__(parent, command, uiCommands, *args, **kwargs)
        
    def addPages(self):
        for effort in self._command.efforts: # FIXME: use getter
            self.addPage(effort)

    def addPage(self, effort):
        page = EffortEditBook(self._book, effort, self, self._effortList)
        self._book.AddPage(page, effort.task().subject())


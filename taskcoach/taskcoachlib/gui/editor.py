import date, widgets, render
import wx, datetime
import wx.lib.masked as masked


class DateEntry(wx.Panel):
    defaultDate = 'None'

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

    def renderTimeDelta(timeDelta):
        return 
    def get(self):
        try:
            hours, minutes, seconds = [int(x) for x in self._entry.GetValue().split(':')]
        except ValueError:
            hours, minutes, seconds = 0, 0, 0 
        return date.TimeDelta(hours=hours, minutes=minutes, seconds=seconds)
            
class GridCursor:
    def __init__(self, columns):
        self._columns = columns
        self._nextPosition = (0, 0)
    
    def _updatePosition(self, colspan):
        row, column = self._nextPosition
        if column == self._columns - colspan:
            row += 1
            column = 0
        else:
            column += colspan
        self._nextPosition = (row, column)
                    
    def next(self, colspan=1):
        row, column = self._nextPosition
        self._updatePosition(colspan)
        return row, column

    def maxRow(self):
        row, column = self._nextPosition
        if column == 0:
            return max(0, row-1)
        else:
            return row


class Page(wx.Panel):
    def __init__(self, parent, columns, *args, **kwargs):
        super(Page, self).__init__(parent, -1, *args, **kwargs)
        self._sizer = wx.GridBagSizer(vgap=5, hgap=5)
        self._columns = columns
        self._position = GridCursor(columns)
        self._sizer.AddGrowableCol(columns-1)
        self._borderWidth = 5
        self.SetSizerAndFit(self._sizer)
        
    def addEntry(self, label, *controls, **kwargs):
        controls = [control for control in controls if control is not None]
        self._sizer.Add(wx.StaticText(self, -1, label), self._position.next(),
            flag=wx.ALL|wx.ALIGN_RIGHT, border=self._borderWidth)
        for control in controls:
            if type(control) == type(''):
                control = wx.StaticText(self, -1, control)
            colspan = self._columns - len(controls)
            self._sizer.Add(control, self._position.next(colspan), span=(1, colspan),
                flag=wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=self._borderWidth)
        if 'growable' in kwargs and kwargs['growable']:
            self._sizer.AddGrowableRow(self._position.maxRow())


class TaskEditBook(widgets.Listbook):
    def __init__(self, parent, task, uiCommands, *args, **kwargs):
        super(TaskEditBook, self).__init__(parent)
        self._task = task
        self._uiCommands = uiCommands
        self.addSubjectPage()
        self.addDatesPage()
        self.addEffortPage()
        
    def addSubjectPage(self):
        subjectPage = Page(self, columns=2)
        self._subjectEntry = wx.TextCtrl(subjectPage, -1, self._task.subject())
        self._descriptionEntry = wx.TextCtrl(subjectPage, -1, 
            self._task.description(), style=wx.TE_MULTILINE)
        self._descriptionEntry.SetSizeHints(400, 150)
        subjectPage.addEntry('Subject:', self._subjectEntry)
        subjectPage.addEntry('Description:', self._descriptionEntry, growable=True)
        self.AddPage(subjectPage, 'Description', 'description')
        
    def addDatesPage(self):
        datesPage = Page(self, columns=3)
        datesReadonly = bool(self._task.children()) 
        if datesReadonly:
            startDateComment = '(Minimum of all subtask start dates)'
            dueDateComment = '(Maximum of all subtask due dates)'
        else:
            startDateComment = dueDateComment = None
        self._startDateEntry = DateEntry(datesPage, self._task.startDate(), 
            readonly=datesReadonly)
        self._dueDateEntry = DateEntry(datesPage, self._task.dueDate(), 
            readonly=datesReadonly)
        self._completedCheckBox = wx.CheckBox(datesPage, -1, '')
        self.Bind(wx.EVT_CHECKBOX, self.completed, self._completedCheckBox)
        self._completionDateEntry = DateEntry(datesPage, self._task.completionDate(), 
            callback=self.onSetCompletionDate)
        self._completedCheckBox.SetValue(self._task.completed())
        datesPage.addEntry('Start date:', self._startDateEntry, startDateComment)
        datesPage.addEntry('Due date:', self._dueDateEntry, dueDateComment)
        datesPage.addEntry('Completed:', self._completedCheckBox)
        datesPage.addEntry('Completion date:', self._completionDateEntry)
        self.AddPage(datesPage, 'Dates', 'date')
    
    def addEffortPage(self):
        effortPage = Page(self, columns=3)
        self._budgetEntry = TimeDeltaEntry(effortPage, self._task.budget())
        entriesArgs = [(['', 'For this task'], {}),
                       (['Budget:', self._budgetEntry], {}),
                       (['Time spent:', render.timeSpent(self._task.duration())], {}),
                       (['Budget left:', render.budget(self._task.budgetLeft())], {})]
        if self._task.children():
            entriesArgs[0][0].append('For this task including all subtasks')
            entriesArgs[1][0].append(render.budget(self._task.budget(recursive=True)))
            entriesArgs[2][0].append(render.timeSpent(self._task.duration(recursive=True)))
            entriesArgs[3][0].append(render.budget(self._task.budgetLeft(recursive=True)))
        if self._task.duration(recursive=True):
            import viewercontainer, viewerfactory, effort
            viewerContainer = viewercontainer.ViewerChoicebook(effortPage)
            myEffortList = effort.SingleTaskEffortList(self._task)
            viewerfactory._addEffortViewers(viewerContainer, myEffortList, self._uiCommands)
            entriesArgs.append((['Effort lists:', viewerContainer], {'growable': True}))
        for entryArgs, entryKwArgs in entriesArgs:
            effortPage.addEntry(*entryArgs, **entryKwArgs)
        self.AddPage(effortPage, 'Effort', 'start')
            
    def completed(self, event):
        if event.IsChecked():
            self._completionDateEntry.setToday()
        else:
            self._completionDateEntry.set()

    def onSetCompletionDate(self, event):
        if not hasattr(self, '_completionDateEntry'):
            return
        if self._completionDateEntry.get() != date.Date() and not self._completedCheckBox.GetValue():
            self._completedCheckBox.SetValue(True)

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


class EffortEditBook(Page):
    def __init__(self, parent, effort, editor, *args, **kwargs):
        super(EffortEditBook, self).__init__(parent, columns=2, *args, **kwargs)
        self._editor = editor
        self._effort = effort
        self.addStartAndStopEntries()
        self.addDescriptionEntry()
        
    def addStartAndStopEntries(self):
        self._startEntry = widgets.DateTimeCtrl(self, self._effort.getStart(),
            self.preventNegativeEffortDuration)
        self._stopEntry = widgets.DateTimeCtrl(self, self._effort.getStop(),
            self.preventNegativeEffortDuration)
        self.addEntry('Start:', self._startEntry)
        self.addEntry('Stop:', self._stopEntry)
        
    def addDescriptionEntry(self):
        self._descriptionEntry = wx.TextCtrl(self, -1, 
            self._effort.getDescription(), style=wx.TE_MULTILINE)
        self._descriptionEntry.SetSizeHints(400, 150)
        self.addEntry('Description:', self._descriptionEntry)
        
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


class EditorWithCommand(widgets.TabbedDialog):
    def __init__(self, parent, command, *args, **kwargs):
        self._command = command
        super(EditorWithCommand, self).__init__(parent, str(command), *args, **kwargs)

    def ok(self, *args, **kwargs):
        super(EditorWithCommand, self).ok(*args, **kwargs)
        self._command.do()

            
class TaskEditor(EditorWithCommand):
    def __init__(self, parent, command, uiCommands, bitmap='edit', *args, **kwargs):
        self._uiCommands = uiCommands
        super(TaskEditor, self).__init__(parent, command, bitmap, *args, **kwargs)
        wx.CallAfter(self[0]._subjectEntry.SetFocus)
        
    def addPages(self):
        for task in self._command.items:
            self.addPage(task)

    def addPage(self, task):
        page = TaskEditBook(self._notebook, task, self._uiCommands)
        self._notebook.AddPage(page, str(task))
        
    
class EffortEditor(EditorWithCommand):
    def addPages(self):
        for effort in self._command.efforts: # FIXME: use getter
            self.addPage(effort)

    def addPage(self, effort):
        page = EffortEditBook(self._notebook, effort, self)
        self._notebook.AddPage(page, str(effort.task()))


import wx, task, patterns, config, gui, meta, help, command


class UICommandContainer(object):
    ''' Mixin with wx.Menu or wx.ToolBar (sub)class. '''

    def appendUICommands(self, uiCommands, uiCommandNames):
        for commandName in uiCommandNames:
            if commandName:
                if type(commandName) == type(''): # commandName can be a string or an actual UICommand
                    commandName = uiCommands[commandName]
                self.appendUICommand(commandName)
            else:
                self.AppendSeparator()


class UICommand(object):
    ''' Base user interface command. An UICommand is some action that can be associated
        with menu's and/or toolbars. It contains the menutext and helptext to be displayed,
        code to deal with wx.EVT_UPDATE_UI and methods to attach the command to a menu or
        toolbar. Subclasses should implement doCommand() and optionally override enabled(). '''
        
    bitmap = None
    menuText = '?'
    helpText = ''
    kind = wx.ITEM_NORMAL

    def __init__(self, *args, **kwargs):
        super(UICommand, self).__init__(*args, **kwargs)
        self._id = wx.NewId()

    def id(self):
        return self._id

    def setMenuItemMarginWidth(self, item, width=16):
        if '__WXMSW__' in wx.PlatformInfo:
            item.SetMarginWidth(width)

    def appendToMenu(self, menu, window):
        item = wx.MenuItem(menu, self._id, self.menuText, self.helpText, 
            self.kind)
        self.setMenuItemMarginWidth(item)
        if self.bitmap:
            item.SetBitmap(wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_MENU, 
                (16, 16)))
        menu.AppendItem(item)
        self.bind(window)
        return item

    def appendToToolBar(self, toolbar, window):
        toolbar.AddLabelTool(self._id, '',
            wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_TOOLBAR, 
            toolbar.GetToolBitmapSize()), wx.NullBitmap, self.kind, 
            shortHelp=wx.MenuItem.GetLabelFromText(self.menuText),
            longHelp=self.helpText)
        self.bind(window)

    def bind(self, window):
        window.Bind(wx.EVT_MENU, self.onCommandActivate, id=self._id)
        window.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI, id=self._id)

    def onCommandActivate(self, event):
        ''' For Menu's and ToolBars, activating the command is not
            possible when not enabled, because menu items and toolbar
            buttons are disabled through onUpdateUI. For other controls such 
            as the ListCtrl and the TreeCtrl the EVT_UPDATE_UI event is not 
            sent, so we need an explicit check here. Otherwise hitting return 
            on an empty selection in the ListCtrl would bring up the 
            TaskEditor. '''
        if self.enabled():
            self.doCommand(event)

    def doCommand(self, event):
        raise NotImplementedError

    def onUpdateUI(self, event):
        event.Enable(bool(self.enabled()))

    def enabled(self):
        ''' Can be overridden in a subclass. '''
        return True


class SettingsCommand(UICommand):
    ''' SettingsCommands are saved in the settings (a ConfigParser). '''
    
    section = 'view' # XXX all settings are currently in one section

    def __init__(self, settings, *args, **kwargs):
        self.settings = settings
        super(SettingsCommand, self).__init__(*args, **kwargs)

    def appendToMenu(self, *args, **kwargs):
        item = super(SettingsCommand, self).appendToMenu(*args, **kwargs)
        item.Check(self.checked())
        return item

    def sendCommandActivateEvent(self):
        self.onCommandActivate(wx.CommandEvent(0, self._id))


class UICheckCommand(SettingsCommand):
    kind = wx.ITEM_CHECK
    bitmap = 'on' # 'on' == checkmark shaped image

    def appendToMenu(self, *args, **kwargs):
        item = super(UICheckCommand, self).appendToMenu(*args, **kwargs)
        if not self.checked():
            self.sendCommandActivateEvent()

    def checked(self):
        return self.settings.getboolean(self.section, self.setting)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(event.IsChecked()))


class UIRadioCommand(SettingsCommand):
    kind = wx.ITEM_RADIO

    def setMenuItemMarginWidth(self, *args, **kwargs):
        pass # SetMarginWidth doesn't work for wx.ITEM_RADIO menu items

    def appendToMenu(self, *args, **kwargs):
        item = super(UIRadioCommand, self).appendToMenu(*args, **kwargs)
        if self.checked():
            self.sendCommandActivateEvent()

    def checked(self):
        return self.settings.get(self.section, self.setting) == str(self.value)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(self.value))


class IOCommand(UICommand):
    def __init__(self, iocontroller, *args, **kwargs):
        self.iocontroller = iocontroller
        super(IOCommand, self).__init__(*args, **kwargs)


class MainWindowCommand(UICommand):
    def __init__(self, mainwindow, *args, **kwargs):
        self.mainwindow = mainwindow
        super(MainWindowCommand, self).__init__(*args, **kwargs)


class EffortCommand(UICommand):
    def __init__(self, effortList, *args, **kwargs):
        super(EffortCommand, self).__init__(*args, **kwargs)
        self.effortList = effortList

        
class ViewerCommand(UICommand):
    def __init__(self, viewer, *args, **kwargs):
        self.viewer = viewer
        super(ViewerCommand, self).__init__(*args, **kwargs)


class FilterCommand(UICommand):
    def __init__(self, filteredTaskList, *args, **kwargs):
        self.filteredTaskList = filteredTaskList
        super(FilterCommand, self).__init__(*args, **kwargs)


class UICommandsCommand(UICommand):
    def __init__(self, uiCommands, *args, **kwargs):
        self.uiCommands = uiCommands
        super(UICommandsCommand, self).__init__(*args, **kwargs)    

# Mixins: 

class NeedsSelection(object):
    def enabled(self):
        return self.viewer.curselection()
 
class NeedsSelectedTasks(NeedsSelection):
    def enabled(self):
        return super(NeedsSelectedTasks, self).enabled() and self.viewer.isShowingTasks()

class NeedsSelectedEffort(NeedsSelection):
    def enabled(self):
        return super(NeedsSelectedEffort, self).enabled() and self.viewer.isShowingEffort()
               
class NeedsTasks(object):
    def enabled(self):
        return self.viewer.isShowingTasks()
        
class NeedsItems(object):
    def enabled(self):
        return self.viewer.size() 

class NeedsHidableColumns(object):
    def enabled(self):
        return self.viewer.canHideColumns()
 
# Commands:

class FileOpen(IOCommand):
    bitmap = 'fileopen'
    menuText = '&Open...\tCtrl+O'
    helpText = 'Open a %s file'%meta.name

    def doCommand(self, event):
        self.iocontroller.open()

class FileMerge(IOCommand):
    bitmap = 'merge'
    menuText = '&Merge...'
    helpText = 'Merge tasks from another file with the current file'

    def doCommand(self, event):
        self.iocontroller.merge()

class FileClose(IOCommand):
    bitmap = 'close'
    menuText = '&Close'
    helpText = 'Close the current file'

    def doCommand(self, event):
        self.iocontroller.close()

class FileSave(IOCommand):
    bitmap = 'save'
    menuText = '&Save\tCtrl+S'
    helpText = 'Save the current file'

    def doCommand(self, event):
        self.iocontroller.save()

class FileSaveAs(IOCommand):
    bitmap = 'saveas'
    menuText = 'S&ave as...'
    helpText = 'Save the current file under a new name'

    def doCommand(self, event):
        self.iocontroller.saveas()

class FileExportXML(IOCommand):
    bitmap = 'export'
    menuText = 'Export tasks to &XML...'
    helptext = 'Export the tasks to a XML file'
    
    def doCommand(self, event):
        self.iocontroller.exportToXML()
        
        
class FileSaveSelection(NeedsSelectedTasks, IOCommand, ViewerCommand):
    bitmap = 'saveselection'
    menuText = 'Sa&ve selection...'
    helpText = 'Save the selected tasks to a separate file'
    
    def doCommand(self, event):
        self.iocontroller.saveselection(self.viewer.curselection()), 

class FileQuit(MainWindowCommand):
    bitmap = 'exit'
    menuText = '&Quit\tCtrl+Q'
    helpText = 'Exit %s'%meta.name

    def doCommand(self, event):
        self.mainwindow.quit()

def getUndoMenuText():
    return '&%s\tCtrl+Z'%patterns.CommandHistory().undostr() 

class EditUndo(UICommand):
    bitmap = 'undo'
    menuText = getUndoMenuText()
    helpText = 'Undo the last command'

    def doCommand(self, event):
        patterns.CommandHistory().undo()

    def onUpdateUI(self, event):
        event.SetText(getUndoMenuText())
        super(EditUndo, self).onUpdateUI(event)

    def enabled(self):
        return patterns.CommandHistory().hasHistory()


def getRedoMenuText():
    return '&%s\tCtrl+Y'%patterns.CommandHistory().redostr() 

class EditRedo(UICommand):
    bitmap = 'redo'
    menuText = getRedoMenuText()
    helpText = 'Redo the last command that was undone'

    def doCommand(self, event):
        patterns.CommandHistory().redo()

    def onUpdateUI(self, event):
        event.SetText(getRedoMenuText())
        super(EditRedo, self).onUpdateUI(event)

    def enabled(self):
        return patterns.CommandHistory().hasFuture()


class EditCut(NeedsSelectedTasks, FilterCommand, ViewerCommand): # FIXME: only works for tasks atm
    bitmap = 'cut'
    menuText = 'Cu&t\tCtrl+X'
    helpText = 'Cut the selected task(s) to the clipboard'

    def doCommand(self, event):
        cutCommand = command.CutTaskCommand(self.filteredTaskList, self.viewer.curselection())
        cutCommand.do()

class EditCopy(NeedsSelectedTasks, FilterCommand, ViewerCommand): # FIXME: only works for tasks atm
    bitmap = 'copy'
    menuText = '&Copy\tCtrl+C'
    helpText = 'Copy the selected task(s) to the clipboard'

    def doCommand(self, event):
        copyCommand = command.CopyTaskCommand(self.filteredTaskList, self.viewer.curselection())
        copyCommand.do()

class EditPaste(FilterCommand):
    bitmap = 'paste'
    menuText = '&Paste\tCtrl+V'
    helpText = 'Paste task(s) from the clipboard'

    def doCommand(self, event):
        pasteCommand = command.PasteTaskCommand(self.filteredTaskList)
        pasteCommand.do()

    def enabled(self):
        return task.Clipboard()


class EditPasteAsSubtask(FilterCommand, ViewerCommand):
    menuText = 'P&aste as subtask'
    helpText = 'Paste task(s) as children of the selected task'

    def doCommand(self, event):
        pasteCommand = command.PasteTaskAsSubtaskCommand(self.filteredTaskList, 
            self.viewer.curselection())
        pasteCommand.do()

    def enabled(self):
        return task.Clipboard() and self.viewer.curselection()


class SelectAll(NeedsItems, ViewerCommand):
    menuText = '&All\tCtrl+A'
    helpText = 'Select all items in the current view'

    def doCommand(self, event):
        self.viewer.selectall()


class SelectCompleted(NeedsTasks, ViewerCommand):
    menuText = '&Completed tasks' 
    helpText = 'Select all completed tasks'

    def doCommand(self, event):
        self.viewer.select_completedTasks(), 


class InvertSelection(NeedsItems, ViewerCommand):
    menuText = '&Invert selection\tCtrl+I'
    helpText = 'Select unselected items and unselect selected items'

    def doCommand(self, event):
        self.viewer.invertselection()


class ClearSelection(NeedsSelection, ViewerCommand):
    menuText = 'C&lear selection'
    helpText = 'Unselect all items'

    def doCommand(self, event):
        self.viewer.clearselection()


class ViewCompletedTasks(FilterCommand, UICheckCommand):
    menuText = '&Completed tasks'
    helpText = 'Show/hide completed tasks'
    setting ='completedtasks'

    def doCommand(self, event):
        super(ViewCompletedTasks, self).doCommand(event)
        self.filteredTaskList.setViewCompletedTasks(event.IsChecked())


class ViewInactiveTasks(FilterCommand, UICheckCommand):
    menuText = '&Inactive tasks'
    helpText = 'Show/hide inactive tasks'
    setting = 'inactivetasks'

    def doCommand(self, event):
        super(ViewInactiveTasks, self).doCommand(event)
        self.filteredTaskList.setViewInactiveTasks(event.IsChecked())


class ViewStartDate(NeedsHidableColumns, ViewerCommand, UICheckCommand):
    menuText = '&Start date'
    helpText = 'Show/hide start date column'
    setting = 'startdate'

    def doCommand(self, event):
        super(ViewStartDate, self).doCommand(event)
        self.viewer.showStartDate(event.IsChecked())


class ViewDueDate(NeedsHidableColumns, ViewerCommand, UICheckCommand):
    menuText = '&Due date'
    helpText = 'Show/hide due date column'
    setting = 'duedate'

    def doCommand(self, event):
        super(ViewDueDate, self).doCommand(event)
        self.viewer.showDueDate(event.IsChecked())


class ViewDaysLeft(NeedsHidableColumns, ViewerCommand, UICheckCommand):
    menuText = 'Days &left'
    helpText = 'Show/hide days left column'
    setting = 'daysleft'

    def doCommand(self, event):
        super(ViewDaysLeft, self).doCommand(event)
        self.viewer.showDaysLeft(event.IsChecked())


class ViewCompletionDate(NeedsHidableColumns, ViewerCommand, UICheckCommand):
    menuText = 'Co&mpletion date'
    helpText = 'Show/hide completion date column'
    setting = 'completiondate'

    def doCommand(self, event):
        super(ViewCompletionDate, self).doCommand(event)
        self.viewer.showCompletionDate(event.IsChecked())


class ViewTimeSpent(NeedsHidableColumns, ViewerCommand, UICheckCommand):
    menuText = '&Time spent'
    helpText = 'Show/hide time spent column'
    setting = 'timespent'

    def doCommand(self, event):
        super(ViewTimeSpent, self).doCommand(event)
        self.viewer.showTimeSpent(event.IsChecked())


class ViewTotalTimeSpent(NeedsHidableColumns, ViewerCommand, UICheckCommand):
    menuText = 'T&otal time spent'
    helpText = 'Show/hide total time spent column (total time includes time spent on subtasks)'
    setting = 'totaltimespent'
    
    def doCommand(self, event):
        super(ViewTotalTimeSpent, self).doCommand(event)
        self.viewer.showTotalTimeSpent(event.IsChecked())
        
        
class ViewToolBar(MainWindowCommand, UIRadioCommand):
    setting = 'toolbar'

    def doCommand(self, event):
        super(ViewToolBar, self).doCommand(event)
        self.mainwindow.setToolBarSize(self.value)

class ViewToolBarHide(ViewToolBar):
    value = None
    menuText = '&Hide'
    helpText = 'Hide the toolbar'

class ViewToolBarSmall(ViewToolBar):
    value = (16, 16)
    menuText = '&Small images' 
    helpText = 'Small images (16x16) on the toolbar'

class ViewToolBarMedium(ViewToolBar):
    value = (22, 22)
    menuText = '&Medium-sized images'
    helpText = 'Medium-sized images (22x22) on the toolbar'

class ViewToolBarBig(ViewToolBar):
    value = (32, 32)
    menuText = '&Large images'
    helpText = 'Large images (32x32) on the toolbar'


class ViewFindDialog(MainWindowCommand, UICheckCommand):
    menuText = '&Find dialog'
    helpText = 'Show/hide find dialog'
    setting = 'finddialog'
    
    def doCommand(self, event):
        super(ViewFindDialog, self).doCommand(event)
        self.mainwindow.showFindDialog(event.IsChecked())


class ViewStatusBar(MainWindowCommand, UICheckCommand):
    menuText = 'St&atusbar'
    helpText = 'Show/hide status bar'
    setting = 'statusbar'

    def doCommand(self, event):
        super(ViewStatusBar, self).doCommand(event)
        self.mainwindow.GetStatusBar().Show(event.IsChecked())
        self.mainwindow.SendSizeEvent()


class ViewSplashScreen(UICheckCommand):
    menuText = 'S&plash screen'
    helpText = 'Show/skip splash screen when starting %s'%meta.name
    section = 'window'
    setting = 'splash'


class ViewDueBefore(FilterCommand, UIRadioCommand):
    setting = 'tasksdue'

    def doCommand(self, event):
        super(ViewDueBefore, self).doCommand(event)
        self.filteredTaskList.viewTasksDueBefore(self.value) 


class ViewDueToday(ViewDueBefore):
    value = 'Today'
    menuText = '&Today'
    helpText = 'Only show tasks due today'

class ViewDueTomorrow(ViewDueBefore):
    value = 'Tomorrow'
    menuText = 'T&omorrow' 
    helpText = 'Only show tasks due today and tomorrow'

class ViewDueWorkWeek(ViewDueBefore):
    value = 'Workweek'
    menuText = 'Wo&rk week' 
    helpText = 'Only show tasks due this work week (i.e. before Friday)'

class ViewDueWeek(ViewDueBefore):
    value = 'Week'
    menuText = '&Week'
    helpText = 'Only show tasks due this week (i.e. before Sunday)'

class ViewDueMonth(ViewDueBefore):
    value = 'Month'
    menuText = '&Month'
    helpText = 'Only show tasks due this month'

class ViewDueYear(ViewDueBefore):
    value = 'Year'
    menuText = '&Year'
    helpText = 'Only show tasks due this year'

class ViewDueUnlimited(ViewDueBefore):
    value = 'Unlimited'
    menuText = '&Unlimited'
    helpText = 'Show all tasks' 


class TaskNew(MainWindowCommand, FilterCommand, EffortCommand, UICommandsCommand):
    bitmap = 'new'
    menuText = '&New task...\tINS' 
    helpText = 'Insert a new task'

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewTaskCommand(self.filteredTaskList),
            self.effortList, self.uiCommands, bitmap=self.bitmap)
        editor.Show(show)
        return editor


class TaskNewSubTask(NeedsSelectedTasks, MainWindowCommand,
        FilterCommand, EffortCommand, ViewerCommand, UICommandsCommand):

    menuText = 'New &subtask...\tCtrl+INS'
    helpText = 'Insert a new subtask into the selected task'

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewSubTaskCommand(self.filteredTaskList, 
                self.viewer.curselection()),
            self.effortList, self.uiCommands, bitmap='new')
        editor.Show(show)
        return editor


class TaskEdit(NeedsSelectedTasks, MainWindowCommand, FilterCommand, 
        EffortCommand, ViewerCommand, UICommandsCommand):

    bitmap = 'edit'
    menuText = '&Edit task...'
    helpText = 'Edit the selected task'

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.EditTaskCommand(self.filteredTaskList, 
                self.viewer.curselection()),
            self.effortList, self.uiCommands)
        editor.Show(show)
        return editor


class TaskMarkCompleted(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    bitmap = 'markcompleted'
    menuText = '&Mark completed'
    helpText = 'Mark the selected task(s) completed'

    def doCommand(self, event):
        markCompletedCommand = command.MarkCompletedCommand(self.filteredTaskList, 
            self.viewer.curselection())
        markCompletedCommand.do()

    def enabled(self):
        return super(TaskMarkCompleted, self).enabled() and \
            [task for task in self.viewer.curselection() if not task.completed()]


class TaskDelete(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    bitmap = 'delete'
    menuText = '&Delete task\tCtrl+D'
    helpText = 'Delete the selected task(s)'

    def doCommand(self, event):
        deleteCommand = command.DeleteTaskCommand(self.filteredTaskList, 
            self.viewer.curselection())
        deleteCommand.do()


class EffortNew(NeedsSelectedTasks, MainWindowCommand, EffortCommand, ViewerCommand):
    bitmap = 'start'
    menuText = '&New effort'
    helpText = 'Add a effort period to the selected task(s)'
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow, 
            command.NewEffortCommand(self.effortList, self.viewer.curselection()))
        editor.Show()
        return editor 

class EffortEdit(NeedsSelectedEffort, MainWindowCommand, EffortCommand, ViewerCommand):
    bitmap = 'edit'
    menuText = '&Edit effort'
    helpText = 'Edit the selected effort period(s)'
    
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow,
            command.EditEffortCommand(self.effortList, 
                self.viewer.curselection()))
        editor.Show()
        return editor

class EffortDelete(NeedsSelectedEffort, EffortCommand, ViewerCommand):
    bitmap = 'delete'
    menuText = '&Delete effort'
    helpText = 'Delete the selected effort period(s)'

    def doCommand(self, event):
        delete = command.DeleteEffortCommand(self.effortList,
            self.viewer.curselection())
        delete.do()


class EffortStart(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    bitmap = 'start'
    menuText = '&Start tracking effort'
    helpText = 'Start tracking effort for the selected task(s)'
    adjacent = False
    
    def doCommand(self, event):
        start = command.StartEffortCommand(self.filteredTaskList, self.viewer.curselection(),
            adjacent=self.adjacent)
        start.do()
        
    def enabled(self):
        if not self.viewer.isShowingTasks():
            return False
        return [task for task in self.viewer.curselection() if not
            (task.isBeingTracked() or task.completed() or task.inactive())]


class EffortStartAdjacent(EffortStart):
    menuText = 'S&tart tracking from last stop time'
    helpText = 'Start tracking effort for the selected task(s) with start time ' \
         'equal to end time of last effort'
    adjacent = True
        
    def enabled(self):
        return (self.taskList.maxDateTime() is not None) and super(EffortStartAdjacent, self).enabled()


class EffortStop(FilterCommand):
    bitmap = 'stop'
    menuText = 'St&op tracking effort'
    helpText = 'Stop tracking effort for the active task(s)'

    def doCommand(self, event):
        stop = command.StopEffortCommand(self.filteredTaskList)
        stop.do()

    def enabled(self):
        return bool([task for task in self.filteredTaskList if task.isBeingTracked()])


class HelpCommand(UICommand):
    bitmap = 'help'

class HelpTasks(HelpCommand):
    menuText = '&Tasks'
    helpText = 'Help about the possible states of tasks'

    def doCommand(self, event):
        help.Tasks()

class HelpColors(HelpCommand):
    menuText = '&Colors'
    helpText = 'Help about the possible colors of tasks'

    def doCommand(self, event):
        help.Colors()


class InfoCommand(UICommand):
    bitmap = 'info'

class HelpAbout(InfoCommand):
    menuText = '&About'
    helpText = 'Version and contact information about %s'%meta.name

    def doCommand(self, event):
        help.About()

class HelpLicense(InfoCommand):
    menuText = '&License'
    helpText = '%s license'%meta.name

    def doCommand(self, event):
        help.License()


class MainWindowRestore(MainWindowCommand):
    menuText = '&Restore'
    helpText = 'Restore the window to its previous state'
    bitmap = 'restore'

    def doCommand(self, event):
        self.mainwindow.restore(event)
    


class UICommands(dict):
    def __init__(self, mainwindow, iocontroller, viewer, settings, 
            filteredTaskList, effortList):
        super(UICommands, self).__init__()
    
        # File commands
        self['open'] = FileOpen(iocontroller)
        self['merge'] = FileMerge(iocontroller)
        self['close'] = FileClose(iocontroller)
        self['save'] = FileSave(iocontroller)
        self['saveas'] = FileSaveAs(iocontroller)
        self['saveselection'] = FileSaveSelection(iocontroller, viewer)
        self['exportxml'] = FileExportXML(iocontroller)
        self['quit'] = FileQuit(mainwindow)

        # menuEdit commands
        self['undo'] = EditUndo()
        self['redo'] = EditRedo()
        self['cut'] = EditCut(filteredTaskList, viewer)
        self['copy'] = EditCopy(filteredTaskList, viewer)
        self['paste'] = EditPaste(filteredTaskList)
        self['pasteassubtask'] = EditPasteAsSubtask(filteredTaskList, viewer)

        # Selection commands
        self['selectall'] = SelectAll(viewer)
        self['selectcompleted'] = SelectCompleted(viewer)
        self['invertselection'] = InvertSelection(viewer)
        self['clearselection'] = ClearSelection(viewer)

        # View commands
        self['viewcompletedtasks'] = ViewCompletedTasks(filteredTaskList, 
            settings)
        self['viewinactivetasks'] = ViewInactiveTasks(filteredTaskList,
            settings)
            
        self['viewstartdate'] = ViewStartDate(viewer, settings)
        self['viewduedate'] = ViewDueDate(viewer, settings)
        self['viewdaysleft'] = ViewDaysLeft(viewer, settings)
        self['viewcompletiondate'] = ViewCompletionDate(viewer, settings)
        self['viewtimespent'] = ViewTimeSpent(viewer, settings)
        self['viewtotaltimespent'] = ViewTotalTimeSpent(viewer, settings)

        self['toolbarhide'] = ViewToolBarHide(mainwindow, settings)
        self['toolbarsmall'] = ViewToolBarSmall(mainwindow, settings)
        self['toolbarmedium'] = ViewToolBarMedium(mainwindow, settings)
        self['toolbarbig'] = ViewToolBarBig(mainwindow, settings)
        self['viewfinddialog'] = ViewFindDialog(mainwindow, settings)
        self['viewstatusbar'] = ViewStatusBar(mainwindow, settings)
        self['viewsplashscreen'] = ViewSplashScreen(settings)

        self['viewduetoday'] = ViewDueToday(filteredTaskList, settings)
        self['viewduetomorrow'] = ViewDueTomorrow(filteredTaskList, settings)
        self['viewdueworkweek'] = ViewDueWorkWeek(filteredTaskList, settings)
        self['viewdueweek'] = ViewDueWeek(filteredTaskList, settings)
        self['viewduemonth'] = ViewDueMonth(filteredTaskList, settings)
        self['viewdueyear'] = ViewDueYear(filteredTaskList, settings)
        self['viewdueunlimited'] = ViewDueUnlimited(filteredTaskList, settings)

        # Task menu
        self['new'] = TaskNew(mainwindow, filteredTaskList, effortList, self)
        self['newsubtask'] = TaskNewSubTask(mainwindow, filteredTaskList, 
            effortList, viewer, self)
        self['edit'] = TaskEdit(mainwindow, filteredTaskList, effortList, 
            viewer, self)
        self['markcompleted'] = TaskMarkCompleted(filteredTaskList, viewer)
        self['delete'] = TaskDelete(filteredTaskList, viewer)
        
        # Effort menu
        self['neweffort'] = EffortNew(mainwindow, effortList, viewer)
        self['editeffort'] = EffortEdit(mainwindow, effortList, viewer)
        self['deleteeffort'] = EffortDelete(effortList, viewer)
        self['starteffort'] = EffortStart(filteredTaskList, viewer)
        self['starteffortadjacent'] = EffortStartAdjacent(filteredTaskList, viewer)
        self['stopeffort'] = EffortStop(filteredTaskList)
        
        # Help menu
        self['helptasks'] = HelpTasks()
        self['helpcolors'] = HelpColors()
        self['about'] = HelpAbout()
        self['license'] = HelpLicense()

        # Taskbar menu
        self['restore'] = MainWindowRestore(mainwindow)



import wx, task, patterns, config, gui, meta, help, command
from i18n import _


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
    
    def __init__(self, menuText='?', helpText='', bitmap='nobitmap',
            kind=wx.ITEM_NORMAL, *args, **kwargs):
        super(UICommand, self).__init__(*args, **kwargs)
        self.menuText = menuText
        self.helpText = helpText
        self.bitmap = bitmap
        self.kind = kind
        self._id = wx.NewId()

    def id(self):
        return self._id

    def appendToMenu(self, menu, window):
        self.menuItem = wx.MenuItem(menu, self._id, self.menuText, self.helpText, 
            self.kind)
        if self.bitmap:
            self.menuItem.SetBitmap(wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_MENU, 
                (16, 16)))
        menu.AppendItem(self.menuItem)
        self.bind(window)

    def appendToToolBar(self, toolbar, window):
        bitmap = wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_TOOLBAR, 
            toolbar.GetToolBitmapSize())
        toolbar.AddLabelTool(self._id, '',
            bitmap, wx.NullBitmap, self.kind, 
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

    def __init__(self, settings=None, setting=None, section='view', *args, **kwargs):
        self.settings = settings
        self.section = section
        self.setting = setting
        super(SettingsCommand, self).__init__(*args, **kwargs)


class BooleanSettingsCommand(SettingsCommand):
    def __init__(self, value=None, *args, **kwargs):
        self.value = value
        super(BooleanSettingsCommand, self).__init__(*args, **kwargs)
        
    def appendToMenu(self, *args, **kwargs):
        super(BooleanSettingsCommand, self).appendToMenu(*args, **kwargs)
        self.check()
        
    def check(self):
        checked = self.checked()
        self.menuItem.Check(checked)
        if self.commandNeedsToBeActivated(checked):
            self.sendCommandActivateEvent()

    def sendCommandActivateEvent(self):
        self.onCommandActivate(wx.CommandEvent(0, self._id))
        

class UICheckCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        super(UICheckCommand, self).__init__(kind=wx.ITEM_CHECK, 
            bitmap='on', *args, **kwargs)
            
    def commandNeedsToBeActivated(self, checked):
        return not checked

    def checked(self):
        return self.settings.getboolean(self.section, self.setting)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(event.IsChecked()))


class UIRadioCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        super(UIRadioCommand, self).__init__(kind=wx.ITEM_RADIO, bitmap=None,
            *args, **kwargs)
            
    def commandNeedsToBeActivated(self, checked):
        return checked
        
    def checked(self):
        return self.settings.get(self.section, self.setting) == str(self.value)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(self.value))


class IOCommand(UICommand):
    def __init__(self, iocontroller=None, *args, **kwargs):
        self.iocontroller = iocontroller
        super(IOCommand, self).__init__(*args, **kwargs)


class MainWindowCommand(UICommand):
    def __init__(self, mainwindow=None, *args, **kwargs):
        self.mainwindow = mainwindow
        super(MainWindowCommand, self).__init__(*args, **kwargs)


class EffortCommand(UICommand):
    def __init__(self, effortList=None, *args, **kwargs):
        self.effortList = effortList
        super(EffortCommand, self).__init__(*args, **kwargs)

        
class ViewerCommand(UICommand):
    def __init__(self, viewer=None, *args, **kwargs):
        self.viewer = viewer
        super(ViewerCommand, self).__init__(*args, **kwargs)


class FilterCommand(UICommand):
    def __init__(self, filteredTaskList=None, *args, **kwargs):
        self.filteredTaskList = filteredTaskList
        super(FilterCommand, self).__init__(*args, **kwargs)


class UICommandsCommand(UICommand):
    def __init__(self, uiCommands=None, *args, **kwargs):
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

 
# Commands:

class FileOpen(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileOpen, self).__init__(menuText=_('&Open...\tCtrl+O'),
            helpText=_('Open a %s file'%meta.name), bitmap='fileopen', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.open()

class FileMerge(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileMerge, self).__init__(menuText=_('&Merge...'),
            helpText=_('Merge tasks from another file with the current file'), 
            bitmap='merge', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.merge()

class FileClose(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileClose, self).__init__(menuText=_('&Close'),
            helpText=_('Close the current file'), bitmap='close', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.close()

class FileSave(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileSave, self).__init__(menuText=_('&Save\tCtrl+S'),
            helpText=_('Save the current file'), bitmap='save', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.save()
        
    def enabled(self):
        return self.iocontroller.needSave()

class FileSaveAs(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveAs, self).__init__(menuText=_('S&ave as...'),
            helpText=_('Save the current file under a new name'), 
            bitmap='saveas', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.saveas()
        
class FileSaveSelection(NeedsSelectedTasks, IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveSelection, self).__init__(menuText=_('Sa&ve selection...'),
            helpText=_('Save the selected tasks to a separate file'), 
            bitmap='saveselection', *args, **kwargs)
    
    def doCommand(self, event):
        self.iocontroller.saveselection(self.viewer.curselection()), 

class FileQuit(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(FileQuit, self).__init__(menuText=_('&Quit\tCtrl+Q'), 
            helpText=_('Exit %s'%meta.name), bitmap='exit', *args, **kwargs)

    def doCommand(self, event):
        self.mainwindow.quit()


def getUndoMenuText():
    return '%s\tCtrl+Z'%patterns.CommandHistory().undostr(_('&Undo')) 

class EditUndo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditUndo, self).__init__(menuText=getUndoMenuText(),
            helpText=_('Undo the last command'), bitmap='undo', *args, **kwargs)
            
    def doCommand(self, event):
        patterns.CommandHistory().undo()

    def onUpdateUI(self, event):
        event.SetText(getUndoMenuText())
        super(EditUndo, self).onUpdateUI(event)

    def enabled(self):
        return patterns.CommandHistory().hasHistory()


def getRedoMenuText():
    return '%s\tCtrl+Y'%patterns.CommandHistory().redostr(_('&Redo')) 

class EditRedo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditRedo, self).__init__(menuText=getRedoMenuText(),
            helpText=_('Redo the last command that was undone'), bitmap='redo',
            *args, **kwargs)

    def doCommand(self, event):
        patterns.CommandHistory().redo()

    def onUpdateUI(self, event):
        event.SetText(getRedoMenuText())
        super(EditRedo, self).onUpdateUI(event)

    def enabled(self):
        return patterns.CommandHistory().hasFuture()


class EditCut(NeedsSelectedTasks, FilterCommand, ViewerCommand): # FIXME: only works for tasks atm
    def __init__(self, *args, **kwargs):
        
        super(EditCut, self).__init__(menuText=_('Cu&t\tCtrl+X'), 
            helpText=_('Cut the selected task(s) to the clipboard'), bitmap='cut', 
            *args, **kwargs)

    def doCommand(self, event):
        cutCommand = command.CutTaskCommand(self.filteredTaskList, self.viewer.curselection())
        cutCommand.do()


class EditCopy(NeedsSelectedTasks, FilterCommand, ViewerCommand): # FIXME: only works for tasks atm
    def __init__(self, *args, **kwargs):
        super(EditCopy, self).__init__(menuText=_('&Copy\tCtrl+C'), 
            helpText=_('Copy the selected task(s) to the clipboard'), bitmap='copy',
            *args, **kwargs)

    def doCommand(self, event):
        copyCommand = command.CopyTaskCommand(self.filteredTaskList, self.viewer.curselection())
        copyCommand.do()

class EditPaste(FilterCommand):
    def __init__(self, *args, **kwargs):
        super(EditPaste, self).__init__(menuText=_('&Paste\tCtrl+V'), 
            helpText=_('Paste task(s) from the clipboard'), bitmap='paste', 
            *args, **kwargs)

    def doCommand(self, event):
        pasteCommand = command.PasteTaskCommand(self.filteredTaskList)
        pasteCommand.do()

    def enabled(self):
        return task.Clipboard()


class EditPasteAsSubtask(FilterCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditPasteAsSubtask, self).__init__(menuText=_('P&aste as subtask'), 
            helpText=_('Paste task(s) as subtask(s) of the selected task'),
            bitmap='pasteassubtask', *args, **kwargs)

    def doCommand(self, event):
        pasteCommand = command.PasteTaskAsSubtaskCommand(self.filteredTaskList, 
            self.viewer.curselection())
        pasteCommand.do()

    def enabled(self):
        return task.Clipboard() and self.viewer.curselection()


class SelectAll(NeedsItems, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(SelectAll, self).__init__(menuText=_('&All\tCtrl+A'),
            helpText=_('Select all items in the current view'), bitmap='selectall',
            *args, **kwargs)
        
    def doCommand(self, event):
        self.viewer.selectall()


class InvertSelection(NeedsItems, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(InvertSelection, self).__init__(menuText=_('&Invert selection\tCtrl+I'),
            helpText=_('Select unselected items and unselect selected items'), *args,
            **kwargs)

    def doCommand(self, event):
        self.viewer.invertselection()


class ClearSelection(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ClearSelection, self).__init__(menuText=_('&Clear selection'), 
            helpText=_('Unselect all items'), *args, **kwargs)

    def doCommand(self, event):
        self.viewer.clearselection()


class ViewAllTasks(FilterCommand, SettingsCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        super(ViewAllTasks, self).__init__(menuText=_('&All tasks'),
            helpText=_('Show all tasks (reset all filters)'), bitmap='viewalltasks',
            *args, **kwargs)
    
    def doCommand(self, event):
        for uiCommandName in ['viewcompletedtasks', 'viewinactivetasks', 
            'viewoverduetasks', 'viewactivetasks', 'viewoverbudgettasks', 
            'viewcompositetasks']:
            uiCommand = self.uiCommands[uiCommandName]
            self.settings.set(uiCommand.section, uiCommand.setting, 'True')
            uiCommand.check()
        
        self.settings.set(self.section, 'tasksdue', 'Unlimited')    
        for uiCommandName in ['viewdueunlimited', 'viewduetoday', 'viewduetomorrow',
            'viewdueworkweek', 'viewdueweek', 'viewduemonth', 'viewdueyear']:
            self.uiCommands[uiCommandName].check()
        self.filteredTaskList.setViewAll()


class ViewCompletedTasks(FilterCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCompletedTasks, self).__init__(menuText=_('&Completed'), 
            helpText=_('Show/hide completed tasks'), setting='completedtasks',
            *args, **kwargs)

    def doCommand(self, event):
        super(ViewCompletedTasks, self).doCommand(event)
        self.filteredTaskList.setViewCompletedTasks(event.IsChecked())


class ViewInactiveTasks(FilterCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewInactiveTasks, self).__init__(menuText=_('&Inactive'), 
            helpText=_('Show/hide inactive tasks (tasks with a start date in the future)'),
            setting='inactivetasks', *args, **kwargs)

    def doCommand(self, event):
        super(ViewInactiveTasks, self).doCommand(event)
        self.filteredTaskList.setViewInactiveTasks(event.IsChecked())

class ViewOverDueTasks(FilterCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewOverDueTasks, self).__init__(menuText=_('&Over due'), 
            helpText=_('Show/hide over due tasks (tasks with a due date in the past)'),
            setting='overduetasks', *args, **kwargs)

    def doCommand(self, event):
        super(ViewOverDueTasks, self).doCommand(event)
        self.filteredTaskList.setViewOverDueTasks(event.IsChecked())

class ViewActiveTasks(FilterCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewActiveTasks, self).__init__(menuText=_('&Active'),
            helpText=_('Show/hide active tasks (tasks with a start date in the past and a due date in the future)'),
            setting='activetasks', *args, **kwargs)    

    def doCommand(self, event):
        super(ViewActiveTasks, self).doCommand(event)
        self.filteredTaskList.setViewActiveTasks(event.IsChecked())    
 
class ViewOverBudgetTasks(FilterCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewOverBudgetTasks, self).__init__(menuText=_('Over &budget'), 
            helpText=_('Show/hide tasks that are over budget'), 
            setting='overbudgettasks', *args, **kwargs)

    def doCommand(self, event):
        super(ViewOverBudgetTasks, self).doCommand(event)
        self.filteredTaskList.setViewOverBudgetTasks(event.IsChecked())
               

class ViewCompositeTasks(ViewerCommand, FilterCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCompositeTasks, self).__init__(menuText=_('Tasks &with subtasks'), 
            helpText=_('Show/hide tasks with subtasks'), setting='compositetasks', 
            *args, **kwargs)        

    def doCommand(self, event):
        super(ViewCompositeTasks, self).doCommand(event)
        self.viewer.setViewCompositeTasks(event.IsChecked())


class ViewColumn(ViewerCommand, UICheckCommand):   
    def __init__(self, column=0, *args, **kwargs):
        self.column = column
        super(ViewColumn, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        super(ViewColumn, self).doCommand(event)
        self.viewer.showColumn(_(self.column), event.IsChecked())
        

class ViewExpandAll(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewExpandAll, self).__init__(menuText=_('&Expand all tasks'),
            helpText=_('Expand all tasks with subtasks'), *args, **kwargs)
            
    def doCommand(self, event):
        self.viewer.expandAll()


class ViewExpandSelected(NeedsSelectedTasks, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewExpandSelected, self).__init__(bitmap='viewexpand',
            menuText=_('E&xpand'), helpText=_('Expand the selected task(s)'),
            *args, **kwargs)
            
    def doCommand(self, event):
        self.viewer.expandSelectedItems()
            
class ViewCollapseAll(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCollapseAll, self).__init__(menuText=_('&Collapse all tasks'),
            helpText=_('Collapse all tasks with subtasks'), *args, **kwargs)
    
    def doCommand(self, event):
        self.viewer.collapseAll()
 
class ViewCollapseSelected(NeedsSelectedTasks, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCollapseSelected, self).__init__(bitmap='viewcollapse',
            menuText=_('C&ollapse'),
            helpText=_('Collapse the selected tasks with subtasks'), *args, **kwargs)
    
    def doCommand(self, event):
        self.viewer.collapseSelectedItems()
             
        
class ViewToolBar(MainWindowCommand, UIRadioCommand):
    def __init__(self, *args, **kwargs):
        super(ViewToolBar, self).__init__(setting='toolbar', *args, **kwargs)
        
    def doCommand(self, event):
        super(ViewToolBar, self).doCommand(event)
        self.mainwindow.setToolBarSize(self.value)



class ViewFindDialog(MainWindowCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewFindDialog, self).__init__(menuText=_('&Find dialog'),
            helpText=_('Show/hide find dialog'), setting='finddialog', 
            *args, **kwargs)
    
    def doCommand(self, event):
        super(ViewFindDialog, self).doCommand(event)
        self.mainwindow.showFindDialog(event.IsChecked())


class ViewStatusBar(MainWindowCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewStatusBar, self).__init__(menuText=_('Status&bar'),
            helpText=_('Show/hide status bar'), setting='statusbar', *args,
            **kwargs)

    def doCommand(self, event):
        super(ViewStatusBar, self).doCommand(event)
        self.mainwindow.GetStatusBar().Show(event.IsChecked())
        self.mainwindow.SendSizeEvent()


class ViewSplashScreen(UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewSplashScreen, self).__init__(menuText=_('S&plash screen'),
            helpText=_('Show/skip splash screen when starting %s'%meta.name),
            section='window', setting='splash', *args, **kwargs)


class ViewDueBefore(FilterCommand, UIRadioCommand):
    def __init__(self, *args, **kwargs):
        super(ViewDueBefore, self).__init__(setting='tasksdue', *args, **kwargs)
        
    def doCommand(self, event):
        super(ViewDueBefore, self).doCommand(event)
        self.filteredTaskList.viewTasksDueBefore(self.value) 


class ViewLanguage(MainWindowCommand, UIRadioCommand):
    def __init__(self, *args, **kwargs):
        super(ViewLanguage, self).__init__(setting='language', *args, **kwargs)
        
    def doCommand(self, event):
        if self.settings.get(self.section, self.setting) == self.value:
            return
        super(ViewLanguage, self).doCommand(event)
        dialog = wx.MessageDialog(self.mainwindow,
            _('This setting will take effect after you restart %s'%meta.name),
            _('Language setting'), wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()    
    
    
    
class TaskNew(MainWindowCommand, FilterCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskNew, self).__init__(bitmap='new', 
            menuText=_('&New task...\tINS'), helpText=_('Insert a new task'), *args,
            **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewTaskCommand(self.filteredTaskList),
            self.uiCommands, self.settings, bitmap=self.bitmap)
        editor.Show(show)
        return editor


class TaskNewSubTask(NeedsSelectedTasks, MainWindowCommand,
        FilterCommand, ViewerCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskNewSubTask, self).__init__(bitmap='newsubtask',
            menuText=_('New &subtask...\tCtrl+INS'),
            helpText=_('Insert a new subtask into the selected task'), *args,
            **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewSubTaskCommand(self.filteredTaskList, 
                self.viewer.curselection()),
            self.uiCommands, self.settings, bitmap='new')
        editor.Show(show)
        return editor


class TaskEdit(NeedsSelectedTasks, MainWindowCommand, FilterCommand, 
        ViewerCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskEdit, self).__init__(bitmap='edit',
            menuText=_('&Edit task...'), helpText=_('Edit the selected task'), 
            *args, **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.EditTaskCommand(self.filteredTaskList, 
                self.viewer.curselection()), self.uiCommands, self.settings)
        editor.Show(show)
        return editor


class TaskMarkCompleted(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMarkCompleted, self).__init__(bitmap='markcompleted',
            menuText=_('&Mark completed'),
            helpText=_('Mark the selected task(s) completed'), *args, **kwargs)

    def doCommand(self, event):
        markCompletedCommand = command.MarkCompletedCommand(self.filteredTaskList, 
            self.viewer.curselection())
        markCompletedCommand.do()

    def enabled(self):
        return super(TaskMarkCompleted, self).enabled() and \
            [task for task in self.viewer.curselection() if not task.completed()]


class TaskDelete(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskDelete, self).__init__(bitmap='delete',
            menuText=_('&Delete task\tCtrl+D'),
            helpText=_('Delete the selected task(s)'), *args, **kwargs)

    def doCommand(self, event):
        deleteCommand = command.DeleteTaskCommand(self.filteredTaskList, 
            self.viewer.curselection())
        deleteCommand.do()


class EffortNew(NeedsSelectedTasks, MainWindowCommand, EffortCommand,
        ViewerCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        super(EffortNew, self).__init__(bitmap='start',  
            menuText=_('&New effort...'), 
            helpText=_('Add a effort period to the selected task(s)'),
            *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow, 
            command.NewEffortCommand(self.effortList, self.viewer.curselection()),
            self.uiCommands)
        editor.Show()
        return editor 

class EffortEdit(NeedsSelectedEffort, MainWindowCommand, EffortCommand, 
        ViewerCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        super(EffortEdit, self).__init__(bitmap='edit',
            menuText=_('&Edit effort...'),
            helpText=_('Edit the selected effort period(s)'), *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow,
            command.EditEffortCommand(self.effortList, 
                self.viewer.curselection()), self.uiCommands)
        editor.Show()
        return editor

class EffortDelete(NeedsSelectedEffort, EffortCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EffortDelete, self).__init__(bitmap='delete',
            menuText=_('&Delete effort'),
            helpText=_('Delete the selected effort period(s)'), *args, **kwargs)

    def doCommand(self, event):
        delete = command.DeleteEffortCommand(self.effortList,
            self.viewer.curselection())
        delete.do()


class EffortStart(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        self.adjacent = False
        myOptions = {'bitmap': 'start', 'menuText': _('&Start tracking effort'),
            'helpText': _('Start tracking effort for the selected task(s)')}
        myOptions.update(kwargs)
        super(EffortStart, self).__init__(*args, **myOptions)
    
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
    def __init__(self, *args, **kwargs):
        super(EffortStartAdjacent, self).__init__(menuText=_('S&tart tracking from last stop time'),
            helpText=_('Start tracking effort for the selected task(s) with start time ' \
            'equal to end time of last effort'), *args, **kwargs)
        self.adjacent = True
        
    def enabled(self):
        return (self.filteredTaskList.maxDateTime() is not None) and super(EffortStartAdjacent, self).enabled()


class EffortStop(FilterCommand):
    def __init__(self, *args, **kwargs):
        super(EffortStop, self).__init__(bitmap='stop',
            menuText=_('St&op tracking effort'),
            helpText=_('Stop tracking effort for the active task(s)'), *args, **kwargs)

    def doCommand(self, event):
        stop = command.StopEffortCommand(self.filteredTaskList)
        stop.do()

    def enabled(self):
        return bool([task for task in self.filteredTaskList if task.isBeingTracked()])


class HelpCommand(UICommand):
    def __init__(self, *args, **kwargs):
        super(HelpCommand, self).__init__(bitmap='help', *args, **kwargs)

class HelpTasks(HelpCommand):
    def __init__(self, *args, **kwargs):
        super(HelpTasks, self).__init__(menuText=_('&Tasks'),
            helpText=_('Help about the possible states of tasks'), *args, **kwargs)

    def doCommand(self, event):
        help.Tasks()

class HelpColors(HelpCommand):
    def __init__(self, *args, **kwargs):
        super(HelpColors, self).__init__(menuText=_('&Colors'),
            helpText=_('Help about the possible colors of tasks'), *args, **kwargs)

    def doCommand(self, event):
        help.Colors()


class InfoCommand(UICommand):
    def __init__(self, *args, **kwargs):
        super(InfoCommand, self).__init__(bitmap='info', *args, **kwargs)

class HelpAbout(InfoCommand):
    def __init__(self, *args, **kwargs):
        super(HelpAbout, self).__init__(menuText=_('&About %s'%meta.name),
            helpText=_('Version and contact information about %s'%meta.name), *args, **kwargs)

    def doCommand(self, event):
        help.About()

class HelpLicense(InfoCommand):
    def __init__(self, *args, **kwargs):
        super(HelpLicense, self).__init__(menuText=_('&License'),
            helpText=_('%s license'%meta.name), *args, **kwargs)

    def doCommand(self, event):
        help.License()


class MainWindowRestore(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(MainWindowRestore, self).__init__(menuText=_('&Restore'),
            helpText=_('Restore the window to its previous state'),
            bitmap='restore', *args, **kwargs)

    def doCommand(self, event):
        self.mainwindow.restore(event)
    


class UICommands(dict):
    def __init__(self, mainwindow, iocontroller, viewer, settings, 
            filteredTaskList, effortList):
        super(UICommands, self).__init__()
    
        # File commands
        self['open'] = FileOpen(iocontroller=iocontroller)
        self['merge'] = FileMerge(iocontroller=iocontroller)
        self['close'] = FileClose(iocontroller=iocontroller)
        self['save'] = FileSave(iocontroller=iocontroller)
        self['saveas'] = FileSaveAs(iocontroller=iocontroller)
        self['saveselection'] = FileSaveSelection(iocontroller=iocontroller, 
            viewer=viewer)
        self['quit'] = FileQuit(mainwindow=mainwindow)

        # menuEdit commands
        self['undo'] = EditUndo()
        self['redo'] = EditRedo()
        self['cut'] = EditCut(filteredTaskList=filteredTaskList, viewer=viewer)
        self['copy'] = EditCopy(filteredTaskList=filteredTaskList, viewer=viewer)
        self['paste'] = EditPaste(filteredTaskList=filteredTaskList)
        self['pasteassubtask'] = EditPasteAsSubtask(filteredTaskList=filteredTaskList, viewer=viewer)

        # Selection commands
        self['selectall'] = SelectAll(viewer=viewer)
        self['invertselection'] = InvertSelection(viewer=viewer)
        self['clearselection'] = ClearSelection(viewer=viewer)

        # View commands
        self['viewalltasks'] = ViewAllTasks(filteredTaskList=filteredTaskList, settings=settings, uiCommands=self)
        self['viewcompletedtasks'] = ViewCompletedTasks(filteredTaskList=filteredTaskList, 
            settings=settings)
        self['viewinactivetasks'] = ViewInactiveTasks(filteredTaskList=filteredTaskList,
            settings=settings)
        self['viewactivetasks'] = ViewActiveTasks(filteredTaskList=filteredTaskList,
            settings=settings)    
        self['viewoverduetasks'] = ViewOverDueTasks(filteredTaskList=filteredTaskList,
            settings=settings)    
        self['viewoverbudgettasks'] = ViewOverBudgetTasks(filteredTaskList=filteredTaskList,
            settings=settings)
        self['viewcompositetasks'] = ViewCompositeTasks(viewer=viewer, filteredTaskList=filteredTaskList,
            settings=settings)
            
        self['viewstartdate'] = ViewColumn(column='Start date', viewer=viewer, 
            settings=settings, 
            menuText=_('&Start date'), helpText = _('Show/hide start date column'),
            setting='startdate')
        self['viewduedate'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('&Due date'), helpText=_('Show/hide due date column'),
            setting='duedate', column='Due date')
        self['viewdaysleft'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('D&ays left'), helpText=_('Show/hide days left column'),
            setting='daysleft', column='Days left')
        self['viewcompletiondate'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('Co&mpletion date'), helpText=_('Show/hide completion date column'),
            setting='completiondate', column='Completion date')
        self['viewbudget'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('&Budget'), helpText=_('Show/hide budget column'),
            setting='budget', column='Budget')
        self['viewtotalbudget'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('Total b&udget'),
            helpText=_('Show/hide total budget column (total budget includes budget for subtasks)'),
            setting='totalbudget', column='Total budget')
        self['viewtimespent'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('&Time spent'), helpText=_('Show/hide time spent column'),
            setting='timespent', column='Time spent')
        self['viewtotaltimespent'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('T&otal time spent'),
            helpText=_('Show/hide total time spent column (total time includes time spent on subtasks)'),
            setting='totaltimespent', column='Total time spent')
        self['viewbudgetleft'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('Budget &left'), helpText=_('Show/hide budget left column'),
            setting='budgetleft', column='Budget left')
        self['viewtotalbudgetleft'] = ViewColumn(viewer=viewer, settings=settings,
            menuText=_('Total budget l&eft'),
            helpText=_('Show/hide total budget left column (total budget left includes budget left for subtasks)'),
            setting='totalbudgetleft', column='Total budget left')
    
        self['viewexpandall'] = ViewExpandAll(viewer=viewer)
        self['viewcollapseall'] = ViewCollapseAll(viewer=viewer)
        self['viewexpandselected'] = ViewExpandSelected(viewer=viewer)
        self['viewcollapseselected'] = ViewCollapseSelected(viewer=viewer)
        
        self['viewlanguageenglish'] = ViewLanguage(value='en', menuText=_('&English'),
            helpText=_('Show English user interface after restart'), mainwindow=mainwindow, 
            settings=settings)
        self['viewlanguagedutch'] = ViewLanguage(value='nl', menuText=_('&Dutch'), 
            helpText=_('Show Dutch user interface after restart'), 
            mainwindow=mainwindow, settings=settings)
        self['viewlanguagefrench'] = ViewLanguage(value='fr', menuText=_('&French'),
            helpText=_('Show French user interface after restart'),
            mainwindow=mainwindow, settings=settings)

        self['toolbarhide'] = ViewToolBar(mainwindow=mainwindow, settings=settings,
            value=None, menuText=_('&Hide'), helpText=_('Hide the toolbar'))
        self['toolbarsmall'] = ViewToolBar(mainwindow=mainwindow, settings=settings,
            value=(16, 16), menuText=_('&Small images'), 
            helpText=_('Small images (16x16) on the toolbar'))
        self['toolbarmedium'] = ViewToolBar(mainwindow=mainwindow, settings=settings,
            value=(22, 22), menuText=_('&Medium-sized images'),
            helpText=_('Medium-sized images (22x22) on the toolbar'))
        self['toolbarbig'] = ViewToolBar(mainwindow=mainwindow, settings=settings,
            value=(32, 32), menuText=_('&Large images'),
            helpText=_('Large images (32x32) on the toolbar'))

        self['viewfinddialog'] = ViewFindDialog(mainwindow=mainwindow, settings=settings)
        self['viewstatusbar'] = ViewStatusBar(mainwindow=mainwindow, settings=settings)
        self['viewsplashscreen'] = ViewSplashScreen(settings=settings)

        self['viewduetoday'] = ViewDueBefore(menuText=_('&Today'), 
            helpText=_('Only show tasks due today'), value='Today', 
            filteredTaskList=filteredTaskList, settings=settings)
        self['viewduetomorrow'] = ViewDueBefore(menuText=_('T&omorrow'), 
            helpText=_('Only show tasks due today and tomorrow'), value='Tomorrow', 
            filteredTaskList=filteredTaskList, settings=settings)
        self['viewdueworkweek'] = ViewDueBefore(menuText=_('Wo&rk week'),
            helpText=_('Only show tasks due this work week (i.e. before Friday)'),
            value='Workweek', filteredTaskList=filteredTaskList, settings=settings)
        self['viewdueweek'] = ViewDueBefore(menuText=_('&Week'),
            helpText=_('Only show tasks due this week (i.e. before Sunday)'), value='Week',
            filteredTaskList=filteredTaskList, settings=settings)
        self['viewduemonth'] = ViewDueBefore(menuText=_('&Month'), 
            helpText=_('Only show tasks due this month'), value='Month',
            filteredTaskList=filteredTaskList, settings=settings)
        self['viewdueyear'] = ViewDueBefore(menuText=_('&Year'),
            helpText=_('Only show tasks due this year'), value='Year',
            filteredTaskList=filteredTaskList, settings=settings)
        self['viewdueunlimited'] = ViewDueBefore(menuText=_('&Unlimited'), 
            helpText=_('Show all tasks'), value='Unlimited', 
            filteredTaskList=filteredTaskList, settings=settings)

        # Task menu
        self['new'] = TaskNew(mainwindow=mainwindow, 
            filteredTaskList=filteredTaskList, uiCommands=self, settings=settings)
        self['newsubtask'] = TaskNewSubTask(mainwindow=mainwindow, 
            filteredTaskList=filteredTaskList, viewer=viewer, uiCommands=self, 
            settings=settings)
        self['edit'] = TaskEdit(mainwindow=mainwindow, 
            filteredTaskList=filteredTaskList, viewer=viewer, uiCommands=self, 
            settings=settings)
        self['markcompleted'] = TaskMarkCompleted(filteredTaskList=filteredTaskList,
            viewer=viewer)
        self['delete'] = TaskDelete(filteredTaskList=filteredTaskList, viewer=viewer)
        
        # Effort menu
        self['neweffort'] = EffortNew(mainwindow=mainwindow, effortList=effortList,
            viewer=viewer, uiCommands=self)
        self['editeffort'] = EffortEdit(mainwindow=mainwindow, effortList=effortList, 
            viewer=viewer, uiCommands=self)
        self['deleteeffort'] = EffortDelete(effortList=effortList, viewer=viewer)
        self['starteffort'] = EffortStart(filteredTaskList=filteredTaskList, viewer=viewer)
        self['starteffortadjacent'] = EffortStartAdjacent(filteredTaskList=filteredTaskList, 
            viewer=viewer)
        self['stopeffort'] = EffortStop(filteredTaskList=filteredTaskList)
        
        # Help menu
        self['helptasks'] = HelpTasks()
        self['helpcolors'] = HelpColors()
        self['about'] = HelpAbout()
        self['license'] = HelpLicense()

        # Taskbar menu
        self['restore'] = MainWindowRestore(mainwindow=mainwindow)



import wx, task, patterns, config, gui, meta, command
from gui.dialog import helpdialog
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
    ''' Base user interface command. An UICommand is some action that can be 
        associated with menu's and/or toolbars. It contains the menutext and 
        helptext to be displayed, code to deal with wx.EVT_UPDATE_UI and 
        methods to attach the command to a menu or toolbar. Subclasses should 
        implement doCommand() and optionally override enabled(). '''
    
    def __init__(self, menuText='?', helpText='', bitmap='nobitmap',
            kind=wx.ITEM_NORMAL, *args, **kwargs):
        super(UICommand, self).__init__(*args, **kwargs)
        self.menuText = menuText
        self.helpText = helpText
        self.bitmap = bitmap
        self.kind = kind
        self.menuItems = [] # uiCommands can be used in multiple menu's

    def appendToMenu(self, menu, window, position=None):
        # FIXME: rename to addToMenu
        id = wx.NewId()
        menuItem = wx.MenuItem(menu, id, self.menuText, self.helpText, 
            self.kind)
        self.menuItems.append(menuItem)
        if self.bitmap:
            menuItem.SetBitmap(wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_MENU, 
                (16, 16)))
        if position is None:
            menu.AppendItem(menuItem)
        else:
            menu.InsertItem(position, menuItem)
        self.bind(window, id)
        return id
    
    def removeFromMenu(self, menu, window):
        for menuItem in self.menuItems:
            if menuItem.GetMenu() == menu:
                self.menuItems.remove(menuItem)
                id = menuItem.GetId()
                menu.Remove(id)
                break
        self.unbind(window, id)
        
    def appendToToolBar(self, toolbar):
        id = wx.NewId()
        bitmap = wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_TOOLBAR, 
            toolbar.GetToolBitmapSize())
        toolbar.AddLabelTool(id, '',
            bitmap, wx.NullBitmap, self.kind, 
            shortHelp=wx.MenuItem.GetLabelFromText(self.menuText),
            longHelp=self.helpText)
        self.bind(toolbar, id)
        return id

    def bind(self, window, id):
        window.Bind(wx.EVT_MENU, self.onCommandActivate, id=id)
        window.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI, id=id)

    def unbind(self, window, id):
        for eventType in [wx.EVT_MENU, wx.EVT_UPDATE_UI]:
            window.Unbind(eventType, id=id)
        
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
            
    __call__ = onCommandActivate

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
        
    def onUpdateUI(self, event):
        event.Check(self.isSettingChecked())     
        super(BooleanSettingsCommand, self).onUpdateUI(event)
        

class UICheckCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        super(UICheckCommand, self).__init__(kind=wx.ITEM_CHECK, 
            bitmap=self.getBitmap(), *args, **kwargs)
            
    def isSettingChecked(self):
        return self.settings.getboolean(self.section, self.setting)

    def doCommand(self, event):
        self.settings.set(self.section, self.setting, str(event.IsChecked()))
        
    def getBitmap(self):
        if '__WXMSW__' in wx.PlatformInfo:
            # Use pretty Nuvola checkmark bitmap
            return 'on' 
        else:
            # Use default checkmark. Providing our own bitmap causes
            # "(python:8569): Gtk-CRITICAL **: gtk_check_menu_item_set_active: 
            # assertion `GTK_IS_CHECK_MENU_ITEM (check_menu_item)' failed"
            # on systems that use Gtk
            return None


class UIRadioCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        super(UIRadioCommand, self).__init__(kind=wx.ITEM_RADIO, bitmap=None,
            *args, **kwargs)
            
    def isSettingChecked(self):
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
            helpText=_('Open a %s file')%meta.name, bitmap='fileopen', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.open()


class RecentFileOpen(IOCommand):
    def __init__(self, *args, **kwargs):
        self.__filename = kwargs.pop('filename')
        index = kwargs.pop('index')
        super(RecentFileOpen, self).__init__(menuText='&%d %s'%(index, self.__filename),
            helpText=_('Open %s')%self.__filename, *args, **kwargs)
            
    def doCommand(self, event):
        self.iocontroller.open(self.__filename)

        
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
            helpText=_('Exit %s')%meta.name, bitmap='exit', *args, **kwargs)

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


class EditPreferences(MainWindowCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(EditPreferences, self).__init__(menuText=_('Preferences...'),
            helpText=_('Edit preferences'), bitmap='configure', *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.Preferences(parent=self.mainwindow, title=_('Edit preferences'), 
            settings=self.settings)
        editor.Show()


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
        self.settings.set(self.section, 'tasksdue', 'Unlimited')    
        self.filteredTaskList.setSubject()
        self.filteredTaskList.removeAllCategories()


class ViewCategories(MainWindowCommand, FilterCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCategories, self).__init__(menuText=_('Tasks by catego&ries...'),
            helpText=_('Show/hide tasks by category'), bitmap='category', *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.CategoriesFilterDialog(parent=self.mainwindow,
            title=_('View categories'), taskList=self.filteredTaskList)
        editor.Show()

    def enabled(self):
        return self.filteredTaskList.categories() 
        
        
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
             
        
class TaskNew(MainWindowCommand, FilterCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskNew, self).__init__(bitmap='new', 
            menuText=_('&New task...\tINS'), helpText=_('Insert a new task'), *args,
            **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewTaskCommand(self.filteredTaskList),
            self.uiCommands, self.settings, self.filteredTaskList.categories(), bitmap=self.bitmap)
        editor.Show(show)


class TaskNewSubTask(NeedsSelectedTasks, MainWindowCommand,
        FilterCommand, ViewerCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskNewSubTask, self).__init__(bitmap='newsubtask',
            menuText=_('New &subtask...\tCtrl+INS'),
            helpText=_('Insert a new subtask into the selected task'), *args,
            **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewSubTaskCommand(self.filteredTaskList, self.viewer.curselection()),
            self.uiCommands, self.settings, self.filteredTaskList.categories(), bitmap='new')
        editor.Show(show)


class TaskEdit(NeedsSelectedTasks, MainWindowCommand, FilterCommand, 
        ViewerCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskEdit, self).__init__(bitmap='edit',
            menuText=_('&Edit task...'), helpText=_('Edit the selected task'), 
            *args, **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.EditTaskCommand(self.filteredTaskList, self.viewer.curselection()), 
            self.uiCommands, self.settings,
            self.filteredTaskList.categories())
        editor.Show(show)


class TaskMarkCompleted(NeedsSelectedTasks, FilterCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMarkCompleted, self).__init__(bitmap='markcompleted',
            menuText=_('&Mark completed\tCtrl+ENTER'),
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
            menuText=_('&Delete task\tDEL'),
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
            self.uiCommands, self.effortList)
        editor.Show()


class EffortEdit(NeedsSelectedEffort, MainWindowCommand, EffortCommand, 
        ViewerCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        super(EffortEdit, self).__init__(bitmap='edit',
            menuText=_('&Edit effort...'),
            helpText=_('Edit the selected effort period(s)'), *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow,
            command.EditEffortCommand(self.effortList, self.viewer.curselection()),
            self.uiCommands, self.effortList)
        editor.Show()


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
        super(EffortStart, self).__init__(bitmap='start', 
            menuText=_('&Start tracking effort'), 
            helpText=_('Start tracking effort for the selected task(s)'), 
            *args, **kwargs)
    
    def doCommand(self, event):
        start = command.StartEffortCommand(self.filteredTaskList, self.viewer.curselection())
        start.do()
        
    def enabled(self):
        if not self.viewer.isShowingTasks():
            return False
        return [task for task in self.viewer.curselection() if not
            (task.isBeingTracked() or task.completed() or task.inactive())]


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


class DialogCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.closed = True
        super(DialogCommand, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        self.closed = False
        dialog = self.dialog()
        dialog.Bind(wx.EVT_CLOSE, self.onClose)
        dialog.Bind(wx.EVT_BUTTON, self.onClose)
        
    def onClose(self, event):
        self.closed = True
        event.Skip()
        
    def enabled(self):
        return self.closed


class HelpCommand(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(HelpCommand, self).__init__(bitmap='help', *args, **kwargs)
        
class HelpTasks(HelpCommand):
    def __init__(self, *args, **kwargs):
        self.dialog = helpdialog.Tasks
        super(HelpTasks, self).__init__(menuText=_('&Tasks'),
            helpText=_('Help about the possible states of tasks'), *args, **kwargs)

class HelpColors(HelpCommand):
    def __init__(self, *args, **kwargs):
        self.dialog = helpdialog.Colors
        super(HelpColors, self).__init__(menuText=_('&Colors'),
            helpText=_('Help about the possible colors of tasks'), *args, **kwargs)

class InfoCommand(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(InfoCommand, self).__init__(bitmap='info', *args, **kwargs)

class HelpAbout(InfoCommand):
    def __init__(self, *args, **kwargs):
        self.dialog = helpdialog.About
        super(HelpAbout, self).__init__(menuText=_('&About %s')%meta.name,
            helpText=_('Version and contact information about %s')%meta.name, *args, **kwargs)

class HelpLicense(InfoCommand):
    def __init__(self, *args, **kwargs):
        self.dialog = helpdialog.License
        super(HelpLicense, self).__init__(menuText=_('&License'),
            helpText=_('%s license')%meta.name, *args, **kwargs)


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
        self.__iocontroller = iocontroller
    
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
        self['editpreferences'] = EditPreferences(mainwindow=mainwindow, settings=settings)
        
        # Selection commands
        self['selectall'] = SelectAll(viewer=viewer)
        self['invertselection'] = InvertSelection(viewer=viewer)
        self['clearselection'] = ClearSelection(viewer=viewer)

        # View commands
        self['viewalltasks'] = ViewAllTasks(filteredTaskList=filteredTaskList, settings=settings, uiCommands=self)
        self['viewcompletedtasks'] = UICheckCommand(menuText=_('&Completed'), 
            helpText=_('Show/hide completed tasks'), setting='completedtasks',
            settings=settings)
        self['viewinactivetasks'] = UICheckCommand(menuText=_('&Inactive'), 
            helpText=_('Show/hide inactive tasks (tasks with a start date in the future)'),
            setting='inactivetasks', settings=settings)
        self['viewactivetasks'] = UICheckCommand(menuText=_('&Active'), 
            helpText=_('Show/hide active tasks (tasks with a start date in the past and a due date in the future)'),
            setting='activetasks', settings=settings)    
        self['viewoverduetasks'] = UICheckCommand(menuText=_('&Over due'), 
            helpText=_('Show/hide active tasks (tasks with a start date in the past and a due date in the future)'),
            setting='overduetasks', settings=settings)    
        self['viewoverbudgettasks'] = UICheckCommand(menuText=_('Over &budget'), 
            helpText=_('Show/hide tasks that are over budget'),
            setting='overbudgettasks', settings=settings)
        self['viewcompositetasks'] = UICheckCommand(
            menuText=_('Tasks &with subtasks'), 
            helpText=_('Show/hide tasks with subtasks'), 
            setting='compositetasks', settings=settings)

        
        self['viewcategories'] = ViewCategories(mainwindow=mainwindow, 
            filteredTaskList=filteredTaskList)

        # Column show/hide commands
        for menuText, helpText, setting in \
            [(_('&Start date'), _('Show/hide start date column'), 'startdate'),
             (_('&Due date'), _('Show/hide due date column'), 'duedate'),
             (_('D&ays left'), _('Show/hide days left column'), 'timeleft'),
             (_('Co&mpletion date'), _('Show/hide completion date column'), 'completiondate'),
             (_('&Budget'), _('Show/hide budget column'), 'budget'),
             (_('Total b&udget'), _('Show/hide total budget column (total budget includes budget for subtasks)'), 'totalbudget'),
             (_('&Time spent'), _('Show/hide time spent column'), 'timespent'),
             (_('T&otal time spent'), _('Show/hide total time spent column (total time includes time spent on subtasks)'), 'totaltimespent'),
             (_('Budget &left'), _('Show/hide budget left column'), 'budgetleft'),
             (_('Total budget l&eft'), _('Show/hide total budget left column (total budget left includes budget left for subtasks)'), 'totalbudgetleft'),
             (_('&Priority'), _('Show/hide priority column'), 'priority'),
             (_('O&verall priority'), _('Show/hide overall priority column (overall priority is the maximum priority of a task and all its subtasks)'), 'totalpriority'),
             (_('Last modification time'), _('Show/hide last modification time column'), 'lastmodificationtime'),
             (_('Overall last modification time'), _('Show/hide overall last modification time column (overall last modification time is the most recent modification time of a task and all it subtasks'), 'totallastmodificationtime')]:
            key = 'view' + setting
            self[key] = UICheckCommand(menuText=menuText, helpText=helpText, setting=setting, settings=settings)
    
        self['viewexpandall'] = ViewExpandAll(viewer=viewer)
        self['viewcollapseall'] = ViewCollapseAll(viewer=viewer)
        self['viewexpandselected'] = ViewExpandSelected(viewer=viewer)
        self['viewcollapseselected'] = ViewCollapseSelected(viewer=viewer)
                
        self['viewsortorder'] = UICheckCommand(menuText=_('&Ascending'),
            helpText=_('Sort tasks ascending (checked) or descending (unchecked)'),
            setting='sortascending', settings=settings)
        self['viewsortcasesensitive'] = UICheckCommand(menuText=_('Sort case sensitive'),
            helpText=_('When comparing text, sorting is case sensitive (checked) or insensitive (unchecked)'),
            setting='sortcasesensitive', settings=settings)
        self['viewsortbystatusfirst'] = UICheckCommand(menuText=_('Sort by status &first'),
            helpText=_('Sort tasks by status (active/inactive/completed) first'),
            setting='sortbystatusfirst', settings=settings)
        
        # Sort by column commands
        for menuText, helpText, value in \
            [(_('Sub&ject'), _('Sort tasks by subject'), 'subject'),
             (_('&Start date'), _('Sort tasks by start date'), 'startDate'),
             (_('&Due date'), _('Sort tasks by due date'), 'dueDate'),
             (_('&Completion date'), _('Sort tasks by completion date'), 'completionDate'),
             (_('&Days left'), _('Sort tasks by number of days left'), 'timeLeft'),
             (_('&Budget'), _('Sort tasks by budget'), 'budget'),
             (_('Total b&udget'), _('Sort tasks by total budget'), 'totalbudget'),
             (_('&Time spent'), _('Sort tasks by time spent'), 'timeSpent'),
             (_('T&otal time spent'), _('Sort tasks by total time spent'), 'totaltimeSpent'),
             (_('Budget &left'), _('Sort tasks by budget left'), 'budgetLeft'),
             (_('Total budget l&eft'), _('Sort tasks by total budget left'), 'totalbudgetLeft'),
             (_('&Priority'), _('Sort tasks by priority'), 'priority'),
             (_('Overall priority'), _('Sort tasks by overall priority'), 'totalpriority'),
             (_('Last modification time'), _('Sort tasks by last modification time'), 'lastModificationTime'),
             (_('Overall last modification time'), _('Sort tasks by overall last modification time'), 'totallastModificationTime')]:
            key = 'viewsortby' + value
            key = key.lower()
            self[key] = UIRadioCommand(settings=settings, setting='sortby', value=value,
                                       menuText=menuText, helpText=helpText)
        
        # Toolbar size commands                
        for key, value, menuText, helpText in \
            [('hide', None, _('&Hide'), _('Hide the toolbar')),
             ('small', (16, 16), _('&Small images'), _('Small images (16x16) on the toolbar')),
             ('medium', (22, 22), _('&Medium-sized images'), _('Medium-sized images (22x22) on the toolbar')),
             ('big', (32, 32), _('&Large images'), _('Large images (32x32) on the toolbar'))]:
            key = 'toolbar' + key     
            self[key] = UIRadioCommand(settings=settings, setting='toolbar',
                value=value, menuText=menuText, helpText=helpText)
                                                         
        self['viewfinddialog'] = UICheckCommand(settings=settings,
            menuText=_('&Find dialog'), helpText=_('Show/hide find dialog'), 
            setting='finddialog')
        self['viewstatusbar'] = UICheckCommand(settings=settings, 
            menuText=_('Status&bar'), helpText=_('Show/hide status bar'), 
            setting='statusbar')

        # View tasks due before commands
        for value, menuText, helpText in \
            [('Today', _('&Today'), _('Only show tasks due today')),
             ('Tomorrow', _('T&omorrow'), _('Only show tasks due today and tomorrow')),
             ('Workweek', _('Wo&rk week'), _('Only show tasks due this work week (i.e. before Friday)')),
             ('Week', _('&Week'), _('Only show tasks due this week (i.e. before Sunday)')),
             ('Month', _('&Month'), _('Only show tasks due this month')),
             ('Year', _('&Year'), _('Only show tasks due this year')),
             ('Unlimited', _('&Unlimited'), _('Show all tasks'))]:
            key = 'viewdue' + value
            key = key.lower()
            self[key] = UIRadioCommand(settings=settings, setting='tasksdue', value=value,
                                       menuText=menuText, helpText=helpText)
                                       
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
        self['stopeffort'] = EffortStop(filteredTaskList=filteredTaskList)
        
        # Help menu
        self['helptasks'] = HelpTasks()
        self['helpcolors'] = HelpColors()
        self['about'] = HelpAbout()
        self['license'] = HelpLicense()

        # Taskbar menu
        self['restore'] = MainWindowRestore(mainwindow=mainwindow)

    def createRecentFileOpenUICommand(self, filename, index):
        return RecentFileOpen(filename=filename, index=index, iocontroller=self.__iocontroller)

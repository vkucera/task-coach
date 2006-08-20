import wx, patterns, config, gui, meta, command, help, widgets, urllib, os
from gui import render
from i18n import _
import domain.task as task
import thirdparty.desktop as desktop
import persistence.html

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
            kind=wx.ITEM_NORMAL, id=None, *args, **kwargs):
        super(UICommand, self).__init__(*args, **kwargs)
        self.menuText = menuText
        self.helpText = helpText
        self.bitmap = bitmap
        self.kind = kind
        self.id = id or wx.NewId()
        self.menuItems = [] # uiCommands can be used in multiple menu's

    def appendToMenu(self, menu, window, position=None):
        # FIXME: rename to addToMenu
        menuItem = wx.MenuItem(menu, self.id, self.menuText, self.helpText, 
            self.kind)
        self.menuItems.append(menuItem)
        if self.bitmap:
            menuItem.SetBitmap(wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_MENU, 
                (16, 16)))
        if position is None:
            menu.AppendItem(menuItem)
        else:
            menu.InsertItem(position, menuItem)
        self.bind(window, self.id)
        return self.id
    
    def removeFromMenu(self, menu, window):
        for menuItem in self.menuItems:
            if menuItem.GetMenu() == menu:
                self.menuItems.remove(menuItem)
                id = menuItem.GetId()
                menu.Remove(id)
                break
        self.unbind(window, id)
        
    def appendToToolBar(self, toolbar):
        bitmap = wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_TOOLBAR, 
            toolbar.GetToolBitmapSize())
        toolbar.AddLabelTool(self.id, '',
            bitmap, wx.NullBitmap, self.kind, 
            shortHelp=wx.MenuItem.GetLabelFromText(self.menuText),
            longHelp=self.helpText)
        self.bind(toolbar, self.id)
        return self.id

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
        if self.enabled(event):
            self.doCommand(event)
            
    __call__ = onCommandActivate

    def doCommand(self, event):
        raise NotImplementedError

    def onUpdateUI(self, event):
        event.Enable(bool(self.enabled(event)))

    def enabled(self, event):
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
    def __init__(self, *args, **kwargs):
        self.iocontroller = kwargs.pop('iocontroller', None)
        super(IOCommand, self).__init__(*args, **kwargs)


class MainWindowCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.mainwindow = kwargs.pop('mainwindow', None)
        super(MainWindowCommand, self).__init__(*args, **kwargs)


class TaskListCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.taskList = kwargs.pop('taskList', None)
        super(TaskListCommand, self).__init__(*args, **kwargs)
        
        
class EffortListCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.effortList = kwargs.pop('effortList', None)
        super(EffortListCommand, self).__init__(*args, **kwargs)


class ViewerCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.viewer = kwargs.pop('viewer', None)
        super(ViewerCommand, self).__init__(*args, **kwargs)


class UICommandsCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.uiCommands = kwargs.pop('uiCommands', None)
        super(UICommandsCommand, self).__init__(*args, **kwargs)    


class UICheckGroupCommand(UICommandsCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        self.uiCommandNames = kwargs.pop('uiCommandNames')
        super(UICheckGroupCommand, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        for uiCommandName in self.uiCommandNames:
            uiCommand = self.uiCommands[uiCommandName]
            self.settings.set(uiCommand.section, uiCommand.setting,
                              str(event.IsChecked()))
        super(UICheckGroupCommand, self).doCommand(event)

    def onUpdateUI(self, event):
        # This check command is off when one or more of the check commands in 
        # the group is off and on when all check commands in the group are on
        for uiCommandName in self.uiCommandNames:
            uiCommand = self.uiCommands[uiCommandName]
            if not self.settings.getboolean(uiCommand.section, uiCommand.setting):
                self.settings.set(self.section, self.setting, 'False')
                break
        else:
            self.settings.set(self.section, self.setting, 'True')
        super(UICheckGroupCommand, self).onUpdateUI(event)
        

# Mixins: 

class NeedsSelection(object):
    def enabled(self, event):
        return self.viewer.curselection()
 
class NeedsSelectedTasks(NeedsSelection):
    def enabled(self, event):
        return super(NeedsSelectedTasks, self).enabled(event) and \
            self.viewer.isShowingTasks()

class NeedsSelectedEffort(NeedsSelection):
    def enabled(self, event):
        return super(NeedsSelectedEffort, self).enabled(event) and \
            self.viewer.isShowingEffort()
               
class NeedsAtLeastOneTask(object):
    def enabled(self, event):
        return len(self.taskList) > 0
        
class NeedsItems(object):
    def enabled(self, event):
        return self.viewer.size() 


# Commands:

class FileOpen(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileOpen, self).__init__(menuText=_('&Open...\tCtrl+O'),
            helpText=_('Open a %s file')%meta.name, bitmap='fileopen',
            id=wx.ID_OPEN, *args, **kwargs)

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
            helpText=_('Close the current file'), bitmap='close',
            id=wx.ID_CLOSE, *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.close()


class FileSave(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileSave, self).__init__(menuText=_('&Save\tCtrl+S'),
            helpText=_('Save the current file'), bitmap='save',
            id=wx.ID_SAVE, *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.save()
        
    def enabled(self, event):
        return self.iocontroller.needSave()


class FileSaveAs(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveAs, self).__init__(menuText=_('S&ave as...'),
            helpText=_('Save the current file under a new name'), 
            bitmap='saveas', id=wx.ID_SAVEAS, *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.saveas()
        

class FileSaveSelection(NeedsSelectedTasks, IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveSelection, self).__init__(menuText=_('Sa&ve selection...'),
            helpText=_('Save the selected tasks to a separate file'), 
            bitmap='saveselection', *args, **kwargs)
    
    def doCommand(self, event):
        self.iocontroller.saveselection(self.viewer.curselection()), 


# FIXME: Move the printing specific stuff somewhere else

import patterns
class PrinterSettings(object):
    def __init__(self):
        self.printData = wx.PrintData()
        self.pageSetupData = wx.PageSetupDialogData(self.printData)

    def updatePageSetupData(self, data):
        self.pageSetupData = wx.PageSetupDialogData(data)
        self.updatePrintData(data.GetPrintData())

    def updatePrintData(self, printData):
        self.printData = wx.PrintData(printData)
        self.pageSetupData.SetPrintData(self.printData)

printerSettings = PrinterSettings()

def createPrintout(viewer):
    htmlText = persistence.viewer2html(viewer)
    printout = wx.html.HtmlPrintout()
    printout.SetHtmlText(htmlText)
    printout.SetFooter(_('Page') + ' @PAGENUM@/@PAGESCNT@', wx.html.PAGE_ALL)
    printout.SetFonts('Arial', 'Courier')
    global printerSettings
    top, left = printerSettings.pageSetupData.GetMarginTopLeft()
    bottom, right = printerSettings.pageSetupData.GetMarginBottomRight()
    printout.SetMargins(top, bottom, left, right)
    return printout


class PrintPageSetup(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(PrintPageSetup, self).__init__(\
            menuText=_('Page setup...'), 
            helpText=_('Setup the characteristics of the printer page'), 
            bitmap='pagesetup', id=wx.ID_PRINT_SETUP, *args, **kwargs)

    def doCommand(self, event):
        global printerSettings
        dialog = wx.PageSetupDialog(self.mainwindow, 
            printerSettings.pageSetupData)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            printerSettings.updatePageSetupData(dialog.GetPageSetupData())
        dialog.Destroy()


class PrintPreview(ViewerCommand, MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(PrintPreview, self).__init__(\
            menuText=_('Print preview'), 
            helpText=_('Show a preview of what the print will look like'), 
            bitmap='printpreview', id=wx.ID_PREVIEW, *args, **kwargs)

    def doCommand(self, event):
        global printerSettings 
        printout = createPrintout(self.viewer)
        printout2 = createPrintout(self.viewer)
        preview = wx.PrintPreview(printout, printout2, 
            printerSettings.printData)
        previewFrame = wx.PreviewFrame(preview, self.mainwindow, 
            _('Print preview'), size=(750, 700))
        previewFrame.Initialize()
        previewFrame.Show()
        

class Print(ViewerCommand, MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(Print, self).__init__(\
            menuText=_('Print...'), 
            helpText=_('Print the current file'), 
            bitmap='print', id=wx.ID_PRINT, *args, **kwargs)

    def doCommand(self, event):
        global printerSettings 
        printout = createPrintout(self.viewer)
        printDialogData = wx.PrintDialogData(printerSettings.printData)
        printDialog = wx.Printer(printDialogData)
        printDialog.Print(self.mainwindow, printout, prompt=True)
 

class FileExportAsICS(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileExportAsICS, self).__init__(menuText=_('Export as &iCalendar...'), 
            helpText=_('Export the current file in iCalendar (*.ics) format'),
            bitmap='exportasics', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.exportAsICS()


class FileExportAsHTML(IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileExportAsHTML, self).__init__(menuText=_('Export as &HTML...'), 
            helpText=_('Export the current view as HTML file'),
            bitmap='exportashtml', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.exportAsHTML(self.viewer)
    

class FileQuit(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(FileQuit, self).__init__(menuText=_('&Quit\tCtrl+Q'), 
            helpText=_('Exit %s')%meta.name, bitmap='exit', 
            id=wx.ID_EXIT, *args, **kwargs)

    def doCommand(self, event):
        self.mainwindow.Close()


def getUndoMenuText():
    return '%s\tCtrl+Z'%patterns.CommandHistory().undostr(_('&Undo')) 

class EditUndo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditUndo, self).__init__(menuText=getUndoMenuText(),
            helpText=_('Undo the last command'), bitmap='undo',
            id=wx.ID_UNDO, *args, **kwargs)
            
    def doCommand(self, event):
        patterns.CommandHistory().undo()

    def onUpdateUI(self, event):
        event.SetText(getUndoMenuText())
        super(EditUndo, self).onUpdateUI(event)

    def enabled(self, event):
        return patterns.CommandHistory().hasHistory()


def getRedoMenuText():
    return '%s\tCtrl+Y'%patterns.CommandHistory().redostr(_('&Redo')) 

class EditRedo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditRedo, self).__init__(menuText=getRedoMenuText(),
            helpText=_('Redo the last command that was undone'), bitmap='redo',
            id=wx.ID_REDO, *args, **kwargs)

    def doCommand(self, event):
        patterns.CommandHistory().redo()

    def onUpdateUI(self, event):
        event.SetText(getRedoMenuText())
        super(EditRedo, self).onUpdateUI(event)

    def enabled(self, event):
        return patterns.CommandHistory().hasFuture()


class EditCut(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):        
        super(EditCut, self).__init__(menuText=_('Cu&t\tCtrl+X'), 
            helpText=_('Cut the selected item(s) to the clipboard'), 
            bitmap='cut', id=wx.ID_CUT, *args, **kwargs)

    def doCommand(self, event):
        cutCommand = command.CutCommand(self.viewer.model(),
                                        self.viewer.curselection())
        cutCommand.do()


class EditCopy(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditCopy, self).__init__(menuText=_('&Copy\tCtrl+C'), 
            helpText=_('Copy the selected item(s) to the clipboard'), 
            bitmap='copy', id=wx.ID_COPY, *args, **kwargs)

    def doCommand(self, event):
        copyCommand = command.CopyCommand(self.viewer.model(), 
                                          self.viewer.curselection())
        copyCommand.do()


class EditPaste(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditPaste, self).__init__(menuText=_('&Paste\tCtrl+V'), 
            helpText=_('Paste item(s) from the clipboard'), bitmap='paste', 
            id=wx.ID_PASTE, *args, **kwargs)

    def doCommand(self, event):
        pasteCommand = command.PasteCommand()
        pasteCommand.do()

    def enabled(self, event):
        return task.Clipboard()


class EditPasteIntoTask(NeedsSelectedTasks, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditPasteIntoTask, self).__init__(menuText=_('P&aste into task'), 
            helpText=_('Paste item(s) from the clipboard into the selected task'),
            bitmap='pasteintotask', *args, **kwargs)

    def doCommand(self, event):
        pasteCommand = command.PasteIntoTaskCommand(
            items=self.viewer.curselection())
        pasteCommand.do()

    def enabled(self, event):
        return super(EditPasteIntoTask, self).enabled(event) and task.Clipboard()


class EditPreferences(MainWindowCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(EditPreferences, self).__init__(menuText=_('Preferences...'),
            helpText=_('Edit preferences'), bitmap='configure', 
            *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.Preferences(parent=self.mainwindow, 
            title=_('Edit preferences'), settings=self.settings)
        editor.Show()


class SelectAll(NeedsItems, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(SelectAll, self).__init__(menuText=_('&All\tCtrl+A'),
            helpText=_('Select all items in the current view'), 
            bitmap='selectall', id=wx.ID_SELECTALL, *args, **kwargs)
        
    def doCommand(self, event):
        self.viewer.selectall()


class InvertSelection(NeedsItems, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(InvertSelection, self).__init__( \
            menuText=_('&Invert selection\tCtrl+I'),
            helpText=_('Select unselected items and unselect selected items'), 
            *args, **kwargs)

    def doCommand(self, event):
        self.viewer.invertselection()


class ClearSelection(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ClearSelection, self).__init__(menuText=_('&Clear selection'), 
            helpText=_('Unselect all items'), *args, **kwargs)

    def doCommand(self, event):
        self.viewer.clearselection()


class ViewAllTasks(SettingsCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        super(ViewAllTasks, self).__init__(menuText=_('&All tasks'),
            helpText=_('Show all tasks (reset all filters)'), 
            bitmap='viewalltasks', *args, **kwargs)
    
    def doCommand(self, event):
        for uiCommandName in ['viewcompletedtasks', 'viewinactivetasks', 
            'viewoverduetasks', 'viewactivetasks', 'viewoverbudgettasks', 
            'viewcompositetasks']:
            uiCommand = self.uiCommands[uiCommandName]
            self.settings.set(uiCommand.section, uiCommand.setting, 'True')
        self.settings.set(self.section, 'tasksdue', 'Unlimited')    
        self.settings.set(self.section, 'tasksearchfilterstring', '')
        self.settings.setlist(self.section, 'taskcategoryfilterlist', [])


class HideCurrentColumn(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(HideCurrentColumn, self).__init__(menuText=_('&Hide this column'),
            helpText=_('Hide the selected column'), *args, **kwargs)
    
    def doCommand(self, event):
        columnPopupMenu = event.GetEventObject()
        self.viewer.hideColumn(columnPopupMenu.columnIndex)
        
    def enabled(self, event):
        # Unfortunately the event (an UpdateUIEvent) does not give us any
        # information to determine the current column, so we have to find 
        # the column ourselves. We use the current mouse position to do so.

        widget = self.viewer.getWidget()
        x, y = widget.ScreenToClient(wx.GetMousePosition())
        item, flag, columnIndex = widget.HitTest((x, y))
        return self.viewer.isHideableColumn(columnIndex)
    
    
class ViewCategories(MainWindowCommand, TaskListCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCategories, self).__init__( \
            menuText=_('Tasks by catego&ries...'),
            helpText=_('Show/hide tasks by category'), bitmap='category', 
            *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.CategoriesFilterDialog(parent=self.mainwindow,
            title=_('View categories'), taskList=self.taskList,
            settings=self.settings)
        editor.Show()

    def enabled(self, event):
        return self.taskList.categories() 
        
        
class ViewExpandAll(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewExpandAll, self).__init__( \
            menuText=_('&Expand all tasks\tShift+Ctrl+E'),
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
        super(ViewCollapseAll, self).__init__( \
            menuText=_('&Collapse all tasks\tShift+Ctrl+C'),
            helpText=_('Collapse all tasks with subtasks'), *args, **kwargs)
    
    def doCommand(self, event):
        self.viewer.collapseAll()
 

class ViewCollapseSelected(NeedsSelectedTasks, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCollapseSelected, self).__init__(bitmap='viewcollapse',
            menuText=_('C&ollapse'),
            helpText=_('Collapse the selected tasks with subtasks'), 
            *args, **kwargs)
    
    def doCommand(self, event):
        self.viewer.collapseSelectedItems()
             
        
class TaskNew(MainWindowCommand, TaskListCommand, UICommandsCommand, \
              SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskNew, self).__init__(bitmap='new', 
            menuText=self.getMenuText(), helpText=_('Insert a new task'), 
            *args, **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewTaskCommand(self.taskList),
            self.taskList, self.uiCommands, self.settings, 
            self.taskList.categories(), bitmap=self.bitmap)
        editor.Show(show)

    def getMenuText(self):
        # There is a bug in wxWidget/wxPython on the Mac that causes the 
        # INSERT accelerator to be mapped so some other key sequence ('c' in
        # this case) so that whenever that key sequence is typed, this command
        # is invoked. Hence, we use a different accelarator on the Mac.
        menuText = _('&New task...')
        if '__WXMAC__' in wx.PlatformInfo:
            menuText += u'\tCtrl+N'
        else:
            menuText += u'\tCtrl+INS'
        return menuText 


class TaskNewSubTask(NeedsSelectedTasks, MainWindowCommand,
        TaskListCommand, ViewerCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskNewSubTask, self).__init__(bitmap='new_subtask',
            menuText=self.getMenuText(),
            helpText=_('Insert a new subtask into the selected task'), *args,
            **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.NewSubTaskCommand(self.taskList, 
            self.viewer.curselection()), self.taskList, self.uiCommands, 
            self.settings, self.taskList.categories(), bitmap='new')
        editor.Show(show)

    def getMenuText(self):
        # There is a bug in wxWidget/wxPython on the Mac that causes the 
        # Ctrl+INSERT accelerator to be mapped so some other key sequence 
        # so that whenever that key sequence is typed, this command is 
        # invoked. Hence, we use a different accelerator on the Mac.
        menuText = _('New &subtask...')
        if '__WXMAC__' in wx.PlatformInfo:
            menuText += u'\tShift+Ctrl+N'
        else:
            menuText += u'\tShift+Ctrl+INS'
        return menuText  
        

class TaskEdit(NeedsSelectedTasks, MainWindowCommand, TaskListCommand, 
        ViewerCommand, UICommandsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskEdit, self).__init__(bitmap='edit',
            menuText=_('&Edit task...'), helpText=_('Edit the selected task'), 
            *args, **kwargs)

    def doCommand(self, event, show=True):
        editor = gui.TaskEditor(self.mainwindow, 
            command.EditTaskCommand(self.taskList, 
            self.viewer.curselection()), self.taskList, 
            self.uiCommands, self.settings, self.taskList.categories())
        editor.Show(show)


class TaskMarkCompleted(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMarkCompleted, self).__init__(bitmap='markcompleted',
            menuText=_('&Mark completed\tCtrl+ENTER'),
            helpText=_('Mark the selected task(s) completed'), *args, **kwargs)

    def doCommand(self, event):
        markCompletedCommand = command.MarkCompletedCommand( \
            self.taskList, self.viewer.curselection())
        markCompletedCommand.do()

    def enabled(self, event):
        return super(TaskMarkCompleted, self).enabled(event) and \
            [task for task in self.viewer.curselection() \
             if not task.completed()]


class TaskDelete(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskDelete, self).__init__(bitmap='delete',
            menuText=_('&Delete task\tCtrl+DEL'),
            helpText=_('Delete the selected task(s)'), *args, **kwargs)

    def doCommand(self, event):
        deleteCommand = command.DeleteCommand(self.taskList, 
            self.viewer.curselection())
        deleteCommand.do()


class TaskDragAndDrop(TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskDragAndDrop, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        dragAndDropCommand = command.DragAndDropTaskCommand( \
            self.taskList, self.viewer.draggedItems(), 
            drop=self.viewer.curselection())
        if dragAndDropCommand.canDo():
            dragAndDropCommand.do()


class TaskMail(NeedsSelectedTasks, ViewerCommand):
    def doCommand(self, event):
        tasks = self.viewer.curselection()
        if len(tasks) > 1:
            subject = _('Tasks')
            bodyLines = []
            for task in tasks:
                bodyLines.append(render.subject(task, recursively=True) + '\n')
                if task.description():
                    bodyLines.extend(task.description().splitlines())
                    bodyLines.append('\n')
        else:
            subject = render.subject(tasks[0], recursively=True)
            bodyLines = tasks[0].description().splitlines()
        body = urllib.quote('\r\n'.join(bodyLines))
        mailToURL = 'mailto:%s?subject=%s&body=%s'%( \
            _('Please enter recipient'), subject, body)
        desktop.open(mailToURL)


class TaskAddAttachment(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskAddAttachment, self).__init__(menuText=_('&Add attachment'),
            helpText=_('Browse for files to add as attachment to the selected task(s)'),
            bitmap='attachment', *args, **kwargs)
        
    def doCommand(self, event):
        filename = widgets.AttachmentSelector()
        if filename:
            addAttachmentCommand = command.AddAttachmentToTaskCommand( \
                self.taskList, self.viewer.curselection(), 
                attachments=[filename])
            addAttachmentCommand.do()
                

class EffortNew(NeedsAtLeastOneTask, MainWindowCommand, EffortListCommand,
        ViewerCommand, UICommandsCommand, TaskListCommand):
    def __init__(self, *args, **kwargs):
        super(EffortNew, self).__init__(bitmap='start',  
            menuText=_('&New effort...'), 
            helpText=_('Add an effort period to the selected task(s)'),
            *args, **kwargs)
            
    def doCommand(self, event):
        if self.viewer.isShowingTasks() and self.viewer.curselection():
            selectedTasks = self.viewer.curselection()
        else:
            subjectDecoratedTaskList = [(render.subject(task, 
                recursively=True), task) for task in self.taskList]
            subjectDecoratedTaskList.sort() # Sort by subject
            selectedTasks = [subjectDecoratedTaskList[0][1]]
        editor = gui.EffortEditor(self.mainwindow, 
            command.NewEffortCommand(self.effortList, selectedTasks),
            self.uiCommands, self.effortList, self.taskList)
        editor.Show()


class EffortEdit(NeedsSelectedEffort, MainWindowCommand, EffortListCommand, 
        ViewerCommand, UICommandsCommand, TaskListCommand):
    def __init__(self, *args, **kwargs):
        super(EffortEdit, self).__init__(bitmap='edit',
            menuText=_('&Edit effort...'),
            helpText=_('Edit the selected effort period(s)'), *args, **kwargs)
            
    def doCommand(self, event):
        editor = gui.EffortEditor(self.mainwindow,
            command.EditEffortCommand(self.effortList, 
            self.viewer.curselection()), self.uiCommands, self.effortList, 
            self.taskList)
        editor.Show()


class EffortDelete(NeedsSelectedEffort, EffortListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EffortDelete, self).__init__(bitmap='delete',
            menuText=_('&Delete effort'),
            helpText=_('Delete the selected effort period(s)'), *args, **kwargs)

    def doCommand(self, event):
        delete = command.DeleteCommand(self.effortList,
            self.viewer.curselection())
        delete.do()


class EffortStart(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EffortStart, self).__init__(bitmap='start', 
            menuText=_('&Start tracking effort'), 
            helpText=_('Start tracking effort for the selected task(s)'), 
            *args, **kwargs)
    
    def doCommand(self, event):
        start = command.StartEffortCommand(self.taskList, 
            self.viewer.curselection())
        start.do()
        
    def enabled(self, event):
        if not self.viewer.isShowingTasks():
            return False
        return [task for task in self.viewer.curselection() if not
            (task.isBeingTracked() or task.completed() or task.inactive())]


class EffortStop(TaskListCommand):
    def __init__(self, *args, **kwargs):
        super(EffortStop, self).__init__(bitmap='stop',
            menuText=_('St&op tracking effort'),
            helpText=_('Stop tracking effort for the active task(s)'), 
            *args, **kwargs)

    def doCommand(self, event):
        stop = command.StopEffortCommand(self.taskList)
        stop.do()

    def enabled(self, event):
        return bool([task for task in self.taskList if \
                     task.isBeingTracked()])


class DialogCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self._dialogTitle = kwargs.pop('dialogTitle')
        self._dialogText = kwargs.pop('dialogText')
        self.closed = True
        super(DialogCommand, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        self.closed = False
        dialog = widgets.HTMLDialog(self._dialogTitle, self._dialogText, 
                                    bitmap=self.bitmap)
        for event in wx.EVT_CLOSE, wx.EVT_BUTTON:
            dialog.Bind(event, self.onClose)
        dialog.Show()
        
    def onClose(self, event):
        self.closed = True
        event.Skip()
        
    def enabled(self, event):
        return self.closed

        
class Help(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(Help, self).__init__(menuText=_('&Help contents'),
            helpText=_('Help about the program'), bitmap='help', 
            dialogTitle=_('Help'), dialogText=help.helpHTML, id=wx.ID_HELP, 
            *args, **kwargs)


class Tips(SettingsCommand, MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(Tips, self).__init__(menuText=_('&Tips'),
            helpText=_('Tips about the program'), bitmap='help', *args, **kwargs)

    def doCommand(self, event):
        help.showTips(self.mainwindow, self.settings)
        

class InfoCommand(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(InfoCommand, self).__init__(bitmap='info', *args, **kwargs)
    
    
class HelpAbout(InfoCommand):
    def __init__(self, *args, **kwargs):
        super(HelpAbout, self).__init__(menuText=_('&About %s')%meta.name,
            helpText=_('Version and contact information about %s')%meta.name, 
            dialogTitle=_('Help: About %s')%meta.name, 
            dialogText=help.aboutHTML, id=wx.ID_ABOUT, *args, **kwargs)
  
  
class HelpLicense(InfoCommand):
    def __init__(self, *args, **kwargs):
        super(HelpLicense, self).__init__(menuText=_('&License'),
            helpText=_('%s license')%meta.name,
            dialogTitle=_('Help: %s license')%meta.name, 
            dialogText=meta.licenseHTML, *args, **kwargs)


class MainWindowRestore(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(MainWindowRestore, self).__init__(menuText=_('&Restore'),
            helpText=_('Restore the window to its previous state'),
            bitmap='restore', *args, **kwargs)

    def doCommand(self, event):
        self.mainwindow.restore(event)
    


class UICommands(dict):
    def __init__(self, mainwindow, iocontroller, viewer, settings, 
            taskList, effortList):
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
        self['printpagesetup'] = PrintPageSetup(mainwindow=mainwindow)
        self['printpreview'] = PrintPreview(mainwindow=mainwindow, 
            viewer=viewer)
        self['print'] = Print(mainwindow=mainwindow, viewer=viewer)
        self['exportasics'] = FileExportAsICS(iocontroller=iocontroller)
        self['exportashtml'] = FileExportAsHTML(iocontroller=iocontroller, 
            viewer=viewer)
        self['quit'] = FileQuit(mainwindow=mainwindow)

        # menuEdit commands
        self['undo'] = EditUndo()
        self['redo'] = EditRedo()
        self['cut'] = EditCut(viewer=viewer)
        self['copy'] = EditCopy(viewer=viewer)
        self['paste'] = EditPaste()
        self['pasteintotask'] = EditPasteIntoTask(viewer=viewer)
        self['editpreferences'] = EditPreferences(mainwindow=mainwindow, 
                                                  settings=settings)
        
        # Selection commands
        self['selectall'] = SelectAll(viewer=viewer)
        self['invertselection'] = InvertSelection(viewer=viewer)
        self['clearselection'] = ClearSelection(viewer=viewer)

        # View commands
        self['viewalltasks'] = ViewAllTasks(settings=settings, uiCommands=self)
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
            taskList=taskList, settings=settings)

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
             (_('&Hourly fee'), _('Show/hide hourly fee column'), 'hourlyfee'),
             (_('&Fixed fee'), _('Show/hide fixed fee column'), 'fixedfee'),
             (_('&Total fixed fee'), _('Show/hide total fixed fee column'), 'totalfixedfee'),
             (_('&Revenue'), _('Show/hide revenue column'), 'revenue'),
             (_('T&otal revenue'), _('Show/hide total revenue column'), 'totalrevenue'),
             (_('Last modification time'), _('Show/hide last modification time column'), 'lastmodificationtime'),
             (_('Overall last modification time'), _('Show/hide overall last modification time column (overall last modification time is the most recent modification time of a task and all it subtasks'), 'totallastmodificationtime'),
             (_('&Time spent'), _('Show/hide time spent column'), 'efforttimespent'),
             (_('T&otal time spent'), _('Show/hide total time spent column'), 'totalefforttimespent'),
             (_('&Revenue'), _('Show/hide revenue column'), 'effortrevenue'),
             (_('To&tal revenue'), _('Show/hide total revenue column'), 'totaleffortrevenue')]:
            key = 'view' + setting
            self[key] = UICheckCommand(menuText=menuText, helpText=helpText, setting=setting, settings=settings)
    
        self['viewalldatecolumns'] = UICheckGroupCommand(menuText=_('All date columns'), 
              helpText=_('Show/hide all date-related columns'), 
              uiCommandNames=['viewstartdate', 'viewduedate', 'viewtimeleft', 
              'viewcompletiondate'], uiCommands=self, settings=settings, 
              setting='alldatecolumns')
        self['viewallbudgetcolumns'] = UICheckGroupCommand(menuText=_('All budget columns'),
              helpText=_('Show/hide all budget-related columns'),
              uiCommandNames=['viewbudget', 'viewtotalbudget', 'viewtimespent', 
              'viewtotaltimespent', 'viewbudgetleft','viewtotalbudgetleft'],
              uiCommands=self, settings=settings, setting='allbudgetcolumns')
        self['viewallfinancialcolumns'] = UICheckGroupCommand(menuText=_('All financial columns'),
              helpText=_('Show/hide all finance-related columns'),
              uiCommandNames=['viewhourlyfee', 'viewfixedfee', 'viewtotalfixedfee', 
              'viewrevenue', 'viewtotalrevenue'],
              uiCommands=self, settings=settings, setting='allfinancialcolumns')
        self['hidecurrentcolumn'] = HideCurrentColumn(viewer=viewer)

              
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
             (_('&Hourly fee'), _('Sort tasks by hourly fee'), 'hourlyFee'),
             (_('&Fixed fee'), _('Sort tasks by fixed fee'), 'fixedFee'),
             (_('Total fi&xed fee'), _('Sort tasks by total fixed fee'), 'totalfixedFee'),
             (_('&Revenue'), _('Sort tasks by revenue'), 'revenue'),
             (_('Total re&venue'), _('Sort tasks by total revenue'), 'totalrevenue'),
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
                                                         
        self['viewstatusbar'] = UICheckCommand(settings=settings, 
            menuText=_('Status&bar'), helpText=_('Show/hide status bar'), 
            setting='statusbar')
        self['viewfiltersidebar'] = UICheckCommand(settings=settings,
            menuText=_('&Filter sidebar'), 
            helpText=_('Show/hide filter sidebar'),
            setting='filtersidebar')

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
            self[key] = UIRadioCommand(settings=settings, setting='tasksdue',
                value=value, menuText=menuText, helpText=helpText)
                                       
        # Task menu
        self['new'] = TaskNew(mainwindow=mainwindow, taskList=taskList, 
            uiCommands=self, settings=settings)
        self['newsubtask'] = TaskNewSubTask(mainwindow=mainwindow, 
            taskList=taskList, viewer=viewer, uiCommands=self, 
            settings=settings)
        self['edit'] = TaskEdit(mainwindow=mainwindow, taskList=taskList, 
            viewer=viewer, uiCommands=self, settings=settings)
        self['markcompleted'] = TaskMarkCompleted(taskList=taskList,
            viewer=viewer)
        self['delete'] = TaskDelete(taskList=taskList, viewer=viewer)
        self['mailtask'] = TaskMail(viewer=viewer, menuText=_('Mail task'), 
            helpText=_('Mail the task, using your default mailer'), 
            bitmap='email')
        self['addattachmenttotask'] = TaskAddAttachment(taskList=taskList,
                                                        viewer=viewer)
        # Task related, but not on any menu:
        self['draganddroptask'] = TaskDragAndDrop(taskList=taskList, 
                                                  viewer=viewer)

        # Effort menu
        self['neweffort'] = EffortNew(mainwindow=mainwindow, viewer=viewer,
            effortList=effortList, uiCommands=self, taskList=taskList)
        self['editeffort'] = EffortEdit(mainwindow=mainwindow, viewer=viewer,
            effortList=effortList, uiCommands=self, taskList=taskList)
        self['deleteeffort'] = EffortDelete(effortList=effortList, 
                                            viewer=viewer)
        self['starteffort'] = EffortStart(taskList=taskList, viewer=viewer)
        self['stopeffort'] = EffortStop(taskList=taskList)
        
        # Help menu
        self['help'] = Help()
        self['tips'] = Tips(settings=settings, mainwindow=mainwindow)
        self['about'] = HelpAbout()
        self['license'] = HelpLicense()

        # Taskbar menu
        self['restore'] = MainWindowRestore(mainwindow=mainwindow)

    def createRecentFileOpenUICommand(self, filename, index):
        return RecentFileOpen(filename=filename, index=index, 
            iocontroller=self.__iocontroller)

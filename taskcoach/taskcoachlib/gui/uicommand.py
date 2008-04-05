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

import wx, patterns, gui, meta, command, help, widgets, persistence
from i18n import _
from domain import task, attachment
from thirdparty import desktop
import urllib

''' User interface commands (subclasses of UICommand) are actions that can
    be invoked by the user via the user interface (menu's, toolbar, etc.).
    See the Taskmaster pattern described here: 
    http://www.objectmentor.com/resources/articles/taskmast.pdf 
'''


class UICommandContainer(object):
    ''' Mixin with wx.Menu or wx.ToolBar (sub)class. '''

    def appendUICommands(self, uiCommands, uiCommandNames):
        for commandName in uiCommandNames:
            if commandName is None:
                self.AppendSeparator()
                continue
            elif type(commandName) == type(()): # This only works for menu's
                menuTitle, menuUICommandNames = commandName[0], commandName[1:]
                self.appendSubMenuWithUICommands(uiCommands, menuTitle, 
                                                 menuUICommandNames)
                continue
            elif type(commandName) == type(''): # commandName can be a string or an actual UICommand
                commandName = uiCommands[commandName]
            self.appendUICommand(commandName)

    def appendSubMenuWithUICommands(self, uiCommands, menuTitle, uiCommandNames):
        subMenu = gui.menu.Menu(self._window)
        self.appendMenu(menuTitle, subMenu)
        subMenu.appendUICommands(uiCommands, uiCommandNames)
        

class UICommand(object):
    ''' Base user interface command. An UICommand is some action that can be 
        associated with menu's and/or toolbars. It contains the menutext and 
        helptext to be displayed, code to deal with wx.EVT_UPDATE_UI and 
        methods to attach the command to a menu or toolbar. Subclasses should 
        implement doCommand() and optionally override enabled(). '''
    
    def __init__(self, menuText='?', helpText='', bitmap='nobitmap', 
             kind=wx.ITEM_NORMAL, id=None, bitmap2=None, *args, **kwargs):
        super(UICommand, self).__init__(*args, **kwargs)
        self.menuText = menuText
        self.helpText = helpText
        self.bitmap = bitmap
        self.bitmap2 = bitmap2
        self.kind = kind
        self.id = id or wx.NewId()
        self.toolbar = None
        self.menuItems = [] # uiCommands can be used in multiple menu's

    def appendToMenu(self, menu, window, position=None):
        # FIXME: rename to addToMenu
        menuItem = wx.MenuItem(menu, self.id, self.menuText, self.helpText, 
            self.kind)
        self.menuItems.append(menuItem)
        if self.bitmap2 and self.kind == wx.ITEM_CHECK and not '__WXGTK__' in wx.PlatformInfo:
            bitmap1 = wx.ArtProvider_GetBitmap(self.bitmap, wx.ART_MENU, 
                (16, 16))
            bitmap2 = wx.ArtProvider_GetBitmap(self.bitmap2, wx.ART_MENU, 
                (16, 16))
            menuItem.SetBitmaps(bitmap1, bitmap2)
        elif self.bitmap and self.kind == wx.ITEM_NORMAL:
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
        self.toolbar = toolbar
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
            
    def __call__(self, *args, **kwargs):
        return self.onCommandActivate(*args, **kwargs)
        
    def doCommand(self, event):
        raise NotImplementedError

    def onUpdateUI(self, event):
        event.Enable(bool(self.enabled(event)))
        if self.toolbar and (not self.helpText or self.menuText == '?'):
            self.updateToolHelp()
        
    def enabled(self, event):
        ''' Can be overridden in a subclass. '''
        return True

    def updateToolHelp(self):
        shortHelp = wx.MenuItem.GetLabelFromText(self.getMenuText())
        if shortHelp != self.toolbar.GetToolShortHelp(self.id):
            self.toolbar.SetToolShortHelp(self.id, shortHelp)
        longHelp = self.getHelpText()
        if longHelp != self.toolbar.GetToolLongHelp(self.id):
            self.toolbar.SetToolLongHelp(self.id, longHelp)


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

    def appendToMenu(self, menu, window, position=None):
        id = super(BooleanSettingsCommand, self).appendToMenu(menu, window, position)
        menuItem = menu.FindItemById(id)
        menuItem.Check(self.isSettingChecked())
        

class UICheckCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        super(UICheckCommand, self).__init__(kind=wx.ITEM_CHECK, 
            bitmap=self.getBitmap(), *args, **kwargs)
        
    def isSettingChecked(self):
        return self.settings.getboolean(self.section, self.setting)

    def _isMenuItemChecked(self, event):
        # There's a bug in wxPython 2.8.3 on Windows XP that causes 
        # event.IsChecked() to return the wrong value in the context menu.
        # The menu on the main window works fine. So we first try to access the
        # context menu to get the checked state from the menu item itself.
        # This will fail if the event is coming from the window, but in that
        # case we can event.IsChecked() expect to work so we use that.
        try:
            return event.GetEventObject().FindItemById(event.GetId()).IsChecked()
        except AttributeError:
            return event.IsChecked()
        
    def doCommand(self, event):
        self.settings.set(self.section, self.setting, 
            str(self._isMenuItemChecked(event)))
        
    def getBitmap(self):
        # Using our own bitmap for checkable menu items does not work on
        # all platforms, most notably Gtk where providing our own bitmap causes
        # "(python:8569): Gtk-CRITICAL **: gtk_check_menu_item_set_active: 
        # assertion `GTK_IS_CHECK_MENU_ITEM (check_menu_item)' failed"
        return None


class UIRadioCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        super(UIRadioCommand, self).__init__(kind=wx.ITEM_RADIO, bitmap='', 
                                             *args, **kwargs)
        
    def onUpdateUI(self, event):
        if self.isSettingChecked():
            super(UIRadioCommand, self).onUpdateUI(event)

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


class CategoriesCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories', None)
        super(CategoriesCommand, self).__init__(*args, **kwargs)


class NotesCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.notes = kwargs.pop('notes', None)
        super(NotesCommand, self).__init__(*args, **kwargs)
        

class ViewerCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.viewer = kwargs.pop('viewer', None)
        super(ViewerCommand, self).__init__(*args, **kwargs)


class UICommandsCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.uiCommands = kwargs.pop('uiCommands', None)
        super(UICommandsCommand, self).__init__(*args, **kwargs)    


# Mixins: 

class NeedsSelection(object):
    def enabled(self, event):
        return super(NeedsSelection, self).enabled(event) and \
            self.viewer.curselection()

class NeedsTaskViewer(object):
    def enabled(self, event):
        return super(NeedsTaskViewer, self).enabled(event) and \
            self.viewer.isShowingTasks()

class NeedsEffortViewer(object):
    def enabled(self, event):
        return super(NeedsEffortViewer, self).enabled(event) and \
            self.viewer.isShowingEffort()

class NeedsCategoryViewer(object):
    def enabled(self, event):
        return super(NeedsCategoryViewer, self).enabled(event) and \
            self.viewer.isShowingCategories()

class NeedsNoteViewer(object):
    def enabled(self, event):
        return super(NeedsNoteViewer, self).enabled(event) and \
            self.viewer.isShowingNotes()
            
class NeedsSelectedTasks(NeedsTaskViewer, NeedsSelection):
    pass

class NeedsSelectedTasksWithAttachments(NeedsSelectedTasks):
    def enabled(self, event):
        return super(NeedsSelectedTasksWithAttachments, self).enabled(event) and \
            bool([task for task in self.viewer.curselection() if task.attachments()])

class NeedsSelectedEffort(NeedsEffortViewer, NeedsSelection):
    pass

class NeedsSelectedCategory(NeedsCategoryViewer, NeedsSelection):
    pass

class NeedsSelectedNote(NeedsNoteViewer, NeedsSelection):
    pass

class NeedsAtLeastOneTask(object):
    def enabled(self, event):
        return len(self.taskList) > 0
        
class NeedsItems(object):
    def enabled(self, event):
        return self.viewer.size() 

class NeedsTreeViewer(object):
    def enabled(self, event):
        return super(NeedsTreeViewer, self).enabled(event) and \
            self.viewer.isTreeViewer()
            
class NeedsListViewer(object):
    def enabled(self, event):
        return super(NeedsListViewer, self).enabled(event) and \
            (not self.viewer.isTreeViewer())

class DisableWhenTextCtrlHasFocus(object):
    def enabled(self, event):
        if isinstance(wx.Window.FindFocus(), wx.TextCtrl):
            return False
        else:
            return super(DisableWhenTextCtrlHasFocus, self).enabled(event)

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
        super(FileClose, self).__init__(menuText=_('&Close\tCtrl+W'),
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
        super(FileSaveAs, self).__init__(menuText=_('S&ave as...\tShift+Ctrl+S'),
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

class Printout(wx.html.HtmlPrintout):
    def __init__(self, viewer, printSelectionOnly=False, *args, **kwargs):
        super(Printout, self).__init__(*args, **kwargs)
        htmlText = persistence.viewer2html(viewer, 
                                           selectionOnly=printSelectionOnly)
        self.SetHtmlText(htmlText)
        self.SetFooter(_('Page') + ' @PAGENUM@/@PAGESCNT@', wx.html.PAGE_ALL)
        self.SetFonts('Arial', 'Courier')
        global printerSettings
        top, left = printerSettings.pageSetupData.GetMarginTopLeft()
        bottom, right = printerSettings.pageSetupData.GetMarginBottomRight()
        self.SetMargins(top, bottom, left, right)

                
class PrintPageSetup(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(PrintPageSetup, self).__init__(\
            menuText=_('Page setup...\tShift+Ctrl+P'), 
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
        printout = Printout(self.viewer)
        printout2 = Printout(self.viewer)
        preview = wx.PrintPreview(printout, printout2, 
            printerSettings.printData)
        previewFrame = wx.PreviewFrame(preview, self.mainwindow, 
            _('Print preview'), size=(750, 700))
        previewFrame.Initialize()
        previewFrame.Show()
        

class Print(ViewerCommand, MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(Print, self).__init__(\
            menuText=_('Print...\tCtrl+P'), 
            helpText=_('Print the current file'), 
            bitmap='print', id=wx.ID_PRINT, *args, **kwargs)

    def doCommand(self, event):
        global printerSettings 
        printDialogData = wx.PrintDialogData(printerSettings.printData)
        printDialogData.EnableSelection(True)
        printer = wx.Printer(printDialogData)
        if not printer.PrintDialog(self.mainwindow):
            return
        printout = Printout(self.viewer, 
            printSelectionOnly=printer.PrintDialogData.Selection)
        # If the user checks the selection radio button, the ToPage property 
        # gets set to 1. Looks like a bug to me. The simple work-around is to
        # reset the ToPage property to the MaxPage value if necessary:
        if printer.PrintDialogData.Selection:
            printer.PrintDialogData.ToPage = printer.PrintDialogData.MaxPage
        printer.Print(self.mainwindow, printout, prompt=False)
 

class FileExportAsICS(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileExportAsICS, self).__init__(\
            menuText=_('Export effort as &iCalendar...'), 
            helpText=_('Export effort in iCalendar (*.ics) format'),
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


class FileExportAsCSV(IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileExportAsCSV, self).__init__(menuText=_('Export as &CSV...'),
            helpText=_('Export the current view in Comma Separated Values (CSV) format'),
            bitmap='exportascsv', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.exportAsCSV(self.viewer)
        
        
class FileQuit(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(FileQuit, self).__init__(menuText=_('&Quit\tCtrl+Q'), 
            helpText=_('Exit %s')%meta.name, bitmap='exit', 
            id=wx.ID_EXIT, *args, **kwargs)

    def doCommand(self, event):
        self.mainwindow.Close(force=True)


def getUndoMenuText():
    return '%s\tCtrl+Z'%patterns.CommandHistory().undostr(_('&Undo')) 

class EditUndo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditUndo, self).__init__(menuText=getUndoMenuText(),
            helpText=_('Undo the last command'), bitmap='undo',
            id=wx.ID_UNDO, *args, **kwargs)
            
    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Undo()
        else:
            patterns.CommandHistory().undo()

    def onUpdateUI(self, event):
        event.SetText(getUndoMenuText())
        super(EditUndo, self).onUpdateUI(event)

    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            return windowWithFocus.CanUndo()
        else:
            return patterns.CommandHistory().hasHistory() and \
                super(EditUndo, self).enabled(event)


def getRedoMenuText():
    return '%s\tCtrl+Y'%patterns.CommandHistory().redostr(_('&Redo')) 

class EditRedo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditRedo, self).__init__(menuText=getRedoMenuText(),
            helpText=_('Redo the last command that was undone'), bitmap='redo',
            id=wx.ID_REDO, *args, **kwargs)

    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Redo()
        else:
            patterns.CommandHistory().redo()

    def onUpdateUI(self, event):
        event.SetText(getRedoMenuText())
        super(EditRedo, self).onUpdateUI(event)

    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            return windowWithFocus.CanRedo()
        else:
            return patterns.CommandHistory().hasFuture() and \
                super(EditRedo, self).enabled(event)


class EditCut(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):        
        super(EditCut, self).__init__(menuText=_('Cu&t\tCtrl+X'), 
            helpText=_('Cut the selected item(s) to the clipboard'), 
            bitmap='cut', id=wx.ID_CUT, *args, **kwargs)

    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Cut()
        else:
            cutCommand = command.CutCommand(self.viewer.model(),
                                            self.viewer.curselection())
            cutCommand.do()

    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            return windowWithFocus.CanCut()
        else:
            return super(EditCut, self).enabled(event)


class EditCopy(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditCopy, self).__init__(menuText=_('&Copy\tCtrl+C'), 
            helpText=_('Copy the selected item(s) to the clipboard'), 
            bitmap='copy', id=wx.ID_COPY, *args, **kwargs)

    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Copy()
        else:
            copyCommand = command.CopyCommand(self.viewer.model(), 
                                              self.viewer.curselection())
            copyCommand.do()

    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            return windowWithFocus.CanCopy()
        else:
            return super(EditCopy, self).enabled(event)
        

class EditPaste(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditPaste, self).__init__(menuText=_('&Paste\tCtrl+V'), 
            helpText=_('Paste item(s) from the clipboard'), bitmap='paste', 
            id=wx.ID_PASTE, *args, **kwargs)

    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Paste()
        else:
            pasteCommand = command.PasteCommand()
            pasteCommand.do()
    
    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            return windowWithFocus.CanPaste()
        else:
            return task.Clipboard() and super(EditPaste, self).enabled(event)


class EditPasteIntoTask(NeedsSelectedTasks, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditPasteIntoTask, self).__init__(menuText=_('P&aste into task\tShift+Ctrl+V'), 
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
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.SetSelection(-1, -1) # Select all text
        else:
            self.viewer.selectall()


class InvertSelection(NeedsItems, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(InvertSelection, self).__init__( \
            menuText=_('&Invert selection'),
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


class ResetFilter(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ResetFilter, self).__init__(menuText=_('&Clear all filters'),
            helpText=_('Show all items (reset all filters)'), 
            bitmap='viewalltasks', *args, **kwargs)
    
    def doCommand(self, event):
        self.viewer.resetFilter()


class ViewViewer(SettingsCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        self.viewerClass = kwargs['viewerClass']
        self.viewerArgs = kwargs['viewerArgs']
        self.viewerKwargs = kwargs.get('viewerKwargs', {})
        self.viewerBitmap = kwargs['viewerBitmap']
        super(ViewViewer, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        self.viewer.Freeze()
        newViewer = self.viewerClass(self.viewer.containerWidget, 
                                     *self.viewerArgs, **self.viewerKwargs)
        self.viewer.addViewer(newViewer, newViewer.title(), self.viewerBitmap)
        setting = self.viewerClass.__name__.lower() + 'count'
        viewerCount = self.settings.getint('view', setting)
        self.settings.set('view', setting, str(viewerCount+1))
        self.viewer.Thaw()
        

class RenameViewer(SettingsCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(RenameViewer, self).__init__(menuText=_('&Rename viewer...'),
            helpText=_('Rename the selected viewer'), *args, **kwargs)
        
    def doCommand(self, event):
        dialog = wx.TextEntryDialog(wx.GetApp().TopWindow, 
            _('New title for the viewer:'), _('Rename viewer'), 
            self.viewer.title())
        if dialog.ShowModal() == wx.ID_OK:
            self.viewer.setTitle(dialog.GetValue())
        dialog.Destroy()
        
        
class ActivateViewer(ViewerCommand):
    def __init__(self, *args, **kwargs):
        self.direction = kwargs.pop('forward')
        super(ActivateViewer, self).__init__(*args, **kwargs)

    def doCommand(self, event):
        self.viewer.containerWidget.AdvanceSelection(self.direction)
        
    def enabled(self, event):
        return self.viewer.containerWidget.PageCount > 1
        

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
        # Use wx.Point because CustomTreeCtrl assumes a wx.Point instance:
        item, flag, columnIndex = widget.HitTest(wx.Point(x, y), 
                                                 alwaysReturnColumn=True)
        # The TreeListCtrl returns -1 for the first column sometimes,
        # don't understand why. Work around as follows:
        if columnIndex == -1:
            columnIndex = 0
        return self.viewer.isHideableColumn(columnIndex)


class ViewColumn(ViewerCommand, UICheckCommand):
    def isSettingChecked(self):
        return self.viewer.isVisibleColumnByName(self.setting)
    
    def doCommand(self, event):
        self.viewer.showColumnByName(self.setting, self._isMenuItemChecked(event))


class ViewColumns(ViewerCommand, UICheckCommand):
    def isSettingChecked(self):
        for columnName in self.setting:
            if not self.viewer.isVisibleColumnByName(columnName):
                return False
        return True
    
    def doCommand(self, event):
        show = self._isMenuItemChecked(event)
        for columnName in self.setting:
            self.viewer.showColumnByName(columnName, show)
                        
    
class ViewExpandAll(NeedsTreeViewer, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewExpandAll, self).__init__( \
            menuText=_('&Expand all items\tShift+Ctrl+E'),
            helpText=_('Expand all items with subitems'), *args, **kwargs)

    def enabled(self, event):
        return super(ViewExpandAll, self).enabled(event) and \
            self.viewer.isAnyItemExpandable()
                
    def doCommand(self, event):
        self.viewer.expandAll()


class ViewExpandSelected(NeedsSelection, NeedsTreeViewer, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewExpandSelected, self).__init__(bitmap='viewexpand',
            menuText=_('E&xpand'), helpText=_('Expand the selected item(s)'),
            *args, **kwargs)
    
    def enabled(self, event):
        return super(ViewExpandSelected, self).enabled(event) and \
            self.viewer.isSelectionExpandable()
                
    def doCommand(self, event):
        self.viewer.expandSelectedItems()
            

class ViewCollapseAll(NeedsTreeViewer, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCollapseAll, self).__init__( \
            menuText=_('&Collapse all items\tShift+Ctrl+C'),
            helpText=_('Collapse all items with subitems'), *args, **kwargs)
    
    def enabled(self, event):
        return super(ViewCollapseAll, self).enabled(event) and \
            self.viewer.isAnyItemCollapsable()
    
    def doCommand(self, event):
        self.viewer.collapseAll()
        

class ViewCollapseSelected(NeedsTreeViewer, NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCollapseSelected, self).__init__(bitmap='viewcollapse',
            menuText=_('C&ollapse'),
            helpText=_('Collapse the selected items with subitems'), 
            *args, **kwargs)

    def enabled(self, event):
        return super(ViewCollapseSelected, self).enabled(event) and \
            self.viewer.isSelectionCollapsable()
    
    def doCommand(self, event):
        self.viewer.collapseSelectedItems()


class ViewerSortByCommand(ViewerCommand, UIRadioCommand):        
    def isSettingChecked(self):
        return self.viewer.isSortedBy(self.value)
    
    def doCommand(self, event):
        self.viewer.sortBy(self.value)


class ViewerSortOrderCommand(ViewerCommand, UICheckCommand):
    def isSettingChecked(self):
        return self.viewer.isSortOrderAscending()
    
    def doCommand(self, event):
        self.viewer.setSortOrderAscending(self._isMenuItemChecked(event))
    
    
class ViewerSortCaseSensitive(ViewerCommand, UICheckCommand):
    def isSettingChecked(self):
        return self.viewer.isSortCaseSensitive()
    
    def doCommand(self, event):
        self.viewer.setSortCaseSensitive(self._isMenuItemChecked(event))


class ViewerSortByTaskStatusFirst(ViewerCommand, UICheckCommand):
    def isSettingChecked(self):
        return self.viewer.isSortByTaskStatusFirst()
    
    def doCommand(self, event):
        self.viewer.setSortByTaskStatusFirst(self._isMenuItemChecked(event))


class ViewerFilterByDueDate(ViewerCommand, UIRadioCommand):
    def isSettingChecked(self):
        return self.viewer.isFilteredByDueDate(self.value)
    
    def doCommand(self, event):
        self.viewer.setFilteredByDueDate(self.value)


class ViewerHideActiveTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideActiveTasks, self).__init__(menuText=_('&Active'), 
            helpText=_('Show/hide active tasks (tasks with a start date in the past and a due date in the future)'),
            *args, **kwargs)
        
    def isSettingChecked(self):
        return self.viewer.isHidingActiveTasks()
        
    def doCommand(self, event):
        self.viewer.hideActiveTasks(self._isMenuItemChecked(event))


class ViewerHideInactiveTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideInactiveTasks, self).__init__(menuText=_('&Inactive'), 
            helpText=_('Show/hide inactive tasks (tasks with a start date in the future)'),
            *args, **kwargs)
        
    def isSettingChecked(self):
        return self.viewer.isHidingInactiveTasks()
        
    def doCommand(self, event):
        self.viewer.hideInactiveTasks(self._isMenuItemChecked(event))

        
class ViewerHideCompletedTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideCompletedTasks, self).__init__(menuText=_('&Completed'), 
            helpText=_('Show/hide completed tasks'), *args, **kwargs)
         
    def isSettingChecked(self):
        return self.viewer.isHidingCompletedTasks()
        
    def doCommand(self, event):
        self.viewer.hideCompletedTasks(self._isMenuItemChecked(event))


class ViewerHideOverdueTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideOverdueTasks, self).__init__(menuText=_('&Over due'), 
            helpText=_('Show/hide over due tasks (tasks with a due date in the past)'),
            *args, **kwargs)

    def isSettingChecked(self):
        return self.viewer.isHidingOverdueTasks()
        
    def doCommand(self, event):
        self.viewer.hideOverdueTasks(self._isMenuItemChecked(event))


class ViewerHideOverbudgetTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideOverbudgetTasks, self).__init__(menuText=_('Over &budget'), 
            helpText=_('Show/hide tasks that are over budget'),
            *args, **kwargs)
        
    def isSettingChecked(self):
        return self.viewer.isHidingOverbudgetTasks()
        
    def doCommand(self, event):
        self.viewer.hideOverbudgetTasks(self._isMenuItemChecked(event))


class ViewerHideCompositeTasks(ViewerCommand, NeedsListViewer, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideCompositeTasks, self).__init__(menuText=_('Hide tasks &with subtasks'),
            helpText=_('Show/hide tasks with subtasks'), *args, **kwargs)
            
    def isSettingChecked(self):
        return self.viewer.isHidingCompositeTasks()
        
    def doCommand(self, event):
        self.viewer.hideCompositeTasks(self._isMenuItemChecked(event))


class NewDomainObject(ViewerCommand, TaskListCommand):
    def __init__(self, *args, **kwargs):
        super(NewDomainObject, self).__init__(menuText=_('New item'),
            bitmap='new', *args, **kwargs)
        
    def doCommand(self, event, show=True):
        dialog = self.viewer.newItemDialog(bitmap=self.bitmap)
        dialog.Show(show)
        
    def enabled(self, event):
        if self.viewer.isShowingEffort():
            enabled = len(self.taskList) > 0
        else:
            enabled = True
        return enabled and super(NewDomainObject, self).enabled(event)
    
    def getHelpText(self):
        return self.viewer.model().newItemHelpText
    
    def getMenuText(self):
        return self.viewer.model().newItemMenuText
    

class NewSubDomainObject(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(NewSubDomainObject, self).__init__(menuText=_('New subitem'),
            bitmap='newsub', *args, **kwargs)
        
    def doCommand(self, event, show=True):
        dialog = self.viewer.newSubItemDialog(bitmap=self.bitmap)
        dialog.Show(show)

    def enabled(self, event):
        return not self.viewer.isShowingEffort() and \
            super(NewSubDomainObject, self).enabled(event)
            
    def getHelpText(self):
        return self.viewer.model().newSubItemHelpText
    
    def getMenuText(self):
        return self.viewer.model().newSubItemMenuText
     

class EditDomainObject(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditDomainObject, self).__init__(menuText=('Edit item'),
            bitmap='edit', *args, **kwargs)
        
    def doCommand(self, event, show=True):
        dialog = self.viewer.editItemDialog(bitmap=self.bitmap)
        dialog.Show(show)

    def getHelpText(self):
        return self.viewer.model().editItemHelpText
    
    def getMenuText(self):
        return self.viewer.model().editItemMenuText


class DeleteDomainObject(NeedsSelection, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(DeleteDomainObject, self).__init__(menuText=_('Delete item'),
            bitmap='delete', *args, **kwargs)
        
    def doCommand(self, event):
        deleteCommand = self.viewer.deleteItemCommand()
        deleteCommand.do()

    def getHelpText(self):
        return self.viewer.model().deleteItemHelpText
    
    def getMenuText(self):
        return self.viewer.model().deleteItemMenuText

        
class TaskNew(TaskListCommand, CategoriesCommand, SettingsCommand, 
              UICommandsCommand, MainWindowCommand):
    def __init__(self, *args, **kwargs):
        taskList = kwargs['taskList']
        super(TaskNew, self).__init__(bitmap='new', 
            menuText=taskList.newItemMenuText, 
            helpText=taskList.newItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        newTaskDialog = gui.dialog.editor.TaskEditor(self.mainwindow, 
            command.NewTaskCommand(self.taskList, 
            categories=self.categoriesForTheNewTask()), 
            self.taskList, self.uiCommands, self.settings, self.categories, 
            bitmap=self.bitmap)
        newTaskDialog.Show(show)
        return newTaskDialog # for testing purposes

    def categoriesForTheNewTask(self):
        return [category for category in self.categories if category.isFiltered()]


class NewTaskWithSelectedCategories(TaskNew, ViewerCommand):
    def categoriesForTheNewTask(self):
        return self.viewer.curselection()
    

class TaskNewSubTask(NeedsSelectedTasks,  TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        taskList = kwargs['taskList']
        super(TaskNewSubTask, self).__init__(bitmap='newsub',
            menuText=taskList.newSubItemMenuText,
            helpText=taskList.newSubItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        dialog = self.viewer.newSubTaskDialog(bitmap=self.bitmap)
        dialog.Show(show)
        

class TaskEdit(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        taskList = kwargs['taskList']
        super(TaskEdit, self).__init__(bitmap='edit',
            menuText=taskList.editItemMenuText, 
            helpText=taskList.editItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        editor = self.viewer.editTaskDialog(bitmap=self.bitmap)
        editor.Show(show)


class TaskDelete(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        taskList = kwargs['taskList']
        super(TaskDelete, self).__init__(bitmap='delete',
            menuText=taskList.deleteItemMenuText,
            helpText=taskList.deleteItemHelpText, *args, **kwargs)

    def doCommand(self, event):
        deleteCommand = self.viewer.deleteTaskCommand()
        deleteCommand.do()


class TaskToggleCompletion(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    defaultMenuText = _('&Mark task completed\tCtrl+RETURN')
    defaultHelpText = _('Mark the selected task(s) completed')
    
    def __init__(self, *args, **kwargs):
        super(TaskToggleCompletion, self).__init__(bitmap='markuncompleted',
            bitmap2='markcompleted', menuText=self.defaultMenuText,
            helpText=self.defaultHelpText,
            kind=wx.ITEM_CHECK, *args, **kwargs)
        self.currentBitmap = self.bitmap
        
    def doCommand(self, event):
        markCompletedCommand = command.MarkCompletedCommand( \
            self.taskList, self.viewer.curselection())
        markCompletedCommand.do()

    def enabled(self, event):
        return super(TaskToggleCompletion, self).enabled(event) and \
            self.allSelectedTasksHaveSameCompletionState()
            
    def onUpdateUI(self, event):
        super(TaskToggleCompletion, self).onUpdateUI(event)
        allSelectedTasksAreCompleted = self.allSelectedTasksAreCompleted()
        self.updateToolState(allSelectedTasksAreCompleted)
        if allSelectedTasksAreCompleted:
            bitmapName = self.bitmap
        else:
            bitmapName = self.bitmap2
        if bitmapName != self.currentBitmap:
            self.currentBitmap = bitmapName
            self.updateToolBitmap(bitmapName)
            self.updateToolHelp()     
            self.updateMenuItems(allSelectedTasksAreCompleted)
    
    def updateToolState(self, allSelectedTasksAreCompleted):
        if not self.toolbar: return # Toolbar is hidden        
        if allSelectedTasksAreCompleted != self.toolbar.GetToolState(self.id): 
            self.toolbar.ToggleTool(self.id, allSelectedTasksAreCompleted)

    def updateToolBitmap(self, bitmapName):
        if not self.toolbar: return # Toolbar is hidden
        bitmap = wx.ArtProvider_GetBitmap(bitmapName, wx.ART_TOOLBAR, 
                                          self.toolbar.GetToolBitmapSize())
        # On wxGTK, changing the bitmap doesn't work when the tool is 
        # disabled, so we first enable it if necessary:
        disable = False
        if not self.toolbar.GetToolEnabled(self.id):
            self.toolbar.EnableTool(self.id, True)
            disable = True
        self.toolbar.SetToolNormalBitmap(self.id, bitmap)
        if disable:
            self.toolbar.EnableTool(self.id, False)     
    
    def updateMenuItems(self, allSelectedTasksAreCompleted):
        menuText = self.getMenuText()
        helpText = self.getHelpText()
        for menuItem in self.menuItems:
            menuItem.Check(allSelectedTasksAreCompleted)
            menuItem.SetItemLabel(menuText)
            menuItem.SetHelp(helpText)
        
    def getMenuText(self):
        if self.allSelectedTasksAreCompleted():
            return _('&Mark task uncompleted\tCtrl+RETURN')
        else:
            return self.defaultMenuText
        
    def getHelpText(self):
        if self.allSelectedTasksAreCompleted():
            return _('Mark the selected task(s) uncompleted')
        else:
            return self.defaultHelpText
        
    def allSelectedTasksAreCompleted(self):
        if self.viewer.isShowingTasks() and self.viewer.curselection():
            for task in self.viewer.curselection():
                if not task.completed():
                    return False
            return True
        else:
            return False
    
    def allSelectedTasksHaveSameCompletionState(self):
        selectedTasks = self.viewer.curselection()
        nrCompleted = len([task for task in selectedTasks if task.completed()])
        return nrCompleted in (0, len(selectedTasks))
    
    
class TaskMaxPriority(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMaxPriority, self).__init__(
            menuText=_('Maximize priority\tShift+Ctrl+I'),
            helpText=_('Make the selected task(s) the highest priority task(s)'), 
            bitmap='maxpriority', *args, **kwargs)
        
    def doCommand(self, event):
        maxPriority = command.MaxPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        maxPriority.do()
    

class TaskMinPriority(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMinPriority, self).__init__(
            menuText=_('Minimize priority\tShift+Ctrl+D'),
            helpText=_('Make the selected task(s) the lowest priority task(s)'), 
            bitmap='minpriority', *args, **kwargs)
        
    def doCommand(self, event):
        minPriority = command.MinPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        minPriority.do()


class TaskIncPriority(NeedsSelectedTasks, TaskListCommand, ViewerCommand):    
    def __init__(self, *args, **kwargs):
        super(TaskIncPriority, self).__init__(
            menuText=_('Increase priority\tCtrl+I'),
            helpText=_('Increase the priority of the selected task(s)'), 
            bitmap='incpriority', *args, **kwargs)
        
    def doCommand(self, event):
        incPriority = command.IncPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        incPriority.do()


class TaskDecPriority(NeedsSelectedTasks, TaskListCommand, ViewerCommand):    
    def __init__(self, *args, **kwargs):
        super(TaskDecPriority, self).__init__(
            menuText=_('Decrease priority\tCtrl+D'),
            helpText=_('Decrease the priority of the selected task(s)'), 
            bitmap='decpriority', *args, **kwargs)
        
    def doCommand(self, event):
        decPriority = command.DecPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        decPriority.do()


class DragAndDropCommand(ViewerCommand):
    def onCommandActivate(self, dropItemIndex, dragItemIndex):
        ''' Override omCommandActivate to be able to accept two items instead
            of one event. '''
        self.doCommand(dropItemIndex, dragItemIndex)

    def doCommand(self, dropItemIndex, dragItemIndex):
        dragItem = [self.viewer.getItemWithIndex(dragItemIndex)]
        if dropItemIndex >= 0:
            dropItem = [self.viewer.getItemWithIndex(dropItemIndex)]
        else:
            dropItem = None
        dragAndDropCommand = self.createCommand(dragItem, dropItem)
        if dragAndDropCommand.canDo():
            dragAndDropCommand.do()


class TaskDragAndDrop(TaskListCommand, DragAndDropCommand):
    def createCommand(self, dragItem, dropItem):
        return command.DragAndDropTaskCommand(self.taskList, dragItem, 
                                              drop=dropItem)


class TaskMail(NeedsSelectedTasks, ViewerCommand):
    def doCommand(self, event):
        tasks = self.viewer.curselection()
        if len(tasks) > 1:
            subject = _('Tasks')
            bodyLines = []
            for task in tasks:
                bodyLines.append(task.subject(recursive=True) + '\n')
                if task.description():
                    bodyLines.extend(task.description().splitlines())
                    bodyLines.append('\n')
        else:
            subject = tasks[0].subject(recursive=True)
            bodyLines = tasks[0].description().splitlines()
        body = urllib.quote('\r\n'.join(bodyLines))
        mailToURL = 'mailto:%s?subject=%s&body=%s'%( \
            _('Please enter recipient'), subject, body)
        desktop.open(mailToURL)


class TaskAddAttachment(NeedsSelectedTasks, TaskListCommand, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskAddAttachment, self).__init__(menuText=_('&Add attachment'),
            helpText=_('Browse for files to add as attachment to the selected task(s)'),
            bitmap='attachment', *args, **kwargs)
        
    def doCommand(self, event):
        filename = widgets.AttachmentSelector()
        if filename:
            base = self.settings.get('file', 'attachmentbase')
            if base:
                filename = attachment.getRelativePath(filename, base)

            addAttachmentCommand = command.AddAttachmentToTaskCommand( \
                self.taskList, self.viewer.curselection(), 
                attachments=[attachment.FileAttachment(filename)])
            addAttachmentCommand.do()


class TaskOpenAllAttachments(NeedsSelectedTasksWithAttachments, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskOpenAllAttachments, self).__init__(menuText=_('&Open all attachments'),
           helpText=_('Open all attachments of the selected task(s)'),
           bitmap='attachment', *args, **kwargs)
        
    def doCommand(self, event):
        base = self.settings.get('file', 'attachmentbase')
        for task in self.viewer.curselection():
            for attachment in task.attachments():
                try:    
                    attachment.open(base)
                except Exception, instance:
                    showerror(str(instance), 
                        caption=_('Error opening attachment'), style=wx.ICON_ERROR)


class EffortNew(NeedsAtLeastOneTask, ViewerCommand, EffortListCommand, 
                TaskListCommand, MainWindowCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        effortList = kwargs['effortList']
        super(EffortNew, self).__init__(bitmap='new',  
            menuText=effortList.newItemMenuText, 
            helpText=effortList.newItemHelpText, *args, **kwargs)
            
    def doCommand(self, event):
        if self.viewer.isShowingTasks() and self.viewer.curselection():
            selectedTasks = self.viewer.curselection()
        else:
            subjectDecoratedTaskList = [(task.subject(recursive=True), 
                task) for task in self.taskList]
            subjectDecoratedTaskList.sort() # Sort by subject
            selectedTasks = [subjectDecoratedTaskList[0][1]]

        newEffortDialog = gui.dialog.editor.EffortEditor(self.mainwindow, 
            command.NewEffortCommand(self.effortList, selectedTasks),
            self.uiCommands, self.effortList, self.taskList, bitmap=self.bitmap)
        newEffortDialog.Show()


class EffortEdit(NeedsSelectedEffort, EffortListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        effortList = kwargs['effortList']
        super(EffortEdit, self).__init__(bitmap='edit',
            menuText=effortList.editItemMenuText,
            helpText=effortList.editItemHelpText, *args, **kwargs)
            
    def doCommand(self, event):
        dialog = self.viewer.editEffortDialog(bitmap=self.bitmap)
        dialog.Show()


class EffortDelete(NeedsSelectedEffort, EffortListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        effortList = kwargs['effortList']
        super(EffortDelete, self).__init__(bitmap='delete',
            menuText=effortList.deleteItemMenuText,
            helpText=effortList.deleteItemHelpText, *args, **kwargs)

    def doCommand(self, event):
        delete = self.viewer.deleteEffortCommand()
        delete.do()


class EffortStart(NeedsSelectedTasks, TaskListCommand, ViewerCommand):
    ''' UICommand to start tracking effort for the selected task(s). '''
    
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


class EffortStartForTask(TaskListCommand):
    ''' UICommand to start tracking for a specific task. This command can
        be used to build a menu with seperate menu items for all tasks. 
        See gui.menu.StartEffortForTaskMenu. '''
        
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task')
        subject = self.task.subject()
        super(EffortStartForTask, self).__init__( \
            bitmap=gui.render.taskBitmapNames(self.task)[0], menuText=subject,
            helpText=_('Start tracking effort for %s')%subject, 
            *args, **kwargs)
        
    def doCommand(self, event):
        start = command.StartEffortCommand(self.taskList, [self.task])
        start.do()
        
    def enabled(self, event):
        return not self.task.isBeingTracked() and not self.task.completed()      
        

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
        # FIXME: when support for python 2.4 is dropped use:
        # return any(True for task in self.taskList if task.isBeingTracked())
        return True in (True for task in self.taskList if task.isBeingTracked())


class CategoryNew(MainWindowCommand, CategoriesCommand, UICommandsCommand):
    def __init__(self, *args, **kwargs):
        categories = kwargs['categories']
        super(CategoryNew, self).__init__(bitmap='new', 
            menuText=categories.newItemMenuText,
            helpText=categories.newItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        newCategoryDialog = gui.dialog.editor.CategoryEditor(self.mainwindow, 
            command.NewCategoryCommand(self.categories),
            self.categories, self.uiCommands, bitmap=self.bitmap)
        newCategoryDialog.Show(show)
        

class CategoryNewSubCategory(NeedsSelectedCategory, CategoriesCommand, 
                             ViewerCommand):
    def __init__(self, *args, **kwargs):
        categories = kwargs['categories']
        super(CategoryNewSubCategory, self).__init__(bitmap='newsub', 
            menuText=categories.newSubItemMenuText, 
            helpText=categories.newSubItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        dialog = self.viewer.newSubCategoryDialog(bitmap=self.bitmap)
        dialog.Show(show)


class CategoryDelete(NeedsSelectedCategory, CategoriesCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        categories = kwargs['categories']
        super(CategoryDelete, self).__init__(bitmap='delete',
            menuText=categories.deleteItemMenuText, 
            helpText=categories.deleteItemHelpText, *args, **kwargs)
        
    def doCommand(self, event):
        delete = self.viewer.deleteCategoryCommand()
        delete.do()


class CategoryEdit(NeedsSelectedCategory, ViewerCommand, CategoriesCommand):
    def __init__(self, *args, **kwargs):
        categories = kwargs['categories']
        super(CategoryEdit, self).__init__(bitmap='edit',
            menuText=categories.editItemMenuText,
            helpText=categories.editItemHelpText, *args, **kwargs)
        
    def doCommand(self, event, show=True):
        dialog = self.viewer.editCategoryDialog(bitmap=self.bitmap)
        dialog.Show(show)


class CategoryDragAndDrop(CategoriesCommand, DragAndDropCommand):
    def createCommand(self, dragItem, dropItem):
        return command.DragAndDropCategoryCommand(self.categories, dragItem, 
                                                  drop=dropItem)


class NoteNew(NotesCommand, MainWindowCommand, CategoriesCommand):
    def __init__(self, *args, **kwargs):
        notes = kwargs['notes']
        super(NoteNew, self).__init__(bitmap='new', 
            menuText=notes.newItemMenuText,
            helpText=notes.newItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        filteredCategories = [category for category in self.categories if
                             category.isFiltered()]    
        dialog = gui.dialog.editor.NoteEditor(self.mainwindow, 
            command.NewNoteCommand(self.notes, categories=filteredCategories),
            self.categories, bitmap=self.bitmap)
        dialog.Show(show)
        return dialog # for testing purposes
    

class NoteNewSubNote(NeedsSelectedNote, NotesCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        notes = kwargs['notes']
        super(NoteNewSubNote, self).__init__(bitmap='newsub', 
            menuText=notes.newSubItemMenuText, 
            helpText=notes.newSubItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        dialog = self.viewer.newSubNoteDialog(bitmap=self.bitmap)
        dialog.Show(show)


class NoteDelete(NeedsSelectedNote, NotesCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        notes = kwargs['notes']
        super(NoteDelete, self).__init__(bitmap='delete',
            menuText=notes.deleteItemMenuText, 
            helpText=notes.deleteItemHelpText, *args, **kwargs)
        
    def doCommand(self, event):
        delete = self.viewer.deleteNoteCommand()
        delete.do()


class NoteEdit(NeedsSelectedNote, ViewerCommand, NotesCommand):
    def __init__(self, *args, **kwargs):
        notes = kwargs['notes']
        super(NoteEdit, self).__init__(bitmap='edit',
            menuText=notes.editItemMenuText,
            helpText=notes.editItemHelpText, *args, **kwargs)
        
    def doCommand(self, event, show=True):
        dialog = self.viewer.editNoteDialog(bitmap=self.bitmap)
        dialog.Show(show)


class NoteDragAndDrop(NotesCommand, DragAndDropCommand):
    def createCommand(self, dragItem, dropItem):
        return command.DragAndDropNoteCommand(self.notes, dragItem, 
                                                  drop=dropItem)
                         
                                                        
class DialogCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self._dialogTitle = kwargs.pop('dialogTitle')
        self._dialogText = kwargs.pop('dialogText')
        self._direction = kwargs.pop('direction', None)
        self.closed = True
        super(DialogCommand, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        self.closed = False
        self.dialog = widgets.HTMLDialog(self._dialogTitle, self._dialogText, 
                                    bitmap=self.bitmap, 
                                    direction=self._direction)
        for event in wx.EVT_CLOSE, wx.EVT_BUTTON:
            self.dialog.Bind(event, self.onClose)
        self.dialog.Show()
        
    def onClose(self, event):
        self.closed = True
        self.dialog.Destroy()
        event.Skip()
        
    def enabled(self, event):
        return self.closed

        
class Help(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(Help, self).__init__(menuText=_('&Help contents\tCtrl+?'),
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
            dialogText=meta.licenseHTML, direction=wx.Layout_LeftToRight, 
            *args, **kwargs)


class MainWindowRestore(MainWindowCommand):
    def __init__(self, *args, **kwargs):
        super(MainWindowRestore, self).__init__(menuText=_('&Restore'),
            helpText=_('Restore the window to its previous state'),
            bitmap='restore', *args, **kwargs)

    def doCommand(self, event):
        self.mainwindow.restore(event)
    

class Search(MainWindowCommand, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        self.searchControl = None
        patterns.Publisher().registerObserver(self.onViewerChanged,
            self.viewer.viewerChangeEventType())
        
    def onViewerChanged(self, event):
        if self.searchControl:
            searchable = self.viewer.isSearchable()
            if searchable:
                searchString, matchCase, includeSubItems = self.viewer.getSearchFilter()
                self.searchControl.SetValue(searchString)
                self.searchControl.setMatchCase(matchCase)
                self.searchControl.setIncludeSubItems(includeSubItems)
            self.searchControl.Enable(searchable)
                    
    def onFind(self, searchString, matchCase, includeSubItems):
        self.viewer.setSearchFilter(searchString, matchCase, includeSubItems)

    def appendToToolBar(self, toolbar):
        searchString, matchCase, includeSubItems = self.viewer.getSearchFilter()
        self.searchControl = widgets.SearchCtrl(toolbar, value=searchString,
            style=wx.TE_PROCESS_ENTER, matchCase=matchCase, 
            includeSubItems=includeSubItems, callback=self.onFind)
        toolbar.AddControl(self.searchControl)


class ViewColumnUICommandsMixin(object):
    def addViewColumnUICommands(self, viewer):
        for menuText, helpText, columnName in \
            [(_('&Attachments'), _('Show/hide attachment column'), 'attachments'),
             (_('&Categories'), _('Show/hide categories column'), 'categories'),
             (_('Overall categories'), _('Show/hide overall categories column (overall categories includes all parent task categories, recursively)'), 'totalCategories'),
             (_('&Description'), _('Show/hide description column'), 'description'),
             (_('&Reminder'), _('Show/hide reminder column'), 'reminder'),
             (_('&Start date'), _('Show/hide start date column'), 'startDate'),
             (_('&Due date'), _('Show/hide due date column'), 'dueDate'),
             (_('D&ays left'), _('Show/hide days left column'), 'timeLeft'),
             (_('Co&mpletion date'), _('Show/hide completion date column'), 'completionDate'),
             (_('&Recurrence'), _('Show/hide recurrence column'), 'recurrence'),
             (_('&Budget'), _('Show/hide budget column'), 'budget'),
             (_('Total b&udget'), _('Show/hide total budget column (total budget includes budget for subtasks)'), 'totalBudget'),
             (_('&Time spent'), _('Show/hide time spent column'), 'timeSpent'),
             (_('T&otal time spent'), _('Show/hide total time spent column (total time includes time spent on subtasks)'), 'totalTimeSpent'),
             (_('Budget &left'), _('Show/hide budget left column'), 'budgetLeft'),
             (_('Total budget l&eft'), _('Show/hide total budget left column (total budget left includes budget left for subtasks)'), 'totalBudgetLeft'),
             (_('&Priority'), _('Show/hide priority column'), 'priority'),
             (_('O&verall priority'), _('Show/hide overall priority column (overall priority is the maximum priority of a task and all its subtasks)'), 'totalPriority'),
             (_('&Hourly fee'), _('Show/hide hourly fee column'), 'hourlyFee'),
             (_('&Fixed fee'), _('Show/hide fixed fee column'), 'fixedFee'),
             (_('&Total fixed fee'), _('Show/hide total fixed fee column'), 'totalFixedFee'),
             (_('&Revenue'), _('Show/hide revenue column'), 'revenue'),
             (_('T&otal revenue'), _('Show/hide total revenue column'), 'totalRevenue')]:
            key = 'view' + columnName
            self[key] = ViewColumn(menuText=menuText, helpText=helpText, setting=columnName, viewer=viewer)

        self['viewalldatecolumns'] = ViewColumns(menuText=_('All date columns'), 
              helpText=_('Show/hide all date-related columns'), 
              setting=['startDate', 'dueDate', 'timeLeft', 'completionDate', 'recurrence'], 
              viewer=viewer)
        self['viewallbudgetcolumns'] = ViewColumns(menuText=_('All budget columns'),
              helpText=_('Show/hide all budget-related columns'),
              setting=['budget', 'totalBudget', 'timeSpent', 'totalTimeSpent', 
              'budgetLeft','totalBudgetLeft'], viewer=viewer)
        self['viewallfinancialcolumns'] = ViewColumns(menuText=_('All financial columns'),
              helpText=_('Show/hide all finance-related columns'),
              setting=['hourlyFee', 'fixedFee', 'totalFixedFee', 'revenue', 
              'totalRevenue'], viewer=viewer)
        self['hidecurrentcolumn'] = HideCurrentColumn(viewer=viewer)


class EditorUICommands(dict, ViewColumnUICommandsMixin):
    ''' UICommands that need to be seperately created for each (task) editor. '''
    def __init__(self, viewer, effortList):
        super(EditorUICommands, self).__init__()
        self['editeffort'] = EffortEdit(viewer=viewer, effortList=effortList)
        self['deleteeffort'] = EffortDelete(effortList=effortList, 
                                            viewer=viewer)
        self['cut'] = EditCut(viewer=viewer)
        self['copy'] = EditCopy(viewer=viewer)
        self['pasteintotask'] = EditPasteIntoTask(viewer=viewer)
        self.addViewColumnUICommands(viewer)


class UICommands(dict, ViewColumnUICommandsMixin):
    ''' All UICommands for the mainwindow. '''
    def __init__(self, mainwindow, iocontroller, viewer, settings, 
            taskList, effortList, categories, notes):
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
        self['exportascsv'] = FileExportAsCSV(iocontroller=iocontroller,
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
        self['renameviewer'] = RenameViewer(viewer=viewer, settings=settings)
        self['activatenextviewer'] = ActivateViewer(viewer=viewer,
            menuText=_('&Activate next viewer\tCtrl+PgDn'),
            helpText=_('Activate the next open viewer'), forward=True,
            bitmap='activatenextviewer')
        self['activatepreviousviewer'] = ActivateViewer(viewer=viewer,
            menuText=_('Activate &previous viewer\tCtrl+PgUp'),
            helpText=_('Activate the previous open viewer'), forward=False,
            bitmap='activatepreviousviewer')
        self['resetfilter'] = ResetFilter(viewer=viewer)
        self['hidecompletedtasks'] = ViewerHideCompletedTasks(viewer=viewer)
        self['hideinactivetasks'] = ViewerHideInactiveTasks(viewer=viewer)
        self['hideactivetasks'] = ViewerHideActiveTasks(viewer=viewer)    
        self['hideoverduetasks'] = ViewerHideOverdueTasks(viewer=viewer)    
        self['hideoverbudgettasks'] = ViewerHideOverbudgetTasks(viewer=viewer)
        self['hidecompositetasks'] = ViewerHideCompositeTasks(viewer=viewer)
        
        # Column show/hide commands
        self.addViewColumnUICommands(viewer)    
              
        self['viewexpandall'] = ViewExpandAll(viewer=viewer)
        self['viewcollapseall'] = ViewCollapseAll(viewer=viewer)
        self['viewexpandselected'] = ViewExpandSelected(viewer=viewer)
        self['viewcollapseselected'] = ViewCollapseSelected(viewer=viewer)
                
        self['viewsortorder'] = ViewerSortOrderCommand(menuText=_('&Ascending'),
            helpText=_('Sort ascending (checked) or descending (unchecked)'),
            viewer=viewer)
        self['viewsortcasesensitive'] = ViewerSortCaseSensitive(\
            viewer=viewer, menuText=_('Sort case sensitive'),
            helpText=_('When comparing text, sorting is case sensitive (checked) or insensitive (unchecked)'))
        self['viewsortbystatusfirst'] = ViewerSortByTaskStatusFirst(\
            viewer=viewer, menuText=_('Sort by status &first'),
            helpText=_('Sort tasks by status (active/inactive/completed) first'))
            
        # Sort by column commands
        for menuText, helpText, value in \
            [(_('Sub&ject'), _('Sort by subject'), 'subject'),
             (_('&Description'), _('Sort by description'), 'description'),
             (_('&Category'), _('Sort by category'), 'categories'),
             (_('Overall categories'), _('Sort by overall categories'), 'totalCategories'),
             (_('&Start date'), _('Sort tasks by start date'), 'startDate'),
             (_('&Due date'), _('Sort tasks by due date'), 'dueDate'),
             (_('&Completion date'), _('Sort tasks by completion date'), 'completionDate'),
             (_('D&ays left'), _('Sort tasks by number of days left'), 'timeLeft'),
             (_('&Recurrence'), _('Sort tasks by recurrence'), 'recurrence'), 
             (_('&Budget'), _('Sort tasks by budget'), 'budget'),
             (_('Total b&udget'), _('Sort tasks by total budget'), 'totalBudget'),
             (_('&Time spent'), _('Sort tasks by time spent'), 'timeSpent'),
             (_('T&otal time spent'), _('Sort tasks by total time spent'), 'totalTimeSpent'),
             (_('Budget &left'), _('Sort tasks by budget left'), 'budgetLeft'),
             (_('Total budget l&eft'), _('Sort tasks by total budget left'), 'totalBudgetLeft'),
             (_('&Priority'), _('Sort tasks by priority'), 'priority'),
             (_('Overall priority'), _('Sort tasks by overall priority'), 'totalPriority'),
             (_('&Hourly fee'), _('Sort tasks by hourly fee'), 'hourlyFee'),
             (_('&Fixed fee'), _('Sort tasks by fixed fee'), 'fixedFee'),
             (_('Total fi&xed fee'), _('Sort tasks by total fixed fee'), 'totalFixedFee'),
             (_('&Revenue'), _('Sort tasks by revenue'), 'revenue'),
             (_('Total re&venue'), _('Sort tasks by total revenue'), 'totalRevenue'),
             (_('&Reminder'), _('Sort tasks by reminder date and time'), 'reminder')]:
            key = 'viewsortby' + value.lower()
            self[key] = ViewerSortByCommand(viewer=viewer, value=value,
                menuText=menuText, helpText=helpText)
        
        for key, menuText, helpText, viewerClass, viewerArgs, viewerKwargs, bitmap in \
            (('viewtasklistviewer', _('Task &list'), 
            _('Open a new tab with a viewer that displays tasks in a list'), 
            gui.viewer.TaskListViewer, (taskList, self, settings), 
            dict(categories=categories), 'listview'),
            ('viewtasktreeviewer', _('Task &tree'),
            _('Open a new tab with a viewer that displays tasks in a tree'),
            gui.viewer.TaskTreeListViewer, (taskList, self, settings),
            dict(categories=categories), 'treeview'),
            ('viewcategoryviewer', _('&Category'),
            _('Open a new tab with a viewer that displays categories'),
            gui.viewer.CategoryViewer, (categories, self, settings), {},
            'category'),
            ('vieweffortdetailviewer', _('&Effort detail'),
            _('Open a new tab with a viewer that displays effort details'),
            gui.viewer.EffortListViewer, (taskList, self, settings), {}, 
            'start'),
            ('vieweffortperdayviewer', _('Effort per &day'),
            _('Open a new tab with a viewer that displays effort per day'),
            gui.viewer.EffortPerDayViewer, (taskList, self, settings), {},
            'date'),
            ('vieweffortperweekviewer', _('Effort per &week'),
            _('Open a new tab with a viewer that displays effort per week'),
            gui.viewer.EffortPerWeekViewer, (taskList, self, settings), {},
            'date'),
            ('vieweffortpermonthviewer', _('Effort per &month'),
            _('Open a new tab with a viewer that displays effort per month'),
            gui.viewer.EffortPerMonthViewer, (taskList, self, settings), {},
            'date'),
            ('viewnoteviewer', _('&Note'), 
            _('Open a new tab with a viewer that displays notes'),
            gui.viewer.NoteViewer, (notes, self, settings), 
            dict(categories=categories), 'note')):
            self[key] = ViewViewer(viewer=viewer, menuText=menuText, 
                helpText=helpText, bitmap=bitmap, viewerClass=viewerClass,
                viewerArgs=viewerArgs, viewerKwargs=viewerKwargs, 
                viewerBitmap=bitmap, settings=settings)
        
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

        # View tasks due before commands
        for value, menuText, helpText in \
            [('Today', _('&Today'), _('Only show tasks due today')),
             ('Tomorrow', _('T&omorrow'), _('Only show tasks due today and tomorrow')),
             ('Workweek', _('Wo&rk week'), _('Only show tasks due this work week (i.e. before Friday)')),
             ('Week', _('&Week'), _('Only show tasks due this week (i.e. before Sunday)')),
             ('Month', _('&Month'), _('Only show tasks due this month')),
             ('Year', _('&Year'), _('Only show tasks due this year')),
             ('Unlimited', _('&Unlimited'), _('Show all tasks'))]:
            key = 'viewdue' + value.lower()
            self[key] = ViewerFilterByDueDate(menuText=menuText,
                                            helpText=helpText, viewer=viewer,
                                            value=value)
            
        # Generic domain object commands
        self['new'] = NewDomainObject(viewer=viewer, taskList=taskList)
        self['edit'] = EditDomainObject(viewer=viewer)
        self['delete'] = DeleteDomainObject(viewer=viewer)
        self['newsub'] = NewSubDomainObject(viewer=viewer)
        
        # Task menu
        self['newtask'] = TaskNew(mainwindow=mainwindow, taskList=taskList,
            settings=settings, uicommands=self, categories=categories)
        self['newtaskwithselectedcategories'] = \
            NewTaskWithSelectedCategories(mainwindow=mainwindow,
                taskList=taskList, settings=settings, uicommands=self,
                categories=categories, viewer=viewer)
        self['newsubtask'] = TaskNewSubTask(taskList=taskList, viewer=viewer)
        self['edittask'] = TaskEdit(taskList=taskList, viewer=viewer)
        self['toggletaskcompletion'] = TaskToggleCompletion(taskList=taskList,
                                                            viewer=viewer)
        self['deletetask'] = TaskDelete(taskList=taskList, viewer=viewer)
        self['mailtask'] = TaskMail(viewer=viewer, menuText=_('Mail task'), 
            helpText=_('Mail the task, using your default mailer'), 
            bitmap='email')
        self['addattachmenttotask'] = TaskAddAttachment(taskList=taskList,
                                                        viewer=viewer,
                                                        settings=settings)
        self['openalltaskattachments'] = TaskOpenAllAttachments(viewer=viewer, settings=settings)
        self['incpriority'] = TaskIncPriority(taskList=taskList, viewer=viewer)
        self['decpriority'] = TaskDecPriority(taskList=taskList, viewer=viewer)
        self['maxpriority'] = TaskMaxPriority(taskList=taskList, viewer=viewer)
        self['minpriority'] = TaskMinPriority(taskList=taskList, viewer=viewer)
        
        # Effort menu
        self['neweffort'] = EffortNew(viewer=viewer, effortList=effortList,
            taskList=taskList, mainwindow=mainwindow, uicommands=self)
        self['editeffort'] = EffortEdit(viewer=viewer, effortList=effortList)
        self['deleteeffort'] = EffortDelete(effortList=effortList, 
                                            viewer=viewer)
        self['starteffort'] = EffortStart(taskList=taskList, viewer=viewer)
        self['stopeffort'] = EffortStop(taskList=taskList)
        
        # Category menu
        self['newcategory'] = CategoryNew(mainwindow=mainwindow, 
            categories=categories, uiCommands=self)
        self['newsubcategory'] = CategoryNewSubCategory(viewer=viewer, 
            categories=categories)
        self['deletecategory'] = CategoryDelete(viewer=viewer, 
            categories=categories)
        self['editcategory'] = CategoryEdit(viewer=viewer, 
            categories=categories)
        
        # Note menu
        self['newnote'] = NoteNew(mainwindow=mainwindow, notes=notes, 
                                  categories=categories)
        self['newsubnote'] = NoteNewSubNote(viewer=viewer, notes=notes)
        self['deletenote'] = NoteDelete(viewer=viewer, notes=notes)
        self['editnote'] = NoteEdit(viewer=viewer, notes=notes)
        
        # Help menu
        self['help'] = Help()
        self['tips'] = Tips(settings=settings, mainwindow=mainwindow)
        self['about'] = HelpAbout()
        self['license'] = HelpLicense()

        # Taskbar menu
        self['restore'] = MainWindowRestore(mainwindow=mainwindow)
        
        # Toolbar specific
        self['search'] = Search(mainwindow=mainwindow, viewer=viewer, settings=settings)
        
        # Drag and drop related, not on any menu:
        self['draganddroptask'] = TaskDragAndDrop(taskList=taskList, 
                                                  viewer=viewer)
        self['draganddropcategory'] = CategoryDragAndDrop(viewer=viewer,
            categories=categories)
        self['draganddropnote'] = NoteDragAndDrop(viewer=viewer, notes=notes)

    def createRecentFileOpenUICommand(self, filename, index):
        return RecentFileOpen(filename=filename, index=index, 
            iocontroller=self.__iocontroller)


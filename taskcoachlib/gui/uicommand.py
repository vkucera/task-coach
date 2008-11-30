'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>

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

import wx, os
from taskcoachlib import patterns, meta, command, help, widgets, persistence
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, attachment
from taskcoachlib.mailer import writeMail
import dialog, render, viewer, codecs


''' User interface commands (subclasses of UICommand) are actions that can
    be invoked by the user via the user interface (menu's, toolbar, etc.).
    See the Taskmaster pattern described here: 
    http://www.objectmentor.com/resources/articles/taskmast.pdf 
'''


class UICommandContainer(object):
    ''' Mixin with wx.Menu or wx.ToolBar (sub)class. '''

    def appendUICommands(self, *uiCommands):
        for command in uiCommands:
            if command is None:
                self.AppendSeparator()
            elif type(command) == type(()): # This only works for menu's
                menuTitle, menuUICommands = command[0], command[1:]
                self.appendSubMenuWithUICommands(menuTitle, menuUICommands)
            else:
                self.appendUICommand(command)

    def appendSubMenuWithUICommands(self, menuTitle, uiCommands):
        import menu
        subMenu = menu.Menu(self._window)
        self.appendMenu(menuTitle, subMenu)
        subMenu.appendUICommands(*uiCommands)
        

class UICommand(object):
    ''' Base user interface command. An UICommand is some action that can be 
        associated with menu's and/or toolbars. It contains the menutext and 
        helptext to be displayed, code to deal with wx.EVT_UPDATE_UI and 
        methods to attach the command to a menu or toolbar. Subclasses should 
        implement doCommand() and optionally override enabled(). '''
    
    def __init__(self, menuText='', helpText='', bitmap='nobitmap', 
             kind=wx.ITEM_NORMAL, id=None, bitmap2=None, *args, **kwargs):
        super(UICommand, self).__init__()
        self.menuText = menuText or '<%s>'%_('None')
        self.helpText = helpText
        self.bitmap = bitmap
        self.bitmap2 = bitmap2
        self.kind = kind
        self.id = id or wx.NewId()
        self.toolbar = None
        self.menuItems = [] # uiCommands can be used in multiple menu's

    def __eq__(self, other):
        try:
            return self.menuText == other.menuText
        except AttributeError:
            return False

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
        if not self.toolbar: return # Not attached to a toolbar or it's hidden
        shortHelp = wx.MenuItem.GetLabelFromText(self.getMenuText())
        if shortHelp != self.toolbar.GetToolShortHelp(self.id):
            self.toolbar.SetToolShortHelp(self.id, shortHelp)
        longHelp = self.getHelpText()
        if longHelp != self.toolbar.GetToolLongHelp(self.id):
            self.toolbar.SetToolLongHelp(self.id, longHelp)

    def mainWindow(self):
        return wx.GetApp().TopWindow


class SettingsCommand(UICommand):
    ''' SettingsCommands are saved in the settings (a ConfigParser). '''

    def __init__(self, settings=None, setting=None, section='view', 
                 *args, **kwargs):
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
        id = super(BooleanSettingsCommand, self).appendToMenu(menu, window, 
                                                              position)
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


class AttachmentsCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.attachments = kwargs.pop('attachments', None)
        super(AttachmentsCommand, self).__init__(*args, **kwargs)


class ViewerCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.viewer = kwargs.pop('viewer', None)
        super(ViewerCommand, self).__init__(*args, **kwargs)

    def __eq__(self, other):
        return super(ViewerCommand, self).__eq__(other) and \
            self.viewer.settingsSection() == other.viewer.settingsSection()


# Mixins: 

class PopupButton(object):
    """Mix this with a UICommand for toolbar pop-up menu"""

    def doCommand(self, event):
        import menu
        popupMenu = self.createPopupMenu()
        if self.toolbar:
            x, y = self.toolbar.GetPosition()
            w, h = self.toolbar.GetSize()
            menuX = wx.GetMousePosition()[0] - self.mainWindow().GetPosition()[0] - 0.5 * self.toolbar.GetToolSize()[0]
            menuY = y + h
            self.mainWindow().PopupMenu(popupMenu, (menuX, menuY))
        else:
            self.mainWindow().PopupMenu(popupMenu)

    def createPopupMenu(self):
        raise NotImplementedError


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

class NeedsAttachmentViewer(object):
    def enabled(self, event):
        return super(NeedsAttachmentViewer, self).enabled(event) and \
            self.viewer.isShowingAttachments()

class NeedsSelectedTasks(NeedsTaskViewer, NeedsSelection):
    pass

class NeedsOneSelectedTask(NeedsTaskViewer, NeedsSelection):
    def enabled(self, event):
        return super(NeedsOneSelectedTask, self).enabled(event) and \
               len(self.viewer.curselection()) == 1

class NeedsSelectionWithAttachments(NeedsSelection):
    def enabled(self, event):
        return super(NeedsSelectionWithAttachments, self).enabled(event) and \
            not self.viewer.isShowingEffort() and \
            bool([item for item in self.viewer.curselection() if item.attachments()])

class NeedsSelectedEffort(NeedsEffortViewer, NeedsSelection):
    pass

class NeedsSelectedCategory(NeedsCategoryViewer, NeedsSelection):
    pass

class NeedsSelectedNote(NeedsNoteViewer, NeedsSelection):
    pass

class NeedsSelectedAttachments(NeedsAttachmentViewer, NeedsSelection):
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

class NeedsSetting(object):
    def __init__(self, *args, **kwargs):
        self.__section = kwargs.pop('section')
        self.__setting = kwargs.pop('setting')

        super(NeedsSetting, self).__init__(*args, **kwargs)

    def enabled(self, event):
        return super(NeedsSetting, self).enabled(event) and \
               bool(self.settings.get(self.__section, self.__setting))

class NeedsDeletedItems(object):
    def enabled(self, event):
        return super(NeedsDeletedItems, self).enabled(event) and \
               self.iocontroller.hasDeletedItems()

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


class FileSaveSelectedTaskAsTemplate(NeedsOneSelectedTask, IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveSelectedTaskAsTemplate, self).__init__(\
            menuText=_('Save selected task as &template'),
            helpText=_('Save the selected task as a task template'),
            bitmap='saveselection', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.saveastemplate(self.viewer.curselection()[0])


class FileAddTemplate(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileAddTemplate, self).__init__(\
            menuText=_('Add template'),
            helpText=_('Add a new template from a template file\n'),
            bitmap='fileopen', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.addtemplate()


class FilePurgeDeletedItems(NeedsDeletedItems, IOCommand):
    def __init__(self, *args, **kwargs):
        super(FilePurgeDeletedItems, self).__init__(\
            menuText=_('Purge deleted items'),
            helpText=_('Actually delete deleted tasks and notes (see the SyncML chapter in Help'),
            bitmap='delete', *args, **kwargs)

    def doCommand(self, event):
        if (wx.MessageBox(_('''Purging deleted items is undoable.
If you're planning on enabling
the SyncML feature again with the
same server you used previously,
these items will probably come back.

Do you still want to purge?'''),
                          _('Warning'), wx.YES_NO) == wx.YES):
            self.iocontroller.purgeDeletedItems()


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
    def __init__(self, aViewer, printSelectionOnly=False, *args, **kwargs):
        super(Printout, self).__init__(*args, **kwargs)
        htmlText = persistence.viewer2html(aViewer, 
                                           selectionOnly=printSelectionOnly)
        self.SetHtmlText(htmlText)
        self.SetFooter(_('Page') + ' @PAGENUM@/@PAGESCNT@', wx.html.PAGE_ALL)
        self.SetFonts('Arial', 'Courier')
        global printerSettings
        top, left = printerSettings.pageSetupData.GetMarginTopLeft()
        bottom, right = printerSettings.pageSetupData.GetMarginBottomRight()
        self.SetMargins(top, bottom, left, right)

                
class PrintPageSetup(UICommand):
    def __init__(self, *args, **kwargs):
        super(PrintPageSetup, self).__init__(\
            menuText=_('Page setup...\tShift+Ctrl+P'), 
            helpText=_('Setup the characteristics of the printer page'), 
            bitmap='pagesetup', id=wx.ID_PRINT_SETUP, *args, **kwargs)

    def doCommand(self, event):
        global printerSettings
        dialog = wx.PageSetupDialog(self.mainWindow(), 
            printerSettings.pageSetupData)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            printerSettings.updatePageSetupData(dialog.GetPageSetupData())
        dialog.Destroy()


class PrintPreview(ViewerCommand):
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
        previewFrame = wx.PreviewFrame(preview, self.mainWindow(), 
            _('Print preview'), size=(750, 700))
        previewFrame.Initialize()
        previewFrame.Show()
        

class Print(ViewerCommand):
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
        if not printer.PrintDialog(self.mainWindow()):
            return
        printout = Printout(self.viewer, 
            printSelectionOnly=printer.PrintDialogData.Selection)
        # If the user checks the selection radio button, the ToPage property 
        # gets set to 1. Looks like a bug to me. The simple work-around is to
        # reset the ToPage property to the MaxPage value if necessary:
        if printer.PrintDialogData.Selection:
            printer.PrintDialogData.ToPage = printer.PrintDialogData.MaxPage
        printer.Print(self.mainWindow(), printout, prompt=False)
 

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


class FileExportAsVCalendar(IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileExportAsVCalendar, self).__init__(menuText=_('Export as &VCalendar...'),
            helpText=_('Export the current view in VCalendar format'),
            bitmap='exportasvcal', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.exportAsVCalendar(self.viewer)


class FileSynchronize(IOCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(FileSynchronize, self).__init__(menuText=_('S&yncML synchronization'),
            helpText=_('Synchronize with a SyncML server'),
            bitmap='sync', *args, **kwargs)

    def doCommand(self, event):
        password = wx.GetPasswordFromUser(_('Please enter your password:'), 
                                          _('Task Coach SyncML password'))
        if password:
            self.iocontroller.synchronize(password)


class FileQuit(UICommand):
    def __init__(self, *args, **kwargs):
        super(FileQuit, self).__init__(menuText=_('&Quit\tCtrl+Q'), 
            helpText=_('Exit %s')%meta.name, bitmap='exit', 
            id=wx.ID_EXIT, *args, **kwargs)

    def doCommand(self, event):
        self.mainWindow().Close(force=True)


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
            cutCommand = command.CutCommand(self.viewer.presentation(),
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
            copyCommand = command.CopyCommand(self.viewer.presentation(), 
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


class EditPreferences(SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(EditPreferences, self).__init__(menuText=_('Preferences...'),
            helpText=_('Edit preferences'), bitmap='configure', 
            id=wx.ID_PREFERENCES, *args, **kwargs)
            
    def doCommand(self, event, show=True):
        editor = dialog.preferences.Preferences(parent=self.mainWindow(), 
            title=_('Edit preferences'), settings=self.settings)
        editor.Show(show=show)


class EditSyncPreferences(IOCommand):
    def __init__(self, *args, **kwargs):
        super(EditSyncPreferences, self).__init__(menuText=_('SyncML preferences...'),
            helpText=_('Edit SyncML preferences'), bitmap='sync',
            *args, **kwargs)

    def doCommand(self, event, show=True):
        editor = dialog.syncpreferences.SyncMLPreferences(parent=self.mainWindow(),
            iocontroller=self.iocontroller,
            title=_('Edit SyncML preferences'))
        editor.Show(show=show)


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
        self.taskFile = kwargs.pop('taskFile')
        self.viewerClass = kwargs.pop('viewerClass')
        kwargs.setdefault('bitmap', self.viewerClass.defaultBitmap) 
        super(ViewViewer, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        viewer.addOneViewer(self.viewer, self.taskFile, self.settings, self.viewerClass)
        self.increaseViewerCount()
        
    def increaseViewerCount(self):
        setting = self.viewerClass.__name__.lower() + 'count'
        viewerCount = self.settings.getint('view', setting)
        self.settings.set('view', setting, str(viewerCount+1))
        

class RenameViewer(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(RenameViewer, self).__init__(menuText=_('&Rename viewer...'),
            helpText=_('Rename the selected viewer'), *args, **kwargs)
        
    def doCommand(self, event):
        dialog = wx.TextEntryDialog(self.mainWindow(), 
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
        widget = self.viewer.getWidget() # Must use method to make sure viewer dispatch works!
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
        self.viewer.showColumnByName(self.setting, 
                                     self._isMenuItemChecked(event))


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
        self.viewer.expandSelected()
            

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
        self.viewer.collapseSelected()


class ViewerSortByCommand(ViewerCommand, UIRadioCommand):        
    def isSettingChecked(self):
        return self.viewer.isSortedBy(self.value)
    
    def doCommand(self, event):
        self.viewer.sortBy(self.value)


class ViewerSortOrderCommand(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerSortOrderCommand, self).__init__(menuText=_('&Ascending'),
            helpText=_('Sort ascending (checked) or descending (unchecked)'),
            *args, **kwargs)

    def isSettingChecked(self):
        return self.viewer.isSortOrderAscending()
    
    def doCommand(self, event):
        self.viewer.setSortOrderAscending(self._isMenuItemChecked(event))
    
    
class ViewerSortCaseSensitive(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerSortCaseSensitive, self).__init__(\
            menuText=_('Sort case sensitive'),
            helpText=_('When comparing text, sorting is case sensitive (checked) or insensitive (unchecked)'),
            *args, **kwargs)

    def isSettingChecked(self):
        return self.viewer.isSortCaseSensitive()
    
    def doCommand(self, event):
        self.viewer.setSortCaseSensitive(self._isMenuItemChecked(event))


class ViewerSortByTaskStatusFirst(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerSortByTaskStatusFirst, self).__init__(\
            menuText=_('Sort by status &first'),
            helpText=_('Sort tasks by status (active/inactive/completed) first'),
            *args, **kwargs)

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


class ViewerHideCompositeTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideCompositeTasks, self).__init__(menuText=_('C&omposite'),
            helpText=_('Show/hide tasks with subtasks in list mode'), 
            *args, **kwargs)
            
    def isSettingChecked(self):
        return self.viewer.isHidingCompositeTasks()
        
    def doCommand(self, event):
        self.viewer.hideCompositeTasks(self._isMenuItemChecked(event))

    def enabled(self, event):
        return not self.viewer.isTreeViewer()


class ObjectCommandBase(ViewerCommand):
    """Base class for delete and edit L{UICommand}s.
    @cvar __containerName__: The name of the object list in
        the keyword arguments (e.g. 'notes', 'taskList'...)
    @cvar __bitmap__: Name of the bitmap for this command"""

    __containerName__ = None
    __bitmap__ = None

    def __init__(self, *args, **kwargs):
        kwargs['bitmap'] = self.__bitmap__
        super(ObjectCommandBase, self).__init__(*args, **kwargs)


class ObjectEdit(ObjectCommandBase):
    """Base class for L{UICommand}s to edit objects. This will use the
    L{Viewer.editItemDialog} method to open an edit dialog."""

    __bitmap__ = 'edit'

    def __init__(self, *args, **kwargs):
        kwargs['menuText'] = kwargs[self.__containerName__].editItemMenuText
        kwargs['helpText'] = kwargs[self.__containerName__].editItemHelpText
        super(ObjectEdit, self).__init__(*args, **kwargs)

    def doCommand(self, event, show=True):
        editor = self.viewer.editItemDialog(bitmap=self.bitmap,
                                            items=self.viewer.curselection())
        editor.Show(show)


class ObjectDelete(ObjectCommandBase):
    """Base class for L{UICommand}s to delete objects. This will use
    the L{Viewer.deleteItemCommand} method to get the actual delete
    command."""

    __bitmap__ = 'delete'

    def __init__(self, *args, **kwargs):
        kwargs['menuText'] = kwargs[self.__containerName__].deleteItemMenuText
        kwargs['helpText'] = kwargs[self.__containerName__].deleteItemHelpText
        super(ObjectDelete, self).__init__(*args, **kwargs)

    def doCommand(self, event):
        deleteCommand = self.viewer.deleteItemCommand()
        deleteCommand.do()

        
class TaskNew(TaskListCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        taskList = kwargs['taskList']
        if 'menuText' not in kwargs:
            kwargs['menuText'] = taskList.newItemMenuText
            kwargs['helpText'] = taskList.newItemHelpText
        super(TaskNew, self).__init__(bitmap='new', *args, **kwargs)

    def doCommand(self, event, show=True):
        newTaskDialog = dialog.editor.TaskEditor(self.mainWindow(), 
            command.NewTaskCommand(self.taskList, 
            categories=self.categoriesForTheNewTask()), 
            self.mainWindow().taskFile, self.settings, bitmap=self.bitmap)
        newTaskDialog.Show(show)
        return newTaskDialog # for testing purposes

    def categoriesForTheNewTask(self):
        categories = self.mainWindow().taskFile.categories()
        return [category for category in categories if category.isFiltered()]


class TaskNewFromTemplate(TaskNew):
    def __init__(self, filename, *args, **kwargs):
        super(TaskNewFromTemplate, self).__init__(*args, **kwargs)
        self.__filename = filename
        task = self.__readTemplate()
        self.menuText = task.subject()

    def __readTemplate(self):
        return persistence.TemplateXMLReader(file(self.__filename,
                                                  'rU')).read()

    def doCommand(self, event, show=True):
        # The task template is read every time because it's the
        # TemplateXMLReader that evaluates dynamic values (Today()
        # should be evaluated at task creation for instance).
        task = self.__readTemplate()
        kwargs = task.__getcopystate__()
        kwargs['categories'] = self.categoriesForTheNewTask()
        newTaskDialog = dialog.editor.TaskEditor(self.mainWindow(), 
            command.NewTaskCommand(self.taskList, **kwargs),
            self.mainWindow().taskFile, self.settings, bitmap=self.bitmap)
        newTaskDialog.Show(show)
        return newTaskDialog # for testing purposes


class TaskNewFromTemplateButton(PopupButton, TaskListCommand, SettingsCommand):
    def createPopupMenu(self):
        import menu
        return menu.TaskTemplateMenu(self.mainWindow(), self.taskList, 
                                     self.settings)

    def getMenuText(self):
        return _('New task &from template')

    def getHelpText(self):
        return _('Create a new task from a template')


class NewTaskWithSelectedCategories(TaskNew, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(NewTaskWithSelectedCategories, self).__init__(\
            menuText=_('New task with selected categories...'),
            helpText=_('Insert a new task with the selected categories checked'),
            *args, **kwargs)

    def categoriesForTheNewTask(self):
        return self.viewer.curselection()
    

class TaskNewSubTask(NeedsSelectedTasks,  TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        taskList = kwargs['taskList']
        super(TaskNewSubTask, self).__init__(bitmap='newsub',
            menuText=taskList.newSubItemMenuText,
            helpText=taskList.newSubItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        dialog = self.viewer.newSubItemDialog(bitmap=self.bitmap)
        dialog.Show(show)
        

class TaskEdit(ObjectEdit, NeedsSelectedTasks, TaskListCommand):
    __containerName__ = 'taskList'


class TaskDelete(ObjectDelete, NeedsSelectedTasks, TaskListCommand):
    __containerName__ = 'taskList'


class TaskToggleCompletion(NeedsSelectedTasks, ViewerCommand):
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
            self.viewer.presentation(), self.viewer.curselection())
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


class MailItem(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(MailItem, self).__init__(bitmap='email', *args, **kwargs)

    def doCommand(self, event, mail=writeMail, showerror=wx.MessageBox):
        items = self.viewer.curselection()
        subject = self.subject(items)
        body = self.body(items)
        self.mail(subject, body, mail, showerror)

    def subject(self, items):
        if len(items) > 1:
            return self.subjectForMultipleItems()
        else:
            return items[0].subject(recursive=True)
        
    def body(self, items):
        if len(items) > 1:
            bodyLines = []
            for item in items:
                bodyLines.append(item.subject(recursive=True) + '\n')
                if item.description():
                    bodyLines.extend(item.description().splitlines())
                    bodyLines.append('\n')
        else:
            bodyLines = items[0].description().splitlines()
        return '\r\n'.join(bodyLines)        

    def mail(self, subject, body, mail, showerror):
        try:
            mail('', subject, body)
        except Exception, reason:
            showerror(_('Cannot send email:\n%s')%reason, 
                      caption=_('%s mail error')%meta.name, style=wx.ICON_ERROR)        
        

class TaskMail(NeedsSelectedTasks, MailItem):
    def __init__(self, *args, **kwargs):
        super(TaskMail, self).__init__(menuText=_('Mail task'),
            helpText=_('Mail the task, using your default mailer'),
            *args, **kwargs)

    def subjectForMultipleItems(self):
        return _('Tasks')


class NoteMail(NeedsSelectedNote, MailItem):
    def __init__(self, *args, **kwargs):
        super(NoteMail, self).__init__(menuText=_('Mail note'),
            helpText=_('Mail the note, using your default mailer'),
            *args, **kwargs)

    def subjectForMultipleItems(self):
        return _('Notes')


class TaskAddNote(NeedsSelectedTasks, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(TaskAddNote, self).__init__(menuText=_('Add &note'),
            helpText=_('Add a note to the selected task(s)'),
            bitmap='note', *args, **kwargs)
            
    def doCommand(self, event, show=True):
        noteDialog = dialog.editor.NoteEditor(self.mainWindow(), 
            command.AddTaskNoteCommand(self.viewer.presentation(), 
                self.viewer.curselection()),
            self.settings, self.viewer.presentation(),
            self.mainWindow().taskFile, bitmap=self.bitmap)
        noteDialog.Show(show)
        return noteDialog # for testing purposes


class CategoryAddNote(NeedsSelectedCategory, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(CategoryAddNote, self).__init__(menuText=_('Add &note'),
            helpText=_('Add a note to the selected category(ies)'),
            bitmap='note', *args, **kwargs)
            
    def doCommand(self, event, show=True):
        noteDialog = dialog.editor.NoteEditor(self.mainWindow(), 
            command.AddCategoryNoteCommand(self.viewer.presentation(), 
                self.viewer.curselection()),
            self.settings, self.viewer.presentation(),  
            self.mainWindow().taskFile, bitmap=self.bitmap)
        noteDialog.Show(show)
        return noteDialog # for testing purposes
        

class AttachmentAddNote(NeedsSelectedAttachments, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(AttachmentAddNote, self).__init__(menuText=_('Add &note'),
            helpText=_('Add a note to the selected attachment(s)'),
            bitmap='note', *args, **kwargs)

    def doCommand(self, event, show=True):
        noteDialog = dialog.editor.NoteEditor(self.mainWindow(), 
            command.AddAttachmentNoteCommand(self.viewer.presentation(), 
                self.viewer.curselection()),
            self.settings, self.mainWindow().taskFile, bitmap=self.bitmap)
        noteDialog.Show(show)
        return noteDialog # for testing purposes


class AddAttachment(NeedsSelection, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(AddAttachment, self).__init__(menuText=_('&Add attachment'),          
            bitmap='attachment', *args, **kwargs)
        
    def doCommand(self, event):
        filename = widgets.AttachmentSelector()
        if not filename:
            return
        base = self.settings.get('file', 'attachmentbase')
        if base:
            filename = attachment.getRelativePath(filename, base)
        addAttachmentCommand = command.AddAttachmentCommand( \
            self.viewer.presentation(), self.viewer.curselection(), 
            attachments=[attachment.FileAttachment(filename)])
        addAttachmentCommand.do()


class AddTaskAttachment(NeedsTaskViewer, AddAttachment):
    def __init__(self, *args, **kwargs):
        super(AddTaskAttachment, self).__init__(\
            helpText=_('Browse for files to add as attachment to the selected task(s)'),
            *args, **kwargs)


class AddCategoryAttachment(NeedsCategoryViewer, AddAttachment):
    def __init__(self, *args, **kwargs):
        super(AddCategoryAttachment, self).__init__(\
            helpText=_('Browse for files to add as attachment to the selected categories'),
            *args, **kwargs)


class AddNoteAttachment(NeedsNoteViewer, AddAttachment):
    def __init__(self, *args, **kwargs):
        super(AddNoteAttachment, self).__init__(\
            helpText=_('Browse for files to add as attachment to the selected note(s)'),
            *args, **kwargs)
            

class OpenAllAttachments(NeedsSelectionWithAttachments, ViewerCommand, 
                         SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(OpenAllAttachments, self).__init__(\
           menuText=_('&Open all attachments'), 
           bitmap='attachment', *args, **kwargs)
        
    def doCommand(self, event):
        base = self.settings.get('file', 'attachmentbase')
        for item in self.viewer.curselection():
            for attachment in item.attachments():
                try:    
                    attachment.open(base)
                except Exception, instance:
                    showerror(str(instance), 
                        caption=_('Error opening attachment'), 
                        style=wx.ICON_ERROR)


class OpenAllTaskAttachments(NeedsTaskViewer, OpenAllAttachments):
    def __init__(self, *args, **kwargs):
        super(OpenAllTaskAttachments, self).__init__(\
            helpText=_('Open all attachments of the selected task(s)'),
            *args, **kwargs)


class OpenAllCategoryAttachments(NeedsCategoryViewer, OpenAllAttachments):
    def __init__(self, *args, **kwargs):
        super(OpenAllCategoryAttachments, self).__init__(\
            helpText=_('Open all attachments of the selected categories'),
            *args, **kwargs)


class OpenAllNoteAttachments(NeedsNoteViewer, OpenAllAttachments):
    def __init__(self, *args, **kwargs):
        super(OpenAllNoteAttachments, self).__init__(\
            helpText=_('Open all attachments of the selected note(s)'),
            *args, **kwargs)
            

class EffortNew(NeedsAtLeastOneTask, ViewerCommand, EffortListCommand, 
                TaskListCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        effortList = kwargs['effortList']
        super(EffortNew, self).__init__(bitmap='new',  
            menuText=effortList.newItemMenuText, 
            helpText=effortList.newItemHelpText, *args, **kwargs)

    def doCommand(self, event):
        if self.viewer.isShowingTasks() and self.viewer.curselection():
            selectedTasks = self.viewer.curselection()
        elif self.viewer.isShowingEffort():
            selectedTasks = [self.firstTask(self.viewer.tasksToShowEffortFor)]
        else:
            selectedTasks = [self.firstTask(self.taskList)]

        newEffortDialog = dialog.editor.EffortEditor(self.mainWindow(), 
            command.NewEffortCommand(self.effortList, selectedTasks),
            self.mainWindow().taskFile, self.settings, bitmap=self.bitmap)
        newEffortDialog.Show()

    @staticmethod    
    def firstTask(tasks):
        subjectDecoratedTasks = [(task.subject(recursive=True), 
            task) for task in tasks]
        subjectDecoratedTasks.sort()
        return subjectDecoratedTasks[0][1]


class EffortEdit(ObjectEdit, NeedsSelectedEffort, EffortListCommand):
    __containerName__ = 'effortList'


class EffortDelete(ObjectDelete, NeedsSelectedEffort, EffortListCommand):
    __containerName__ = 'effortList'


class EffortStart(NeedsSelectedTasks, ViewerCommand, TaskListCommand):
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
        return super(EffortStart, self).enabled(event) and \
            bool([task for task in self.viewer.curselection() if not
             (task.isBeingTracked() or task.completed() or task.inactive())])


class EffortStartForTask(TaskListCommand):
    ''' UICommand to start tracking for a specific task. This command can
        be used to build a menu with seperate menu items for all tasks. 
        See gui.menu.StartEffortForTaskMenu. '''
        
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task')
        subject = self.task.subject() or _('(No subject)') 
        super(EffortStartForTask, self).__init__( \
            bitmap=render.taskBitmapNames(self.task)[0], menuText=subject,
            helpText=_('Start tracking effort for %s')%subject, 
            *args, **kwargs)
        
    def doCommand(self, event):
        start = command.StartEffortCommand(self.taskList, [self.task])
        start.do()
        
    def enabled(self, event):
        return not self.task.isBeingTracked() and not self.task.completed()      


class EffortStartButton(PopupButton, TaskListCommand):
    def __init__(self, *args, **kwargs):
        super(EffortStartButton, self).__init__(bitmap='startmenu',
            menuText=_('&Start tracking effort'),
            helpText=_('Select a task via the menu and start tracking effort for it'),
            *args, **kwargs)

    def createPopupMenu(self):
        import menu
        return menu.StartEffortForTaskMenu(self.mainWindow(), self.taskList)

    def enabled(self, event):
        return len(self.taskList) > 0
    

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


class CategoryNew(CategoriesCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        categories = kwargs['categories']
        super(CategoryNew, self).__init__(bitmap='new', 
            menuText=categories.newItemMenuText,
            helpText=categories.newItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        newCategoryDialog = dialog.editor.CategoryEditor(self.mainWindow(), 
            command.NewCategoryCommand(self.categories),
            self.settings, self.mainWindow().taskFile, bitmap=self.bitmap)
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


class CategoryDelete(ObjectDelete, NeedsSelectedCategory, CategoriesCommand):
    __containerName__ = 'categories'


class CategoryEdit(ObjectEdit, NeedsSelectedCategory, CategoriesCommand):
    __containerName__ = 'categories'


class CategoryDragAndDrop(CategoriesCommand, DragAndDropCommand):
    def createCommand(self, dragItem, dropItem):
        return command.DragAndDropCategoryCommand(self.categories, dragItem, 
                                                  drop=dropItem)


class NoteNew(NotesCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        notes = kwargs['notes']
        if 'menuText' not in kwargs:
            kwargs['menuText'] = notes.newItemMenuText
            kwargs['helpText'] = notes.newItemHelpText
        super(NoteNew, self).__init__(bitmap='new', *args, **kwargs)

    def doCommand(self, event, show=True):
        noteDialog = dialog.editor.NoteEditor(self.mainWindow(), 
            command.NewNoteCommand(self.notes,
                  categories=self.categoriesForTheNewNote()),
            self.settings, self.notes, self.mainWindow().taskFile,
            bitmap=self.bitmap)
        noteDialog.Show(show)
        return noteDialog # for testing purposes

    def categoriesForTheNewNote(self):
        categories = self.mainWindow().taskFile.categories()
        return [category for category in categories if category.isFiltered()]
    

class NewNoteWithSelectedCategories(NoteNew, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(NewNoteWithSelectedCategories, self).__init__(\
            menuText=_('New note with selected categories...'),
            helpText=_('Insert a new note with the selected categories checked'),
            *args, **kwargs)

    def categoriesForTheNewNote(self):
        return self.viewer.curselection()


class NoteNewSubNote(NeedsSelectedNote, NotesCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        notes = kwargs['notes']
        super(NoteNewSubNote, self).__init__(bitmap='newsub', 
            menuText=notes.newSubItemMenuText, 
            helpText=notes.newSubItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        dialog = self.viewer.newSubNoteDialog(bitmap=self.bitmap)
        dialog.Show(show)


class NoteDelete(ObjectDelete, NeedsSelectedNote, NotesCommand):
    __containerName__ = 'notes'


class NoteEdit(ObjectEdit, NeedsSelectedNote, NotesCommand):
    __containerName__ = 'notes'


class NoteDragAndDrop(NotesCommand, DragAndDropCommand):
    def createCommand(self, dragItem, dropItem):
        return command.DragAndDropNoteCommand(self.notes, dragItem, 
                                                  drop=dropItem)
                         
                                                        
class AttachmentNew(AttachmentsCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        attachments = kwargs['attachments']
        if 'menuText' not in kwargs:
            kwargs['menuText'] = attachments.newItemMenuText
            kwargs['helpText'] = attachments.newItemHelpText
        super(AttachmentNew, self).__init__(bitmap='new', *args, **kwargs)

    def doCommand(self, event, show=True):
        attachmentDialog = dialog.editor.AttachmentEditor(self.mainWindow(), 
            command.NewAttachmentCommand(self.attachments),
            self.settings, self.attachments, self.mainWindow().taskFile, 
            bitmap=self.bitmap)
        attachmentDialog.Show(show)
        return attachmentDialog # for testing purposes


class AttachmentDelete(ObjectDelete, NeedsSelectedAttachments, AttachmentsCommand):
    __containerName__ = 'attachments'


class AttachmentEdit(ObjectEdit, NeedsSelectedAttachments, AttachmentsCommand):
    __containerName__ = 'attachments'


class AttachmentOpen(NeedsSelectedAttachments, ViewerCommand, AttachmentsCommand):
    def __init__(self, *args, **kwargs):
        attachments = kwargs['attachments']
        super(AttachmentOpen, self).__init__(bitmap='fileopen',
            menuText=attachments.openItemMenuText,
            helpText=attachments.openItemHelpText, *args, **kwargs)

    def doCommand(self, event, showerror=wx.MessageBox):
        for attachment in self.viewer.curselection():
            try:
                attachment.open()
            except Exception, instance:
                showerror(unicode(instance), 
                          caption=_('Error opening attachment'), 
                          style=wx.ICON_ERROR)


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
        if '__WXMAC__' in wx.PlatformInfo:
            # Use default keyboard shortcut for Mac OS X:
            menuText = _('&Help contents\tCtrl+?') 
        else:
            # Use a letter, because 'Ctrl-?' doesn't work on Windows:
            menuText = _('&Help contents\tCtrl+H')
        super(Help, self).__init__(menuText=menuText,
            helpText=_('Help about the program'), bitmap='help', 
            dialogTitle=_('Help'), dialogText=help.helpHTML, id=wx.ID_HELP, 
            *args, **kwargs)


class Tips(SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(Tips, self).__init__(menuText=_('&Tips'),
            helpText=_('Tips about the program'), bitmap='help', *args, **kwargs)

    def doCommand(self, event):
        help.showTips(self.mainWindow(), self.settings)
        

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


class MainWindowRestore(UICommand):
    def __init__(self, *args, **kwargs):
        super(MainWindowRestore, self).__init__(menuText=_('&Restore'),
            helpText=_('Restore the window to its previous state'),
            bitmap='restore', *args, **kwargs)

    def doCommand(self, event):
        self.mainWindow().restore(event)
    

class Search(ViewerCommand, SettingsCommand):
    # Search can only be attached to a real viewer, not to a viewercontainer
    def __init__(self, *args, **kwargs):
        super(Search, self).__init__(*args, **kwargs)
        assert self.viewer.isSearchable()
                           
    def onFind(self, searchString, matchCase, includeSubItems):
        self.viewer.setSearchFilter(searchString, matchCase, includeSubItems)

    def appendToToolBar(self, toolbar):
        searchString, matchCase, includeSubItems = self.viewer.getSearchFilter()
        self.searchControl = widgets.SearchCtrl(toolbar, value=searchString,
            style=wx.TE_PROCESS_ENTER, matchCase=matchCase, 
            includeSubItems=includeSubItems, callback=self.onFind)
        toolbar.AddControl(self.searchControl)


class ToolbarChoiceCommand(UICommand):
    def appendToToolBar(self, toolbar):
        ''' Add our choice control to the toolbar. '''
        self.choiceCtrl = wx.Choice(toolbar, choices=self.choiceLabels)
        self.currentChoice = self.choiceCtrl.Selection
        self.choiceCtrl.Bind(wx.EVT_CHOICE, self.onChoice)
        toolbar.AddControl(self.choiceCtrl)
        
    def onChoice(self, event):
        ''' The user selected a choice from the choice control. '''
        choiceIndex = event.GetInt()
        if choiceIndex == self.currentChoice:
            return
        self.currentChoice = choiceIndex
        self.doChoice(self.choiceData[choiceIndex])
        
    def setChoice(self, choice):
        ''' Programmatically set the current choice in the choice control. '''
        index = self.choiceData.index(choice)
        self.choiceCtrl.Selection = index
        self.currentChoice = index


class EffortViewerAggregationChoice(ViewerCommand, ToolbarChoiceCommand):
    choiceLabels = [_('Effort details'), _('Effort per day'), 
                         _('Effort per week'), _('Effort per month')]
    choiceData = ['details', 'day', 'week', 'month']

    def doChoice(self, choice):
        self.viewer.showEffortAggregation(choice)
        

class TaskViewerTreeOrListChoice(ViewerCommand, ToolbarChoiceCommand):
    choiceLabels = [_('Tree of tasks'), _('List of tasks')]
    choiceData = [True, False]
    
    def doChoice(self, choice):
        self.viewer.showTree(choice)
        

class CategoryViewerFilterChoice(SettingsCommand, ToolbarChoiceCommand):
    choiceLabels = [_('Filter on all checked categories'),
                    _('Filter on any checked category')]
    choiceData = [True, False]

    def doChoice(self, choice):
        self.settings.set('view', 'categoryfiltermatchall', str(choice))


class ToggleAutoColumnResizing(UICheckCommand, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(ToggleAutoColumnResizing, self).__init__(\
            menuText=_('&Automatic column resizing'),
            helpText=_('When checked, automatically resize columns to fill'
                       ' available space'), 
            *args, **kwargs)
        wx.CallAfter(self.updateWidget)

    def updateWidget(self):
        self.viewer.getWidget().ToggleAutoResizing(self.isSettingChecked())

    def isSettingChecked(self):
        return self.settings.getboolean(self.viewer.settingsSection(),
                                        'columnautoresizing')
    
    def doCommand(self, event):
        self.settings.set(self.viewer.settingsSection(), 'columnautoresizing',
                          str(self._isMenuItemChecked(event)))
        self.updateWidget()

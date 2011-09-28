# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
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

import wx
from taskcoachlib import patterns, meta, command, help, widgets, persistence, thirdparty, render # pylint: disable-msg=W0622
from taskcoachlib.i18n import _
from taskcoachlib.domain import base, task, note, category, attachment, effort
from taskcoachlib.mailer import sendMail
from taskcoachlib.thirdparty.wxScheduler import wxSCHEDULER_NEXT, wxSCHEDULER_PREV, wxSCHEDULER_TODAY
from taskcoachlib.thirdparty import desktop, hypertreelist
from taskcoachlib.gui.wizard import CSVImportWizard
from taskcoachlib.tools import anonymize
import dialog, viewer, printer


''' User interface commands (subclasses of UICommand) are actions that can
    be invoked by the user via the user interface (menu's, toolbar, etc.).
    See the Taskmaster pattern described here: 
    http://www.objectmentor.com/resources/articles/taskmast.pdf 
''' # pylint: disable-msg=W0105


class UICommandContainerMixin(object):
    ''' Mixin with wx.Menu or wx.ToolBar (sub)class. '''

    def appendUICommands(self, *uiCommands):
        for uiCommand in uiCommands:
            if uiCommand is None:
                self.AppendSeparator()
            elif type(uiCommand) == type(()): # This only works for menu's
                menuTitle, menuUICommands = uiCommand[0], uiCommand[1:]
                self.appendSubMenuWithUICommands(menuTitle, menuUICommands)
            else:
                self.appendUICommand(uiCommand)

    def appendSubMenuWithUICommands(self, menuTitle, uiCommands):
        import menu
        subMenu = menu.Menu(self._window)
        self.appendMenu(menuTitle, subMenu)
        subMenu.appendUICommands(*uiCommands) # pylint: disable-msg=W0142
        

class UICommand(object):
    ''' Base user interface command. An UICommand is some action that can be 
        associated with menu's and/or toolbars. It contains the menutext and 
        helptext to be displayed, code to deal with wx.EVT_UPDATE_UI and 
        methods to attach the command to a menu or toolbar. Subclasses should 
        implement doCommand() and optionally override enabled(). '''
    
    def __init__(self, menuText='', helpText='', bitmap='nobitmap', 
             kind=wx.ITEM_NORMAL, id=None, bitmap2=None, *args, **kwargs): # pylint: disable-msg=W0622
        super(UICommand, self).__init__()
        menuText = menuText or '<%s>'%_('None')
        self.menuText = menuText if '&' in menuText else '&' + menuText
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

    def addToMenu(self, menu, window, position=None):
        menuItem = wx.MenuItem(menu, self.id, self.menuText, self.helpText, 
            self.kind)
        self.menuItems.append(menuItem)
        self.addBitmapToMenuItem(menuItem)
        if position is None:
            menu.AppendItem(menuItem)
        else:
            menu.InsertItem(position, menuItem)
        self.bind(window, self.id)
        return self.id
    
    def addBitmapToMenuItem(self, menuItem):
        if self.bitmap2 and self.kind == wx.ITEM_CHECK and '__WXGTK__' != wx.Platform:
            bitmap1 = self.__getBitmap(self.bitmap) 
            bitmap2 = self.__getBitmap(self.bitmap2)
            menuItem.SetBitmaps(bitmap1, bitmap2)
        elif self.bitmap and self.kind == wx.ITEM_NORMAL:
            menuItem.SetBitmap(self.__getBitmap(self.bitmap))
    
    def removeFromMenu(self, menu, window):
        for menuItem in self.menuItems:
            if menuItem.GetMenu() == menu:
                self.menuItems.remove(menuItem)
                menuId = menuItem.GetId()
                menu.Remove(menuId)
                break
        self.unbind(window, menuId)
        
    def appendToToolBar(self, toolbar):
        self.toolbar = toolbar
        bitmap = self.__getBitmap(self.bitmap, wx.ART_TOOLBAR, 
                                  toolbar.GetToolBitmapSize())
        toolbar.AddLabelTool(self.id, '',
            bitmap, wx.NullBitmap, self.kind, 
            shortHelp=wx.MenuItem.GetLabelFromText(self.menuText),
            longHelp=self.helpText)
        self.bind(toolbar, self.id)
        return self.id

    def bind(self, window, itemId):
        window.Bind(wx.EVT_MENU, self.onCommandActivate, id=itemId)
        window.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI, id=itemId)

    def unbind(self, window, itemId):
        for eventType in [wx.EVT_MENU, wx.EVT_UPDATE_UI]:
            window.Unbind(eventType, id=itemId)
        
    def onCommandActivate(self, event, *args, **kwargs):
        ''' For Menu's and ToolBars, activating the command is not
            possible when not enabled, because menu items and toolbar
            buttons are disabled through onUpdateUI. For other controls such 
            as the ListCtrl and the TreeCtrl the EVT_UPDATE_UI event is not 
            sent, so we need an explicit check here. Otherwise hitting return 
            on an empty selection in the ListCtrl would bring up the 
            TaskEditor. '''
        if self.enabled(event):
            return self.doCommand(event, *args, **kwargs)
            
    def __call__(self, *args, **kwargs):
        return self.onCommandActivate(*args, **kwargs)
        
    def doCommand(self, event):
        raise NotImplementedError # pragma: no cover

    def onUpdateUI(self, event):
        event.Enable(bool(self.enabled(event)))
        if self.toolbar and (not self.helpText or self.menuText == '?'):
            self.updateToolHelp()
        
    def enabled(self, event): # pylint: disable-msg=W0613
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
            
    def updateMenuText(self, menuText):
        self.menuText = menuText
        if '__WXMSW__' == wx.Platform:
            for menuItem in self.menuItems[:]:
                menu = menuItem.GetMenu()
                pos = menu.GetMenuItems().index(menuItem)
                newMenuItem = wx.MenuItem(menu, self.id, menuText, self.helpText, self.kind)
                self.addBitmapToMenuItem(newMenuItem)
                menu.DeleteItem(menuItem)
                self.menuItems.remove(menuItem)
                self.menuItems.append(newMenuItem)
                menu.InsertItem(pos, newMenuItem)
        else:
            for menuItem in self.menuItems:
                menuItem.SetItemLabel(menuText)

    def mainWindow(self):
        return wx.GetApp().TopWindow
    
    def getMenuText(self):
        return self.menuText
    
    def getHelpText(self):
        return self.helpText

    def __getBitmap(self, bitmapName, bitmapType=wx.ART_MENU, bitmapSize=(16, 16)):
        return wx.ArtProvider_GetBitmap(bitmapName, bitmapType, bitmapSize)
    

class SettingsCommand(UICommand): # pylint: disable-msg=W0223
    ''' SettingsCommands are saved in the settings (a ConfigParser). '''

    def __init__(self, settings=None, setting=None, section='view', 
                 *args, **kwargs):
        self.settings = settings
        self.section = section
        self.setting = setting
        super(SettingsCommand, self).__init__(*args, **kwargs)


class BooleanSettingsCommand(SettingsCommand): # pylint: disable-msg=W0223
    def __init__(self, value=None, *args, **kwargs):
        self.value = value
        super(BooleanSettingsCommand, self).__init__(*args, **kwargs)
        
    def onUpdateUI(self, event):
        event.Check(self.isSettingChecked())
        super(BooleanSettingsCommand, self).onUpdateUI(event)

    def addToMenu(self, menu, window, position=None):
        menuId = super(BooleanSettingsCommand, self).addToMenu(menu, window, 
                                                              position)
        menuItem = menu.FindItemById(menuId)
        menuItem.Check(self.isSettingChecked())
        
    def isSettingChecked(self):
        raise NotImplementedError # pragma: no cover
    

class UICheckCommand(BooleanSettingsCommand):
    def __init__(self, *args, **kwargs):
        kwargs['bitmap'] = kwargs.get('bitmap', self.getBitmap())
        super(UICheckCommand, self).__init__(kind=wx.ITEM_CHECK, 
            *args, **kwargs)
        
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


class IOCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.iocontroller = kwargs.pop('iocontroller', None)
        super(IOCommand, self).__init__(*args, **kwargs)


class TaskListCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.taskList = kwargs.pop('taskList', None)
        super(TaskListCommand, self).__init__(*args, **kwargs)
        
        
class EffortListCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.effortList = kwargs.pop('effortList', None)
        super(EffortListCommand, self).__init__(*args, **kwargs)


class CategoriesCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories', None)
        super(CategoriesCommand, self).__init__(*args, **kwargs)


class NotesCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.notes = kwargs.pop('notes', None)
        super(NotesCommand, self).__init__(*args, **kwargs)


class AttachmentsCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.attachments = kwargs.pop('attachments', None)
        super(AttachmentsCommand, self).__init__(*args, **kwargs)


class ViewerCommand(UICommand): # pylint: disable-msg=W0223
    def __init__(self, *args, **kwargs):
        self.viewer = kwargs.pop('viewer', None)
        super(ViewerCommand, self).__init__(*args, **kwargs)

    def __eq__(self, other):
        return super(ViewerCommand, self).__eq__(other) and \
            self.viewer.settingsSection() == other.viewer.settingsSection()


# Mixins: 

class PopupButtonMixin(object):
    ''' Mix this with a UICommand for a toolbar pop-up menu. '''

    def doCommand(self, event): # pylint: disable-msg=W0613
        try:
            args = [self.__menu]
        except AttributeError:
            self.__menu = self.createPopupMenu() # pylint: disable-msg=W0201
            args = [self.__menu]
        if self.toolbar:
            args.append(self.menuXY())
        self.mainWindow().PopupMenu(*args) # pylint: disable-msg=W0142

    def menuXY(self):
        ''' Location to pop up the menu. '''
        return self.mainWindow().ScreenToClient((self.menuX(), self.menuY()))

    def menuX(self):
        buttonWidth = self.toolbar.GetToolSize()[0]
        mouseX = wx.GetMousePosition()[0]
        return mouseX - 0.5 * buttonWidth

    def menuY(self):
        toolbarY = self.toolbar.GetScreenPosition()[1]
        toolbarHeight = self.toolbar.GetSize()[1]
        return toolbarY + toolbarHeight
    
    def createPopupMenu(self):
        raise NotImplementedError # pragma: no cover


class NeedsSelectionMixin(object):
    def enabled(self, event):
        return super(NeedsSelectionMixin, self).enabled(event) and \
            self.viewer.curselection()


class NeedsSelectedCategorizableMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedCategorizableMixin, self).enabled(event) and \
            (self.viewer.curselectionIsInstanceOf(task.Task) or \
             self.viewer.curselectionIsInstanceOf(note.Note))


class NeedsOneSelectedItemMixin(object):
    def enabled(self, event):
        return super(NeedsOneSelectedItemMixin, self).enabled(event) and \
            len(self.viewer.curselection()) == 1


class NeedsSelectedCompositeMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedCompositeMixin, self).enabled(event) and \
            (self.viewer.curselectionIsInstanceOf(task.Task) or \
             self.viewer.curselectionIsInstanceOf(note.Note) or \
             self.viewer.curselectionIsInstanceOf(category.Category))
    

class NeedsOneSelectedCompositeItemMixin(NeedsOneSelectedItemMixin, 
                                         NeedsSelectedCompositeMixin):
    pass


class NeedsTaskOrEffortViewerMixin(object):
    def enabled(self, event):
        return super(NeedsTaskOrEffortViewerMixin, self).enabled(event) and \
            (self.viewer.isShowingTasks() or self.viewer.isShowingEffort())


class NeedsAttachmentViewerMixin(object):
    def enabled(self, event):
        return super(NeedsAttachmentViewerMixin, self).enabled(event) and \
            self.viewer.isShowingAttachments()


class NeedsSelectedTasksMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedTasksMixin, self).enabled(event) and \
            self.viewer.curselectionIsInstanceOf(task.Task)


class NeedsSelectedTasksOrEffortsMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedTasksOrEffortsMixin, self).enabled(event) and \
            (self.viewer.curselectionIsInstanceOf(task.Task) or \
             self.viewer.curselectionIsInstanceOf(effort.Effort))


class NeedsSelectedNoteOwnersMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedNoteOwnersMixin, self).enabled(event) and \
            (self.viewer.curselectionIsInstanceOf(task.Task) or \
             self.viewer.curselectionIsInstanceOf(category.Category) or \
             self.viewer.curselectionIsInstanceOf(attachment.Attachment))


class NeedsSelectedNoteOwnersMixinWithNotes(NeedsSelectedNoteOwnersMixin):
    def enabled(self, event):
        # pylint: disable-msg=E1101
        return super(NeedsSelectedNoteOwnersMixinWithNotes, self).enabled(event) and \
            any([item.notes() for item in self.viewer.curselection()])
            

class NeedsSelectedAttachmentOwnersMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedAttachmentOwnersMixin, self).enabled(event) and \
            (self.viewer.curselectionIsInstanceOf(task.Task) or \
             self.viewer.curselectionIsInstanceOf(category.Category) or \
             self.viewer.curselectionIsInstanceOf(note.Note))


class NeedsOneSelectedTaskMixin(NeedsSelectedTasksMixin, NeedsOneSelectedItemMixin):
    pass


class NeedsSelectionWithAttachmentsMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectionWithAttachmentsMixin, self).enabled(event) and \
            any(item.attachments() for item in self.viewer.curselection() if not isinstance(item, effort.Effort))


class NeedsSelectedEffortMixin(NeedsSelectionMixin):
    def enabled(self, event):
        return super(NeedsSelectedEffortMixin, self).enabled(event) and \
            self.viewer.curselectionIsInstanceOf(effort.Effort)


class NeedsSelectedAttachmentsMixin(NeedsAttachmentViewerMixin, NeedsSelectionMixin):
    pass


class NeedsAtLeastOneTaskMixin(object):
    def enabled(self, event): # pylint: disable-msg=W0613
        return len(self.taskList) > 0
    
    
class NeedsAtLeastOneCategoryMixin(object):
    def enabled(self, event): # pylint: disable-msg=W0613
        return len(self.categories) > 0
        
        
class NeedsItemsMixin(object):
    def enabled(self, event): # pylint: disable-msg=W0613
        return self.viewer.size() 


class NeedsTreeViewerMixin(object):
    def enabled(self, event):
        return super(NeedsTreeViewerMixin, self).enabled(event) and \
            self.viewer.isTreeViewer()


class NeedsDeletedItemsMixin(object):
    def enabled(self, event):
        return super(NeedsDeletedItemsMixin, self).enabled(event) and \
               self.iocontroller.hasDeletedItems()


# Commands:

class FileOpen(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileOpen, self).__init__(menuText=_('&Open...\tCtrl+O'),
            helpText=help.fileOpen, bitmap='fileopen', id=wx.ID_OPEN, 
            *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.open()


class RecentFileOpen(IOCommand):
    def __init__(self, *args, **kwargs):
        self.__filename = kwargs.pop('filename')
        index = kwargs.pop('index')
        super(RecentFileOpen, self).__init__(menuText='%d %s'%(index, self.__filename),
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
            helpText=help.fileClose, bitmap='close', id=wx.ID_CLOSE, 
            *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.close()


class FileSave(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileSave, self).__init__(menuText=_('&Save\tCtrl+S'),
            helpText=help.fileSave, bitmap='save', id=wx.ID_SAVE, 
            *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.save()
        
    def enabled(self, event):
        return self.iocontroller.needSave()


class FileMergeDiskChanges(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileMergeDiskChanges, self).__init__(menuText=_('Merge &disk changes\tCtrl+D'),
            helpText=help.fileMergeDiskChanges, bitmap='mergedisk', 
            *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.mergeDiskChanges()

    def enabled(self, event):
        return self.iocontroller.changedOnDisk()


class FileSaveAs(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveAs, self).__init__(menuText=_('S&ave as...\tShift+Ctrl+S'),
            helpText=help.fileSaveAs, bitmap='saveas', id=wx.ID_SAVEAS, 
            *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.saveas()
        

class FileSaveSelection(NeedsSelectedTasksMixin, IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveSelection, self).__init__(menuText=_('Sa&ve selection...'),
            helpText=_('Save the selected tasks to a separate file'), 
            bitmap='saveselection', *args, **kwargs)
    
    def doCommand(self, event):
        self.iocontroller.saveselection(self.viewer.curselection()) 


class FileSaveSelectedTaskAsTemplate(NeedsOneSelectedTaskMixin, IOCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(FileSaveSelectedTaskAsTemplate, self).__init__(\
            menuText=_('Save selected task as &template'),
            helpText=_('Save the selected task as a task template'),
            bitmap='saveselection', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.saveastemplate(self.viewer.curselection()[0])


class FileImportTemplate(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileImportTemplate, self).__init__(\
            menuText=_('&Import template...'),
            helpText=_('Import a new template from a template file'),
            bitmap='fileopen', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.importTemplate()


class FileEditTemplates(SettingsCommand, UICommand):
    def __init__(self, *args, **kwargs):
        super(FileEditTemplates, self).__init__(\
            menuText=_('Edit templates...'),
            helpText=_('Edit existing templates'), *args, **kwargs)

    def doCommand(self, event):
        dlg = dialog.templates.TemplatesDialog(self.settings, self.mainWindow(), 
                                               title=_('Edit templates'))
        dlg.Show()


class FilePurgeDeletedItems(NeedsDeletedItemsMixin, IOCommand):
    def __init__(self, *args, **kwargs):
        super(FilePurgeDeletedItems, self).__init__(\
            menuText=_('&Purge deleted items'),
            helpText=_('Actually delete deleted tasks and notes (see the SyncML chapter in Help)'),
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


class PrintPageSetup(SettingsCommand, UICommand):
    def __init__(self, *args, **kwargs):
        super(PrintPageSetup, self).__init__(\
            menuText=_('&Page setup...\tShift+Ctrl+P'),
            helpText=help.printPageSetup, bitmap='pagesetup', 
            id=wx.ID_PRINT_SETUP, *args, **kwargs)

    def doCommand(self, event):
        printerSettings = printer.PrinterSettings(self.settings)
        pageSetupDialog = wx.PageSetupDialog(self.mainWindow(), 
                                             printerSettings.pageSetupData)
        result = pageSetupDialog.ShowModal()
        if result == wx.ID_OK:
            printerSettings.updatePageSetupData(pageSetupDialog.GetPageSetupData())
        pageSetupDialog.Destroy()


class PrintPreview(ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(PrintPreview, self).__init__(\
            menuText=_('&Print preview...'), 
            helpText=_('Show a preview of what the print will look like'), 
            bitmap='printpreview', id=wx.ID_PREVIEW, *args, **kwargs)

    def doCommand(self, event):
        printout, printout2 = printer.Printout(self.viewer, self.settings, 
                                               twoPrintouts=True)
        printerSettings = printer.PrinterSettings(self.settings)
        preview = wx.PrintPreview(printout, printout2, 
                                  printerSettings.printData)
        previewFrame = wx.PreviewFrame(preview, self.mainWindow(), 
            _('Print preview'), size=(750, 700))
        previewFrame.Initialize()
        previewFrame.Show()
      

class Print(ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(Print, self).__init__(menuText=_('&Print...\tCtrl+P'), 
            helpText=help.print_, bitmap='print', id=wx.ID_PRINT, 
            *args, **kwargs)

    def doCommand(self, event): 
        printerSettings = printer.PrinterSettings(self.settings)
        printDialogData = wx.PrintDialogData(printerSettings.printData)
        printDialogData.EnableSelection(True)
        wxPrinter = wx.Printer(printDialogData)
        if not wxPrinter.PrintDialog(self.mainWindow()):
            return
        printout = printer.Printout(self.viewer, self.settings,
            printSelectionOnly=wxPrinter.PrintDialogData.Selection)
        # If the user checks the selection radio button, the ToPage property 
        # gets set to 1. Looks like a bug to me. The simple work-around is to
        # reset the ToPage property to the MaxPage value if necessary:
        if wxPrinter.PrintDialogData.Selection:
            wxPrinter.PrintDialogData.ToPage = wxPrinter.PrintDialogData.MaxPage
        wxPrinter.Print(self.mainWindow(), printout, prompt=False)
 
 
class FileExportCommand(IOCommand, SettingsCommand):    
    def doCommand(self, event):
        exportDialog = self.ExportDialogClass(self.mainWindow(), settings=self.settings) # pylint: disable-msg=E1101
        if wx.ID_OK == exportDialog.ShowModal():
            selectedViewer = exportDialog.selectedViewer()
            exportOptions = exportDialog.options()
            self.exportFunction()(selectedViewer, **exportOptions) # pylint: disable-msg=W0142
        exportDialog.Destroy()
    
    def exportFunction(self):
        ''' Return a function that does the actual export. The function should
            take the selected viewer as the first parameter and possibly a
            number of keyword arguments for export options. '''
        raise NotImplementedError # pragma: no cover
 

class FileExportAsHTML(FileExportCommand):
    ExportDialogClass = dialog.export.ExportAsHTMLDialog
    
    def __init__(self, *args, **kwargs):
        super(FileExportAsHTML, self).__init__(menuText=_('Export as &HTML...'), 
            helpText=_('Export items from a viewer in HTML format'),
            bitmap='exportashtml', *args, **kwargs)

    def exportFunction(self):
        return self.iocontroller.exportAsHTML


class FileExportAsCSV(FileExportCommand):
    ExportDialogClass = dialog.export.ExportAsCSVDialog
    
    def __init__(self, *args, **kwargs):
        super(FileExportAsCSV, self).__init__(menuText=_('Export as &CSV...'),
            helpText=_('Export items from a viewer in Comma Separated Values (CSV) format'),
            bitmap='exportascsv', *args, **kwargs)
        
    def exportFunction(self):
        return self.iocontroller.exportAsCSV


class FileExportAsICalendar(FileExportCommand):
    ExportDialogClass = dialog.export.ExportAsICalendarDialog
    
    def __init__(self, *args, **kwargs):
        super(FileExportAsICalendar, self).__init__(menuText=_('Export as &iCalendar...'),
            helpText=_('Export items from a viewer in iCalendar format'),
            bitmap='exportasvcal', *args, **kwargs)
     
    def exportFunction(self):
        return self.iocontroller.exportAsICalendar

    def enabled(self, event):
        return any(self.exportableViewer(viewer) for viewer in self.mainWindow().viewer)
        
    def exportableViewer(self, viewer):
        return viewer.isShowingTasks() or \
               (viewer.isShowingEffort() and not viewer.isShowingAggregatedEffort())


class FileExportAsTodoTxt(FileExportCommand):
    ExportDialogClass = dialog.export.ExportAsTodoTxtDialog
    
    def __init__(self, *args, **kwargs):
        super(FileExportAsTodoTxt, self).__init__(menuText=_('Export as &Todo.txt...'),
            helpText=_('Export items from a viewer in Todo.txt format (see todotxt.com)'),
            bitmap='exportascsv', *args, **kwargs)
        
    def exportFunction(self):
        return self.iocontroller.exportAsTodoTxt
    
    def enabled(self, event):
        return any(self.exportableViewer(viewer) for viewer in self.mainWindow().viewer)
    
    def exportableViewer(self, viewer):
        return viewer.isShowingTasks()
    
    
class FileImportCSV(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileImportCSV, self).__init__(menuText=_('&Import CSV...'),
            helpText=_('Import tasks from a Comma Separated Values (CSV) file'),
            bitmap='exportascsv', *args, **kwargs)

    def doCommand(self, event):
        filename = wx.FileSelector(_('Import CSV'), wildcard='*.csv')
        if filename:
            wiz = CSVImportWizard(filename, None, wx.ID_ANY, _('Import CSV'))
            if wiz.RunWizard():
                self.iocontroller.importCSV(**wiz.GetOptions())
                
                
class FileImportTodoTxt(IOCommand):
    def __init__(self, *args, **kwargs):
        super(FileImportTodoTxt, self).__init__(menuText=_('&Import Todo.txt...'),
            helpText=_('Import tasks from a Todo.txt (see todotxt.com) file'),
            bitmap='exportascsv', *args, **kwargs)

    def doCommand(self, event):
        filename = wx.FileSelector(_('Import Todo.txt'), wildcard='*.txt')
        if filename:
            self.iocontroller.importTodoTxt(filename)
            

class FileSynchronize(IOCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(FileSynchronize, self).__init__(menuText=_('S&yncML synchronization...'),
            helpText=_('Synchronize with a SyncML server'),
            bitmap='arrows_looped_icon', *args, **kwargs)

    def doCommand(self, event):
        self.iocontroller.synchronize()


class FileQuit(UICommand):
    def __init__(self, *args, **kwargs):
        super(FileQuit, self).__init__(menuText=_('&Quit\tCtrl+Q'), 
            helpText=help.fileQuit, bitmap='exit', id=wx.ID_EXIT, 
            *args, **kwargs)

    def doCommand(self, event):
        self.mainWindow().Close(force=True)


def getUndoMenuText():
    return '%s\tCtrl+Z'%patterns.CommandHistory().undostr(_('&Undo')) 

class EditUndo(UICommand):
    def __init__(self, *args, **kwargs):
        super(EditUndo, self).__init__(menuText=getUndoMenuText(),
            helpText=help.editUndo, bitmap='undo', id=wx.ID_UNDO, 
            *args, **kwargs)
            
    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Undo()
        else:
            patterns.CommandHistory().undo()

    def onUpdateUI(self, event):
        self.updateMenuText(getUndoMenuText())
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
            helpText=help.editRedo, bitmap='redo', id=wx.ID_REDO, 
            *args, **kwargs)

    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            windowWithFocus.Redo()
        else:
            patterns.CommandHistory().redo()

    def onUpdateUI(self, event):
        self.updateMenuText(getRedoMenuText())
        super(EditRedo, self).onUpdateUI(event)

    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if isinstance(windowWithFocus, wx.TextCtrl):
            return windowWithFocus.CanRedo()
        else:
            return patterns.CommandHistory().hasFuture() and \
                super(EditRedo, self).enabled(event)


class EditCut(NeedsSelectionMixin, ViewerCommand):    
    def __init__(self, *args, **kwargs):     
        super(EditCut, self).__init__(menuText=_('Cu&t\tCtrl+X'), 
            helpText=help.editCut, bitmap='cut', *args, **kwargs)

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


class EditCopy(NeedsSelectionMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditCopy, self).__init__(menuText=_('&Copy\tCtrl+C'), 
            helpText=help.editCopy, bitmap='copy', *args, **kwargs)

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
            helpText=help.editPaste, bitmap='paste', id=wx.ID_PASTE, 
            *args, **kwargs)

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
            return command.Clipboard() and super(EditPaste, self).enabled(event)


class EditPasteAsSubItem(NeedsSelectedCompositeMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(EditPasteAsSubItem, self).__init__(
            menuText=_('P&aste as subitem\tShift+Ctrl+V'), 
            helpText=help.editPasteAsSubitem, bitmap='pasteintotask', 
            *args, **kwargs)

    def doCommand(self, event):
        pasteCommand = command.PasteAsSubItemCommand(
            items=self.viewer.curselection())
        pasteCommand.do()

    def enabled(self, event):
        if not (super(EditPasteAsSubItem, self).enabled(event) and command.Clipboard()):
            return False
        targetClass = self.viewer.curselection()[0].__class__
        for item in command.Clipboard().peek():
            if item.__class__ != targetClass:
                return False
        return True


class EditPreferences(SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(EditPreferences, self).__init__(menuText=_('&Preferences...\tAlt+P'),
            helpText=help.editPreferences, bitmap='wrench_icon',
            id=wx.ID_PREFERENCES, *args, **kwargs)
            
    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        editor = dialog.preferences.Preferences(parent=self.mainWindow(), 
            title=_('Preferences'), settings=self.settings)
        editor.Show(show=show)


class EditSyncPreferences(IOCommand):
    def __init__(self, *args, **kwargs):
        super(EditSyncPreferences, self).__init__(menuText=_('&SyncML preferences...'),
            helpText=_('Edit SyncML preferences'), bitmap='arrows_looped_icon',
            *args, **kwargs)

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        editor = dialog.syncpreferences.SyncMLPreferences(parent=self.mainWindow(),
            iocontroller=self.iocontroller,
            title=_('SyncML preferences'))
        editor.Show(show=show)


class SelectAll(NeedsItemsMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(SelectAll, self).__init__(menuText=_('&All\tCtrl+A'),
            helpText=help.editSelectAll, bitmap='selectall', id=wx.ID_SELECTALL, 
            *args, **kwargs)
        
    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if self.windowIsTextCtrl(windowWithFocus):
            windowWithFocus.SetSelection(-1, -1) # Select all text
        else:
            self.viewer.selectall()
            
    @staticmethod
    def windowIsTextCtrl(window):
        return isinstance(window, wx.TextCtrl) or \
               isinstance(window, hypertreelist.EditCtrl)



class ClearSelection(NeedsSelectionMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ClearSelection, self).__init__(menuText=_('&Clear selection'), 
            helpText=_('Unselect all items'), *args, **kwargs)

    def doCommand(self, event):
        self.viewer.clearselection()


class ResetFilter(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ResetFilter, self).__init__(menuText=_('&Clear all filters\tShift-Ctrl-R'),
            helpText=help.resetFilter, bitmap='viewalltasks', *args, **kwargs)
    
    def doCommand(self, event):
        self.viewer.resetFilter()
        
        
class ResetCategoryFilter(NeedsAtLeastOneCategoryMixin, CategoriesCommand):
    def __init__(self, *args, **kwargs):
        super(ResetCategoryFilter, self).__init__(menuText=_('&Reset all categories\tCtrl-R'),
            helpText=help.resetCategoryFilter, *args, **kwargs)

    def doCommand(self, event):
        self.categories.resetAllFilteredCategories()
        
        
class ToggleCategoryFilter(UICommand):
    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        subject = self.category.subject()
        # Would like to use wx.ITEM_RADIO for mutually exclusive categories, but
        # a menu with radio items always has to have at least of the items 
        # checked, while we allow none of the mutually exclusive categories to
        # be checked. Dynamically changing between wx.ITEM_CHECK and 
        # wx.ITEM_RADIO would be a work-around in theory, using wx.ITEM_CHECK 
        # when none of the mutually exclusive categories is checked and 
        # wx.ITEM_RADIO otherwise, but dynamically changing the type of menu 
        # items isn't possible. Hence, we use wx.ITEM_CHECK, even for mutual 
        # exclusive categories.
        kind = wx.ITEM_CHECK
        super(ToggleCategoryFilter, self).__init__(menuText='&' + subject,
            helpText=_('Show/hide items belonging to %s')%subject, kind=kind, 
            *args, **kwargs)

    def doCommand(self, event):
        self.category.setFiltered(event.IsChecked())
        

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
        
        
class ViewEffortViewerForSelectedTask(NeedsOneSelectedTaskMixin, SettingsCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        self.viewerClass = viewer.EffortViewer
        self.taskFile = kwargs.pop('taskFile')
        kwargs['bitmap'] = viewer.EffortViewer.defaultBitmap
        super(ViewEffortViewerForSelectedTask, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        viewer.addOneViewer(self.viewer, self.taskFile, self.settings, 
                            self.viewerClass, tasksToShowEffortFor=task.TaskList(self.viewer.curselection()))
        

class RenameViewer(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(RenameViewer, self).__init__(menuText=_('&Rename viewer...'),
            helpText=_('Rename the selected viewer'), *args, **kwargs)
        
    def doCommand(self, event):
        activeViewer = self.viewer.activeViewer()
        viewerNameDialog = wx.TextEntryDialog(self.mainWindow(), 
            _('New title for the viewer:'), _('Rename viewer'), 
            activeViewer.title())
        if viewerNameDialog.ShowModal() == wx.ID_OK:
            activeViewer.setTitle(viewerNameDialog.GetValue())
        viewerNameDialog.Destroy()
        
    def enabled(self, event):
        return bool(self.viewer.activeViewer())
        
        
class ActivateViewer(ViewerCommand):
    def __init__(self, *args, **kwargs):
        self.direction = kwargs.pop('forward')
        super(ActivateViewer, self).__init__(*args, **kwargs)

    def doCommand(self, event):
        self.viewer.containerWidget.advanceSelection(self.direction)
        
    def enabled(self, event):
        return self.viewer.containerWidget.viewerCount() > 1
        

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
        columnIndex = widget.HitTest(wx.Point(x, y))[2]
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
                        
    
class ViewExpandAll(NeedsTreeViewerMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewExpandAll, self).__init__( \
            menuText=_('&Expand all items\tShift+Ctrl+E'),
            helpText=help.viewExpandAll, *args, **kwargs)

    def enabled(self, event):
        return super(ViewExpandAll, self).enabled(event) and \
            self.viewer.isAnyItemExpandable()
                
    def doCommand(self, event):
        self.viewer.expandAll()
            

class ViewCollapseAll(NeedsTreeViewerMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(ViewCollapseAll, self).__init__( \
            menuText=_('&Collapse all items\tShift+Ctrl+C'),
            helpText=help.viewCollapseAll, *args, **kwargs)
    
    def enabled(self, event):
        return super(ViewCollapseAll, self).enabled(event) and \
            self.viewer.isAnyItemCollapsable()
    
    def doCommand(self, event):
        self.viewer.collapseAll()


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
            menuText=_('Sort &case sensitive'),
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


class ViewerFilterByDueDateTime(ViewerCommand, UIRadioCommand):
    def isSettingChecked(self):
        return self.viewer.isFilteredByDueDateTime(self.value)
    
    def doCommand(self, event):
        self.viewer.setFilteredByDueDateTime(self.value)


class ViewerFilterByCompletionDateTime(ViewerCommand, UIRadioCommand):
    def isSettingChecked(self):
        return self.viewer.isFilteredByCompletionDateTime(self.value)
    
    def doCommand(self, event):
        self.viewer.setFilteredByCompletionDateTime(self.value)


class ViewerFilterByStartDateTime(ViewerCommand, UIRadioCommand):
    def isSettingChecked(self):
        return self.viewer.isFilteredByStartDateTime(self.value)
    
    def doCommand(self, event):
        self.viewer.setFilteredByStartDateTime(self.value)
        

class ViewerHideInactiveTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideInactiveTasks, self).__init__(menuText=_('Hide &inactive tasks'), 
            helpText=_('Show/hide inactive tasks (tasks with a start date in the future)'),
            *args, **kwargs)
        
    def isSettingChecked(self):
        return not self.viewer.isFilteredByStartDateTime('Never')
        
    def doCommand(self, event):
        self.viewer.freeze()
        try:
            filter = 'Always' if self._isMenuItemChecked(event) else 'Never'
            self.viewer.setFilteredByStartDateTime(filter)
        finally:
            self.viewer.thaw()


class ViewerHideActiveTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideActiveTasks, self).__init__(menuText=_('Hide &active tasks'), 
            helpText=_('Show/hide active tasks (tasks with a start date in the past that are not completed)'),
            *args, **kwargs)
        
    def isSettingChecked(self):
        return self.viewer.isHidingActiveTasks()
        
    def doCommand(self, event):
        self.viewer.hideActiveTasks(self._isMenuItemChecked(event))

        
class ViewerHideCompletedTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideCompletedTasks, self).__init__(menuText=_('Hide &completed tasks'), 
            helpText=_('Show/hide completed tasks'), *args, **kwargs)
         
    def isSettingChecked(self):
        return not self.viewer.isFilteredByCompletionDateTime('Never')
        
    def doCommand(self, event):
        self.viewer.freeze()
        try:
            filter = 'Always' if self._isMenuItemChecked(event) else 'Never'
            self.viewer.setFilteredByCompletionDateTime(filter)
        finally:
            self.viewer.thaw()


class ViewerHideCompositeTasks(ViewerCommand, UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(ViewerHideCompositeTasks, self).__init__(menuText=_('Hide c&omposite tasks'),
            helpText=_('Show/hide tasks with subtasks in list mode'), 
            *args, **kwargs)
            
    def isSettingChecked(self):
        return self.viewer.isHidingCompositeTasks()
        
    def doCommand(self, event):
        self.viewer.hideCompositeTasks(self._isMenuItemChecked(event))

    def enabled(self, event):
        return not self.viewer.isTreeViewer()


class Edit(NeedsSelectionMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(Edit, self).__init__(menuText=_('&Edit...\tRETURN'),
            helpText=_('Edit the selected item(s)'), bitmap='edit', 
            *args, **kwargs)

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        windowWithFocus = wx.Window.FindFocus()
        editCtrl = self.findEditCtrl(windowWithFocus)
        if editCtrl:
            editCtrl.AcceptChanges()
            if editCtrl:
                editCtrl.Finish()
            return
        try:
            columnName = event.columnName
        except AttributeError:
            columnName = ''
        editor = self.viewer.editItemDialog(self.viewer.curselection(), 
                                            self.bitmap, columnName)
        editor.Show(show)    

    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if self.findEditCtrl(windowWithFocus):
            return True
        elif '__WXMAC__' == wx.Platform and isinstance(windowWithFocus, wx.TextCtrl):
            return False
        else:
            return super(Edit, self).enabled(event)        

    def findEditCtrl(self, windowWithFocus):
        while windowWithFocus:
            if isinstance(windowWithFocus, thirdparty.hypertreelist.EditCtrl):
                break
            windowWithFocus = windowWithFocus.GetParent()
        return windowWithFocus


class EditTrackedTasks(TaskListCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(EditTrackedTasks, self).__init__(menuText=_('Edit &tracked task...\tShift-Alt-T'),
            helpText=_('Edit the currently tracked task(s)'), bitmap='edit',
            *args, **kwargs)
        
    def doCommand(self, event, show=True):
        editTaskDialog = dialog.editor.TaskEditor(self.mainWindow(), 
            command.EditTaskCommand(self.taskList, self.taskList.tasksBeingTracked()), 
            self.settings, self.taskList, self.mainWindow().taskFile, 
            bitmap=self.bitmap)
        editTaskDialog.Show(show)
        return editTaskDialog # for testing purposes
        
    def enabled(self, event):
        return any(self.taskList.tasksBeingTracked())
        

class Delete(NeedsSelectionMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(Delete, self).__init__(menuText=_('&Delete\tDEL'),
            helpText=_('Delete the selected item(s)'), bitmap='delete', 
            *args, **kwargs)
        
    def doCommand(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if self.windowIsTextCtrl(windowWithFocus):
            # Simulate Delete key press
            fromIndex, toIndex = windowWithFocus.GetSelection()
            if fromIndex == toIndex: 
                pos = windowWithFocus.GetInsertionPoint()
                fromIndex, toIndex = pos, pos+1
            windowWithFocus.Remove(fromIndex, toIndex)            
        else:
            deleteCommand = self.viewer.deleteItemCommand()
            deleteCommand.do()
        
    def enabled(self, event):
        windowWithFocus = wx.Window.FindFocus()
        if self.windowIsTextCtrl(windowWithFocus):
            return True
        else:
            return super(Delete, self).enabled(event)
        
    @staticmethod
    def windowIsTextCtrl(window):
        return isinstance(window, wx.TextCtrl) or \
               isinstance(window, hypertreelist.EditCtrl)


class TaskNew(TaskListCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        self.taskKeywords = kwargs.pop('taskKeywords', dict())
        taskList = kwargs['taskList']
        if 'menuText' not in kwargs: # Provide for subclassing
            kwargs['menuText'] = taskList.newItemMenuText
            kwargs['helpText'] = taskList.newItemHelpText
        super(TaskNew, self).__init__(bitmap='new', *args, **kwargs)

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        newTaskCommand = command.NewTaskCommand(self.taskList, 
            categories=self.categoriesForTheNewTask(), 
            prerequisites=self.prerequisitesForTheNewTask(),
            dependencies=self.dependenciesForTheNewTask(), 
            **self.taskKeywords)
        newTaskCommand.do() 
        newTaskDialog = dialog.editor.TaskEditor(self.mainWindow(),
            newTaskCommand.items, self.settings, self.taskList, 
            self.mainWindow().taskFile, bitmap=self.bitmap)
        newTaskDialog.Show(show)
        return newTaskDialog # for testing purposes

    def categoriesForTheNewTask(self):
        return self.mainWindow().taskFile.categories().filteredCategories()

    def prerequisitesForTheNewTask(self):
        return []

    def dependenciesForTheNewTask(self):
        return []
    

class TaskNewFromTemplate(TaskNew):
    def __init__(self, filename, *args, **kwargs):
        super(TaskNewFromTemplate, self).__init__(*args, **kwargs)
        self.__filename = filename
        templateTask = self.__readTemplate()
        self.menuText = '&' + templateTask.subject() # pylint: disable-msg=E1103

    def __readTemplate(self):
        return persistence.TemplateXMLReader(file(self.__filename,
                                                  'rU')).read()

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        # The task template is read every time because it's the
        # TemplateXMLReader that evaluates dynamic values (Now()
        # should be evaluated at task creation for instance).
        templateTask = self.__readTemplate()
        kwargs = templateTask.__getcopystate__()  # pylint: disable-msg=E1103
        kwargs['categories'] = self.categoriesForTheNewTask()
        newTaskCommand = command.NewTaskCommand(self.taskList, **kwargs)
        newTaskCommand.do()
        # pylint: disable-msg=W0142
        newTaskDialog = dialog.editor.TaskEditor(self.mainWindow(), 
            newTaskCommand.items, self.settings, self.taskList, 
            self.mainWindow().taskFile, bitmap=self.bitmap)
        newTaskDialog.Show(show)
        return newTaskDialog # for testing purposes
   
   
class TaskNewFromTemplateButton(PopupButtonMixin, TaskListCommand, SettingsCommand):
    def createPopupMenu(self):
        import menu
        return menu.TaskTemplateMenu(self.mainWindow(), self.taskList, 
                                     self.settings)

    def getMenuText(self):
        return _('New task from &template')

    def getHelpText(self):
        return _('Create a new task from a template')


class NewTaskWithSelectedCategories(TaskNew, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(NewTaskWithSelectedCategories, self).__init__(\
            menuText=_('New task with selected &categories...'),
            helpText=_('Insert a new task with the selected categories checked'),
            *args, **kwargs)

    def categoriesForTheNewTask(self):
        return self.viewer.curselection()
    
    
class NewTaskWithSelectedTasksAsPrerequisites(NeedsSelectedTasksMixin, TaskNew, 
                                              ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(NewTaskWithSelectedTasksAsPrerequisites, self).__init__(
            menuText=_('New task with selected tasks as &prerequisites...'),
            helpText=_('Insert a new task with the selected tasks as prerequisite tasks'),
            *args, **kwargs)

    def prerequisitesForTheNewTask(self):
        return self.viewer.curselection()
    

class NewTaskWithSelectedTasksAsDependencies(NeedsSelectedTasksMixin, TaskNew,
                                             ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(NewTaskWithSelectedTasksAsDependencies, self).__init__(
            menuText=_('New task with selected tasks as &dependencies...'),
            helpText=_('Insert a new task with the selected tasks as dependent tasks'),
            *args, **kwargs)

    def dependenciesForTheNewTask(self):
        return self.viewer.curselection()
    

class NewSubItem(NeedsOneSelectedCompositeItemMixin, ViewerCommand):
    shortcut = ('\tCtrl+INS' if '__WXMSW__' == wx.Platform else '\tShift+Ctrl+N')
    defaultMenuText = _('New &subitem...') + shortcut   
    labels = {task.Task: _('New &subtask...'),
              note.Note: _('New &subnote...'),
              category.Category: _('New &subcategory...')}
            
    def __init__(self, *args, **kwargs):
        super(NewSubItem, self).__init__(menuText=self.defaultMenuText,
            helpText=_('Insert a new subitem of the selected item'),
            bitmap='newsub', *args, **kwargs)
    
    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        self.viewer.newSubItemDialog(bitmap=self.bitmap).Show(show)
        
    def onUpdateUI(self, event):
        super(NewSubItem, self).onUpdateUI(event)
        self.updateMenuText(self.__menuText())

    def __menuText(self):
        for class_ in self.labels:
            if self.viewer.curselectionIsInstanceOf(class_):
                return self.labels[class_] + self.shortcut
        return self.defaultMenuText
    

class TaskToggleCompletion(NeedsSelectedTasksMixin, ViewerCommand):
    defaultMenuText = _('&Mark task completed\tCtrl+RETURN')
    defaultHelpText = _('Mark the selected task(s) completed')
    alternativeMenuText = _('&Mark task uncompleted\tCtrl+RETURN')
    alternativeHelpText = _('Mark the selected task(s) uncompleted')
    
    def __init__(self, *args, **kwargs):
        super(TaskToggleCompletion, self).__init__(bitmap='markuncompleted',
            bitmap2='markcompleted', menuText=self.defaultMenuText,
            helpText=self.defaultHelpText,
            kind=wx.ITEM_CHECK, *args, **kwargs)
        self.currentBitmap = None # Don't know yet what our bitmap is
                
    def doCommand(self, event):
        markCompletedCommand = command.MarkCompletedCommand( \
            self.viewer.presentation(), self.viewer.curselection())
        markCompletedCommand.do()
            
    def onUpdateUI(self, event):
        super(TaskToggleCompletion, self).onUpdateUI(event)
        allSelectedTasksAreCompleted = self.allSelectedTasksAreCompleted()
        self.updateToolState(allSelectedTasksAreCompleted)
        bitmapName = self.bitmap if allSelectedTasksAreCompleted else self.bitmap2
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
        menuText = self.getMenuText(allSelectedTasksAreCompleted)
        helpText = self.getHelpText(allSelectedTasksAreCompleted)
        for menuItem in self.menuItems:
            menuItem.Check(allSelectedTasksAreCompleted)
            menuItem.SetItemLabel(menuText)
            menuItem.SetHelp(helpText)
        
    def getMenuText(self, allSelectedTasksAreCompleted=None): # pylint: disable-msg=W0221
        if allSelectedTasksAreCompleted is None:
            allSelectedTasksAreCompleted = self.allSelectedTasksAreCompleted()
        return self.alternativeMenuText if allSelectedTasksAreCompleted else self.defaultMenuText
        
    def getHelpText(self, allSelectedTasksAreCompleted=None): # pylint: disable-msg=W0221
        if allSelectedTasksAreCompleted is None:
            allSelectedTasksAreCompleted = self.allSelectedTasksAreCompleted()
        return self.alternativeHelpText if allSelectedTasksAreCompleted else self.defaultHelpText
        
    def allSelectedTasksAreCompleted(self):
        if super(TaskToggleCompletion, self).enabled(None) and \
           len(self.viewer.curselection()) < 20:
            for selectedTask in self.viewer.curselection():
                if not selectedTask.completed():
                    return False
            return True
        else:
            return False

    
class TaskMaxPriority(NeedsSelectedTasksMixin, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMaxPriority, self).__init__(
            menuText=_('&Maximize priority\tShift+Ctrl+I'),
            helpText=help.taskMaxPriority, bitmap='maxpriority', 
            *args, **kwargs)
        
    def doCommand(self, event):
        maxPriority = command.MaxPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        maxPriority.do()
    

class TaskMinPriority(NeedsSelectedTasksMixin, TaskListCommand, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(TaskMinPriority, self).__init__(
            menuText=_('&Minimize priority\tShift+Ctrl+D'),
            helpText=help.taskMinPriority, bitmap='minpriority', 
            *args, **kwargs)
        
    def doCommand(self, event):
        minPriority = command.MinPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        minPriority.do()


class TaskIncPriority(NeedsSelectedTasksMixin, TaskListCommand, ViewerCommand):    
    def __init__(self, *args, **kwargs):
        super(TaskIncPriority, self).__init__(
            menuText=_('&Increase priority\tCtrl+I'),
            helpText=help.taskIncreasePriority, bitmap='incpriority', 
            *args, **kwargs)
        
    def doCommand(self, event):
        incPriority = command.IncPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        incPriority.do()


class TaskDecPriority(NeedsSelectedTasksMixin, TaskListCommand, ViewerCommand):    
    def __init__(self, *args, **kwargs):
        super(TaskDecPriority, self).__init__(
            menuText=_('&Decrease priority\tCtrl+D'),
            helpText=help.taskDecreasePriority, bitmap='decpriority',
            *args, **kwargs)
        
    def doCommand(self, event):
        decPriority = command.DecPriorityCommand(self.taskList, 
                                                 self.viewer.curselection())
        decPriority.do()


class DragAndDropCommand(ViewerCommand):
    def onCommandActivate(self, dropItem, dragItems, part): # pylint: disable-msg=W0221
        ''' Override onCommandActivate to be able to accept two items instead
            of one event. '''
        self.doCommand(dropItem, dragItems, part)

    def doCommand(self, dropItem, dragItems, part): # pylint: disable-msg=W0221
        dragAndDropCommand = self.createCommand(dropItem=dropItem, dragItems=dragItems, part=part)
        if dragAndDropCommand.canDo():
            dragAndDropCommand.do()
            
    def createCommand(self, dropItem, dragItems, part):
        raise NotImplementedError # pragma: no cover
    

class TaskDragAndDrop(DragAndDropCommand, TaskListCommand):
    def createCommand(self, dropItem, dragItems, part):
        return command.DragAndDropTaskCommand(self.taskList, dragItems, 
                                              drop=[dropItem], part=part)
        

class ToggleCategory(NeedsSelectedCategorizableMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        subject = self.category.subject()
        # Would like to use wx.ITEM_RADIO for mutually exclusive categories, but
        # a menu with radio items always has to have at least of the items 
        # checked, while we allow none of the mutually exclusive categories to
        # be checked. Dynamically changing between wx.ITEM_CHECK and 
        # wx.ITEM_RADIO would be a work-around in theory, using wx.ITEM_CHECK 
        # when none of the mutually exclusive categories is checked and 
        # wx.ITEM_RADIO otherwise, but dynamically changing the type of menu 
        # items isn't possible. Hence, we use wx.ITEM_CHECK, even for mutual 
        # exclusive categories.
        kind = wx.ITEM_CHECK
        super(ToggleCategory, self).__init__(menuText='&' + subject,
            helpText=_('Toggle %s')%subject, kind=kind, *args, **kwargs)
        
    def doCommand(self, event):
        check = command.ToggleCategoryCommand(category=self.category,
                                              items=self.viewer.curselection())
        check.do()
        
    def onUpdateUI(self, event):
        super(ToggleCategory, self).onUpdateUI(event)
        if self.enabled(event):
            check = self.category in self.viewer.curselection()[0].categories()
            for menuItem in self.menuItems:
                menuItem.Check(check)

    def enabled(self, event):
        viewerHasSelection = super(ToggleCategory, self).enabled(event)
        if not viewerHasSelection or self.viewer.isShowingCategories():
            return False
        selectionCategories = self.viewer.curselection()[0].categories()
        for ancestor in self.category.ancestors():
            if ancestor.isMutualExclusive() and ancestor not in selectionCategories:
                return False # Not all mutually exclusive ancestors are checked
        return True # All mutually exclusive ancestors are checked
    

class Mail(NeedsSelectionMixin, ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(menuText=_('&Mail...\tCtrl-M'),
           helpText=help.mailItem, bitmap='envelope_icon', *args, **kwargs)

    def doCommand(self, event, mail=sendMail, showerror=wx.MessageBox): # pylint: disable-msg=W0221
        items = self.viewer.curselection()
        subject = self.subject(items)
        body = self.body(items)
        self.mail(subject, body, mail, showerror)

    def subject(self, items):
        assert items
        if len(items) > 2:
            return _('Several things')
        elif len(items) == 2:
            subjects = [item.subject(recursive=True) for item in items]
            return ' '.join([subjects[0], _('and'), subjects[1]])
        else:
            return items[0].subject(recursive=True)
        
    def body(self, items):
        if len(items) > 1:
            bodyLines = []
            for item in items:
                bodyLines.extend(self.itemToLines(item))
        else:
            bodyLines = items[0].description().splitlines()
        return '\r\n'.join(bodyLines)
    
    def itemToLines(self, item):
        lines = []
        subject = item.subject(recursive=True)
        lines.append(subject)
        if item.description():
            lines.extend(item.description().splitlines())
            lines.extend('\r\n')
        return lines
    
    def mail(self, subject, body, mail, showerror):
        try:
            mail('', subject, body)
        except:
            # Try again with a dummy recipient:
            try:
                mail('recipient@domain.com', subject, body)
            except Exception, reason: # pylint: disable-msg=W0703
                showerror(_('Cannot send email:\n%s')%reason, 
                      caption=_('%s mail error')%meta.name, 
                      style=wx.ICON_ERROR)        
 

class AddNote(NeedsSelectedNoteOwnersMixin, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(AddNote, self).__init__(menuText=_('Add &note...\tCtrl+B'),
            helpText=help.addNote, bitmap='new', *args, **kwargs)
            
    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        addNoteCommand = command.AddNoteCommand(self.viewer.presentation(), 
                                                self.viewer.curselection())
        addNoteCommand.do()
        editDialog = dialog.editor.NoteEditor(self.mainWindow(), 
            addNoteCommand.items, self.settings, self.viewer.presentation(),  
            self.mainWindow().taskFile, bitmap=self.bitmap)
        editDialog.Show(show)
        return editDialog # for testing purposes
    
    
class OpenAllNotes(NeedsSelectedNoteOwnersMixinWithNotes, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(OpenAllNotes, self).__init__(menuText=_('Open all notes...\tShift+Ctrl+B'),
            helpText=help.openAllNotes, bitmap='edit', *args, **kwargs)
        
    def doCommand(self, event):
        for item in self.viewer.curselection():
            for note in item.notes():
                editDialog = dialog.editor.NoteEditor(self.mainWindow(),
                    [note], self.settings, self.viewer.presentation(), 
                    self.mainWindow().taskFile, bitmap=self.bitmap)
                editDialog.Show()


class EffortNew(NeedsAtLeastOneTaskMixin, ViewerCommand, EffortListCommand, 
                TaskListCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        effortList = kwargs['effortList']
        super(EffortNew, self).__init__(bitmap='new',  
            menuText=effortList.newItemMenuText, 
            helpText=effortList.newItemHelpText, *args, **kwargs)

    def doCommand(self, event, show=True):
        if self.viewer and self.viewer.isShowingTasks() and self.viewer.curselection():
            selectedTasks = self.viewer.curselection()
        elif self.viewer and self.viewer.isShowingEffort():
            selectedEfforts = self.viewer.curselection()
            if selectedEfforts:
                selectedTasks = [selectedEfforts[0].task()]
            else:
                selectedTasks = [self.firstTask(self.viewer.domainObjectsToView())]
        else:
            selectedTasks = [self.firstTask(self.taskList)]

        newEffortCommand = command.NewEffortCommand(self.effortList, selectedTasks)
        newEffortCommand.do()
        newEffortDialog = dialog.editor.EffortEditor(self.mainWindow(), 
            newEffortCommand.items, self.settings, self.effortList, 
            self.mainWindow().taskFile, bitmap=self.bitmap)
        if show:
            newEffortDialog.Show()
        return newEffortDialog

    @staticmethod    
    def firstTask(tasks):
        subjectDecoratedTasks = [(eachTask.subject(recursive=True), 
            eachTask) for eachTask in tasks]
        subjectDecoratedTasks.sort()
        return subjectDecoratedTasks[0][1]


class EffortStart(NeedsSelectedTasksMixin, ViewerCommand, TaskListCommand):
    ''' UICommand to start tracking effort for the selected task(s). '''
    
    def __init__(self, *args, **kwargs):
        super(EffortStart, self).__init__(bitmap='clock_icon',
            menuText=_('&Start tracking effort\tCtrl-T'), 
            helpText=help.effortStart, *args, **kwargs)
    
    def doCommand(self, event):
        start = command.StartEffortCommand(self.taskList, 
            self.viewer.curselection())
        start.do()
        
    def enabled(self, event):
        return super(EffortStart, self).enabled(event) and \
            any(not task.completed() and not task.isBeingTracked() \
                for task in self.viewer.curselection())


class EffortStartForEffort(NeedsSelectedEffortMixin, ViewerCommand, 
                           TaskListCommand):
    ''' UICommand to start tracking for the task(s) of selected effort(s). '''

    def __init__(self, *args, **kwargs): 
        super(EffortStartForEffort, self).__init__(bitmap='clock_icon',
            menuText=_('&Start tracking effort'),
            helpText=_('Start tracking effort for the task(s) of the selected effort(s)'), *args, **kwargs)
        
    def doCommand(self, event):
        start = command.StartEffortCommand(self.taskList, self.trackableTasks())
        start.do()

    def enabled(self, event):
        return super(EffortStartForEffort, self).enabled(event) and \
            self.trackableTasks()

    def trackableTasks(self):
        tasks = set([effort.task() for effort in self.viewer.curselection()])
        return [task for task in tasks if not task.completed() \
                and not task.isBeingTracked()]


class EffortStartForTask(TaskListCommand):
    ''' UICommand to start tracking for a specific task. This command can
        be used to build a menu with separate menu items for all tasks. 
        See gui.menu.StartEffortForTaskMenu. '''
        
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task')
        subject = self.task.subject() or _('(No subject)') 
        super(EffortStartForTask, self).__init__( \
            bitmap=self.task.icon(recursive=True), menuText='&'+subject,
            helpText=_('Start tracking effort for %s')%subject, 
            *args, **kwargs)
        
    def doCommand(self, event):
        start = command.StartEffortCommand(self.taskList, [self.task])
        start.do()
        
    def enabled(self, event):
        return not self.task.isBeingTracked() and not self.task.completed()


class EffortStartButton(PopupButtonMixin, TaskListCommand):
    def __init__(self, *args, **kwargs):
        kwargs['taskList'] = base.filter.DeletedFilter(kwargs['taskList'])
        super(EffortStartButton, self).__init__(bitmap='clock_menu_icon',
            menuText=_('&Start tracking effort'),
            helpText=_('Select a task via the menu and start tracking effort for it'),
            *args, **kwargs)

    def createPopupMenu(self):
        import menu
        return menu.StartEffortForTaskMenu(self.mainWindow(), self.taskList)

    def enabled(self, event):
        return any(not task.completed() for task in self.taskList)
    

class EffortStop(EffortListCommand, TaskListCommand, patterns.Observer):
    defaultMenuText = _('Stop tracking or resume tracking effort\tShift+Ctrl+T')
    defaultHelpText = help.effortStopOrResume
    stopMenuText = _('St&op tracking %s\tShift+Ctrl+T')
    stopHelpText = _('Stop tracking effort for the active task(s)')
    resumeMenuText = _('&Resume tracking %s\tShift+Ctrl+T')
    resumeHelpText = _('Resume tracking effort for the last tracked task')
    
    def __init__(self, *args, **kwargs):
        super(EffortStop, self).__init__(bitmap='clock_resume_icon', 
            bitmap2='clock_stop_icon', menuText=self.defaultMenuText,
            helpText=self.defaultHelpText, kind=wx.ITEM_CHECK, *args, **kwargs)
        # __trackedEfforts is a list and not a set because when an effort is
        # moved from one task to another task we might get the event that the
        # effort is (re)added to the effortList before the event that the effort
        # was removed from the effortList. If we would use a set, the effort
        # would be missing from the set after the removal event.    
        self.__trackedEfforts = self.__filterTrackedEfforts(self.effortList)
        self.__currentBitmap = None # Don't know yet what our bitmap is
        self.registerObserver(self.onEffortAdded, 
                              eventType=self.effortList.addItemEventType(),
                              eventSource=self.effortList)
        self.registerObserver(self.onEffortRemoved, 
                              eventType=self.effortList.removeItemEventType(),
                              eventSource=self.effortList)
        self.registerObserver(self.onStartTracking,  
                              eventType=effort.Effort.trackStartEventType())
        self.registerObserver(self.onStopTracking, 
                              eventType=effort.Effort.trackStopEventType())
                
    def onEffortAdded(self, event):
        self.__trackedEfforts.extend(self.__filterTrackedEfforts(event.values()))

    def onEffortRemoved(self, event):
        for effort in event.values():
            if effort in self.__trackedEfforts:
                self.__trackedEfforts.remove(effort)
        
    def onStartTracking(self, event):
        self.__trackedEfforts.extend(event.sources())
        
    def onStopTracking(self, event):
        for effort in event.sources():
            if effort in self.__trackedEfforts:
                self.__trackedEfforts.remove(effort) 
                        
    def doCommand(self, event=None):
        if self.__trackedEfforts:
            # Stop the tracked effort(s)
            effortCommand = command.StopEffortCommand(self.effortList)
        else:
            # Resume tracking the last task
            effortCommand = command.StartEffortCommand(self.taskList, 
                                                       [self.mostRecentTrackedTask()])
        effortCommand.do()
        
    def enabled(self, event=None):
        # If there are tracked efforts this command will stop them. If there are
        # untracked efforts this command will resume them. Otherwise this command
        # is disabled.
        return self.anyTrackedEfforts() or self.anyStoppedEfforts()
    
    @staticmethod
    def __filterTrackedEfforts(efforts):
        return [effort for effort in efforts if effort.isBeingTracked()]

    def onUpdateUI(self, event):
        super(EffortStop, self).onUpdateUI(event)
        self.updateUI()
        
    def updateUI(self):
        paused = self.anyStoppedEfforts() and not self.anyTrackedEfforts()
        self.updateToolState(not paused)
        bitmapName = self.bitmap if paused else self.bitmap2
        menuText = self.getMenuText(paused)
        if (bitmapName != self.__currentBitmap) or bool([item for item in self.menuItems if item.GetItemLabel() != menuText]):
            self.__currentBitmap = bitmapName
            self.updateToolBitmap(bitmapName)
            self.updateToolHelp()
            self.updateMenuItems(paused)
    
    def updateToolState(self, paused):
        if not self.toolbar: return # Toolbar is hidden        
        if paused != self.toolbar.GetToolState(self.id): 
            self.toolbar.ToggleTool(self.id, paused)

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
        self.toolbar.Realize()
    
    def updateMenuItems(self, paused):
        menuText = self.getMenuText(paused)
        helpText = self.getHelpText(paused)
        for menuItem in self.menuItems:
            menuItem.Check(paused)
            menuItem.SetItemLabel(menuText)
            menuItem.SetHelp(helpText)
        
    def getMenuText(self, paused=None): # pylint: disable-msg=W0221
        if self.anyTrackedEfforts():
            subject = _('multiple tasks') if len(self.__trackedEfforts) > 1 else self.__trackedEfforts[0].task().subject()
            return self.stopMenuText%self.trimmedSubject(subject)
        if paused is None:
            paused = self.anyStoppedEfforts()
        if paused:
            return self.resumeMenuText%self.trimmedSubject(self.mostRecentTrackedTask().subject())
        else:
            return self.defaultMenuText
        
    def getHelpText(self, paused=None): # pylint: disable-msg=W0221
        if self.anyTrackedEfforts():
            return self.stopHelpText
        if paused is None:
            paused = self.anyStoppedEfforts()
        return self.resumeHelpText if paused else self.defaultHelpText

    def anyStoppedEfforts(self):
        return bool(self.effortList.maxDateTime())
    
    def anyTrackedEfforts(self):
        return bool(self.__trackedEfforts)

    def mostRecentTrackedTask(self):
        stopTimes = [(effort.getStop(), effort) for effort in self.effortList if effort.getStop() is not None]
        return max(stopTimes)[1].task()
    
    @staticmethod
    def trimmedSubject(subject, maxLength=35, postFix='...'):
        trim = len(subject) > maxLength
        return subject[:maxLength - len(postFix)] + postFix if trim else subject
        

class CategoryNew(CategoriesCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(CategoryNew, self).__init__(bitmap='new', 
            menuText=_('New category...\tCtrl-G'),
            helpText=help.categoryNew, *args, **kwargs)

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        newCategoryCommand = command.NewCategoryCommand(self.categories)
        newCategoryCommand.do()
        taskFile = self.mainWindow().taskFile
        newCategoryDialog = dialog.editor.CategoryEditor(self.mainWindow(), 
            newCategoryCommand.items, self.settings, taskFile.categories(), 
            taskFile, bitmap=self.bitmap)
        newCategoryDialog.Show(show)


class CategoryDragAndDrop(DragAndDropCommand, CategoriesCommand):
    def createCommand(self, dropItem, dragItems, part):
        return command.DragAndDropCategoryCommand(self.categories, dragItems, 
                                                  drop=[dropItem], part=part)


class NoteNew(NotesCommand, SettingsCommand, ViewerCommand):
    menuText = _('New note...\tCtrl-J')
    helpText = help.noteNew
    
    def __init__(self, *args, **kwargs):
        super(NoteNew, self).__init__(menuText=self.menuText,
            helpText=self.helpText, bitmap='new', *args, **kwargs)

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        if self.viewer:
            noteDialog = self.viewer.newItemDialog(bitmap=self.bitmap)
        else: 
            newNoteCommand = command.NewNoteCommand(self.notes,
                categories=self.categoriesForTheNewNote())
            newNoteCommand.do()
            noteDialog = dialog.editor.NoteEditor(self.mainWindow(),
                newNoteCommand.items, self.settings, self.notes, 
                self.mainWindow().taskFile, bitmap=self.bitmap)
        noteDialog.Show(show)
        return noteDialog # for testing purposes

    def categoriesForTheNewNote(self):
        return self.mainWindow().taskFile.categories().filteredCategories()
    

class NewNoteWithSelectedCategories(NoteNew, ViewerCommand):
    menuText = _('New &note with selected categories...')
    helpText = _('Insert a new note with the selected categories checked')
    
    def categoriesForTheNewNote(self):
        return self.viewer.curselection()


class NoteDragAndDrop(DragAndDropCommand, NotesCommand):
    def createCommand(self, dropItem, dragItems, part):
        return command.DragAndDropNoteCommand(self.notes, dragItems, 
                                              drop=[dropItem], part=part)
 
                                                        
class AttachmentNew(AttachmentsCommand, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        attachments = kwargs['attachments']
        if 'menuText' not in kwargs:
            kwargs['menuText'] = attachments.newItemMenuText
            kwargs['helpText'] = attachments.newItemHelpText
        super(AttachmentNew, self).__init__(bitmap='new', *args, **kwargs)

    def doCommand(self, event, show=True): # pylint: disable-msg=W0221
        attachmentDialog = self.viewer.newItemDialog(bitmap=self.bitmap)
        attachmentDialog.Show(show)
        return attachmentDialog # for testing purposes


class AddAttachment(NeedsSelectedAttachmentOwnersMixin, ViewerCommand, SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(AddAttachment, self).__init__(menuText=_('&Add attachment...\tShift-Ctrl-A'),
            helpText=help.addAttachment, bitmap='paperclip_icon', *args, **kwargs)
        
    def doCommand(self, event):
        filename = widgets.AttachmentSelector()
        if not filename:
            return
        attachmentBase = self.settings.get('file', 'attachmentbase')
        if attachmentBase:
            filename = attachment.getRelativePath(filename, attachmentBase)
        addAttachmentCommand = command.AddAttachmentCommand( \
            self.viewer.presentation(), self.viewer.curselection(), 
            attachments=[attachment.FileAttachment(filename)])
        addAttachmentCommand.do()        


def openAttachments(attachments, settings, showerror):
    attachmentBase = settings.get('file', 'attachmentbase')
    for eachAttachment in attachments:
        try:
            eachAttachment.open(attachmentBase)
        except Exception, instance: # pylint: disable-msg=W0703
            showerror(render.exception(Exception, instance), 
                      caption=_('Error opening attachment'), 
                      style=wx.ICON_ERROR)


class AttachmentOpen(NeedsSelectedAttachmentsMixin, ViewerCommand, AttachmentsCommand,
                     SettingsCommand):
    def __init__(self, *args, **kwargs):
        attachments = kwargs['attachments']
        super(AttachmentOpen, self).__init__(bitmap='fileopen',
            menuText=attachments.openItemMenuText,
            helpText=attachments.openItemHelpText, *args, **kwargs)

    def doCommand(self, event, showerror=wx.MessageBox): # pylint: disable-msg=W0221
        openAttachments(self.viewer.curselection(), self.settings, showerror)


class OpenAllAttachments(NeedsSelectionWithAttachmentsMixin, ViewerCommand, 
                         SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(OpenAllAttachments, self).__init__(\
           menuText=_('&Open all attachments...\tShift+Ctrl+O'), 
           helpText=help.openAllAttachments, bitmap='paperclip_icon', 
           *args, **kwargs)
        
    def doCommand(self, event, showerror=wx.MessageBox): # pylint: disable-msg=W0221
        allAttachments = []
        for item in self.viewer.curselection():
            allAttachments.extend(item.attachments())
        openAttachments(allAttachments, self.settings, showerror)
            

class DialogCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self._dialogTitle = kwargs.pop('dialogTitle')
        self._dialogText = kwargs.pop('dialogText')
        self._direction = kwargs.pop('direction', None)
        self.closed = True
        super(DialogCommand, self).__init__(*args, **kwargs)
        
    def doCommand(self, event):
        self.closed = False
        # pylint: disable-msg=W0201
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
        super(Help, self).__init__(menuText=menuText, helpText=help.help,
            bitmap='led_blue_questionmark_icon', dialogTitle=_('Help'),
            dialogText=help.helpHTML, id=wx.ID_HELP, *args, **kwargs)


class Tips(SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(Tips, self).__init__(menuText=_('&Tips'),
            helpText=_('Tips about the program'),
            bitmap='lamp_icon', *args, **kwargs)

    def doCommand(self, event):
        help.showTips(self.mainWindow(), self.settings)


class Anonymize(IOCommand):
    def __init__(self, *args, **kwargs):
        super(Anonymize, self).__init__(menuText=_('Anonymize'),
             helpText = _('Anonymize a task file to attach it to a bug report'),
             *args, **kwargs)

    def doCommand(self, event):
        anonymize(self.iocontroller.filename())

    
class HelpAbout(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(HelpAbout, self).__init__(menuText=_('&About %s')%meta.name,
            helpText=_('Version and contact information about %s')%meta.name, 
            dialogTitle=_('About %s')%meta.name, 
            dialogText=help.aboutHTML, id=wx.ID_ABOUT, 
            bitmap='led_blue_information_icon', *args, **kwargs)
        
  
class HelpLicense(DialogCommand):
    def __init__(self, *args, **kwargs):
        super(HelpLicense, self).__init__(menuText=_('&License'),
            helpText=_('%s license')%meta.name,
            dialogTitle=_('%s license')%meta.name, 
            dialogText=meta.licenseHTML, direction=wx.Layout_LeftToRight, 
            bitmap='document_icon', *args, **kwargs)
        
        
class CheckForUpdate(SettingsCommand):
    def __init__(self, *args, **kwargs):
        super(CheckForUpdate, self).__init__(menuText=_('Check for update'),
            helpText=_('Check for the availability of a new version of %s')%meta.name,
            bitmap='box_icon', *args, **kwargs)
        
    def doCommand(self, event):
        meta.VersionChecker(self.settings, verbose=True).start()
        
        
class URLCommand(UICommand):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        super(URLCommand, self).__init__(*args, **kwargs)
         
    def doCommand(self, event):
        try:
            desktop.open(self.url)
        except Exception, reason:
            wx.MessageBox(_('Cannot open URL:\n%s')%reason, 
                      caption=_('%s URL error')%meta.name, 
                      style=wx.ICON_ERROR)


class FAQ(URLCommand):
    def __init__(self, *args, **kwargs):
        super(FAQ, self).__init__(menuText=_('&Frequently asked questions'),
            helpText=_('Browse the frequently asked questions and answers'),
            bitmap='led_blue_questionmark_icon', url=meta.faq_url, *args, **kwargs)


class ReportBug(URLCommand):
    def __init__(self, *args, **kwargs):
        super(ReportBug, self).__init__(menuText=_('Report a &bug...'),
            helpText=_('Report a bug or browse known bugs'),
            bitmap='bug_icon', url=meta.known_bugs_url, *args, **kwargs)
        
        
class RequestFeature(URLCommand):
    def __init__(self, *args, **kwargs):
        super(RequestFeature, self).__init__(menuText=_('Request a &feature...'),
            helpText=_('Request a new feature or vote for existing requests'),
            bitmap='cogwheel_icon', url=meta.feature_request_url, *args, **kwargs)


class RequestSupport(URLCommand):
    def __init__(self, *args, **kwargs):
        super(RequestSupport, self).__init__(menuText=_('Request &support...'),
            helpText=_('Request user support from the developers'),
            bitmap='life_ring_icon', url=meta.support_request_url, *args, **kwargs)
        

class HelpTranslate(URLCommand):
    def __init__(self, *args, **kwargs):
        super(HelpTranslate, self).__init__( \
            menuText=_('Help improve &translations...'),
            helpText=_('Help improve the translations of %s')%meta.name,
            bitmap='person_talking_icon', url=meta.translations_url, *args, **kwargs)
        

class Donate(URLCommand):
    def __init__(self, *args, **kwargs):
        super(Donate, self).__init__(menuText=_('&Donate...'),
            helpText=_('Donate to support the development of %s')%meta.name,
            bitmap='heart_icon', url=meta.donate_url, *args, **kwargs)
        
        
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
                           
    def onFind(self, searchString, matchCase, includeSubItems, 
               searchDescription):
        self.viewer.setSearchFilter(searchString, matchCase, includeSubItems, 
                                    searchDescription)

    def appendToToolBar(self, toolbar):
        searchString, matchCase, includeSubItems, searchDescription = self.viewer.getSearchFilter()
        # pylint: disable-msg=W0201
        self.searchControl = widgets.SearchCtrl(toolbar, value=searchString,
            style=wx.TE_PROCESS_ENTER, matchCase=matchCase, 
            includeSubItems=includeSubItems, searchDescription=searchDescription,
            callback=self.onFind)
        toolbar.AddControl(self.searchControl)
        self.bindKeyDownInViewer()
        self.bindKeyDownInSearchCtrl()
        
    def bindKeyDownInViewer(self):
        ''' Bind wx.EVT_KEY_DOWN to self.onViewerKeyDown so we can catch
            Ctrl-F. '''
        self.viewer.getWidget().GetMainWindow().Bind(wx.EVT_KEY_DOWN, 
                                                     self.onViewerKeyDown)
        
    def bindKeyDownInSearchCtrl(self):
        ''' Bind wx.EVT_KEY_DOWN to self.onSearchCtrlKeyDown so we can catch 
            the Escape key and drop down the menu on Ctrl-Down. '''
        self.searchControl.getTextCtrl().Bind(wx.EVT_KEY_DOWN, 
                                              self.onSearchCtrlKeyDown)

    def onViewerKeyDown(self, event):
        ''' On Ctrl-F, move focus to the search control. '''
        if event.KeyCode == ord('F') and event.CmdDown() and not event.AltDown():
            self.searchControl.SetFocus()
        else:
            event.Skip()
            
    def onSearchCtrlKeyDown(self, event):
        ''' On Escape, move focus to the viewer, on Ctrl-Down popup the 
            menu. '''
        if event.KeyCode == wx.WXK_ESCAPE:
            self.viewer.SetFocus()
        elif event.KeyCode == wx.WXK_DOWN and event.AltDown():
            self.searchControl.PopupMenu()
        else:
            event.Skip()
            
    def doCommand(self, event):
        pass # Not used
    

class ToolbarChoiceCommandMixin(object):
    def appendToToolBar(self, toolbar):
        ''' Add our choice control to the toolbar. '''
        # pylint: disable-msg=W0201
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
        
    def doChoice(self, choice):
        raise NotImplementedError # pragma: no cover
    
    def doCommand(self, event):
        pass # Not used
        
    def setChoice(self, choice):
        ''' Programmatically set the current choice in the choice control. '''
        index = self.choiceData.index(choice)
        self.choiceCtrl.Selection = index
        self.currentChoice = index


class EffortViewerAggregationChoice(ToolbarChoiceCommandMixin, ViewerCommand):
    choiceLabels = [_('Effort details'), _('Effort per day'), 
                    _('Effort per week'), _('Effort per month')]
    choiceData = ['details', 'day', 'week', 'month']

    def doChoice(self, choice):
        self.viewer.showEffortAggregation(choice)
        

class TaskViewerTreeOrListChoice(ToolbarChoiceCommandMixin, ViewerCommand):
    choiceLabels = [_('Tree of tasks'), _('List of tasks')]
    choiceData = [True, False]
    
    def doChoice(self, choice):
        self.viewer.showTree(choice)
        

class CategoryViewerFilterChoice(ToolbarChoiceCommandMixin, SettingsCommand):
    choiceLabels = [_('Filter on all checked categories'),
                    _('Filter on any checked category')]
    choiceData = [True, False]

    def doChoice(self, choice):
        self.settings.set('view', 'categoryfiltermatchall', str(choice))


class SquareTaskViewerOrderChoice(ToolbarChoiceCommandMixin, ViewerCommand):
    choiceLabels = [_('Budget'), _('Time spent'), _('Fixed fee'), _('Revenue'), _('Priority')]
    choiceData = ['budget', 'timeSpent', 'fixedFee', 'revenue', 'priority']
    
    def doChoice(self, choice):
        self.viewer.orderBy(choice)


class CalendarViewerConfigure(ViewerCommand):
    menuText = _('&Configure')
    helpText = _('Configure the calendar viewer')
    bitmap = 'wrench_icon'

    def __init__(self, *args, **kwargs):
        super(CalendarViewerConfigure, self).__init__( \
            menuText=self.menuText, helpText=self.helpText, bitmap=self.bitmap, 
            *args, **kwargs)

    def doCommand(self, event):
        self.viewer.configure()


class CalendarViewerNavigationCommand(ViewerCommand):
    def __init__(self, *args, **kwargs):
        super(CalendarViewerNavigationCommand, self).__init__( \
            menuText=self.menuText, helpText=self.helpText, bitmap=self.bitmap, 
            *args, **kwargs)

    def doCommand(self, event):
        self.viewer.freeze()
        try:
            self.viewer.SetViewType(self.calendarViewType) # pylint: disable-msg=E1101
        finally:
            self.viewer.thaw()


class CalendarViewerNextPeriod(CalendarViewerNavigationCommand):
    menuText = _('&Next period')
    helpText = _('Show next period')
    bitmap = 'next'
    calendarViewType = wxSCHEDULER_NEXT
    

class CalendarViewerPreviousPeriod(CalendarViewerNavigationCommand):
    menuText = _('&Previous period')
    helpText = _('Show previous period')
    bitmap = 'prev'
    calendarViewType = wxSCHEDULER_PREV
    

class CalendarViewerToday(CalendarViewerNavigationCommand):
    menuText = _('&Today')
    helpText = _('Show today')
    bitmap = 'calendar_icon'
    calendarViewType = wxSCHEDULER_TODAY


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

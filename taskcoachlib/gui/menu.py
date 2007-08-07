import wx, uicommand
from i18n import _


class Menu(wx.Menu, uicommand.UICommandContainer):
    def __init__(self, window):
        super(Menu, self).__init__()
        self._window = window
        
    def __len__(self):
        return self.GetMenuItemCount()

    def appendUICommand(self, uiCommand):
        return uiCommand.appendToMenu(self, self._window)    
    
    def appendMenu(self, text, subMenu, bitmap=None):
        subMenuItem = wx.MenuItem(self, id=wx.NewId(), text=text, subMenu=subMenu)
        if not bitmap and '__WXMSW__' in wx.PlatformInfo:
            # hack to force a 16 bit margin. SetMarginWidth doesn't work
            bitmap = 'nobitmap'
        if bitmap:
            subMenuItem.SetBitmap(wx.ArtProvider_GetBitmap(bitmap, 
                wx.ART_MENU, (16,16)))
        self.AppendItem(subMenuItem)

    def invokeMenuItem(self, menuItem):
        ''' Programmatically invoke the menuItem. This is mainly for testing 
            purposes. '''
        self._window.ProcessEvent(wx.CommandEvent( \
            wx.wxEVT_COMMAND_MENU_SELECTED, winid=menuItem.GetId()))
    
    def openMenu(self):
        ''' Programmatically open the menu. This is mainly for testing 
            purposes. '''
        # On Mac OSX, an explicit UpdateWindowUI is needed to ensure that
        # menu items are updated before the menu is opened. This is not needed
        # on other platforms, but it doesn't hurt either.
        self._window.UpdateWindowUI() 
        self._window.ProcessEvent(wx.MenuEvent(wx.wxEVT_MENU_OPEN, menu=self))


class StaticMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(StaticMenu, self).__init__(mainwindow)
        wx.CallAfter(self.appendUICommands, uiCommands, self.getUICommands())
        
    def getUICommands(self):
        raise NotImplementedError
        
        
class DynamicMenu(Menu):
    def __init__(self, mainwindow, uiCommands, parentMenu=None, 
                 labelInParentMenu=None):
        super(DynamicMenu, self).__init__(mainwindow)
        self._parentMenu = parentMenu
        self._labelInParentMenu = labelInParentMenu
        self._uiCommands = uiCommands
        self._uiCommandNames = None
        mainwindow.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI)

    def onUpdateUI(self, event):
        self.updateUI()
        event.Skip()
        
    def updateUI(self):
        self.updateMenuItemInParentMenu()
        self.updateMenuItems()
        
    def updateMenuItemInParentMenu(self):
        if self._parentMenu:
            myId = self._parentMenu.FindItem(self._labelInParentMenu)
            if myId != wx.NOT_FOUND:
                self._parentMenu.Enable(myId, self.enabled())

    def updateMenuItems(self):
        newCommandNames = self.getUICommands()
        if newCommandNames != self._uiCommandNames:
            self.clearAndFillMenu(newCommandNames)
            self._uiCommandNames = newCommandNames
        
    def clearAndFillMenu(self, commandNames):
        for menuItem in self.MenuItems:
            self.DestroyItem(menuItem)
        self.appendUICommands(self._uiCommands, commandNames)
        
    def enabled(self):
        return True

    def getUICommands(self):
        raise NotImplementedError


class MainMenu(wx.MenuBar):
    def __init__(self, mainwindow, uiCommands, settings):
        super(MainMenu, self).__init__()
        self.Append(FileMenu(mainwindow, uiCommands, settings), _('&File'))
        self.Append(EditMenu(mainwindow, uiCommands), _('&Edit'))
        self.Append(ViewMenu(mainwindow, uiCommands, settings), _('&View'))
        self.Append(TaskMenu(mainwindow, uiCommands), _('&Task'))
        self.Append(EffortMenu(mainwindow, uiCommands), _('Eff&ort'))
        self.Append(CategoryMenu(mainwindow, uiCommands), _('&Category'))
        if settings.getboolean('feature', 'notes'):
            self.Append(NoteMenu(mainwindow, uiCommands), _('&Note'))
        self.Append(HelpMenu(mainwindow, uiCommands), _('&Help'))

'''
class OpenAttachmentsMenu(Menu):
    def __init__(self, mainwindow, uiCommands, settings):
        super(OpenAttachmentsMenu, self).__init__(mainwindow)
        self.Bind(wx.EVT_MENU_OPEN, self.onOpenMenu)
        
    def opOpenMenu(self, event):
        if event.GetMenu() == self:
            self.__clear()
            self.__fill()
        event.Skip()
        
    def __clear(self):
        for item in self.GetMenuItems():
            self.Delete(item)
            
    def __fill(self):
        pass
'''
       
class FileMenu(Menu):
    def __init__(self, mainwindow, uiCommands, settings):
        super(FileMenu, self).__init__(mainwindow)
        self.__settings = settings
        self.__uiCommands = uiCommands
        self.__recentFileUICommands = []
        self.__separator = None
        self.appendUICommands(uiCommands, ['open', 'merge', 'close', None, 
            'save', 'saveas', 'saveselection', None, 'printpagesetup',
            'printpreview', 'print', None])
        self.appendMenu(_('&Export'), ExportMenu(mainwindow, uiCommands),
            'export')
        self.__recentFilesStartPosition = len(self) 
        self.appendUICommands(uiCommands, [None, 'quit'])
        self._window.Bind(wx.EVT_MENU_OPEN, self.onOpenMenu)

    def onOpenMenu(self, event):
        if event.GetMenu() == self:
            self.__removeRecentFileMenuItems()
            self.__insertRecentFileMenuItems()        
        event.Skip()
    
    def __insertRecentFileMenuItems(self):
        recentFiles = eval(self.__settings.get('file', 'recentfiles'))
        if not recentFiles:
            return
        maximumNumberOfRecentFiles = self.__settings.getint('file', 
            'maxrecentfiles')
        recentFiles = recentFiles[:maximumNumberOfRecentFiles]
        self.__separator = self.InsertSeparator(self.__recentFilesStartPosition)
        for index, recentFile in enumerate(recentFiles):
            recentFileNumber = index + 1 # Only computer nerds start counting at 0 :-)
            recentFileMenuPosition = self.__recentFilesStartPosition + 1 + index
            recentFileOpenUICommand = self.__uiCommands.createRecentFileOpenUICommand(recentFile, recentFileNumber)
            recentFileOpenUICommand.appendToMenu(self, self._window, 
                recentFileMenuPosition)
            self.__recentFileUICommands.append(recentFileOpenUICommand)

    def __removeRecentFileMenuItems(self):
        for recentFileUICommand in self.__recentFileUICommands:
            recentFileUICommand.removeFromMenu(self, self._window)
        self.__recentFileUICommands = []
        if self.__separator:
            self.RemoveItem(self.__separator)
            self.__separator = None


class ExportMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ExportMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['exportashtml', 'exportasics', 
                                           'exportascsv'])
        

class EditMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EditMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['undo', 'redo', None, 'cut', 
            'copy', 'paste', 'pasteintotask', None])
        # the spaces are to leave room for command names in the Undo and Redo menuitems:
        self.appendMenu(_('&Select')+' '*50, SelectMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None, 'editpreferences'])


class SelectMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(SelectMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['selectall', 'invertselection', 
            'clearselection'])


class ViewMenu(Menu):
    def __init__(self, mainwindow, uiCommands, settings):
        super(ViewMenu, self).__init__(mainwindow)
        self.appendMenu(_('New viewer'), 
            ViewViewerMenu(mainwindow, uiCommands, settings), 'viewnewviewer')
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('&Filter'), FilterMenu(mainwindow, uiCommands, self, _('&Filter')))
        self.appendMenu(_('&Sort'), SortMenu(mainwindow, uiCommands, self, _('&Sort')))
        self.appendMenu(_('&Columns'), ColumnMenu(mainwindow, uiCommands, self, _('&Columns')))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('&Tree options'), 
            ViewTreeOptionsMenu(mainwindow, uiCommands), 'treeview')
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('T&oolbar'), ToolBarMenu(mainwindow, uiCommands))        
        self.appendUICommands(uiCommands, ['viewstatusbar'])   


class ViewViewerMenu(Menu):
    def __init__(self, mainwindow, uiCommands, settings):
        super(ViewViewerMenu, self).__init__(mainwindow)
        viewViewerCommands = ['viewtasklistviewer', 
            'viewtasktreeviewer', None, 'viewcategoryviewer', None,
            'vieweffortdetailviewer', 'vieweffortperdayviewer', 
            'vieweffortperweekviewer', 'vieweffortpermonthviewer']
        if settings.getboolean('feature', 'notes'):
            viewViewerCommands.extend([None, 'viewnoteviewer'])
        self.appendUICommands(uiCommands, viewViewerCommands)
        
                                      
class ViewTreeOptionsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTreeOptionsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewexpandselected', 
            'viewcollapseselected', None, 'viewexpandall', 'viewcollapseall'])


class FilterMenu(DynamicMenu):
    def enabled(self):
        return self._window.viewer.isFilterable()
    
    def getUICommands(self):
        return self._window.viewer.getFilterUICommands()
    
    
class ColumnMenu(DynamicMenu):
    def enabled(self):
        return self._window.viewer.hasHideableColumns()
    
    def getUICommands(self):
        return self._window.viewer.getColumnUICommands()
        

class SortMenu(DynamicMenu):
    def enabled(self):
        return self._window.viewer.isSortable()
    
    def getUICommands(self):
        return self._window.viewer.getSortUICommands()


class ToolBarMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ToolBarMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['toolbarhide', 'toolbarsmall',
            'toolbarmedium', 'toolbarbig'])


class TaskMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(TaskMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['newtask', 'newsubtask', 
            None, 'edittask', 'markcompleted', None, 'deletetask', None, 
            'mailtask', 'addattachmenttotask', 'openalltaskattachments'])
            
            
class EffortMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EffortMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['neweffort', 'editeffort', 
            'deleteeffort', None, 'starteffort', 'stopeffort'])
        

class CategoryMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(CategoryMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['newcategory', 'newsubcategory', 
            'editcategory', 'deletecategory'])
        
        
class NoteMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(NoteMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['newnote', 'newsubnote', 'editnote',
            'deletenote'])
        
        
class HelpMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(HelpMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['help', 'tips', None, 'about', 'license'])


class TaskBarMenu(Menu):
    def __init__(self, taskBarIcon, uiCommands):
        super(TaskBarMenu, self).__init__(taskBarIcon)
        self.appendUICommands(uiCommands, ['newtask', 'neweffort', 'stopeffort', 
            None, 'restore', 'quit'])


class TaskPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands, treeViewer):
        super(TaskPopupMenu, self).__init__(mainwindow)
        commandsToAppend = ['cut', 'copy', 'paste',
            'pasteintotask', None, 'newtask', 'newsubtask', None, 'edittask', 
            'markcompleted', None, 'deletetask', None, 'mailtask', 
            'addattachmenttotask', 'openalltaskattachments', None, 
            'neweffort', 'starteffort', 'stopeffort']
        if treeViewer:
            commandsToAppend.extend([None, 'viewexpandselected', 
                'viewcollapseselected'])
        self.appendUICommands(uiCommands, commandsToAppend)


class EffortPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EffortPopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste', 
           'pasteintotask', None, 'newtask', None, 'neweffort', 'editeffort', 
           'deleteeffort', None, 'stopeffort'])


class CategoryPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(CategoryPopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste', None, 
            'newtask', None, 'newcategory', 'newsubcategory', 'editcategory', 
            'deletecategory', None, 'stopeffort', None, 'viewexpandselected',
            'viewcollapseselected'])


class NotePopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(NotePopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste', None,
            'newtask', None, 'newnote', 'newsubnote', 'editnote', 'deletenote',
            None, 'stopeffort', None, 'viewexpandselected', 
            'viewcollapseselected'])
        
        
# Column header popup menu

class ColumnPopupMenu(StaticMenu):           
    def __setColumn(self, columnIndex):
        self.__columnIndex = columnIndex
    
    def __getColumn(self):
        return self.__columnIndex
    
    # columnIndex is the index of the column clicked by the user to popup this menu
    # This property should be set by the control popping up this menu (see 
    # widgets._CtrlWithColumnPopupMenu.
    columnIndex = property(__getColumn, __setColumn) 
                            
    def getUICommands(self):
        return ['hidecurrentcolumn', None] + \
            self._window.getColumnUICommands()

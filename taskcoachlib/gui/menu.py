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
    
    def appendMenu(self, text, subMenu):
        subMenuItem = wx.MenuItem(self, text=text, subMenu=subMenu)
        # hack to force a 16 bit margin. SetMarginWidth doesn't work
        if '__WXMSW__' in wx.PlatformInfo:
            subMenuItem.SetBitmap(wx.ArtProvider_GetBitmap('nobitmap', 
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


class MainMenu(wx.MenuBar):
    def __init__(self, mainwindow, uiCommands, settings):
        super(MainMenu, self).__init__()
        self.Append(FileMenu(mainwindow, uiCommands, settings), _('&File'))
        self.Append(EditMenu(mainwindow, uiCommands), _('&Edit'))
        self.Append(ViewMenu(mainwindow, uiCommands), _('&View'))
        self.Append(TaskMenu(mainwindow, uiCommands), _('&Task'))
        self.Append(EffortMenu(mainwindow, uiCommands), _('Eff&ort'))
        self.Append(HelpMenu(mainwindow, uiCommands), _('&Help'))


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
        self.appendMenu(_('&Export'), ExportMenu(mainwindow, uiCommands))
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
        self.appendUICommands(uiCommands, ['exportashtml', 'exportasics'])
        

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
    def __init__(self, mainwindow, uiCommands):
        super(ViewMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewalltasks'])
        self.appendMenu(_('Tas&ks that are'), 
            ViewTaskStatesMenu(mainwindow, uiCommands))
        self.appendMenu(_('Tasks &due before end of'),
            ViewTasksByDueDateMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, ['viewcategories', None])
        self.appendMenu(_('Task &columns'), ViewTaskColumnsMenu(mainwindow, uiCommands))
        self.appendMenu(_('Effort &columns'), ViewEffortColumnsMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('Task &list options'), 
            ViewTaskListMenu(mainwindow, uiCommands))
        self.appendMenu(_('Task &tree options'), 
            ViewTaskTreeMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('&Sort'), SortMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, [None])
        self.appendMenu(_('T&oolbar'), ToolBarMenu(mainwindow, uiCommands))        
        self.appendUICommands(uiCommands, ['viewstatusbar', 
            'viewfiltersidebar'])   


class ViewTaskColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskColumnsMenu, self).__init__(mainwindow)
        self.appendMenu(_('&Dates'), 
            _ViewTaskDateColumnsMenu(mainwindow, uiCommands))
        self.appendMenu(_('&Budget'), 
            _ViewTaskBudgetColumnsMenu(mainwindow, uiCommands))
        self.appendMenu(_('&Financial'), 
            _ViewTaskFinancialColumnsMenu(mainwindow, uiCommands))
        self.appendUICommands(uiCommands, ['viewpriority', 'viewtotalpriority', 
        'viewlastmodificationtime', 'viewtotallastmodificationtime'])


class _ViewTaskDateColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(_ViewTaskDateColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewalldatecolumns', None, 
            'viewstartdate', 'viewduedate', 'viewcompletiondate', 
            'viewtimeleft'])


class _ViewTaskBudgetColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(_ViewTaskBudgetColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewallbudgetcolumns', None, 
            'viewbudget', 'viewtotalbudget', 'viewtimespent',
            'viewtotaltimespent', 'viewbudgetleft', 'viewtotalbudgetleft'])


class _ViewTaskFinancialColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(_ViewTaskFinancialColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewallfinancialcolumns', None, 
            'viewhourlyfee', 'viewfixedfee', 'viewtotalfixedfee', 
            'viewrevenue', 'viewtotalrevenue'])


class ViewEffortColumnsMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewEffortColumnsMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewefforttimespent',
            'viewtotalefforttimespent', 'vieweffortrevenue',
            'viewtotaleffortrevenue'])

           
class ViewTaskStatesMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskStatesMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewactivetasks',
            'viewinactivetasks', 'viewcompletedtasks', None,
            'viewoverduetasks', 'viewoverbudgettasks'])

                
class ViewTaskListMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskListMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewcompositetasks'])

           
class ViewTaskTreeMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTaskTreeMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewexpandselected', 
            'viewcollapseselected', None, 'viewexpandall', 'viewcollapseall'])


class SortMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(SortMenu, self).__init__(mainwindow)
        # NOTE: 'viewsortorder' needs to be added first to properly initialize 
        # ascending/descending order
        self.appendUICommands(uiCommands, ['viewsortorder', 
            'viewsortcasesensitive', 'viewsortbystatusfirst', None, 
            'viewsortbysubject', 'viewsortbystartdate', 'viewsortbyduedate',
            'viewsortbytimeleft', 'viewsortbycompletiondate',
            'viewsortbybudget', 'viewsortbytotalbudget', 'viewsortbytimespent',
            'viewsortbytotaltimespent', 'viewsortbybudgetleft',
            'viewsortbytotalbudgetleft', 'viewsortbypriority',
            'viewsortbytotalpriority', 'viewsortbyhourlyfee',
            'viewsortbyfixedfee', 'viewsortbylastmodificationtime', 
            'viewsortbytotallastmodificationtime'])
                
    
class ToolBarMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ToolBarMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['toolbarhide', 'toolbarsmall',
            'toolbarmedium', 'toolbarbig'])


class ViewTasksByDueDateMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(ViewTasksByDueDateMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['viewdueunlimited', 'viewduetoday',
            'viewduetomorrow', 'viewdueworkweek', 'viewdueweek',
            'viewduemonth', 'viewdueyear'])


class TaskMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(TaskMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['new', 'newsubtask', 
            None, 'edit', 'markcompleted', None, 'delete', None, 'mailtask',
            'addattachmenttotask'])
            
            
class EffortMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EffortMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['neweffort', 'editeffort', 
            'deleteeffort', None, 'starteffort', 'stopeffort'])
        
        
class HelpMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(HelpMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['help', 'tips', None, 'about', 'license'])


class TaskBarMenu(Menu):
    def __init__(self, taskBarIcon, uiCommands):
        super(TaskBarMenu, self).__init__(taskBarIcon)
        self.appendUICommands(uiCommands, ['new', 'neweffort', 'stopeffort', 
            None, 'restore', 'quit'])


class TaskPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(TaskPopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste',
            'pasteintotask', None, 'new', 'newsubtask', None, 'edit', 
            'markcompleted', None, 'delete', None, 'mailtask', 
            'addattachmenttotask', None, 
            'neweffort', 'starteffort', 'stopeffort', None, 
            'viewexpandselected', 'viewcollapseselected'])


class EffortPopupMenu(Menu):
    def __init__(self, mainwindow, uiCommands):
        super(EffortPopupMenu, self).__init__(mainwindow)
        self.appendUICommands(uiCommands, ['cut', 'copy', 'paste', 
           'pasteintotask', None, 'new', None, 'neweffort', 'editeffort', 
           'deleteeffort', None, 'stopeffort'])


# Column header popup menu's

class _ColumnPopupMenu(Menu):
    def __init__(self, window, uiCommands, *args, **kwargs):
        super(_ColumnPopupMenu, self).__init__(window, *args, **kwargs)
        # FIXME: Can't remember why we need a wx.FutureCall here? Maybe
        # because we need time for the viewer to add columns, so these commands
        # can then hide the right columns?
        wx.FutureCall(1000, lambda: self._fillMenu(window, uiCommands))
    
    def __setColumn(self, columnIndex):
        self.__columnIndex = columnIndex
    
    def __getColumn(self):
        return self.__columnIndex
    
    # columnIndex is the index of the column clicked by the user to popup this menu
    # This property should be set by the control popping up this menu (see 
    # widgets._CtrlWithColumnPopupMenu.
    columnIndex = property(__getColumn, __setColumn) 
                            
    def _fillMenu(self, window, uiCommands):
        raise NotImplementedError
    

class TaskViewerColumnPopupMenu(_ColumnPopupMenu):        
    def _fillMenu(self, window, uiCommands):
        self.appendUICommands(uiCommands, ['hidecurrentcolumn', None])
        self.appendMenu(_('&Dates'), 
            _ViewTaskDateColumnsMenu(window, uiCommands)),
        self.appendMenu(_('&Budget'), 
            _ViewTaskBudgetColumnsMenu(window, uiCommands)),
        self.appendMenu(_('&Financial'), 
            _ViewTaskFinancialColumnsMenu(window, uiCommands))
        self.appendUICommands(uiCommands, ['viewpriority', 'viewtotalpriority',
            'viewlastmodificationtime', 'viewtotallastmodificationtime'])


class EffortViewerColumnPopupMenu(_ColumnPopupMenu):
    def _fillMenu(self, window, uiCommands):
        self.appendUICommands(uiCommands, ['hidecurrentcolumn', None, 
            'viewefforttimespent', 'viewtotalefforttimespent',
            'vieweffortrevenue', 'viewtotaleffortrevenue'])

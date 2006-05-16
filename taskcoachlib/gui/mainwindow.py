import wx, meta, patterns, widgets, command
import viewer, viewercontainer, viewerfactory, help, find, toolbar, uicommand,\
    remindercontroller
from i18n import _
import domain.task as task
import domain.effort as effort

class WindowWithPersistentDimensions(wx.Frame):
    def __init__(self, settings, *args, **kwargs):
        super(WindowWithPersistentDimensions, self).__init__(None, -1, '')
        self._settings = settings
        self._section = 'window'
        self.setDimensions()
        self.Bind(wx.EVT_SIZE, self.onChangeSize)
        if self.getSetting('iconized'):
            self.Iconize(True)
            wx.CallAfter(self.Hide)
        
    def setSetting(self, setting, value):
        self._settings.set(self._section, setting, str(value))
        
    def getSetting(self, setting):
        return eval(self._settings.get(self._section, setting))
        
    def setDimensions(self):
        width, height = self.getSetting('size')
        x, y = self.getSetting('position')
        self.SetDimensions(x, y, width, height)

    def onChangeSize(self, event):
        self.setSetting('size', event.GetSize())
        event.Skip()
                
    def savePosition(self):
        iconized = self.IsIconized()
        if not iconized:
            self.setSetting('position', self.GetPosition())
        self.setSetting('iconized', iconized)

        
class MainWindow(WindowWithPersistentDimensions):
    def __init__(self, iocontroller, taskFile, filteredTaskList,
            effortList, settings, splash=None, *args, **kwargs):
        super(MainWindow, self).__init__(settings, *args, **kwargs)
        self.iocontroller = iocontroller
        self.taskFile = taskFile
        self.filteredTaskList = filteredTaskList
        self.settings = settings
        self.effortList = effortList
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_SIZE, self.onSize)
        wx.GetApp().Bind(wx.EVT_QUERY_END_SESSION, self.onEndSession)

        self.splash = splash

        self.createWindowComponents()
        self.initWindowComponents()
        self.initWindow()
        self.registerForWindowComponentChanges()
        wx.CallAfter(self.showTips)

    def createWindowComponents(self):
        self.createFilterSideBar()
        self.panel = wx.Panel(self, -1)
        self.viewer = viewercontainer.ViewerNotebook(self.panel, self.settings, 'mainviewer') 
        self.findDialog = find.FindPanel(self.panel, self.viewer, self.settings)
        self.initLayout()
        self.uiCommands = uicommand.UICommands(self, self.iocontroller,
            self.viewer, self.settings, self.filteredTaskList, self.effortList)
        viewerfactory.addTaskViewers(self.viewer, self.filteredTaskList, 
            self.uiCommands, self.settings)
        viewerfactory.addEffortViewers(self.viewer, self.effortList, 
            self.filteredTaskList, self.uiCommands, self.settings, 'effortviewer')
        import status
        self.SetStatusBar(status.StatusBar(self, self.taskFile,
                          self.filteredTaskList, self.viewer))
        import menu
        self.SetMenuBar(menu.MainMenu(self, self.uiCommands, self.settings))
        self.createTaskBarIcon(self.uiCommands)
        self.reminderController = remindercontroller.ReminderController(self.taskFile)
        
    def createFilterSideBar(self):
        defaultWidth = self.settings.getint('view', 'filtersidebarwidth')
        self.filterSideBarWindow = wx.SashLayoutWindow(self,
            style=wx.NO_BORDER|wx.SW_3D|wx.CLIP_CHILDREN)
        self.filterSideBarWindow.SetSashVisible(wx.SASH_RIGHT, True)
        self.filterSideBarWindow.SetOrientation(wx.LAYOUT_VERTICAL)
        self.filterSideBarWindow.SetAlignment(wx.LAYOUT_LEFT)
        self.filterSideBarWindow.SetDefaultSize((defaultWidth, 1000))
        self.filterSideBarWindow.Bind(wx.EVT_SASH_DRAGGED, self.onDragSash)
        self.text = wx.StaticText(self.filterSideBarWindow, label='Hi there')

    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.viewer, proportion=1, flag=wx.EXPAND)
        self._sizer.Add(self.findDialog, flag=wx.EXPAND|wx.ALL, border=1)
        self.panel.SetSizerAndFit(self._sizer)

    def initWindow(self):
        self.SetTitle(patterns.observer.Notification(self, filename=self.taskFile.filename()))
        self.setIcon()
        self.displayMessage(_('Welcome to %(name)s version %(version)s')%{'name': meta.name, 
            'version': meta.version}, pane=1)

    def setIcon(self):
        bundle = wx.IconBundle()
        for size in [(16, 16), (22, 22), (32, 32), (48, 48), (64, 64), (128, 128)]:
            icon = wx.ArtProvider_GetIcon('taskcoach', wx.ART_FRAME_ICON, size)
            bundle.AddIcon(icon)
        self.SetIcons(bundle)

    def initWindowComponents(self):
        self.onShowFindDialog()
        self.onShowToolBar()
        self.onShowFilterSideBar()
        # We use CallAfter because otherwise the statusbar will appear at the 
        # top of the window when it is initially hidden and later shown.
        wx.CallAfter(self.onShowStatusBar) 
                
    def registerForWindowComponentChanges(self):
        self.taskFile.registerObserver(self.SetTitle, 'FilenameChanged')
        self.settings.registerObserver(self.onShowFindDialog, 
            ('view', 'finddialog'))
        self.settings.registerObserver(self.onShowStatusBar, 
            ('view', 'statusbar'))
        self.settings.registerObserver(self.onShowToolBar, 
            ('view', 'toolbar'))
        self.settings.registerObserver(self.onShowFilterSideBar,
            ('view', 'filtersidebar'))

    def showTips(self):
        if self.settings.getboolean('window', 'tips'):
            if self.splash:
                self.splash.Hide()
            help.showTips(self, self.settings)

    def onSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.panel)
        # Make sure WindowWithPersistentDimensions.onSize is invoked too:
        event.Skip() 

    def onDragSash(self, event):
        width = event.GetDragRect().width
        if width < 50:
            self.settings.set('view', 'filtersidebar', 'False')
        else:
            self.settings.set('view', 'filtersidebarwidth', str(width))
            self.filterSideBarWindow.SetDefaultSize((width, 1000))
            wx.LayoutAlgorithm().LayoutWindow(self, self.panel)
                         
    def onShowFindDialog(self, *args, **kwargs):
        self.showFindDialog(self.settings.getboolean('view', 'finddialog'))

    def onShowStatusBar(self, *args, **kwargs):
        self.showStatusBar(self.settings.getboolean('view', 'statusbar'))

    def onShowToolBar(self, *args, **kwargs):
        self.showToolBar(eval(self.settings.get('view', 'toolbar')))

    def onShowFilterSideBar(self, *args, **kwargs):
        self.filterSideBarWindow.Show(self.settings.getboolean('view',
            'filtersidebar'))
        self.filterSideBarWindow.SizeWindows()
        wx.LayoutAlgorithm().LayoutWindow(self, self.panel)

    def createTaskBarIcon(self, uiCommands):
        if self.canCreateTaskBarIcon():
            import taskbaricon, menu
            self.taskBarIcon = taskbaricon.TaskBarIcon(self, self.taskFile)
            self.taskBarIcon.setPopupMenu(menu.TaskBarMenu(self.taskBarIcon,
                uiCommands))
        self.Bind(wx.EVT_ICONIZE, self.onIconify)

    def canCreateTaskBarIcon(self):
        try:
            import taskbaricon
            return True
        except:
            return False

    def SetTitle(self, notification, *args, **kwargs):
        if notification.filename == []:
            return
        title = meta.name
        if notification.filename:
            title += ' - %s'%notification.filename
        super(MainWindow, self).SetTitle(title)    

    def displayMessage(self, message, pane=0):
        self.GetStatusBar().SetStatusText(message, pane)

    def quit(self, event=None):
        if not self.iocontroller.close():
            return
        # FIXME: I'm not sure unicode strings will work in the TaskCoach.ini
        # file, so just to be sure we'll clear a possible search string:
        self.settings.set('view', 'tasksearchfilterstring', '') 
        self.settings.set('file', 'lastfile', self.taskFile.lastFilename())
        if hasattr(self, 'taskBarIcon'):
            self.taskBarIcon.RemoveIcon()
        self.savePosition()
        self.settings.save()
        wx.GetApp().ProcessIdle()
        wx.GetApp().ExitMainLoop()
        
    def onClose(self, event):
        if event.CanVeto() and self.settings.getboolean('window', 
                                                        'hidewhenclosed'):
            event.Veto()
            self.Iconize()
        else:
            self.quit()

    def onEndSession(self, event):
        event.Veto()
        print 'onEndSession'
        wx.MessageBox('bla') 
        return False 
    
    def restore(self, event):
        self.Show()
        self.Raise()
        self.Refresh() # This is not necessary on Windows/Linux Ubuntu/Mac but
                       # might help to fix bug 1429540 (Linux Mandrake)
        self.Iconize(False)

    def onIconify(self, event):
        if event.Iconized() and self.settings.getboolean('window', 
                                                         'hidewheniconized'):
            self.Hide()

    def showFindDialog(self, show=True):
        if not show:
            self.findDialog.clear()
        self._sizer.Show(self.findDialog, show)
        self._sizer.Layout()

    def showStatusBar(self, show=True):
        # FIXME: First hiding the statusbar, then hiding the toolbar, then
        # showing the statusbar puts it in the wrong place (only on Linux?)
        self.GetStatusBar().Show(show)
        self._sizer.Layout()
        self.SendSizeEvent()

    def showToolBar(self, size):
        if self.GetToolBar():
            self.GetToolBar().Destroy()
        if size is None:
            self.SendSizeEvent()
        else:
            self.SetToolBar(toolbar.ToolBar(self, self.uiCommands, size=size))
    

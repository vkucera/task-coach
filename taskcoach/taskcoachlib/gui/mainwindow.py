import wx, meta, patterns, widgets, task, command, effort
import viewer, viewercontainer, viewerfactory, help, find, toolbar, uicommand
from i18n import _

class WindowWithPersistentDimensions(wx.Frame):
    def __init__(self, settings, *args, **kwargs):
        super(WindowWithPersistentDimensions, self).__init__(None, -1, '')
        self._settings = settings
        self._section = 'window'
        self.Bind(wx.EVT_SIZE, self.onChangeSize)
        self.setDimensions()
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
            effortList, settings, *args, **kwargs):
        super(MainWindow, self).__init__(settings, *args, **kwargs)
        self.iocontroller = iocontroller
        self.taskFile = taskFile
        self.filteredTaskList = filteredTaskList
        self.settings = settings
        self.effortList = effortList
        self.Bind(wx.EVT_CLOSE, self.quit)

        self.createWindowComponents()
        self.initWindow()
        self.initWindowComponents()
        self.registerForWindowComponentChanges()

    def createWindowComponents(self):
        self.panel = wx.Panel(self, -1)
        self.viewer = viewercontainer.ViewerNotebook(self.panel, self.settings, 'mainviewer') 
        self.findDialog = find.FindPanel(self.panel, self.filteredTaskList, self.viewer)
        self.initLayout()
        self.uiCommands = uicommand.UICommands(self, self.iocontroller,
            self.viewer, self.settings, self.filteredTaskList, self.effortList)
        viewerfactory.addTaskViewers(self.viewer, self.filteredTaskList, 
            self.uiCommands, self.settings)
        viewerfactory.addEffortViewers(self.viewer, self.effortList, 
            self.uiCommands, self.settings, 'effortviewer')
        self.SetToolBar(toolbar.ToolBar(self, self.uiCommands))
        import status
        self.SetStatusBar(status.StatusBar(self, self.taskFile,
                          self.filteredTaskList, self.viewer))
        import menu
        self.SetMenuBar(menu.MainMenu(self, self.uiCommands, self.settings))
        self.createTaskBarIcon(self.uiCommands)
        
    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.viewer, proportion=1, flag=wx.EXPAND)
        self._sizer.Add(self.findDialog, flag=wx.EXPAND|wx.ALL, border=1)
        self.panel.SetSizerAndFit(self._sizer)

    def initWindow(self):
        self.SetTitle(patterns.observer.Notification(self, filename=self.taskFile.filename()))
        self.SetIcon(wx.ArtProvider_GetIcon('taskcoach', wx.ART_FRAME_ICON, 
            (16, 16)))
        self.displayMessage(_('Welcome to %(name)s version %(version)s')%{'name': meta.name, 
            'version': meta.version}, pane=1)

    def initWindowComponents(self):
        self.onShowFindDialog()
        # We use CallAfter because otherwise the statusbar will appear at the 
        # top of the window when it is initially hidden and later shown.
        wx.CallAfter(self.onShowStatusBar) 
                
    def registerForWindowComponentChanges(self):
        self.taskFile.registerObserver(self.SetTitle)
        self.settings.registerObserver(self.onShowFindDialog, 
            ('view', 'finddialog'))
        self.settings.registerObserver(self.onShowStatusBar, 
            ('view', 'statusbar'))

    def onShowFindDialog(self, *args, **kwargs):
        self.showFindDialog(self.settings.getboolean('view', 'finddialog'))

    def onShowStatusBar(self, *args, **kwargs):
        self.showStatusBar(self.settings.getboolean('view', 'statusbar'))

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
        self.settings.set('file', 'lastfile', self.taskFile.lastFilename())
        if hasattr(self, 'taskBarIcon'):
            self.taskBarIcon.RemoveIcon()
        self.savePosition()
        self.settings.save()
        wx.GetApp().ProcessIdle()
        wx.GetApp().Exit()

    def restore(self, event):
        self.Show()
        self.Raise()
        self.Iconize(False)

    def onIconify(self, event):
        if event.Iconized():
            self.Hide()

    def showFindDialog(self, show=True):
        if not show:
            self.findDialog.clear()
        self._sizer.Show(self.findDialog, show)
        self._sizer.Layout()

    def showStatusBar(self, show=True):
        # FIXME: First hiding the statusbar, then hiding the toolbar, then
        # showing the statusbar puts it in the wrong place.
        self.GetStatusBar().Show(show)
        self._sizer.Layout()
        self.SendSizeEvent()

    def setToolBarSize(self, size):
        if self.GetToolBar():
            self.GetToolBar().Destroy()
        if size is None:
            self.SendSizeEvent()
        else:
            self.SetToolBar(toolbar.ToolBar(self, self.uiCommands, size=size))
    

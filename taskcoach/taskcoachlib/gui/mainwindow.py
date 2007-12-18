import wx, meta, patterns, widgets, command
import viewer, viewercontainer, viewerfactory, help, toolbar, uicommand,\
    remindercontroller
from i18n import _
from domain import task, effort


class WindowWithPersistentDimensions(wx.Frame):
    def __init__(self, settings, *args, **kwargs):
        super(WindowWithPersistentDimensions, self).__init__(None, -1, '')
        self._settings = settings
        self._section = 'window'
        self.setDimensions()
        self.Bind(wx.EVT_SIZE, self.onChangeSize)
        if self.startIconized():
            self.Iconize(True)
            wx.CallAfter(self.Hide)
            
    def startIconized(self):
        startIconized = self._settings.get(self._section, 'starticonized')
        if startIconized == 'Always':
            return True
        if startIconized == 'Never':
            return False
        return self.getSetting('iconized') 
        
    def setSetting(self, setting, value):
        self._settings.set(self._section, setting, str(value))
        
    def getSetting(self, setting):
        return eval(self._settings.get(self._section, setting))
        
    def setDimensions(self):
        width, height = self.getSetting('size')
        x, y = self.getSetting('position')
        self.SetDimensions(x, y, width, height)
        # Check that the window is on a valid display and move if necessary:
        if wx.Display.GetFromWindow(self) == wx.NOT_FOUND:
            self.SetDimensions(0, 0, width, height)

    def onChangeSize(self, event):
        self.setSetting('size', event.GetSize())
        event.Skip()
                
    def savePosition(self):
        iconized = self.IsIconized()
        if not iconized:
            self.setSetting('position', self.GetPosition())
        self.setSetting('iconized', iconized)

        
class MainWindow(WindowWithPersistentDimensions):
    def __init__(self, iocontroller, taskFile, effortList, settings, 
                 splash=None, *args, **kwargs):
        super(MainWindow, self).__init__(settings, *args, **kwargs)
        self.iocontroller = iocontroller
        self.taskFile = taskFile
        self.settings = settings
        self.effortList = effortList
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.splash = splash
        self.createWindowComponents()
        self.initWindowComponents()
        self.initWindow()
        self.registerForWindowComponentChanges()
        wx.CallAfter(self.closeSplash)
        wx.CallAfter(self.showTips)

    def createWindowComponents(self):
        self.panel = wx.Panel(self)
        self.viewer = viewercontainer.ViewerAUINotebook(self.panel, 
            self.settings, 'mainviewer') 
        self.uiCommands = uicommand.UICommands(self, self.iocontroller,
            self.viewer, self.settings, self.taskFile, self.effortList, 
            self.taskFile.categories(), self.taskFile.notes())
        self.initLayout()
        viewerfactory.addTaskViewers(self.viewer, self.taskFile, 
            self.uiCommands, self.settings, self.taskFile.categories())
        viewerfactory.addEffortViewers(self.viewer, self.taskFile, 
            self.uiCommands, self.settings)
        viewerfactory.addCategoryViewers(self.viewer, self.taskFile.categories(),
            self.uiCommands, self.settings)
        if self.settings.getboolean('feature', 'notes'):
            viewerfactory.addNoteViewers(self.viewer, self.taskFile.notes(),
                                         self.uiCommands, self.settings)
        import status
        self.SetStatusBar(status.StatusBar(self, self.viewer))
        import menu
        self.SetMenuBar(menu.MainMenu(self, self.uiCommands, self.settings))
        self.createTaskBarIcon(self.uiCommands)
        self.reminderController = \
            remindercontroller.ReminderController(self.taskFile, self.settings,
                self.uiCommands)
                
    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.viewer, proportion=1, flag=wx.EXPAND)
        self.panel.SetSizerAndFit(self._sizer)

    def initWindow(self):
        wx.GetApp().SetTopWindow(self)
        self.setTitle(self.taskFile.filename())
        self.setIcon()
        self.displayMessage(_('Welcome to %(name)s version %(version)s')% \
            {'name': meta.name, 'version': meta.version}, pane=1)

    def setIcon(self):
        bundle = wx.IconBundle()
        for size in [(16, 16), (22, 22), (32, 32), (48, 48), (64, 64), 
                     (128, 128)]:
            icon = wx.ArtProvider_GetIcon('taskcoach', wx.ART_FRAME_ICON, size)
            bundle.AddIcon(icon)
        self.SetIcons(bundle)

    def initWindowComponents(self):
        self.onShowToolBar()
        # We use CallAfter because otherwise the statusbar will appear at the 
        # top of the window when it is initially hidden and later shown.
        wx.CallAfter(self.onShowStatusBar) 
                
    def registerForWindowComponentChanges(self):
        patterns.Publisher().registerObserver(self.onFilenameChanged, 
            eventType='taskfile.filenameChanged')
        patterns.Publisher().registerObserver(self.onShowStatusBar, 
            eventType='view.statusbar')
        patterns.Publisher().registerObserver(self.onShowToolBar, 
            eventType='view.toolbar')

    def showTips(self):
        if self.settings.getboolean('window', 'tips'):
            help.showTips(self, self.settings)
            
    def closeSplash(self):
        if self.splash:
            self.splash.Destroy()
                         
    def onShowStatusBar(self, *args, **kwargs):
        self.showStatusBar(self.settings.getboolean('view', 'statusbar'))

    def onShowToolBar(self, *args, **kwargs):
        self.showToolBar(eval(self.settings.get('view', 'toolbar')))

    def createTaskBarIcon(self, uiCommands):
        if self.canCreateTaskBarIcon():
            import taskbaricon, menu
            self.taskBarIcon = taskbaricon.TaskBarIcon(self, self.taskFile, 
                self.settings)
            self.taskBarIcon.setPopupMenu(menu.TaskBarMenu(self.taskBarIcon,
                uiCommands))
        self.Bind(wx.EVT_ICONIZE, self.onIconify)

    def canCreateTaskBarIcon(self):
        try:
            import taskbaricon
            return True
        except:
            return False
        
    def onFilenameChanged(self, event):
        self.setTitle(event.value())

    def setTitle(self, filename):
        title = meta.name
        if filename:
            title += ' - %s'%filename
        self.SetTitle(title)
        
    def displayMessage(self, message, pane=0):
        self.GetStatusBar().SetStatusText(message, pane)

    def quit(self):
        if not self.iocontroller.close():
            return 
        # Clear task file specific settings (FIXME: save these in the task file)
        self.settings.set('view', 'tasksearchfilterstring', '') 
        self.settings.set('file', 'lastfile', self.taskFile.lastFilename())
        # Save the number of viewers for each viewer type:
        counts = {}
        for viewer in self.viewer:
            setting = viewer.__class__.__name__.lower() + 'count'
            counts[setting] = counts.get(setting, 0) + 1
        for key, value in counts.items():
            self.settings.set('view', key, str(value))
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
        else:
            event.Skip()
            
    def showStatusBar(self, show=True):
        # FIXME: First hiding the statusbar, then hiding the toolbar, then
        # showing the statusbar puts it in the wrong place (only on Linux?)
        self.GetStatusBar().Show(show)
        self._sizer.Layout()
        self.SendSizeEvent()

    def showToolBar(self, size):
        if self.GetToolBar():
            self.GetToolBar().Destroy()
        if size is not None:
            self.SetToolBar(toolbar.ToolBar(self, self.uiCommands, size=size))
        self.SendSizeEvent()

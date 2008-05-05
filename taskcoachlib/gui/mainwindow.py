'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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
from taskcoachlib import meta, patterns, widgets, command, help
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, effort
import viewer, viewercontainer, viewerfactory, toolbar, uicommand,\
    remindercontroller



class WindowDimensionsTracker(object):
    ''' Track the dimensions (position and size) of a window in the 
        settings. '''
    def __init__(self, window, settings, *args, **kwargs):
        super(WindowDimensionsTracker, self).__init__(*args, **kwargs)
        self._settings = settings
        self._section = 'window'
        self._window = window
        self.setDimensions()
        self._window.Bind(wx.EVT_SIZE, self.onChangeSize)
        if self.startIconized():
            self._window.Iconize(True)
            wx.CallAfter(self._window.Hide)
            
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
        self._window.SetDimensions(x, y, width, height)
        # Check that the window is on a valid display and move if necessary:
        if wx.Display.GetFromWindow(self._window) == wx.NOT_FOUND:
            self._window.SetDimensions(0, 0, width, height)

    def onChangeSize(self, event):
        self.setSetting('size', event.GetSize())
        event.Skip()
                
    def savePosition(self):
        iconized = self._window.IsIconized()
        if not iconized:
            self.setSetting('position', self._window.GetPosition())
        self.setSetting('iconized', iconized)


class AuiManagedFrameWithNotebookAPI(wx.Frame):
    ''' An AUI managed frame that provides (part of) the notebook API. This
        class is to be moved to the widgets package. '''

    def __init__(self, *args, **kwargs):
        super(AuiManagedFrameWithNotebookAPI, self).__init__(*args, **kwargs)
        self.manager = wx.aui.AuiManager(self, 
            wx.aui.AUI_MGR_DEFAULT|wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE)
        self.Bind(wx.aui.EVT_AUI_RENDER, self.onRender)
        
    def onRender(self, event):
        ''' Whenever the AUI managed frames get rendered, make sure the active
            pane has focus. '''
        for pane in self.manager.GetAllPanes():
            if pane.HasFlag(wx.aui.AuiPaneInfo.optionActive):
                pane.window.SetFocus()
                break
        event.Skip()

    def AddPage(self, page, caption, name): 
        paneInfo = wx.aui.AuiPaneInfo().Name(name).Caption(caption).Left().FloatingSize((300,200))
        # To ensure we have a center pane we make the first pane the center pane:
        if not self.manager.GetAllPanes():
            paneInfo = paneInfo.Center().CloseButton(False)
        self.manager.AddPane(page, paneInfo)
        self.manager.Update()

    def SetPageText(self, index, title):
        self.manager.GetAllPanes()[index].Caption(title)

    def GetPageIndex(self, window):
        for index, paneInfo in enumerate(self.manager.GetAllPanes()):
            if paneInfo.window == window:
                return index
        return wx.NOT_FOUND
     
    def AdvanceSelection(self, forward=True): 
        # FIXME: duplicated from widgets.AUINotebook.AdvanceSelection
        if self.PageCount <= 1:
            return # Not enough viewers to advance selection
        if forward:
            if 0 <= self.Selection < self.PageCount - 1:
                self.Selection += 1
            else:
                self.Selection = 0
        else:
            if 1 <= self.Selection < self.PageCount:
                self.Selection -= 1
            else:
                self.Selection = self.PageCount - 1

    def GetPageCount(self):
        return len(self.manager.GetAllPanes())
    
    PageCount = property(GetPageCount)
        
    def GetSelection(self):
        for index, paneInfo in enumerate(self.manager.GetAllPanes()):
            if paneInfo.HasFlag(wx.aui.AuiPaneInfo.optionActive):
                return index
        return wx.NOT_FOUND

    def SetSelection(self, targetIndex, *args):
        for index, paneInfo in enumerate(self.manager.GetAllPanes()):
            self.manager.GetAllPanes()[index].SetFlag(wx.aui.AuiPaneInfo.optionActive, index==targetIndex)
        self.manager.Update()
        
    Selection = property(GetSelection, SetSelection)
    
    
class MainWindow(AuiManagedFrameWithNotebookAPI):
    pageClosedEvent = wx.aui.EVT_AUI_PANE_CLOSE
    
    def __init__(self, iocontroller, taskFile, settings, 
                 splash=None, *args, **kwargs):
        super(MainWindow, self).__init__(None, -1, '', *args, **kwargs)
        self.dimensionsTracker = WindowDimensionsTracker(self, settings)
        self.iocontroller = iocontroller
        self.taskFile = taskFile
        self.settings = settings
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.splash = splash
        self.createWindowComponents()
        self.initWindowComponents()
        self.initWindow()
        self.registerForWindowComponentChanges()
        wx.CallAfter(self.closeSplash)
        wx.CallAfter(self.showTips)

    def createWindowComponents(self):
        self.viewer = viewercontainer.ViewerContainer(self,
            self.settings, 'mainviewer') 
        self.uiCommands = uicommand.UICommands(self, self.iocontroller,
            self.viewer, self.settings, self.taskFile.tasks(), 
            self.taskFile.efforts(), self.taskFile.categories(), 
            self.taskFile.notes())
        viewerfactory.addTaskViewers(self.viewer, self.taskFile.tasks(), 
            self.uiCommands, self.settings, self.taskFile.categories())
        viewerfactory.addEffortViewers(self.viewer, self.taskFile.tasks(), 
            self.uiCommands, self.settings)
        viewerfactory.addCategoryViewers(self.viewer, self.taskFile.categories(),
            self.uiCommands, self.settings)
        if self.settings.getboolean('feature', 'notes'):
            viewerfactory.addNoteViewers(self.viewer, self.taskFile.notes(),
                                         self.uiCommands, self.settings,
                                         self.taskFile.categories())
        import status
        self.SetStatusBar(status.StatusBar(self, self.viewer))
        import menu
        self.SetMenuBar(menu.MainMenu(self, self.uiCommands, self.settings))
        self.createTaskBarIcon(self.uiCommands)
        self.reminderController = \
            remindercontroller.ReminderController(self.taskFile.tasks(), 
                self.taskFile.categories(), self.settings, self.uiCommands)
        
    def AddPage(self, page, caption, *args):
        name = page.settingsSection()
        super(MainWindow, self).AddPage(page, caption, name)

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
        perspective = self.settings.get('view', 'perspective')
        if perspective:
            self.manager.LoadPerspective(perspective)
        self.manager.Update()
                
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
            self.taskBarIcon = taskbaricon.TaskBarIcon(self, 
                self.taskFile.tasks(), self.settings)
            self.taskBarIcon.setPopupMenu(menu.TaskBarMenu(self.taskBarIcon,
                uiCommands, self.taskFile.tasks()))
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
        # Remember what the user was working on: 
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
        self.settings.set('view', 'perspective', self.manager.SavePerspective())
        self.dimensionsTracker.savePosition()
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
        self.SendSizeEvent()

    def showToolBar(self, size):
        # Current version of wxPython (2.7.8.1) has a bug 
        # (https://sourceforge.net/tracker/?func=detail&atid=109863&aid=1742682&group_id=9863)
        # that makes adding controls to a toolbar not working. Also, when the 
        # toolbar is visible it's nearly impossible to enter text into text
        # controls. Immediately after you click on a text control the focus
        # is removed. We work around it by not having AUI manage the toolbar
        # on Mac OS X:
        if '__WXMAC__' in wx.PlatformInfo:
            if self.GetToolBar():
                self.GetToolBar().Destroy()
            if size is not None:
                self.SetToolBar(toolbar.ToolBar(self, self.uiCommands, size=size))
            self.SendSizeEvent()
        else:
            currentToolbar = self.manager.GetPane('toolbar')
            if currentToolbar.IsOk():
                self.manager.DetachPane(currentToolbar.window)
                currentToolbar.window.Destroy()
            if size is None:
                self.Unbind(self.pageClosedEvent)
            else:
                bar = toolbar.ToolBar(self, self.uiCommands, size=size)
                self.manager.AddPane(bar, wx.aui.AuiPaneInfo().Name('toolbar').
                                     Caption('Toolbar').ToolbarPane().Top().DestroyOnClose().
                                     LeftDockable(False).RightDockable(False))
                self.Bind(self.pageClosedEvent, self.onCloseToolBar)
            self.manager.Update()

    def onCloseToolBar(self, event):
        if event.GetPane().IsToolbar():
            self.settings.set('view', 'toolbar', 'None')
        # Don't call event.Skip(), it crashes TC on Ubuntu. Don't know why.
# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import application, meta, widgets, \
    operating_system # pylint: disable=W0622
from taskcoachlib.gui import viewer, toolbar, uicommand, remindercontroller, \
    artprovider, windowdimensionstracker, idlecontroller
from taskcoachlib.gui.dialog.xfce4warning import XFCE4WarningDialog
from taskcoachlib.gui.threads import DeferredCallMixin, synchronized
from taskcoachlib.i18n import _
from taskcoachlib.powermgt import PowerStateMixin
from taskcoachlib.help.balloontips import BalloonTipManager
from taskcoachlib.thirdparty.pubsub import pub
import taskcoachlib.thirdparty.aui as aui
import wx, ctypes


def turn_on_double_buffering_on_windows(window):
    # This has actually an adverse effect when Aero is enabled...
    from ctypes import wintypes
    dll = ctypes.WinDLL('dwmapi.dll')
    ret = wintypes.BOOL()
    if dll.DwmIsCompositionEnabled(ctypes.pointer(ret)) == 0 and ret.value:
        return
    import win32gui, win32con  # pylint: disable=F0401
    exstyle = win32gui.GetWindowLong(window.GetHandle(), win32con.GWL_EXSTYLE)
    exstyle |= win32con.WS_EX_COMPOSITED
    win32gui.SetWindowLong(window.GetHandle(), win32con.GWL_EXSTYLE, exstyle)


class MainWindow(DeferredCallMixin, PowerStateMixin, BalloonTipManager,
                 widgets.AuiManagedFrameWithDynamicCenterPane):
    def __init__(self, iocontroller, taskStore, settings, *args, **kwargs):
        self.__splash = kwargs.pop('splash', None)
        super(MainWindow, self).__init__(None, -1, '', *args, **kwargs)
        # This prevents the viewers from flickering on Windows 7 when refreshed:
        if operating_system.isWindows7_OrNewer():
            turn_on_double_buffering_on_windows(self)
        self.__dimensions_tracker = windowdimensionstracker.WindowDimensionsTracker(self, settings)
        self.iocontroller = iocontroller
        self.taskStore = taskStore
        self.settings = settings
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_ICONIZE, self.onIconify)
        self.Bind(wx.EVT_SIZE, self.onResize)
        self._create_window_components()  # Not private for test purposes
        self.__init_window_components()
        self.__init_window()
        self.__register_for_window_component_changes()

        self.bonjourRegister = None

        self._idleController = idlecontroller.IdleController(self,
                                                             self.settings,
                                                             self.taskStore.efforts())

        wx.CallAfter(self.checkXFCE4)

    def checkXFCE4(self):
        if operating_system.isGTK():
            mon = application.Application().sessionMonitor
            if mon is not None and \
                    self.settings.getboolean('feature', 'usesm2') and \
                    self.settings.getboolean('feature', 'showsmwarning') and \
                    mon.vendor == 'xfce4-session':
                dlg = XFCE4WarningDialog(self, self.settings)
                dlg.Show()

    def _create_window_components(self):  # Not private for test purposes
        self._create_viewer_container()
        viewer.addViewers(self.viewer, self.taskStore, self.settings)
        self._create_status_bar()
        self.__create_menu_bar()
        self.__create_reminder_controller()
        
    def _create_viewer_container(self):  # Not private for test purposes
        # pylint: disable=W0201
        self.viewer = viewer.ViewerContainer(self, self.settings) 
        
    def _create_status_bar(self):
        from taskcoachlib.gui import status  # pylint: disable=W0404
        self.SetStatusBar(status.StatusBar(self, self.viewer))
        
    def __create_menu_bar(self):
        from taskcoachlib.gui import menu  # pylint: disable=W0404
        self.SetMenuBar(menu.MainMenu(self, self.settings, self.iocontroller, 
                                      self.viewer, self.taskStore))
    
    def __create_reminder_controller(self):
        # pylint: disable=W0201
        self.reminderController = \
            remindercontroller.ReminderController(self, self.taskStore.tasks(),
                self.taskStore.efforts(), self.settings)
        
    def addPane(self, page, caption, floating=False):  # pylint: disable=W0221
        name = page.settingsSection()
        super(MainWindow, self).addPane(page, caption, name, floating=floating)
        
    def __init_window(self):
        self.setTitle(self.taskStore.filename())
        self.SetIcons(artprovider.iconBundle('taskcoach'))
        self.displayMessage(_('Welcome to %(name)s version %(version)s') % \
            {'name': meta.name, 'version': meta.version}, pane=1)

    def __init_window_components(self):
        self.showToolBar(self.settings.getvalue('view', 'toolbar'))
        # We use CallAfter because otherwise the statusbar will appear at the 
        # top of the window when it is initially hidden and later shown.
        wx.CallAfter(self.showStatusBar, 
                     self.settings.getboolean('view', 'statusbar'))
        self.__restore_perspective()
            
    def __restore_perspective(self):
        perspective = self.settings.get('view', 'perspective')
        for viewer_type in viewer.viewerTypes():
            if self.__perspective_and_settings_viewer_count_differ(viewer_type):
                # Different viewer counts may happen when the name of a viewer 
                # is changed between versions
                perspective = ''
                break

        try:
            self.manager.LoadPerspective(perspective)
        except ValueError, reason:
            # This has been reported to happen. Don't know why. Keep going
            # if it does.
            if self.__splash:
                self.__splash.Destroy()
            wx.MessageBox(_('''Couldn't restore the pane layout from TaskCoach.ini:
%s

The default pane layout will be used.

If this happens again, please make a copy of your TaskCoach.ini file '''
'''before closing the program, open a bug report, and attach the '''
'''copied TaskCoach.ini file to the bug report.''') % reason,
            _('%s settings error') % meta.name, style=wx.OK | wx.ICON_ERROR)
            self.manager.LoadPerspective('')
        
        for pane in self.manager.GetAllPanes():
            # Prevent zombie panes by making sure all panes are visible
            if not pane.IsShown():
                pane.Show()
            # Ignore the titles that are saved in the perspective, they may be
            # incorrect when the user changes translation:
            if hasattr(pane.window, 'title'):
                pane.Caption(pane.window.title())
        self.manager.Update()
        
    def __perspective_and_settings_viewer_count_differ(self, viewer_type):
        perspective = self.settings.get('view', 'perspective')
        perspective_viewer_count = perspective.count('name=%s' % viewer_type)
        settings_viewer_count = self.settings.getint('view', 
                                                     '%scount' % viewer_type)
        return perspective_viewer_count != settings_viewer_count
    
    def __register_for_window_component_changes(self):
        pub.subscribe(self.setTitle, 'taskstore.filenameChanged')
        pub.subscribe(self.showStatusBar, 'settings.view.statusbar')
        pub.subscribe(self.showToolBar, 'settings.view.toolbar')
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.onCloseToolBar)

    def setTitle(self, filename):
        title = meta.name
        if filename:
            title += ' - %s' % filename
        self.SetTitle(title)
        
    def displayMessage(self, message, pane=0):
        self.GetStatusBar().SetStatusText(message, pane)
        
    def save_settings(self):
        self.__save_viewer_counts()
        self.__save_perspective()
        self.__save_position()

    def __save_viewer_counts(self):
        ''' Save the number of viewers for each viewer type. '''
        for viewer_type in viewer.viewerTypes():
            count = len([v for v in self.viewer if v.__class__.__name__.lower() == viewer_type])
            self.settings.set('view', viewer_type + 'count', str(count))
            
    def __save_perspective(self):
        perspective = self.manager.SavePerspective()
        self.settings.set('view', 'perspective', perspective)
        
    def __save_position(self):
        self.__dimensions_tracker.save_position()
        
    def onClose(self, event):
        if event.CanVeto() and self.settings.getboolean('window', 
                                                        'hidewhenclosed'):
            event.Veto()
            self.Iconize()
        else:
            if application.Application().quitApplication():
                event.Skip()
                self.taskStore.stop()
                self._idleController.stop()

    def restore(self, event):  # pylint: disable=W0613
        if self.settings.getboolean('window', 'maximized'):
            self.Maximize()
        self.Iconize(False)
        self.Show()
        self.Raise()
        self.Refresh()

    def onIconify(self, event):
        if event.Iconized() and self.settings.getboolean('window', 
                                                         'hidewheniconized'):
            self.Hide()
        else:
            event.Skip()

    def onResize(self, event):
        currentToolbar = self.manager.GetPane('toolbar')
        if currentToolbar.IsOk():
            currentToolbar.window.SetSize((event.GetSize().GetWidth(), -1))
            currentToolbar.window.SetMinSize((event.GetSize().GetWidth(), 42))
        event.Skip()

    def showStatusBar(self, value=True):
        # FIXME: First hiding the statusbar, then hiding the toolbar, then
        # showing the statusbar puts it in the wrong place (only on Linux?)
        self.GetStatusBar().Show(value)
        self.SendSizeEvent()
        
    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this window. ''' 
        uiCommands = [
                uicommand.FileOpen(iocontroller=self.iocontroller), 
                uicommand.FileSave(iocontroller=self.iocontroller),
                uicommand.FileMergeDiskChanges(iocontroller=self.iocontroller),
                uicommand.Print(viewer=self.viewer, settings=self.settings), 
                None, 
                uicommand.EditUndo(), 
                uicommand.EditRedo()]
        if self.settings.getboolean('feature', 'effort'):
            uiCommands.extend([ 
                None, 
                uicommand.EffortStartButton(taskList=self.taskStore.tasks()), 
                uicommand.EffortStop(viewer=self.viewer,
                                     effortList=self.taskStore.efforts(),
                                     taskList=self.taskStore.tasks())])
        return uiCommands

    def getToolBarPerspective(self):
        return self.settings.get('view', 'toolbarperspective')

    def saveToolBarPerspective(self, perspective):
        self.settings.set('view', 'toolbarperspective', perspective)

    def showToolBar(self, value):
        currentToolbar = self.manager.GetPane('toolbar')
        if currentToolbar.IsOk():
            self.manager.DetachPane(currentToolbar.window)
            currentToolbar.window.Destroy()
        if value:
            bar = toolbar.MainToolBar(self, self.settings, size=value)
            self.manager.AddPane(bar, aui.AuiPaneInfo().Name('toolbar').
                                 Caption('Toolbar').ToolbarPane().Top().DestroyOnClose().
                                 LeftDockable(False).RightDockable(False))
            # Using .Gripper(False) does not work here
            wx.CallAfter(bar.SetGripperVisible, False)
        self.manager.Update()

    def onCloseToolBar(self, event):
        if event.GetPane().IsToolbar():
            self.settings.setvalue('view', 'toolbar', None)
        event.Skip()
        
    # Viewers
    
    def advanceSelection(self, forward):
        self.viewer.advanceSelection(forward)
        
    def viewerCount(self):
        return len(self.viewer)

    # Power management

    def OnPowerState(self, state):
        pub.sendMessage('powermgt.%s' % {self.POWERON: 'on', self.POWEROFF: 'off'}[state])

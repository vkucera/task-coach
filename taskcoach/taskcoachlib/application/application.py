'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

import wx, os, locale
from taskcoachlib import patterns

        
class wxApp(wx.App):
    def OnInit(self):
        self.Bind(wx.EVT_QUERY_END_SESSION, self.onQueryEndSession)
        return True
    
    def onQueryEndSession(self, event):
        # This makes sure we don't block shutdown on Windows
        pass # pragma: no cover
    

class Application(object):
    __metaclass__ = patterns.Singleton
    
    def __init__(self, options=None, args=None, **kwargs):
        self._options = options
        self._args = args
        self.wxApp = wxApp(redirect=False)
        self.init(**kwargs)

    def start(self):
        ''' Call this to start the Application. '''
        if self.settings.getboolean('version', 'notify'):
            from taskcoachlib import meta
            # pylint: disable-msg=W0201
            self.vc = meta.VersionChecker(self.settings)
            self.vc.start()
        self.copyDefaultTemplates()
        self.mainwindow.Show()
        self.wxApp.MainLoop()
        
    def copyDefaultTemplates(self):
        ''' Copy default templates that don't exist yet in the user's
            template directory. '''
        from taskcoachlib.persistence import getDefaultTemplates
        templateDir = self.settings.pathToTemplatesDir()
        if len([name for name in os.listdir(templateDir) if name.endswith('.tsktmpl')]) == 0:
            for name, template in getDefaultTemplates():
                filename = os.path.join(templateDir, name + '.tsktmpl')
                if not os.path.exists(filename):
                    file(filename, 'wb').write(template)
        
    def init(self, loadSettings=True, loadTaskFile=True):
        ''' Initialize the application. Needs to be called before 
            Application.start(). ''' 
        self.initConfig(loadSettings)
        self.initLanguage()
        self.initPrinting()
        self.initDomainObjects()
        self.initApplication()
        from taskcoachlib import gui, persistence
        gui.init()
        showSplashScreen = self.settings.getboolean('window', 'splash')
        splash = gui.SplashScreen() if showSplashScreen else None
        # pylint: disable-msg=W0201
        self.taskFile = persistence.LockedTaskFile()
        self.autoSaver = persistence.AutoSaver(self.settings)
        self.autoBackup = persistence.AutoBackup(self.settings)
        self.iocontroller = gui.IOController(self.taskFile, self.displayMessage, 
                                             self.settings)
        self.mainwindow = gui.MainWindow(self.iocontroller, self.taskFile, 
                                         self.settings)
        self.wxApp.SetTopWindow(self.mainwindow)
        if not self.settings.getboolean('file', 'inifileloaded'):
            self.warnUserThatIniFileWasNotLoaded()
        if loadTaskFile:
            self.iocontroller.openAfterStart(self._args)
        wx.SystemOptions.SetOptionInt("mac.textcontrol-use-spell-checker",
            self.settings.getboolean('editor', 'maccheckspelling'))
        self.registerSignalHandlers()
        self.createMutex()
        self.createTaskBarIcon()
        wx.CallAfter(self.closeSplash, splash)
        wx.CallAfter(self.showTips)
                
    def initConfig(self, loadSettings):
        from taskcoachlib import config
        iniFile = self._options.inifile if self._options else None
        # pylint: disable-msg=W0201
        self.settings = config.Settings(loadSettings, iniFile)
        
    def initLanguage(self):
        ''' Initialize the current translation. '''
        from taskcoachlib import i18n
        i18n.Translator(self.determineLanguage(self._options, self.settings))
        
    @staticmethod
    def determineLanguage(options, settings, locale=locale):
        language = None
        if options: 
            # User specified language or .po file on command line
            language = options.pofile or options.language
        if not language:
            # Get language as set by the user via the preferences dialog
            language = settings.get('view', 'language_set_by_user')
        if not language:
            # Get language as set by the user or externally (e.g. PortableApps)
            language = settings.get('view', 'language')
        if not language:
            # Use the user's locale
            language = locale.getdefaultlocale()[0]
            if language == 'C':
                language = None
        if not language:
            # Fall back on what the majority of our users use
            language = 'en_US'
        return language
        
    def initPrinting(self):
        ''' Prepare for printing. '''
        # On Jolicloud, printing crashes unless we do this:
        if '__WXGTK__' == wx.Platform:
            try:
                import gtk
                gtk.remove_log_handlers()
            except ImportError:
                pass

    def initDomainObjects(self):
        ''' Provide relevant domain objects with access to the settings. '''
        from taskcoachlib.domain import task
        task.Task.settings = self.settings
        
    def initApplication(self):
        from taskcoachlib import meta
        self.wxApp.SetAppName(meta.name)
        self.wxApp.SetVendorName(meta.author)
                
    def registerSignalHandlers(self):
        quit = lambda *args: self.quit()
        if '__WXMSW__' == wx.Platform:
            import win32api
            win32api.SetConsoleCtrlHandler(quit, True)
        else:
            import signal
            signal.signal(signal.SIGTERM, quit)
            if hasattr(signal, 'SIGHUP'):
                forcedQuit = lambda *args: self.quit(force=True)
                signal.signal(signal.SIGHUP, forcedQuit) # pylint: disable-msg=E1101
        
    def createMutex(self):
        ''' On Windows, create a mutex so that InnoSetup can check whether the
            application is running. '''
        if '__WXMSW__' == wx.Platform:
            import ctypes
            from taskcoachlib import meta
            ctypes.windll.kernel32.CreateMutexA(None, False, meta.filename)

    def createTaskBarIcon(self):
        if self.canCreateTaskBarIcon():
            from taskcoachlib.gui import taskbaricon, menu
            self.taskBarIcon = taskbaricon.TaskBarIcon(self.mainwindow, 
                self.taskFile.tasks(), self.settings)
            self.taskBarIcon.setPopupMenu(menu.TaskBarMenu(self.taskBarIcon, 
                self.settings, self.taskFile))

    def canCreateTaskBarIcon(self):
        try:
            from taskcoachlib.gui import taskbaricon # pylint: disable-msg=W0612
            return True
        except:
            return False # pylint: disable-msg=W0702
                    
    @staticmethod
    def closeSplash(splash):
        if splash:
            splash.Destroy()
            
    def showTips(self):
        if self.settings.getboolean('window', 'tips'):
            from taskcoachlib import help
            help.showTips(self.mainwindow, self.settings)

    def warnUserThatIniFileWasNotLoaded(self):
        from taskcoachlib import meta
        from taskcoachlib.i18n import _
        reason = self.settings.get('file', 'inifileloaderror')
        wx.MessageBox(\
            _("Couldn't load settings from TaskCoach.ini:\n%s")%reason,
            _('%s file error')%meta.name, style=wx.OK|wx.ICON_ERROR)
        self.settings.setboolean('file', 'inifileloaded', True) # Reset

    def displayMessage(self, message):
        self.mainwindow.displayMessage(message)

    def quit(self, force=False):
        if not self.iocontroller.close(force=force):
            return
        # Remember what the user was working on: 
        self.settings.set('file', 'lastfile', self.taskFile.lastFilename())
        self.mainwindow.saveSettings()
        self.settings.save()
        if hasattr(self, 'taskBarIcon'):
            self.taskBarIcon.RemoveIcon()
        if self.mainwindow.bonjourRegister is not None:
            self.mainwindow.bonjourRegister.stop()
        self.wxApp.ProcessIdle()
        self.wxApp.ExitMainLoop()

        # For PowerStateMixin
        self.mainwindow.OnQuit()

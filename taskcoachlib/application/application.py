'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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

import wx, os, signal

        
class wxApp(wx.App):
    def OnInit(self):
        self.Bind(wx.EVT_QUERY_END_SESSION, self.onQueryEndSession)
        return True
    
    def onQueryEndSession(self, event):
        # This makes sure we don't block shutdown on Windows
        pass
    

class Application(object):
    def __init__(self, options=None, args=None, **kwargs):
        self._options = options
        self._args = args
        self.wxApp = wxApp(redirect=False)
        self.init(**kwargs)

    def start(self):
        ''' Call this to start the Application. '''
        if self.settings.getboolean('version', 'notify'):
            from taskcoachlib import meta
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
        for name, template in getDefaultTemplates():
            filename = os.path.join(templateDir, name + '.tsktmpl')
            if not os.path.exists(filename):
                file(filename, 'wb').write(template)
        
    def init(self, loadSettings=True, loadTaskFile=True):
        ''' Initialize the application. Needs to be called before 
            Application.start(). ''' 
        self.initConfig(loadSettings)
        self.initLanguage()
        from taskcoachlib import gui, persistence, meta
        from taskcoachlib.domain import task
        self.wxApp.SetAppName(meta.name)
        self.wxApp.SetVendorName(meta.author)
        gui.init()
        if self.settings.getboolean('window', 'splash'):
            splash = gui.SplashScreen()
        else:
            splash = None
        self.taskFile = persistence.LockedTaskFile()
        self.autoSaver = persistence.AutoSaver(self.settings)
        self.taskRelationshipManager = task.TaskRelationshipManager( \
            taskList=self.taskFile.tasks(), settings=self.settings)
        self.io = gui.IOController(self.taskFile, self.displayMessage, self.settings)
        self.mainwindow = gui.MainWindow(self.io, self.taskFile, self.settings, 
                                         splash)
        if not self.settings.getboolean('file', 'inifileloaded'):
            self.warnUserThatIniFileWasNotLoaded()
        if loadTaskFile:
            self.io.openAfterStart(self._args)
        wx.SystemOptions.SetOptionInt("mac.textcontrol-use-spell-checker",
                                      self.settings.getboolean('editor', 'maccheckspelling'))
        self.registerSignalHandlers()
        
    def initConfig(self, loadSettings):
        from taskcoachlib import config
        iniFile = self._options.inifile if self._options else None
        self.settings = config.Settings(loadSettings, iniFile)
        
    def initLanguage(self):
        from taskcoachlib import i18n
        language = None
        if self._options:
            language = self._options.pofile or self._options.language
        if not language:
            language = self.settings.get('view', 'language')
        i18n.Translator(language)
                
    def registerSignalHandlers(self):
        signal.signal(signal.SIGTERM, self.onSIGTERM)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self.onSIGHUP)

    def onSIGTERM(self, *args):
        ''' onSIGTERM is called when the process receives a TERM signal. '''
        # Give the user time to save the file:
        self.mainwindow.quit()

    def onSIGHUP(self, *args):
        ''' onSIGHUP is called when the process receives a HUP signal, 
            typically when the user logs out. '''
        # No time to pop up dialogs, force quit:
        self.mainwindow.quit(force=True)

    def warnUserThatIniFileWasNotLoaded(self):
        from taskcoachlib import meta
        from taskcoachlib.i18n import _
        reason = self.settings.get('file', 'inifileloaderror')
        wx.MessageBox(\
            _("Couldn't load settings from TaskCoach.ini:\n%s")%reason,
            _('%s file error')%meta.name, style=wx.ICON_ERROR)
        self.settings.setboolean('file', 'inifileloaded', True) # Reset

    def displayMessage(self, message):
        self.mainwindow.displayMessage(message)

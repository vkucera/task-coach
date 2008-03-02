#!/usr/bin/env python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
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

import sys
if not hasattr(sys, "frozen"):
    import wxversion
    try:
        wxversion.ensureMinimal("2.8-unicode", optionsRequired=True)
    except:
        pass
    try:
        import taskcoachlib
    except ImportError:
        sys.stderr.write('''ERROR: cannot import the library 'taskcoachlib'.
Please see http://www.taskcoach.org/faq.html for more information and
possible resolutions.''')
        sys.exit(1)
    # We don't want to use 'from taskcoachlib import X' all the time, so we add 
    # the taskcoachlib directory to the search path:
    libpath = taskcoachlib.__path__[0]
    if libpath not in sys.path:
        sys.path.insert(0, libpath) 
    del taskcoachlib

import wx

        
class wxApp(wx.App):
    def OnInit(self):
        self.Bind(wx.EVT_QUERY_END_SESSION, self.onQueryEndSession)
        self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)
        return True
    
    def onQueryEndSession(self, event):
        # This makes sure we don't block shutdown on Windows
        pass
    

class App(object):
    def __init__(self, options=None, args=None, **kwargs):
        self._options = options
        self._args = args
        self.wxApp = wxApp(redirect=False)
        self.init(**kwargs)

    def start(self):
        ''' Call this to start the App. '''
        if self.settings.getboolean('version', 'notify'):
            import meta.versionchecker as vc
            self.vc = vc.VersionChecker(self.settings)
            self.vc.start()
        self.mainwindow.Show()
        self.wxApp.MainLoop()
        
    def init(self, loadSettings=True, loadTaskFile=True): 
        import config, i18n
        if self._options:
            iniFile = self._options.inifile
        else:
            iniFile = None
        self.settings = settings = config.Settings(loadSettings, iniFile)
        i18n.Translator(settings.get('view', 'language'))
        import gui, persistence
        from domain import task
        import meta
        self.wxApp.SetAppName(meta.name)
        self.wxApp.SetVendorName(meta.author)
        gui.init()
        if settings.getboolean('window', 'splash'):
            splash = gui.SplashScreen()
        else:
            splash = None
        
        self.taskFile = persistence.TaskFile()
        self.autoSaver = persistence.AutoSaver(settings)
        self.taskRelationshipManager = task.TaskRelationshipManager( \
            taskList=self.taskFile.tasks(), settings=settings)
        self.io = gui.IOController(self.taskFile, self.displayMessage, settings)
        self.mainwindow = gui.MainWindow(self.io, self.taskFile, settings, splash)
        if loadTaskFile:
            self.io.openAfterStart(self._args)
        
    def displayMessage(self, message):
        self.mainwindow.displayMessage(message)


def start():
    import config
    options, args = config.ApplicationOptionParser().parse_args()
    app = App(options, args)
    if options.profile:
        import hotshot
        profiler = hotshot.Profile('.profile')
        profiler.runcall(app.start)
    else:
        app.start()


if __name__ == '__main__':
    start()

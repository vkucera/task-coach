#!/usr/bin/env python

import sys
if not hasattr(sys, "frozen"):
    import wxversion
    try:
        wxversion.ensureMinimal("2.6")
    except:
        pass
    import taskcoachlib
    # We don't want to use 'from taskcoachlib import X' all the time, so we add 
    # the taskcoachlib directory to the search path:
    libpath = taskcoachlib.__path__[0]
    sys.path.insert(0, libpath) 
    del taskcoachlib

import wx


class wxApp(wx.App):
    def OnInit(self):
        return True


class App(object):
    def __init__(self, options=None, args=None, **kwargs):
        self._options = options
        self._args = args
        self.wxApp = wxApp(0)
        self.init(**kwargs)

    def start(self):
        ''' Call this to start the App. '''
        self.mainwindow.Show()
        self.wxApp.MainLoop()

    def init(self, loadSettings=True, loadTaskFile=True): 
        import config, i18n
        settings = config.Settings(loadSettings)
        i18n.Translator(settings.get('view', 'language'))
        import gui, persistence
        import domain.task as task
        import domain.effort as effort
	import meta
        self.wxApp.SetAppName(meta.name)
        self.wxApp.SetVendorName(meta.author)
        gui.init()
        if settings.getboolean('window', 'splash'):
            splash = gui.SplashScreen()
        else:
            splash = None
        
        self.taskFile = persistence.TaskFile()
        self.autoSaver = persistence.AutoSaver(settings, self.taskFile)
        self.taskRelationshipManager = task.TaskRelationshipManager(taskList=self.taskFile, settings=settings)
        effortList = effort.EffortList(self.taskFile)
        self.io = gui.IOController(self.taskFile, self.displayMessage, settings)
        categoryFilteredTaskList = task.filter.CategoryFilter(self.taskFile)
        self.mainwindow = gui.MainWindow(self.io, self.taskFile, 
            categoryFilteredTaskList, effortList, settings, splash)
        self.processCommandLineArguments(settings, loadTaskFile)
        
    def processCommandLineArguments(self, settings, load=True):
        # FIXME: move to IOController
        if self._args:
            filename = self._args[0]
        else:
            filename = settings.get('file', 'lastfile')
        if load and filename:
            self.io.open(filename)

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

#!/usr/bin/env python

import sys
if not hasattr(sys, "frozen"):
    import wxversion
    wxversion.ensureMinimal("2.5.5")
    import taskcoachlib
    # We don't want to use 'from taskcoachlib import X' all the time, so we add 
    # the taskcoachlib directory to the search path:
    libpath = taskcoachlib.__path__[0]
    sys.path.append(libpath) 
    del taskcoachlib

import wx


class wxApp(wx.App):
    def OnInit(self):
        return True


class App(object):
    def __init__(self, options=None, args=None):
        self._options = options
        self._args = args
        self.wxApp = wxApp(0)
        self.init()
        self.mainwindow.Show()
        self.wxApp.MainLoop()

    def init(self, showSplash=True, load=True): 
        import config, i18n
        settings = config.Settings(load)
        i18n.Translator(settings.get('view', 'language'))
        import task, effort, gui
        gui.init()
        if showSplash and settings.getboolean('window', 'splash'):
            splash = gui.SplashScreen()
        
        self.taskFile = task.TaskFile()
        self.autoSaver = task.AutoSaver(settings, self.taskFile)
        effortList = effort.EffortList(self.taskFile)
        self.io = gui.IOController(self.taskFile, self.displayMessage)
        viewFilteredTaskList = task.filter.ViewFilter(self.taskFile)
        categoryFilteredTaskList = task.filter.CategoryFilter(viewFilteredTaskList)
        searchFilteredTaskList = task.filter.SearchFilter(categoryFilteredTaskList)
        sortedTaskList = task.sorter.Sorter(searchFilteredTaskList)
        self.mainwindow = gui.MainWindow(self.io, self.taskFile, 
            sortedTaskList, effortList, settings)
        self.processCommandLineArguments(settings, load)
        
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

    def quit(self):
        self.wxApp.ProcessIdle()
        self.wxApp.Exit()

if __name__ == '__main__':
    import config
    options, args = config.ApplicationOptionParser().parse_args()
    if options.profile:
        import hotshot
        profiler = hotshot.Profile('.profile')
        profiler.runcall(App, options, args)
    else:
        App(options, args)



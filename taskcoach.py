#!/usr/bin/env python

import sys, wx, taskcoachlib

# We don't want to use 'from taskcoachlib import X' all the time, so we add 
# the taskcoachlib directory to the search path:
libpath = taskcoachlib.__path__[0]
sys.path.append(libpath) 
del taskcoachlib

# Now we can directly import taskcoachlib subpackages:
import task, gui, config, effort


class wxApp(wx.App):
    def OnInit(self):
        return True

class App(object):
    def __init__(self):
        self.wxApp = wxApp(0)
        self.init()
        self.mainwindow.Show()
        self.wxApp.MainLoop()

    def init(self, showSplash=True, load=True): 
        gui.init()
        settings = config.Settings(load)
        if showSplash and settings.getboolean('window', 'splash'):
            splash = gui.SplashScreen()
        effortList = effort.EffortList()
        self.taskFile = task.TaskFile(effortList)
        self.io = gui.IOController(self, self.taskFile, effortList, settings)
        viewFilteredTaskList = task.filter.ViewFilter(self.taskFile)
        searchFilteredTaskList = task.filter.SearchFilter(viewFilteredTaskList)
        self.mainwindow = gui.MainWindow(self.io, self.taskFile, 
            searchFilteredTaskList, effortList, settings)
        self.processCommandLineArguments(settings, load)

    def processCommandLineArguments(self, settings, load=True):
        # FIXME: move to IOController
        if len(sys.argv) > 1:
            filename = sys.argv[1]
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
    App()



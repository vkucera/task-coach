import gui, wx, widgets, patterns, task

class DummyWidget(wx.Frame):
    def __init__(self, viewer):
        super(DummyWidget, self).__init__(viewer)
        self._selection = []
        self.viewer = viewer

    def DeleteAllItems(self, *args, **kwargs):
        pass

    def curselection(self):
        return self._selection

    def selection_set(self, index):
        self._selection.append(index)

    def selectall(self):
        self._selection = range(len(self.viewer.list))

    def select(self, indices):
        self._selection = indices

    def GetItemCount(self):
        return len(self.viewer.list)

    def refresh(self, *args, **kwargs):
        pass

    def refreshItem(self, *args, **kwargs):
        pass

    def GetColumnWidth(self, column):
        return 100
        
    def showSort(self, *args, **kwargs):
        pass

    def showColumn(self, *args, **kwargs):
        pass

    def showSortColumn(self, *args, **kwargs):
        pass

    def showSortOrder(self, *args, **kwargs):
        pass


class DummyUICommand(gui.uicommand.UICommand):
    bitmap = 'undo'

    def onCommandActivate(self, event):
        self.activated = True


class DummyUICommands(gui.uicommand.UICommands):
    def __init__(self, iocontroller=None):
        super(DummyUICommands, self).__init__(None, iocontroller, None, None, None, None)
        
    def __getitem__(self, key):
        return DummyUICommand()
        
    def keys(self):
        return ['new', 'stopeffort']


class ViewerWithDummyWidget(gui.viewer.Viewer):
    def createWidget(self):
        self.createImageList()
        return DummyWidget(self)

    
class TaskViewerWithDummyWidget(ViewerWithDummyWidget, gui.viewer.TaskViewer):
    pass


class TaskListViewerWithDummyWidget(ViewerWithDummyWidget, 
        gui.viewer.TaskListViewer):
    pass


class EffortPerDayViewerWithDummyWidget(ViewerWithDummyWidget,
        gui.viewer.EffortPerDayViewer):
    def createSorter(self, *args, **kwargs):
        return gui.viewer.EffortPerDayViewer.createSorter(self, *args, **kwargs)

        
class Settings:
    def registerObserver(self, *args, **kwargs):
        pass
        
    def get(self, section, setting):
        if setting == 'tasksdue':
            return 'Unlimited'
        else:
            return 'subject'
        
    def getboolean(self, *args):
        return True
        
    def set(self, *args):
        pass

        
class TaskList(patterns.ObservableObservablesList):        
    def rootTasks(self):
        return [task for task in self if task.parent() is None]
    
    
class TaskFile(task.TaskFile):
    def load(self, *args, **kwargs):
        pass
        
    merge = save = saveas = load

class MainWindow:
    def setToolBarSize(self, *args, **kwargs):
        pass
        
    showFindDialog = setToolBarSize

class IOController:
    def needSave(self, *args, **kwargs):
        return False

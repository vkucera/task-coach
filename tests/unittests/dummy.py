import gui, wx, widgets, patterns, persistence


class DummyWidget(wx.Frame):
    def __init__(self, viewer):
        super(DummyWidget, self).__init__(viewer)
        self._selection = []
        self.viewer = viewer
        self.refreshedItems = []

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

    def refreshItem(self, index, ):
        self.refreshedItems.append(index)

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
    section = 'view'
    setting = 'setting'

    def onCommandActivate(self, event):
        self.activated = True


class DummyUICommands(gui.uicommand.UICommands):
    def __init__(self, iocontroller=None, taskList=None, effortList=None):
        super(DummyUICommands, self).__init__(None, iocontroller, None, None, 
                                              taskList, effortList, None)
        
    def __getitem__(self, key):
        return DummyUICommand()
        
    def keys(self):
        return ['new', 'stopeffort']


class ViewerWithDummyWidget(gui.viewer.Viewer):
    def createWidget(self):
        self._columns = self._createColumns()
        return DummyWidget(self)

    def _createColumns(self):
        return []

    
class TaskViewerWithDummyWidget(ViewerWithDummyWidget, gui.viewer.TaskViewer):
    def createWidget(self):
        self.createImageList()
        return super(TaskViewerWithDummyWidget, self).createWidget()


class TaskListViewerWithDummyWidget(TaskViewerWithDummyWidget, 
        gui.viewer.TaskListViewer):
    def _createColumns(self):
        return gui.viewer.TaskListViewer._createColumns(self)


class EffortListViewerWithDummyWidget(ViewerWithDummyWidget,
        gui.viewer.EffortListViewer):
    def createSorter(self, *args, **kwargs):
        return gui.viewer.EffortListViewer.createSorter(self, *args, **kwargs)

    def _createColumns(self):
        return gui.viewer.EffortListViewer._createColumns(self)


class EffortPerDayViewerWithDummyWidget(ViewerWithDummyWidget,
        gui.viewer.EffortPerDayViewer):
    def createSorter(self, *args, **kwargs):
        return gui.viewer.EffortPerDayViewer.createSorter(self, *args, **kwargs)

    def _createColumns(self):
        return gui.viewer.EffortPerDayViewer._createColumns(self)

        
class TaskList(patterns.ObservableList):        
    def rootItems(self):
        return [task for task in self if task.parent() is None]
    
    
class TaskFile(persistence.TaskFile):
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

import taskcoach
from domain import task

class MockWxApp(object):
    def SetAppName(self, *args, **kwargs):
        pass

    def SetVendorName(self, *args, **kwargs):
        pass

    
class App(taskcoach.App):
    def __init__(self, args=None):
        self._options = None
        self._args = args or []
        self.wxApp = MockWxApp()
        self.init()

    def init(self):
        super(App, self).init(loadSettings=False)

    def addTasks(self):
        self.parent = task.Task()
        self.child = task.Task()
        self.parent.addChild(self.child)
        self.taskFile.extend([self.parent])



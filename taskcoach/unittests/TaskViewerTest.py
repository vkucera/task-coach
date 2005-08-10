import test, gui, task, dummy

class TaskViewerUnderTest(gui.viewer.TaskViewer):
    def createWidget(self):
        return dummy.DummyWidget(self)
        
class TaskViewerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.viewer = TaskViewerUnderTest(self.frame, self.taskList, {})
        
    def testStatusMessage_EmptyTaskList(self):
        self.assertEqual(('Tasks: 0 selected, 0 visible, 0 total', 
            'Status: 0 over due, 0 inactive, 0 completed'),
            self.viewer.statusMessages())
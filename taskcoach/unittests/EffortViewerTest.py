import test, gui, dummy, effort, config
import domain.task as task

class EffortViewerUnderTest(gui.viewer.EffortViewer):
    def createWidget(self):
        return dummy.DummyWidget(self)
        
class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.settings = config.Settings(load=False)
        self.viewer = EffortViewerUnderTest(self.frame, self.effortList, {}, self.settings)
        
    def testStatusMessage_EmptyTaskList(self):
        self.assertEqual(('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking'),
            self.viewer.statusMessages())
            
    def testStatusMessage_OneTaskNoEffort(self):
        self.taskList.append(task.Task())
        self.assertEqual(('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking'),
            self.viewer.statusMessages())
        
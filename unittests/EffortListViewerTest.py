import test, gui, dummy, config
import domain.task as task
import domain.effort as effort

class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        
    def testCreate(self):
        effortViewer = gui.viewer.EffortListViewer(self.frame, self.effortList, 
            dummy.DummyUICommands(), self.settings, taskList=self.taskList)
        self.assertEqual(0, effortViewer.size())
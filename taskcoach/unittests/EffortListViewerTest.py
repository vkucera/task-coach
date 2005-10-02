import test, gui, effort, dummy, task, config

class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.effortList = effort.EffortList(task.TaskList())
        
    def testCreate(self):
        effortViewer = gui.viewer.EffortListViewer(self.frame, self.effortList, 
            dummy.DummyUICommands(), self.settings)
        self.assertEqual(0, effortViewer.size())
import test, gui, effort, dummy

class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.effortList = effort.EffortList()
        
    def testCreate(self):
        effortViewer = gui.viewer.EffortListViewer(self.frame, self.effortList, 
            dummy.DummyUICommands())
        self.assertEqual(0, effortViewer.size())
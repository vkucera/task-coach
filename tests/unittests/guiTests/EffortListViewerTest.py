import test, gui, config
from domain import task, effort, category, note

class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        
    def testCreate(self):
        effortViewer = gui.viewer.EffortListViewer(self.frame, self.effortList, 
            gui.uicommand.UICommands(self.frame, None, 
                gui.viewercontainer.ViewerContainer(None, self.settings, 
                    'mainviewer'), 
                self.settings, self.taskList, self.effortList, 
                category.CategoryList(), note.NoteContainer()), 
                self.settings, taskList=self.taskList)
        self.assertEqual(0, effortViewer.size())

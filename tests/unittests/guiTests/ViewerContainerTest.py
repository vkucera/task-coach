import test, gui, wx, config
from unittests import dummy
from domain import task, effort, category, note

class ViewerContainerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), 
            settings=self.settings)
        self.container = gui.viewercontainer.ViewerNotebook(self.frame, 
            self.settings, 'mainviewer')
        self.container.addViewer(dummy.ViewerWithDummyWidget(self.container,
            self.taskList, gui.uicommand.UICommands(self.frame, None, None, 
                self.settings, self.taskList, effort.EffortList(self.taskList),
                category.CategoryList(), note.NoteContainer()), self.settings), 
                'Dummy')

    def testCreate(self):
        self.assertEqual(0, self.container.size())

    def testAddTask(self):
        self.taskList.append(task.Task())
        self.assertEqual(1, self.container.size())

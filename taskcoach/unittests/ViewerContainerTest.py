import test, task, gui, wx, dummy, effort


class ViewerContainerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.container = gui.viewercontainer.ViewerNotebook(self.frame)
        self.container.addViewer(dummy.ViewerWithDummyWidget(self.container,
            self.taskList, effort.EffortList(), {}), 'Dummy')

    def testCreate(self):
        self.assertEqual(0, self.container.size())

    def testAddTask(self):
        self.taskList.append(task.Task())
        self.assertEqual(1, self.container.size())

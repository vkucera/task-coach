import test, gui, wx, dummy, effort, config
import domain.task as task

class ViewerTest(test.wxTestCase):
    def setUp(self):
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
        self.settings = config.Settings(load=False)
        self.viewer = dummy.ViewerWithDummyWidget(self.frame,
            self.taskList, dummy.DummyUICommands(), self.settings)

    def testSelectAll(self):
        self.viewer.selectall()
        self.assertEqual([self.task], self.viewer.curselection())


class TaskListViewerTest(test.wxTestCase):
    def setUp(self):
        self.task = task.Task()
        settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]), 
            settings=settings)
        self.viewer = dummy.TaskListViewerWithDummyWidget(self.frame,
            self.taskList, dummy.DummyUICommands(), settings)

    def testGetTimeSpent(self):
        timeSpent = self.viewer.getItemText(0, self.viewer.columns()[7])
        self.assertEqual("0:00:00", timeSpent)

    def testGetTotalTimeSpent(self):
        timeSpent = self.viewer.getItemText(0, self.viewer.columns()[7])
        self.assertEqual("0:00:00", timeSpent)


class ViewerBaseClassTest(test.wxTestCase):
    def testNotImplementedError(self):
        taskList = task.TaskList()
        try:
            baseViewer = gui.viewer.Viewer(self.frame, taskList,
                dummy.DummyUICommands(), {})
            self.fail('Expected NotImplementedError')
        except NotImplementedError:
            pass


class CompositeEffortListViewerTest(test.wxTestCase):
    def setUp(self):
        taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        aTask = task.Task()
        aTask.addEffort(effort.Effort(aTask))
        taskList.append(aTask)
        effortList = effort.EffortList(taskList)
        self.viewer = dummy.EffortPerDayViewerWithDummyWidget(self.frame, 
            effortList, {}, self.settings, taskList=taskList)
            
    def testGetItemText_TimeSpent(self):
        self.assertEqual('0:00:00', 
                         self.viewer.getItemText(0, self.viewer.columns()[2]))
        
    def testGetItemText_Revenue(self):
        self.assertEqual('0.00', 
                         self.viewer.getItemText(0, self.viewer.columns()[3]))
    
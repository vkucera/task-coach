import test, task, gui, wx, dummy, effort


class ViewerTest(test.wxTestCase):
    def setUp(self):
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
        self.viewer = dummy.ViewerWithDummyWidget(self.frame,
            self.taskList, effort.EffortList(self.taskList), {})

    def testSelectTasksThatAreNotInTasklistShouldNotFail(self):
        taskNotInList = task.Task()
        self.viewer.select([taskNotInList])
        self.assertEqual([], self.viewer.curselection())

    def testSelectAll(self):
        self.viewer.selectall()
        self.assertEqual([self.task], self.viewer.curselection())


class TaskListViewerTest(test.wxTestCase):
    def setUp(self):
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
        self.viewer = dummy.TaskListViewerWithDummyWidget(self.frame,
            self.taskList, effort.EffortList(self.taskList), {})

    def testGetTimeSpent(self):
        timeSpent = self.viewer.getItemText(0, 'Time spent')
        self.assertEqual("0:00:00", timeSpent)

    def testGetTotalTimeSpent(self):
        timeSpent = self.viewer.getItemText(0, 'Total time spent')
        self.assertEqual("0:00:00", timeSpent)


class ViewerBaseClassTest(test.wxTestCase):
    def testNotImplementedError(self):
        taskList = task.TaskList()
        try:
            baseViewer = gui.viewer.Viewer(self.frame, taskList,
                effort.EffortList(taskList), {})
            self.fail('Expected NotImplementedError')
        except NotImplementedError:
            pass


class CompositeEffortListViewerTest(test.wxTestCase):
    def testGetItemText(self):
        taskList = task.TaskList()
        aTask = task.Task()
        aTask.addEffort(effort.Effort(aTask))
        taskList.append(aTask)
        effortList = effort.EffortList(taskList)
        viewer = dummy.EffortPerDayViewerWithDummyWidget(self.frame, 
            effortList, {})
        self.assertEqual('0:00:00', viewer.getItemText(0, 'Time spent'))

import test, task, date, dummy, effort, gui
from gui import render

class TaskListViewerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.listViewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            dummy.DummyUICommands())

    def testEmptyTaskList(self):
        self.assertEqual(0, self.listViewer.size())

    def testAddTask(self):
        self.taskList.append(task.Task())
        self.assertEqual(1, self.listViewer.size())

    def testRemoveTask(self):
        self.taskList.append(task.Task())
        del self.taskList[0]
        self.assertEqual(0, self.listViewer.size())

    def testCurrent(self):
        aTask = task.Task(subject='Test')
        self.taskList.append(aTask)
        self.listViewer.widget.select([0])
        self.assertEqual([aTask], self.listViewer.curselection())

    def testOneDayLeft(self):
        aTask = task.Task(subject='Test', duedate=date.Tomorrow())
        self.taskList.append(aTask)
        self.assertEqual(render.daysLeft(aTask.timeLeft()), 
            self.listViewer.widget.GetItem(0, 3).GetText())

    def testChildSubjectRendering(self):
        parent = task.Task(subject='Parent')
        child = task.Task(subject='Child')
        parent.addChild(child)
        self.taskList.append(parent)
        self.assertEqual('Parent%sChild'%render.taskSeparator, 
            self.listViewer.widget.GetItem(0, 0).GetText())

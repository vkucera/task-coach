import test, task, date, dummy, effort, gui
from gui import render

class TaskListViewerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.sorter.Sorter(task.TaskList())
        self.taskList.setSortKey('subject')
        self.listViewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            dummy.DummyUICommands())

    def assertItems(self, *tasks):
        self.assertEqual(len(tasks), self.listViewer.size())
        for index, task in enumerate(tasks):
            self.assertEqual(task, self.listViewer.widget.GetItemText(index))
 
    def testEmptyTaskList(self):
        self.assertItems()

    def testAddTask(self):
        self.taskList.append(task.Task(subject='Test'))
        self.assertItems('Test')

    def testRemoveTask(self):
        self.taskList.append(task.Task())
        del self.taskList[0]
        self.assertItems()

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
        self.assertItems('Parent%sChild'%render.taskSeparator, 'Parent')
           
    def testMarkCompleted(self):
        self.taskList.setSortKey('subject')
        self.taskList.setAscending(True)
        task1 = task.Task(subject='task1')
        task2 = task.Task(subject='task2')
        self.taskList.extend([task1, task2])
        self.assertItems('task1', 'task2')
        task1.setCompletionDate()
        self.assertItems('task2', 'task1')
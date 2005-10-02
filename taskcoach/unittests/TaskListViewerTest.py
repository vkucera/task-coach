import test, task, date, dummy, effort, gui, config, TaskViewerTest
from gui import render


class TaskListViewerTest(TaskViewerTest.CommonTests, test.wxTestCase):
    def setUp(self):
        super(TaskListViewerTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), settings=self.settings)
        self.settings.set('view', 'sortby', 'subject')
        self.task = task.Task('task')
        self.viewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            dummy.DummyUICommands(), self.settings)

    def assertItems(self, *tasks):
        self.assertEqual(len(tasks), self.viewer.size())
        for index, task in enumerate(tasks):
            self.assertEqual(render.subject(task, recursively=True), 
                             self.viewer.widget.GetItemText(index))
                             
    def getItemTextColor(self, index):
        return self.viewer.widget.GetItemTextColour(index)
 
    def testEmptyTaskList(self):
        self.assertItems()

    def testAddTask(self):
        self.taskList.append(self.task)
        self.assertItems(self.task)

    def testRemoveTask(self):
        self.taskList.append(self.task)
        del self.taskList[0]
        self.assertItems()

    def testCurrent(self):
        self.taskList.append(self.task)
        self.viewer.widget.select([0])
        self.assertEqual([self.task], self.viewer.curselection())

    def testOneDayLeft(self):
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        self.assertEqual(render.daysLeft(self.task.timeLeft()), 
            self.viewer.widget.GetItem(0, 3).GetText())

    def testChildSubjectRendering(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems(child, self.task)
           
    def testMarkCompleted(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        task2 = task.Task(subject='task2')
        self.taskList.extend([self.task, task2])
        self.assertItems(self.task, task2)
        self.task.setCompletionDate()
        self.assertItems(task2, self.task)
            
    def testSortByDueDate(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task('zzz')
        child2 = task.Task('child 2')
        task2.addChild(child2)
        self.taskList.extend([self.task, task2])
        self.assertItems(child, child2, self.task, task2) 
        child2.setDueDate(date.Today())
        self.settings.set('view', 'sortby', 'dueDate')
        self.assertItems(child2, child, self.task, task2)
        
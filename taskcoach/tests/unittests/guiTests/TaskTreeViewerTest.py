import test, gui, widgets, config, TaskViewerTest
from unittests import dummy
from domain import task, date, category


class TaskTreeViewerTestCase(test.wxTestCase):
    def setUp(self):
        super(TaskTreeViewerTestCase, self).setUp()
        self.task = task.Task(subject='task')
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.categories = category.CategoryList()
        
    def assertItems(self, *tasks):
        self.viewer.widget.expandAllItems()
        self.assertEqual(self.viewer.size(), len(tasks))
        for index, task in enumerate(tasks):
            if type(task) == type((),):
                task, nrChildren = task
            else:
                nrChildren = 0
            subject = task.subject()
            treeItem = self.viewer.widget.GetItemChildren(recursively=True)[index]
            self.assertEqual(subject, self.viewer.widget.GetItemText(treeItem))
            self.assertEqual(nrChildren, 
                self.viewer.widget.GetChildrenCount(treeItem, recursively=False))

                
class CommonTests(TaskViewerTest.CommonTests):
    ''' Tests common to TaskTreeViewerTest and TaskTreeListViewerTest. '''

    def getFirstItemTextColor(self):
        tree = self.viewer.widget
        firstItem, cookie = tree.GetFirstChild(tree.GetRootItem())
        return tree.GetItemTextColour(firstItem)
        
    def testCreate(self):
        self.assertItems()
        
    def testAddTask(self):
        self.taskList.append(self.task)
        self.assertItems(self.task)

    def testRemoveTask(self):
        self.taskList.append(self.task)
        self.taskList.remove(self.task)
        self.assertItems()

    def testDeleteSelectedTask(self):
        self.taskList.append(self.task)
        self.viewer.selectall()
        self.taskList.removeItems(self.viewer.curselection())
        self.assertItems()

    def testChildOrder(self):
        child1 = task.Task(subject='1')
        self.task.addChild(child1)
        child2 = task.Task(subject='2')
        self.task.addChild(child2)
        self.taskList.append(self.task)
        self.assertItems((self.task, 2), child1, child2)

    def testSortOrder(self):
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending()
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.assertItems((self.task, 1), child, task2)
            
    def testViewDueTodayHidesTasksNotDueToday(self):
        self.viewer.setFilteredByDueDate('Today')
        child = task.Task(subject='child')
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems()
        
    def testViewDueTodayShowsTasksWhoseChildrenAreDueToday(self):
        self.viewer.setFilteredByDueDate('Today')
        child = task.Task(subject='child', dueDate=date.Today())
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems((self.task, 1), child)
        
    def testFilterCompletedTasks(self):
        self.viewer.hideCompletedTasks()
        completedChild = task.Task(completionDate=date.Today())
        notCompletedChild = task.Task()
        self.task.addChild(notCompletedChild)
        self.task.addChild(completedChild)
        self.taskList.append(self.task)
        self.assertItems((self.task, 1), notCompletedChild)
        
    def testGetItemIndexOfChildTask(self):
        child1 = task.Task('1')
        child2 = task.Task('2')
        self.task.addChild(child1)
        self.task.addChild(child2)
        self.taskList.append(self.task)
        self.assertEqual((0, 0), self.viewer.getIndexOfItem(child1))
        
        
class TaskTreeViewerUnderTest(gui.viewer.TaskTreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemDescription,
            self.getItemImage, self.getItemAttr, self.getChildrenCount,
            self.onSelect, dummy.DummyUICommand(), dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget


class TaskTreeViewerTest(CommonTests, TaskTreeViewerTestCase):
    def setUp(self):
        super(TaskTreeViewerTest, self).setUp()
        self.viewer = TaskTreeViewerUnderTest(self.frame, self.taskList, {}, 
            self.settings, categories=self.categories)
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending()        


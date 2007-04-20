import test, gui, widgets, config, TaskViewerTest
from unittests import dummy
from domain import task, date, category


class TaskTreeViewerTestCase(test.wxTestCase):
    def setUp(self):
        super(TaskTreeViewerTestCase, self).setUp()
        self.task = task.Task(subject='task')
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.filter.ViewFilter( \
            task.TaskList(), settings=self.settings, treeMode=True), 
            settings=self.settings, treeMode=True)
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
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        child1 = task.Task(subject='1')
        self.task.addChild(child1)
        child2 = task.Task(subject='2')
        self.task.addChild(child2)
        self.taskList.append(self.task)
        self.assertItems((self.task, 2), child1, child2)

    def testSortOrder(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.assertItems((self.task, 1), child, task2)
            
    def testReverseSortOrder(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.settings.set('view', 'sortascending', 'False')
        self.assertItems(task2, (self.task, 1), child)

    def testReverseSortOrderWithGrandchildren(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        child = task.Task(subject='child')
        self.task.addChild(child)
        grandchild = task.Task(subject='grandchild')
        child.addChild(grandchild)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.settings.set('view', 'sortascending', 'False')
        self.assertItems(task2, (self.task, 1), (child, 1), grandchild)
                
    def testSortByDueDate(self):
        self.settings.set('view', 'sortby', 'subject')
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task('zzz')
        child2 = task.Task('child 2')
        task2.addChild(child2)
        self.taskList.extend([self.task, task2])
        self.assertItems((self.task, 1), child, (task2, 1), child2)
        child2.setDueDate(date.Today())
        self.settings.set('view', 'sortby', 'dueDate')
        self.assertItems((task2, 1), child2, (self.task, 1), child)
        
    def testViewDueTodayHidesTasksNotDueToday(self):
        self.settings.set('view', 'tasksdue', 'Today')
        child = task.Task(subject='child')
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems()
        
    def testViewDueTodayShowsTasksWhoseChildrenAreDueToday(self):
        self.settings.set('view', 'tasksdue', 'Today')
        child = task.Task(subject='child', dueDate=date.Today())
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems((self.task, 1), child)
        
    def testFilterCompletedTasks(self):
        self.settings.set('view', 'completedtasks', 'False')
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
        self.settings.set('view', 'sortascending', 'False')
        self.assertEqual((0, 1), self.viewer.getIndexOfItem(child1))
        
        
class TaskTreeViewerUnderTest(gui.viewer.TaskTreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getChildrenCount,
            self.onSelect, dummy.DummyUICommand(), dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget


class TaskTreeViewerTest(CommonTests, TaskTreeViewerTestCase):
    def setUp(self):
        super(TaskTreeViewerTest, self).setUp()
        self.viewer = TaskTreeViewerUnderTest(self.frame, self.taskList, {}, 
            self.settings, categories=self.categories)
        

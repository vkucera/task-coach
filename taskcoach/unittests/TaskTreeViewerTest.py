import test, task, gui, widgets, dummy, config, date

class TaskTreeViewerTestCase(test.wxTestCase):
    def setUp(self):
        self.task = task.Task(subject='task')
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), settings=self.settings)
        
    def assertItems(self, *tasks):
        self.viewer.widget.expandAllItems()
        self.assertEqual(self.viewer.size(), len(tasks))
        for index, task in enumerate(tasks):
            if type(task) == type((),):
                task, nrChildren = task
            else:
                nrChildren = 0
            subject = task.subject()
            self.assertEqual(subject, self.viewer.widget.GetItemText(self.viewer.widget.GetItem(index)))
            self.assertEqual(nrChildren, self.viewer.widget.GetChildrenCount(self.viewer.widget.GetItem(index), recursively=False))


class CommonTests(object):
    ''' Tests common to TaskTreeViewerTest and TaskTreeListViewerTest. '''
    
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

    def testGetRootIndices(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        grandchild = task.Task(subject='grandchild')
        child.addChild(grandchild)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.assertEqual([self.viewer.list.index(self.task), self.viewer.list.index(task2)],
            self.viewer.getRootIndices())
            
    def testGetChildIndices(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        self.taskList.extend([self.task])
        self.assertEqual([self.viewer.list.index(child)],
            self.viewer.getChildIndices(self.viewer.list.index(self.task)))    
    
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
        pass
        
        
class TaskTreeViewerUnderTest(gui.viewer.TaskTreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getItemId, self.getRootIndices, self.getChildIndices,
            self.onSelect, dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget

class TaskTreeViewerTest(TaskTreeViewerTestCase, CommonTests):
    def setUp(self):
        super(TaskTreeViewerTest, self).setUp()
        self.viewer = TaskTreeViewerUnderTest(self.frame, self.taskList, {}, self.settings)


    
        
        
        

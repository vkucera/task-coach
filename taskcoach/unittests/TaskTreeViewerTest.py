import test, task, gui, widgets, dummy, effort

class TaskTreeViewer(gui.viewer.TaskTreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getItemChildrenCount, self.getItemId,
            self.getItemChildIndex, self.onSelect, dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget

class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task = task.Task(subject='task')
        self.viewer = TaskTreeViewer(self.frame, task.sorter.Sorter(self.taskList),
            effort.EffortList(self.taskList), {})

    def assertItems(self, *tasks):
        self.assertEqual(self.viewer.size(), len(tasks))
        for index, task in enumerate(tasks):
            if type(task) == type((),):
                subject, nrChildren = str(task[0]), task[1]
            else:
                subject, nrChildren = str(task), 0
            self.assertEqual(subject, self.viewer.widget.GetItemText(self.viewer.widget[index]))
            self.assertEqual(nrChildren, self.viewer.widget.GetChildrenCount(self.viewer.widget[index], recursively=False))

    def testCreate(self):
        self.assertEqual(0, self.viewer.size())

    def testAddTask(self):
        self.taskList.append(self.task)
        self.assertEqual(1, self.viewer.size())

    def testRemoveTask(self):
        self.taskList.append(self.task)
        self.taskList.remove(self.task)
        self.assertEqual(0, self.viewer.size())

    def testDelete(self):
        self.taskList.append(self.task)
        self.viewer.selectall()
        self.taskList.removeItems(self.viewer.curselection())
        self.assertEqual(0, self.viewer.size())
    
    def testChildOrder(self):
        child1 = task.Task(subject='1')
        self.task.addChild(child1)
        child2 = task.Task(subject='2')
        self.task.addChild(child2)
        self.taskList.extend([self.task, child1, child2])
        self.viewer.widget.expandAllItems()
        self.assertItems((self.task, 2), child1, child2)
            
    def testSortOrder(self):
        self.viewer.list.setSortKey('subject')
        self.viewer.list.setAscending(True)
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.widget.expandAllItems()
        self.assertItems((self.task, 1), child, task2)
        
    def testReverseSortOrder(self):
        self.viewer.list.setSortKey('subject')
        self.viewer.list.setAscending(True)
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.widget.expandAllItems()
        self.viewer.list.setAscending(False)
        self.assertItems(task2, (self.task, 1), child)
        
    def testReverseSortOrderWithGrandchildren(self):
        self.viewer.list.setSortKey('subject')
        self.viewer.list.setAscending(True)
        child = task.Task(subject='child')
        self.task.addChild(child)
        grandchild = task.Task(subject='grandchild')
        child.addChild(grandchild)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.widget.expandAllItems()
        self.viewer.list.setAscending(False)
        self.assertItems(task2, (self.task, 1), (child, 1), grandchild)
        
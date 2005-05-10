import test, task, gui, widgets, dummy, effort

class TaskTreeViewer(gui.viewer.TaskTreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getItemChildrenCount,
            self.getItemFingerprint, self.onSelect, dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget

class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task = task.Task()
        self.viewer = TaskTreeViewer(self.frame, task.sorter.Sorter(self.taskList),
            effort.EffortList(self.taskList), {})

    def testCreate(self):
        self.assertEqual(0, self.viewer.size())

    def testAddTask(self):
        self.taskList.append(self.task)
        self.assertEqual(1, self.viewer.size())

    def testRemoveTask(self):
        self.taskList.append(self.task)
        self.taskList.remove(self.task)
        self.assertEqual(0, self.viewer.size())

    def testChildOrder(self):
        child1 = task.Task(subject='1')
        self.task.addChild(child1)
        child2 = task.Task(subject='2')
        self.task.addChild(child2)
        self.taskList.extend([self.task, child1, child2])
        self.assertEqual(str(child2), 
            self.viewer.widget.GetItemText(self.viewer.widget[2]))

    def testDelete(self):
        self.taskList.append(self.task)
        self.viewer.selectall()
        self.taskList.removeItems(self.viewer.curselection())
        self.assertEqual(0, self.viewer.size())
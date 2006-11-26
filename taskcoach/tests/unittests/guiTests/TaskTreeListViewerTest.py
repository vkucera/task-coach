import test, gui, widgets, TaskTreeViewerTest, TaskListViewerTest
from unittests import dummy
from gui import render
from domain import task, date, effort, category

class TaskTreeListViewerUnderTest(gui.viewer.TaskTreeListViewer):
    def createWidgetWithColumns(self):
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemImage, self.getItemAttr, self.getItemId,
            self.getRootIndices, self.getChildIndices,
            self.onSelect, dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget

class TaskTreeListViewerTest(TaskTreeViewerTest.CommonTests,
                             TaskListViewerTest.CommonTests,
                             TaskTreeViewerTest.TaskTreeViewerTestCase):
    def setUp(self):
        super(TaskTreeListViewerTest, self).setUp()
        effortList = effort.EffortList(self.taskList)
        categories = category.CategoryList()
        self.viewer = TaskTreeListViewerUnderTest(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, None, 
                self.settings, self.taskList, effortList, categories), 
                self.settings, categories=categories)
          
    def testOneDayLeft(self):
        self.settings.set('view', 'timeleft', 'True')
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        firstItem, cookie = self.viewer.widget.GetFirstChild(self.viewer.widget.GetRootItem())
        self.assertEqual(render.daysLeft(self.task.timeLeft()), 
            self.viewer.widget.GetItemText(firstItem, 3))


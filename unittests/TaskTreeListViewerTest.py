import test, gui, widgets, dummy, TaskTreeViewerTest, TaskListViewerTest
from gui import render
import domain.task as task
import domain.date as date

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
        self.viewer = TaskTreeListViewerUnderTest(self.frame,
            self.taskList, dummy.DummyUICommands(), self.settings)
          
    def testOneDayLeft(self):
        self.settings.set('view', 'timeleft', 'True')
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        firstItem, cookie = self.viewer.widget.GetFirstChild(self.viewer.widget.GetRootItem())
        self.assertEqual(render.daysLeft(self.task.timeLeft()), 
            self.viewer.widget.GetItemText(firstItem, 3))
    
    

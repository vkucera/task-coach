import test, config, gui
import domain.task as task
import unittests.dummy as dummy


class TaskViewerAndCategoryFilterIntegrationTestFixture(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.settings.set('view', 'sortby', 'subject')
        self.viewer = self.TaskViewerClass(self.frame, self.taskList, 
            dummy.DummyUICommands(), self.settings)
        parent = task.Task('parent')
        child = task.Task('child')
        parent.addChild(child)
        self.taskList.append(parent)
        child.addCategory('category')
        self.settings.setlist('view', 'taskcategoryfilterlist', ['category'])


class TaskListViewerAndCategoryFilterIntegrationTest( \
        TaskViewerAndCategoryFilterIntegrationTestFixture):
    TaskViewerClass = gui.viewer.TaskListViewer
            
    def testFilterOnCategoryChildDoesHideParent(self):
        self.assertEqual(1, self.viewer.widget.GetItemCount())


class TaskTreeListViewerAndCategoryFilterIntegrationTest( \
        TaskViewerAndCategoryFilterIntegrationTestFixture):
    TaskViewerClass = gui.viewer.TaskTreeListViewer
            
    def testFilterOnCategoryChildDoesNotHideParent(self):
        self.viewer.expandAll()
        self.assertEqual(2, self.viewer.widget.GetItemCount())
        
    
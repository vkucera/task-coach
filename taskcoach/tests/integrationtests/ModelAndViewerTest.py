import test, config, gui
import domain.task as task
import domain.category as category
import unittests.dummy as dummy


class TaskViewerAndCategoryFilterIntegrationTestFixture(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.categories = category.CategoryList()
        self.category = category.Category('category')
        self.categories.append(self.category)
        self.settings.set('view', 'sortby', 'subject')
        self.viewer = self.TaskViewerClass(self.frame, self.taskList, 
            dummy.DummyUICommands(), self.settings, categories=self.categories)
        parent = task.Task('parent')
        child = task.Task('child')
        parent.addChild(child)
        self.taskList.append(parent)
        self.category.addTask(child)
        self.category.setFiltered()
        

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
        
    
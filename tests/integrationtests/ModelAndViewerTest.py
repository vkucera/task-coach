import test, mock
from domain import task, category


class TaskViewerAndCategoryFilterIntegrationTestFixture(test.wxTestCase):
    def setUp(self):
        self.app = mock.App()
        parent = task.Task('parent')
        child = task.Task('child')
        parent.addChild(child)
        self.category = category.Category('category')
        self.app.mainwindow.taskFile.categories().append(self.category)
        self.app.mainwindow.taskFile.tasks().append(parent)
        self.category.addCategorizable(child)
        self.category.setFiltered()
        
        

class TaskListViewerAndCategoryFilterIntegrationTest( \
        TaskViewerAndCategoryFilterIntegrationTestFixture):
            
    def testFilterOnCategoryChildDoesHideParent(self):
        self.assertEqual(1, self.app.mainwindow.viewer[0].widget.GetItemCount())


class TaskTreeListViewerAndCategoryFilterIntegrationTest( \
        TaskViewerAndCategoryFilterIntegrationTestFixture):
            
    def testFilterOnCategoryChildDoesNotHideParent(self):
        self.app.mainwindow.viewer[1].expandAll()
        self.assertEqual(2, self.app.mainwindow.viewer[1].widget.GetItemCount())
        
    

import test, config, gui
from domain import task, effort, category, note


class TaskViewerAndCategoryFilterIntegrationTestFixture(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.categories = category.CategoryList()
        self.category = category.Category('category')
        self.categories.append(self.category)
        self.notes = note.NoteContainer()
        self.settings.set('view', 'sortby', 'subject')
        viewerContainer = gui.viewercontainer.ViewerContainer(self.frame, 
            self.settings, 'mainviewer')
        self.viewer = self.TaskViewerClass(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, viewerContainer, 
            self.settings, 
            self.taskList, effort.EffortList(self.taskList), self.categories,
            self.notes), 
            self.settings, categories=self.categories)
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
        
    

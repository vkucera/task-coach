import test, gui, config
from unittests import dummy
from domain import task, effort, category, note

class CategoryViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.viewer = gui.viewer.CategoryViewer(self.frame, self.categories, 
            gui.uicommand.UICommands(self.frame, None, 
                gui.viewercontainer.ViewerContainer(None, self.settings, 
                    'mainviewer'), None, self.taskList,
                self.effortList, self.categories, note.NoteContainer()), 
            self.settings)
        
    def testInitialSize(self):
        self.assertEqual(0, self.viewer.size())

    def testCopyCategoryWithChildren(self):
        parent = category.Category('parent')
        child = category.Category('child')
        parent.addChild(child)
        self.categories.append(parent)
        copy = parent.copy()
        self.categories.append(copy)
        self.viewer.expandAll()
        self.assertEqual(4, self.viewer.size())

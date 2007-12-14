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
                gui.viewercontainer.ViewerNotebook(self.frame, self.settings, 
                    'mainviewer'), None, self.taskList,
                self.effortList, self.categories, note.NoteContainer()), 
            self.settings)
        
    def addTwoCategories(self):
        cat1 = category.Category('1')
        cat2 = category.Category('2')
        self.categories.extend([cat2, cat1])
        return cat1, cat2
        
    def testInitialSize(self):
        self.assertEqual(0, self.viewer.size())

    def testCopyCategoryWithChildren(self):
        parent, child = self.addTwoCategories()
        parent.addChild(child)
        copy = parent.copy()
        self.categories.append(copy)
        self.viewer.expandAll()
        self.assertEqual(4, self.viewer.size())

    def testSortInWidget(self):
        self.addTwoCategories()
        widget = self.viewer.widget
        for item, cat in zip(widget.GetItemChildren(), self.viewer.model()):
            self.assertEqual(cat.subject(), widget.GetItemText(item))
            
    def testSelectAll(self):
        self.addTwoCategories()
        self.viewer.widget.SelectItem(self.viewer.widget.GetFirstVisibleItem())
        self.viewer.selectall()
        self.assertEqual(2, len(self.viewer.curselection()))
        
    def testInvertSelection(self):
        self.addTwoCategories()
        self.viewer.invertselection()
        self.assertEqual(2, len(self.viewer.curselection()))

        

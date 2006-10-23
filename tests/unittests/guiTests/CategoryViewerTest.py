import test, gui
from unittests import dummy
import domain.category as category

class CategoryViewerTest(test.wxTestCase):
    def setUp(self):
        self.categories = category.CategoryList()
        self.viewer = gui.viewer.CategoryViewer(self.frame, self.categories, 
            dummy.DummyUICommands())
        
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

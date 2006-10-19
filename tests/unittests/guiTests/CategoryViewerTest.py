import test, gui
from unittests import dummy
import domain.category as category

class CategoryViewerTest(test.wxTestCase):
    def setUp(self):
        self.categories = category.CategorySorter(category.CategoryList())
        self.viewer = gui.viewer.CategoryViewer(self.frame, self.categories, 
            dummy.DummyUICommands())
        
    def testInitialSize(self):
        self.assertEqual(0, self.viewer.size())


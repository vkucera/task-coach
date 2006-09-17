import test
import domain.category as category

class CategoryContainerTest(test.TestCase):
    def setUp(self):
        self.categories = category.CategoryContainer()
        self.category = category.Category('category 1')
        
    def testInitial(self):
        self.assertEqual(0, len(self.categories))
        
    def testRootItems_NoItems(self):
        self.assertEqual([], self.categories.rootItems())
        
    def testRootItems_OneRootItem(self):
        self.categories.append(self.category)
        self.assertEqual([self.category], self.categories.rootItems())
        
    def testRootItems_MultipleRootItems(self):
        cat2 = category.Category('category 2')
        self.categories.extend([self.category, cat2])
        self.assertEqual([self.category, cat2], self.categories.rootItems())
        
    def testRootItems_RootAndChildItems(self):
        subCategory = category.Category('category 1.1')
        self.category.addChild(subCategory)
        self.categories.extend([self.category, subCategory])
        self.assertEqual([self.category], self.categories.rootItems())
        
    def testAddExistingCategory_WithoutTasks(self):
        self.categories.append(self.category)
        self.categories.append(category.Category(self.category.subject()))
        self.assertEqual(2, len(self.categories))
        
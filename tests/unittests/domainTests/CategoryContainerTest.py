import test
import domain.category as category

class CategoryContainerTest(test.TestCase):
    def setUp(self):
        self.categories = category.CategoryList()
        self.category = category.Category('category 1')
                
    def testAddExistingCategory_WithoutTasks(self):
        self.categories.append(self.category)
        self.categories.append(category.Category(self.category.subject()))
        self.assertEqual(2, len(self.categories))
        
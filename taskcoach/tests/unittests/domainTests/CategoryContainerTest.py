import test
from domain import category, task

class CategoryContainerTest(test.TestCase):
    def setUp(self):
        self.categories = category.CategoryList()
        self.category = category.Category('category 1')
                
    def testAddExistingCategory_WithoutTasks(self):
        self.categories.append(self.category)
        self.categories.append(category.Category(self.category.subject()))
        self.assertEqual(2, len(self.categories))
        
    def testRemoveCategoryWithTask(self):
        aTask = task.Task()
        self.categories.append(self.category)
        self.category.addTask(aTask)
        aTask.addCategory(self.category)
        self.categories.removeItems([self.category])
        self.failIf(aTask.categories())

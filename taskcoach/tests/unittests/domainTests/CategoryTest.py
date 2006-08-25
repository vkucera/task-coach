import test
import domain.category as category

class CategoryTest(test.TestCase):
    def testCreateCategory(self):
        cat = category.Category('category')
        self.assertEqual('category', cat)

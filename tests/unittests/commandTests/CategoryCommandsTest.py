import test, command
from unittests import asserts
from CommandTestCase import CommandTestCase
import domain.category as category


class CategoryCommandTestCase(CommandTestCase, asserts.CommandAsserts):
    def setUp(self):
        self.categories = category.CategoryList()
        

class NewCategoryCommandTest(CategoryCommandTestCase):
    def new(self):
        newCategoryCommand = command.NewCategoryCommand(self.categories)
        newCategory = newCategoryCommand.items[0]
        newCategoryCommand.do()
        return newCategory
        
    def testNewCategory(self):
        newCategory = self.new()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([newCategory], self.categories),
            lambda: self.assertEqual([], self.categories))
        

class NewSubCategoryCommandTest(CategoryCommandTestCase):
    def setUp(self):
        super(NewSubCategoryCommandTest, self).setUp()
        self.category = category.Category('category')
        self.categories.append(self.category)
        
    def newSubCategory(self, categories=None):
        newSubCategory = command.NewSubCategoryCommand(self.categories, 
                                                       categories or [])
        newSubCategory.do()

    def testNewSubCategory_WithoutSelection(self):
        self.newSubCategory()
        self.assertDoUndoRedo(lambda: self.assertEqual([self.category], 
                                                       self.categories))

    def testNewSubCategory(self):
        self.newSubCategory([self.category])
        newSubCategory = self.category.children()[0]
        self.assertDoUndoRedo(lambda: self.assertEqual([newSubCategory], 
                                                       self.category.children()),
            lambda: self.assertEqual([self.category], self.categories))

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


class EditCategoryCommandTest(CategoryCommandTestCase):
    def setUp(self):
        super(EditCategoryCommandTest, self).setUp()
        self.category = category.Category('category')
        self.categories.append(self.category)
        
    def editCategory(self, categories=None):
        categories = categories or []
        editCategory = command.EditCategoryCommand(self.categories, categories)
        for category in categories:
            category.setSubject('new')
        editCategory.do()
        
    def testEditCategory_WithoutSelection(self):
        self.editCategory()
        self.assertDoUndoRedo(lambda: self.assertEqual([self.category], 
                                                       self.categories))
        
    def testEditCategory_Subject(self):
        self.editCategory([self.category])
        self.assertDoUndoRedo(lambda: self.assertEqual('new', self.category.subject()),
            lambda: self.assertEqual('category', self.category.subject()))

import test
import domain.category as category
import domain.task as task

class CategoryTest(test.TestCase):
    def setUp(self):
        self.category = category.Category('category')
        self.subCategory = category.Category('subcategory')
        self.task = task.Task('task')
        
    def testCreateWithSubject(self):
        self.assertEqual('category', self.category.subject())
        
    def testRecursiveSubject(self):
        self.category.addChild(self.subCategory)
        self.assertEqual('%s -> %s'%(self.category.subject(),
                         self.subCategory.subject()), 
                         self.subCategory.subject(recursive=True))

    def testNoTasksAfterCreation(self):
        self.assertEqual([], self.category.tasks())
        
    def testAddTask(self):
        self.category.addTask(self.task)
        self.assertEqual([self.task], self.category.tasks())
        
    def testCreateWithTasks(self):
        cat = category.Category('category', [self.task])
        self.assertEqual([self.task], cat.tasks())
        
    def testAddSubCategory(self):
        self.category.addChild(self.subCategory)
        self.assertEqual([self.subCategory], self.category.children())
        
    def testCreateWithSubCategories(self):
        cat = category.Category('category', children=[self.subCategory])
        self.assertEqual([self.subCategory], cat.children())
        
    def testParentOfSubCategory(self):
        self.category.addChild(self.subCategory)
        self.assertEqual(self.category, self.subCategory.parent())
        
    def testParentOfRootCategory(self):
        self.assertEqual(None, self.category.parent())
        
    def testEquality_SameSubjectAndNoParents(self):
        self.assertEqual(category.Category(self.category.subject()), 
                         self.category)
        self.assertEqual(self.category,
                         category.Category(self.category.subject()))
                         
    def testEquality_SameSubjectDifferentParents(self):
        self.category.addChild(self.subCategory)
        self.assertNotEqual(category.Category(self.subCategory.subject()), 
                            self.subCategory)
                         
                         
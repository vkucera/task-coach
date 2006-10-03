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
    
    def testAddTaskToSubCategory(self):
        self.category.addChild(self.subCategory)
        self.subCategory.addTask(self.task)
        self.assertEqual([self.task], self.category.tasks(recursive=True))
     
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
   
    def testNotFilteredByDefault(self):
        self.failIf(self.category.isFiltered())
        
    def testSetFilteredOn(self):
        self.category.setFiltered()
        self.failUnless(self.category.isFiltered())
        
    def testSetFilteredOff(self):
        self.category.setFiltered(False)
        self.failIf(self.category.isFiltered())
    
    def testSetFilteredViaConstructor(self):
        filteredCategory = category.Category('test', filtered=True)
        self.failUnless(filteredCategory.isFiltered())
        
    def testSetFilteredOnAffectsChild(self):
        self.category.addChild(self.subCategory)
        self.category.setFiltered()
        self.failUnless(self.subCategory.isFiltered())
        
    def testSetFilteredOffAffectsChild(self):
        self.subCategory.setFiltered()
        self.category.addChild(self.subCategory)
        self.category.setFiltered(False)
        self.failIf(self.subCategory.isFiltered())
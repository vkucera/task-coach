import test, patterns
import domain.category as category
import domain.task as task

class CategoryTest(test.TestCase):
    def setUp(self):
        self.category = category.Category('category')
        self.subCategory = category.Category('subcategory')
        self.task = task.Task('task')
        self.child = task.Task('child')
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
        
    def testCreateWithSubject(self):
        self.assertEqual('category', self.category.subject())
    
    def testRecursiveSubject(self):
        self.category.addChild(self.subCategory)
        self.assertEqual('%s -> %s'%(self.category.subject(),
                         self.subCategory.subject()), 
                         self.subCategory.subject(recursive=True))
        
    def testSetSubject(self):
        self.category.setSubject('New')
        self.assertEqual('New', self.category.subject())
        
    def testSetSubjectNotification(self):
        eventType = category.Category.subjectChangedEventType()
        patterns.Publisher().registerObserver(self.onEvent, eventType)
        self.category.setSubject('New')
        self.assertEqual([patterns.Event(self.category, eventType, 'New')], 
            self.events)
        
    def testSetSubjectCausesNoNotificationWhenNewSubjectEqualsOldSubject(self):
        eventType = category.Category.subjectChangedEventType()
        patterns.Publisher().registerObserver(self.onEvent, eventType)
        self.category.setSubject(self.category.subject())
        self.failIf(self.events)

    def testNoTasksAfterCreation(self):
        self.assertEqual([], self.category.tasks())
      
    def testAddTask(self):
        self.category.addTask(self.task)
        self.assertEqual([self.task], self.category.tasks())
        self.assertEqual(set([self.category]), self.task.categories())
        
    def testAddTaskTwice(self):
        self.category.addTask(self.task)
        self.category.addTask(self.task)
        self.assertEqual([self.task], self.category.tasks())
        self.assertEqual(set([self.category]), self.task.categories())
        
    def testRemoveTask(self):
        self.category.addTask(self.task)
        self.category.removeTask(self.task)
        self.failIf(self.category.tasks())
        self.failIf(self.task.categories())
        
    def testRemoveTaskThatsNotInThisCategory(self):
        self.category.removeTask(self.task)
        self.failIf(self.category.tasks())
        self.failIf(self.task.categories())
    
    def testCreateWithTasks(self):
        cat = category.Category('category', [self.task])
        self.assertEqual([self.task], cat.tasks())
        self.assertEqual(set([cat]), self.task.categories())
    
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
        self.assertNotEqual(category.Category(self.category.subject()), 
                            self.category)
        self.assertNotEqual(self.category,
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
        
    def testContains_NoTasks(self):
        self.failIf(self.category.contains(self.task))
        
    def testContains_TasksInCategory(self):
        self.category.addTask(self.task)
        self.failUnless(self.category.contains(self.task))
        
    def testContains_TaskInSubCategory(self):
        self.subCategory.addTask(self.task)
        self.category.addChild(self.subCategory)
        self.failUnless(self.category.contains(self.task))
        
    def testContains_ParentInCategory(self):
        self.category.addTask(self.task)
        self.task.addChild(self.child)
        self.failUnless(self.category.contains(self.child))
        
    def testContains_ParentInSubCategory(self):
        self.subCategory.addTask(self.task)
        self.category.addChild(self.subCategory)
        self.task.addChild(self.child)
        self.failUnless(self.category.contains(self.child))
    
    def testContains_ChildInCategory(self):
        self.task.addChild(self.child)
        self.category.addTask(self.child)
        self.failIf(self.category.contains(self.task))
        
    def testContains_ChildInSubCategory(self):
        self.task.addChild(self.child)
        self.subCategory.addTask(self.child)
        self.category.addChild(self.subCategory)
        self.failIf(self.category.contains(self.task))
        
    def testRecursiveContains_ChildInCategory(self):
        self.task.addChild(self.child)
        self.category.addTask(self.child)
        self.failUnless(self.category.contains(self.task, treeMode=True))
        
    def testRecursiveContains_ChildInSubcategory(self):
        self.task.addChild(self.child)
        self.subCategory.addTask(self.child)
        self.category.addChild(self.subCategory)
        self.failUnless(self.category.contains(self.task, treeMode=True))
        
    def testCopy_SubjectIsCopied(self):
        self.category.setSubject('New subject')
        copy = self.category.copy()
        self.assertEqual(copy.subject(), self.category.subject())
        
    def testCopy_FilteredStatusIsCopied(self):
        self.category.setFiltered()
        copy = self.category.copy()
        self.assertEqual(copy.isFiltered(), self.category.isFiltered())
        
    def testCopy_TasksAreCopied(self):
        self.category.addTask(self.task)
        copy = self.category.copy()
        self.assertEqual(copy.tasks(), self.category.tasks())
        
    def testCopy_TasksAreCopiedIntoADifferentList(self):
        copy = self.category.copy()
        self.category.addTask(self.task)
        self.failIf(self.task in copy.tasks())

    def testCopy_ChildrenAreCopied(self):
        self.category.addChild(self.subCategory)
        copy = self.category.copy()
        self.assertEqual(self.subCategory.subject(), copy.children()[0].subject())

import test, config
import domain.task as task
import domain.date as date
import domain.effort as effort


class CommonTaskRelationshipManagerTests(object):
    def setUp(self):
        self.parent = task.Task()
        self.child = task.Task()
        self.parent.addChild(self.child)
        self.child2 = task.Task()
        self.grandchild = task.Task()
        settings = config.Settings(load=False)
        settings.set('behavior', 'markparentcompletedwhenallchildrencompleted', 
            str(self.markParentCompletedWhenAllChildrenCompleted))
        self.taskList = task.TaskList([self.parent, self.child2, self.grandchild])
        self.taskRelationshipManager = \
            task.TaskRelationshipManager(taskList=self.taskList,
                                         settings=settings)
        
    # completion date
    
    def testMarkingOneOfTwoChildsCompletedNeverResultsInACompletedParent(self):
        self.parent.addChild(self.child2)
        self.child.setCompletionDate()
        self.failIf(self.parent.completed())

    def testMarkParentWithOneChildCompleted(self):
        self.parent.setCompletionDate()
        self.failUnless(self.child.completed())

    def testMarkParentWithTwoChildrenCompleted(self):
        self.parent.addChild(self.child2)        
        self.parent.setCompletionDate()
        self.failUnless(self.child.completed())
        self.failUnless(self.child2.completed())

    def testMarkParentNotCompleted(self):
        self.parent.setCompletionDate()
        self.failUnless(self.child.completed())
        self.parent.setCompletionDate(date.Date())
        self.failUnless(self.child.completed())

    def testMarkParentCompletedDoesNotChangeChildCompletionDate(self):
        self.parent.addChild(self.child2)        
        self.child.setCompletionDate(date.Yesterday())
        self.parent.setCompletionDate()
        self.assertEqual(date.Yesterday(), self.child.completionDate())

    def testMarkChildNotCompleted(self):
        self.child.setCompletionDate()
        self.child.setCompletionDate(date.Date())
        self.failIf(self.parent.completed())
 
    def testAddCompletedChild(self):
        self.child2.setCompletionDate()
        self.parent.addChild(self.child2)
        self.failIf(self.parent.completed())

    def testAddUncompletedChild(self):
        self.child.setCompletionDate()
        self.parent.addChild(self.child2)
        self.failIf(self.parent.completed())
    
    def testAddUncompletedGrandchild(self):
        self.parent.setCompletionDate()
        self.child.addChild(self.grandchild)
        self.failIf(self.parent.completed())

    def testMarkParentCompletedYesterday(self):
        self.parent.setCompletionDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.child.completionDate())

    def testMarkTaskCompletedStopsEffortTracking(self):
        self.child.addEffort(effort.Effort(self.child))
        self.child.setCompletionDate()
        self.failIf(self.child.isBeingTracked())

    # due date
        
    def testAddChildWithoutDueDateToParentWithoutDueDate(self):
        self.assertEqual(date.Date(), self.child.dueDate())
        self.assertEqual(date.Date(), self.parent.dueDate())

    def testAddChildWithDueDateToParentWithoutDueDate(self):
        self.child2.setDueDate(date.Today())
        self.parent.addChild(self.child2)
        self.assertEqual(date.Date(), self.parent.dueDate())
        
    def testAddChildWithoutDueDateToParentWithDueDate(self):
        self.parent.setDueDate(date.Tomorrow())
        self.parent.addChild(self.child2)
        self.assertEqual(date.Date(), self.parent.dueDate())
        
    def testAddChildWithDueDateSmallerThanParentDueDate(self):
        self.parent.setDueDate(date.Tomorrow())
        self.child2.setDueDate(date.Today())
        self.parent.addChild(self.child2)
        self.assertEqual(date.Tomorrow(), self.parent.dueDate())
        
    def testAddChildWithDueDateLargerThanParentDueDate(self):
        self.parent.setDueDate(date.Today())
        self.child2.setDueDate(date.Tomorrow())
        self.parent.addChild(self.child2)
        self.assertEqual(date.Tomorrow(), self.parent.dueDate())
        
    def testSetDueDateChildSmallerThanParent(self):
        self.child.setDueDate(date.Today())
        self.assertEqual(date.Date(), self.parent.dueDate())
        
    def testSetDueDateParent(self):
        self.parent.setDueDate(date.Today())
        self.assertEqual(self.parent.dueDate(), self.child.dueDate())
        
    def testSetDueDateParentLargerThanChild(self):
        self.parent.setDueDate(date.Today())
        self.parent.setDueDate(date.Date())
        self.assertEqual(date.Today(), self.child.dueDate())
        
    def testSetDueDateChildLargerThanParent(self):
        self.parent.setDueDate(date.Today())
        self.child.setDueDate(date.Tomorrow())
        self.assertEqual(date.Tomorrow(), self.parent.dueDate())

    # start date

    def testAddChildWithStartDateToParentWithStartDate(self):
        self.assertEqual(date.Today(), self.parent.startDate())
        self.assertEqual(date.Today(), self.child.startDate())
        
    def testAddChildWithBiggerStartDateThanParent(self):
        self.child2.setStartDate(date.Tomorrow())
        self.parent.addChild(self.child2)
        self.assertEqual(date.Today(), self.parent.startDate())
        
    def testAddChildWithSmallerStartDateThanParent(self):
        self.child2.setStartDate(date.Yesterday())
        self.parent.addChild(self.child2)
        self.assertEqual(self.child2.startDate(), self.parent.startDate())
        
    def testSetStartDateParentInfinite(self):
        self.parent.setStartDate(date.Date())
        self.assertEqual(date.Date(), self.child.startDate())
        
    def testSetStartDateParentBiggerThanChildStartDate(self):
        self.parent.setStartDate(date.Tomorrow())
        self.assertEqual(date.Tomorrow(), self.child.startDate())
        
    def testSetChildStartDateInfinite(self):
        self.child.setStartDate(date.Date())
        self.assertEqual(date.Today(), self.parent.startDate())
        
    def testSetChildStartDateEarlierThanParentStartDate(self):
        self.child.setStartDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.parent.startDate())
    

class TaskRelationshipManagerTest(CommonTaskRelationshipManagerTests, test.TestCase):
    markParentCompletedWhenAllChildrenCompleted = True

    # completion date
    
    def testMarkOnlyChildCompleted(self):
        self.child.setCompletionDate()
        self.failUnless(self.parent.completed())
        
    def testMarkOnlyGrandchildCompleted(self):
        self.child.addChild(self.grandchild)
        self.grandchild.setCompletionDate()
        self.failUnless(self.parent.completed())                        
              
    def testAddCompletedChildAsOnlyChild(self):
        self.grandchild.setCompletionDate()
        self.child.addChild(self.grandchild)
        self.failUnless(self.child.completed())
        
    def testMarkChildCompletedYesterday(self):    
        self.child.setCompletionDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.parent.completionDate())
        
    def testRemoveLastUncompletedChild(self):
        self.parent.addChild(self.child2)
        self.child.setCompletionDate()
        self.parent.removeChild(self.child2)
        self.failUnless(self.parent.completed())

        
class TaskRelationshipManagerTestWhenMarkParentCompletedAutomaticallyIsOff( \
        CommonTaskRelationshipManagerTests, test.TestCase):
    markParentCompletedWhenAllChildrenCompleted = False
              
    def testDontMarkOnlyChildCompleted(self):
        self.child.setCompletionDate()
        self.failIf(self.parent.completed())

    def testDontMarkOnlyGrandchildCompleted(self):
        self.child.addChild(self.grandchild)
        self.grandchild.setCompletionDate()
        self.failIf(self.parent.completed())    
 
    def testAddCompletedChildAsOnlyChild(self):
        self.grandchild.setCompletionDate()
        self.child.addChild(self.grandchild)
        self.failIf(self.child.completed())

    def testMarkChildCompletedYesterdayDoesNotAffectParentCompletionDate(self):    
        self.child.setCompletionDate(date.Yesterday())
        self.assertEqual(date.Date(), self.parent.completionDate())

    def testRemoveLastUncompletedChild(self):
        self.parent.addChild(self.child2)
        self.child.setCompletionDate()
        self.parent.removeChild(self.child2)
        self.failIf(self.parent.completed())

    
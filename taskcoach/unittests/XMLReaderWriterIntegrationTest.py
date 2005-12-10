import test
import cStringIO as StringIO
import domain.task as task
import domain.effort as effort
import domain.date as date

class IntegrationTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.reader = task.reader.XMLReader(self.fd)
        self.writer = task.writer.XMLWriter(self.fd)
        self.taskList = task.TaskList()
        self.fillTaskList()
        self.tasksWrittenAndRead = task.TaskList(self.readAndWrite())

    def fillTaskList(self):
        pass

    def readAndWrite(self):
        self.fd.reset()
        self.writer.write(self.taskList)
        self.fd.reset()
        return self.reader.read()


class IntegrationTest_EmptyList(IntegrationTestCase):
    def testEmptyTaskList(self):
        self.assertEqual([], self.tasksWrittenAndRead)
        
        
class IntegrationTest(IntegrationTestCase):
    def fillTaskList(self):
        self.description = 'Description\nLine 2'
        self.task = task.Task('Subject', self.description, 
            startdate=date.Yesterday(), duedate=date.Tomorrow(), 
            completiondate=date.Yesterday(), budget=date.TimeDelta(hours=1), 
            priority=4, lastModificationTime=date.DateTime(2004,1,1), 
            hourlyFee=100.5, fixedFee=1000)
        self.child = task.Task()
        self.task.addChild(self.child)
        self.grandChild = task.Task()
        self.child.addChild(self.grandChild)
        self.task.addEffort(effort.Effort(self.task, start=date.DateTime(2004,1,1), 
            stop=date.DateTime(2004,1,2), description=self.description))
        self.task.addCategory('test')
        self.task2 = task.Task('Task 2', priority=-1954)
        self.taskList.extend([self.task, self.task2])

    def getTaskWrittenAndRead(self, id):
        return [task for task in self.tasksWrittenAndRead if task.id() == id][0]

    def assertAttributeWrittenAndRead(self, task, attribute):
        taskWrittenAndRead = self.getTaskWrittenAndRead(task.id())
        self.assertEqual(getattr(task, attribute)(), 
                         getattr(taskWrittenAndRead, attribute)())

    def testSubject(self):
        self.assertAttributeWrittenAndRead(self.task, 'subject')

    def testDescription(self):
        self.assertAttributeWrittenAndRead(self.task, 'description')
         
    def testStartDate(self):
        self.assertAttributeWrittenAndRead(self.task, 'startDate')
                
    def testDueDate(self):
        self.assertAttributeWrittenAndRead(self.task, 'dueDate')
 
    def testCompletionDate(self):
        self.assertAttributeWrittenAndRead(self.task, 'completionDate')
 
    def testBudget(self):
        self.assertAttributeWrittenAndRead(self.task, 'budget')
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.tasksWrittenAndRead = task.TaskList(self.readAndWrite())
        self.assertAttributeWrittenAndRead(self.task, 'budget')
        
    def testEffort(self):
        self.assertAttributeWrittenAndRead(self.task, 'timeSpent')
        
    def testEffortDescription(self):
        self.assertEqual(self.task.efforts()[0].getDescription(), 
                         self.getTaskWrittenAndRead(self.task.id()).efforts()[0].getDescription())
        
    def testChildren(self):
        self.assertEqual(len(self.task.children()), 
                         len(self.getTaskWrittenAndRead(self.task.id()).children()))
        
    def testGrandChildren(self):
        self.assertEqual(len(self.task.allChildren()),  
                         len(self.getTaskWrittenAndRead(self.task.id()).allChildren()))
       
    def testCategory(self):
        self.assertAttributeWrittenAndRead(self.task, 'categories')
        
    def testPriority(self):
        self.assertAttributeWrittenAndRead(self.task, 'priority')
        
    def testNegativePriority(self):
        self.assertAttributeWrittenAndRead(self.task2, 'priority')
        
    def testLastModificationTime(self):
        delta = abs(self.task.lastModificationTime() - \
                    self.getTaskWrittenAndRead(self.task.id()).lastModificationTime())
        self.failUnless(delta < date.TimeDelta(seconds=1))

    def testHourlyFee(self):
        self.assertAttributeWrittenAndRead(self.task, 'hourlyFee')

    def testFixedFee(self):
        self.assertAttributeWrittenAndRead(self.task, 'fixedFee')
        
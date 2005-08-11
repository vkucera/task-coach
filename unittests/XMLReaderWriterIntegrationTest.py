import test, task, date, effort
import cStringIO as StringIO

class IntegrationTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.reader = task.reader.XMLReader(self.fd)
        self.writer = task.writer.XMLWriter(self.fd)
        self.taskList = task.TaskList()
        self.fillTaskList()
        self.tasksWrittenAndRead = self.readAndWrite()

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
        self.task = task.Task('Subject', self.description, startdate=date.Yesterday(), 
            duedate=date.Tomorrow(), completiondate=date.Yesterday(), 
            budget=date.TimeDelta(hours=1), priority=4, 
            lastModificationTime=date.DateTime(2004,1,1))
        self.child = task.Task()
        self.task.addChild(self.child)
        self.grandChild = task.Task()
        self.child.addChild(self.grandChild)
        self.task.addEffort(effort.Effort(self.task, start=date.DateTime(2004,1,1), 
            stop=date.DateTime(2004,1,2), description=self.description))
        self.task.addCategory('test')
        self.task2 = task.Task(priority=-1954)
        self.taskList.extend([self.task, self.task2])
                 
    def testSubject(self):
        self.assertEqual(self.task.subject(), self.tasksWrittenAndRead[0].subject())

    def testDescription(self):
        self.assertEqual(self.task.description(), self.tasksWrittenAndRead[0].description())
         
    def testStartDate(self):
        self.assertEqual(self.task.startDate(), self.tasksWrittenAndRead[0].startDate())
                
    def testDueDate(self):
        self.assertEqual(self.task.dueDate(), self.tasksWrittenAndRead[0].dueDate())
 
    def testCompletionDate(self):
        self.assertEqual(self.task.completionDate(), self.tasksWrittenAndRead[0].completionDate())
 
    def testBudget(self):
        self.assertEqual(self.task.budget(), self.tasksWrittenAndRead[0].budget())
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.assertEqual(self.task.budget(), self.readAndWrite()[0].budget())
        
    def testEffort(self):
        self.assertEqual(self.task.timeSpent(), self.tasksWrittenAndRead[0].timeSpent())
        
    def testEffortDescription(self):
        self.assertEqual(self.task.efforts()[0].getDescription(), 
            self.tasksWrittenAndRead[0].efforts()[0].getDescription())
        
    def testChildren(self):
        self.assertEqual(len(self.task.children()), len(self.tasksWrittenAndRead[0].children()))
        
    def testGrandChildren(self):
        self.assertEqual(len(self.task.allChildren()), len(self.tasksWrittenAndRead[0].allChildren()))
       
    def testCategory(self):
        self.assertEqual(self.task.categories(), self.tasksWrittenAndRead[0].categories())
        
    def testPriority(self):
        self.assertEqual(self.task.priority(), self.tasksWrittenAndRead[0].priority())
        
    def testNegativePriority(self):
        self.assertEqual(self.task2.priority(), self.tasksWrittenAndRead[1].priority())
        
    def testId(self):
        self.assertEqual(self.task.id(), self.tasksWrittenAndRead[0].id())
        
    def testLastModificationTime(self):
        self.assertEqual(self.task.lastModificationTime(), self.tasksWrittenAndRead[0].lastModificationTime())
        
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
        self.task = task.Task('Subject', 'Description', startdate=date.Yesterday(), 
            duedate=date.Tomorrow(), completiondate=date.Yesterday(), budget=date.TimeDelta(hours=1))
        self.child = task.Task()
        self.task.addChild(self.child)
        self.grandChild = task.Task()
        self.child.addChild(self.grandChild)
        self.task.addEffort(effort.Effort(self.task, start=date.DateTime(2004,1,1), stop=date.DateTime(2004,1,2), description='Yo'))
        self.taskList.append(self.task)
                 
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
        self.assertEqual(self.task.duration(), self.tasksWrittenAndRead[0].duration())
        
    def testEffortDescription(self):
        self.assertEqual(self.task.efforts()[0].getDescription(), 
            self.tasksWrittenAndRead[0].efforts()[0].getDescription())
        
    def testChildren(self):
        self.assertEqual(len(self.task.children()), len(self.tasksWrittenAndRead[0].children()))
        
    def testGrandChildren(self):
        self.assertEqual(len(self.task.allChildren()), len(self.tasksWrittenAndRead[0].allChildren()))
        
        
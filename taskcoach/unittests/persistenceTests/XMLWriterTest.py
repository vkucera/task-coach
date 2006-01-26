import test, persistence
import cStringIO as StringIO
import domain.task as task
import domain.effort as effort
import domain.date as date

class XMLWriterTest(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.writer = persistence.XMLWriter(self.fd)
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
            
    def __writeAndRead(self):
        self.writer.write(self.taskList)
        self.fd.reset()
        return self.fd.read()
    
    def expectInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.failUnless(xmlFragment in xml, '%s not in %s'%(xmlFragment, xml))
    
    def expectNotInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.failIf(xmlFragment in xml, '%s in %s'%(xmlFragment, xml))
    
    # tests
        
    def testVersion(self):
        import meta
        self.expectInXML('<?taskcoach release="%s"'%meta.data.version)
        
    def testTaskSubject(self):
        self.task.setSubject('Subject')
        self.expectInXML('subject="Subject"')
            
    def testTaskDescription(self):
        self.task.setDescription('Description')
        self.expectInXML('<description>Description</description>')
        
    def testEmptyTaskDescriptionIsNotWritten(self):
        self.expectNotInXML('<description>')
        
    def testTaskStartDate(self):
        self.task.setStartDate(date.Date(2004,1,1))
        self.expectInXML('startdate="%s"'%str(self.task.startDate()))
        
    def testNoStartDate(self):
        self.task.setStartDate(date.Date())
        self.expectNotInXML('startdate')
        
    def testTaskDueDate(self):
        self.task.setDueDate(date.Date(2004,1,1))
        self.expectInXML('duedate="%s"'%str(self.task.dueDate()))

    def testNoDueDate(self):
        self.expectNotInXML('duedate')
                
    def testTaskCompletionDate(self):
        self.task.setCompletionDate(date.Date(2004, 1, 1))
        self.expectInXML('completiondate="%s"'%str(self.task.completionDate()))

    def testNoCompletionDate(self):
        self.expectNotInXML('completiondate')
        
    def testChildTask(self):
        self.task.addChild(task.Task(subject='child'))
        self.expectInXML('subject="child"/></task></tasks>')

    def testEffort(self):
        taskEffort = effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2), 'description\nline 2')
        self.task.addEffort(taskEffort)
        self.expectInXML('<effort start="%s" stop="%s"><description>description\nline 2</description></effort>'% \
            (taskEffort.getStart(), taskEffort.getStop()))
            
    def testEmptyEffortDescriptionIsNotWritten(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2)))
        self.expectNotInXML('<description>')
        
    def testActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1)))
        self.expectInXML('<effort start="%s"/>'%self.task.efforts()[0].getStart()) 
                
    def testNoEffortByDefault(self):
        self.expectNotInXML('<efforts>')
        
    def testBudget(self):
        self.task.setBudget(date.TimeDelta(hours=1))
        self.expectInXML('budget="%s"'%str(self.task.budget()))
        
    def testNoBudget(self):
        self.expectNotInXML('budget')
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.expectInXML('budget="25:00:00"')
        
    def testOneCategory(self):
        self.task.addCategory('test')
        self.expectInXML('<category>test</category>')
        
    def testMultipleCategories(self):
        for category in ['test', 'another']:
            self.task.addCategory(category)
        self.expectInXML('<category>test</category><category>another</category>')
        
    def testDefaultPriority(self):
        self.expectNotInXML('priority')
        
    def testPriority(self):
        self.task.setPriority(5)
        self.expectInXML('priority="5"')
        
    def testId(self):
        self.expectInXML('id="%s"'%self.task.id())
        
    def testLastModificationTime(self):
        self.expectInXML('lastModificationTime="%s"'%self.task.lastModificationTime())

    def testTwoTasks(self):
        self.task.setSubject('task 1')
        task2 = task.Task('task 2')
        self.taskList.append(task2)
        self.expectInXML('subject="task 2"')

    def testDefaultHourlyFee(self):
        self.expectNotInXML('hourlyFee')
        
    def testHourlyFee(self):
        self.task.setHourlyFee(100)
        self.expectInXML('hourlyFee="100"')
        
    def testDefaultFixedFee(self):
        self.expectNotInXML('fixedFee')
        
    def testFixedFee(self):
        self.task.setFixedFee(1000)
        self.expectInXML('fixedFee="1000"')

    def testNoReminder(self):
        self.expectNotInXML('reminder')
        
    def testReminder(self):
        self.task.setReminder(date.DateTime(2005, 5, 7, 13, 15, 10))
        self.expectInXML('reminder="%s"'%str(self.task.reminder()))
        
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_None(self):
        self.expectNotInXML('shouldMarkCompletedWhenAllChildrenCompleted')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_True(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = True
        self.expectInXML('shouldMarkCompletedWhenAllChildrenCompleted="True"')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_False(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = False
        self.expectInXML('shouldMarkCompletedWhenAllChildrenCompleted="False"')
              

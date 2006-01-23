import xml, test
import cStringIO as StringIO
import domain.task as task
import domain.effort as effort
import domain.date as date

class XMLWriterTest(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.writer = task.writer.XMLWriter(self.fd)
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
    
    def assertTaskAttribute(self, expectedValue, attribute, index=0):
        xmlDocument = self.writeAndParse()
        self.assertEqual(str(expectedValue),
            xmlDocument.getElementsByTagName('task')[index].getAttribute(attribute))

    def assertEffort(self, effort):
        self.task.addEffort(effort)
        xmlDocument = self.writeAndParse()
        effortNode = xmlDocument.documentElement.getElementsByTagName('effort')[0]
        self.assertEqual(str(effort.getStart()), effortNode.getAttribute('start'))
        self.assertEqual(str(effort.getStop()), effortNode.getAttribute('stop'))
        textNode = effortNode.getElementsByTagName('description')[0].firstChild
        if textNode:
            text = textNode.data
        else:
            text = ''
        self.assertEqual(effort.getDescription(), text)

    def assertDescription(self, task, description):
        documentElement = self.writeAndParse().documentElement
        descriptionTextNode = documentElement.getElementsByTagName('description')[0].firstChild
        self.assertEqual(description, descriptionTextNode.data)
   
    def assertCategories(self, categories):
        for category in categories:
            self.task.addCategory(category)
        xmlDocument = self.writeAndParse()
        for categoryNode in xmlDocument.documentElement.getElementsByTagName('category'):
            self.failUnless(categoryNode.firstChild.data in categories)
        
    def writeAndParse(self):
        self.writer.write(self.taskList)
        self.fd.reset()
        return xml.dom.minidom.parse(self.fd)
    
    def writeAndRead(self):
        self.writer.write(self.taskList)
        self.fd.reset()
        return self.fd.read()
    
    def expectInXML(self, expectedFragment):
        result = self.writeAndRead()
        self.failUnless(expectedFragment in result,
            '%s not in %s'%(expectedFragment, result))
    
    def expectNotInXML(self, expectedFragment):
        self.failIf(expectedFragment in self.writeAndRead())
    
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
        
    def testTaskDueDate(self):
        self.task.setDueDate(date.Date(2004,1,1))
        self.expectInXML('duedate="%s"'%str(self.task.dueDate()))
        
    def testTaskCompletionDate_None(self):
        self.assertTaskAttribute(self.task.dueDate(), 'completiondate')
        self.expectInXML('completiondate="%s"'%str(self.task.completionDate()))
        
    def testTaskCompletionDate(self):
        self.task.setCompletionDate(date.Date(2004, 1, 1))
        self.expectInXML('completiondate="%s"'%str(self.task.completionDate()))
        
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
        self.expectInXML('<effort start="%s" stop="None"/>'%self.task.efforts()[0].getStart()) 
                
    def testNoEffortByDefault(self):
        self.expectNotInXML('<efforts>')
        
    def testBudget(self):
        self.task.setBudget(date.TimeDelta(hours=1))
        self.expectInXML('budget="%s"'%str(self.task.budget()))
        
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
        self.expectInXML('priority="0"')
        
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
        self.assertTaskAttribute('task 2', 'subject', 1)

    def testDefaultHourlyFee(self):
        self.assertTaskAttribute('0', 'hourlyFee')
        
    def testHourlyFee(self):
        self.task.setHourlyFee(100)
        self.assertTaskAttribute('100', 'hourlyFee')

    def testDefaultFixedFee(self):
        self.assertTaskAttribute('0', 'fixedFee')
        
    def testFixedFee(self):
        self.task.setFixedFee(1000)
        self.assertTaskAttribute('1000', 'fixedFee')

    def testNoReminder(self):
        self.assertTaskAttribute(str(self.task.reminder()), 'reminder')
        
    def testReminder(self):
        self.task.setReminder(date.DateTime(2005, 5, 7, 13, 15, 10))
        self.assertTaskAttribute(str(self.task.reminder()), 'reminder')
        
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_None(self):
        self.assertTaskAttribute('', 
            'shouldMarkCompletedWhenAllChildrenCompleted')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_True(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = True
        self.assertTaskAttribute('True', 
            'shouldMarkCompletedWhenAllChildrenCompleted')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_False(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = False
        self.assertTaskAttribute('False', 
            'shouldMarkCompletedWhenAllChildrenCompleted')
              
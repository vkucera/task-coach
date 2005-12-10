import xml, test, date
import cStringIO as StringIO
import domain.task as task
import domain.effort as effort

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
    
    def testVersion(self):
        import meta
        xmlDocument = self.writeAndParse()
        lines = xmlDocument.toxml()
        self.failUnless('<?taskcoach release="%s"'%meta.data.version in lines)
        
    def testTaskSubject(self):
        self.task.setSubject('Subject')
        self.assertTaskAttribute(self.task.subject(), 'subject')
            
    def testTaskDescription(self):
        self.task.setDescription('Description')
        self.assertDescription(self.task, 'Description')
        
    def testTaskStartDate(self):
        self.task.setStartDate(date.Date(2004,1,1))
        self.assertTaskAttribute(self.task.startDate(), 'startdate')
        
    def testTaskDueDate(self):
        self.task.setDueDate(date.Date(2004,1,1))
        self.assertTaskAttribute(self.task.dueDate(), 'duedate')
        
    def testTaskCompletionDate_None(self):
        self.assertTaskAttribute(self.task.dueDate(), 'completiondate')
        
    def testTaskCompletionDate(self):
        self.task.setCompletionDate(date.Date(2004, 1, 1))
        self.assertTaskAttribute(self.task.completionDate(), 'completiondate')
        
    def testChildTask(self):
        self.task.addChild(task.Task(subject='child'))
        xmlDocument = self.writeAndParse()
        parent = xmlDocument.documentElement.getElementsByTagName('task')[0]
        child = parent.getElementsByTagName('task')[0]
        self.assertEqual('child', child.getAttribute('subject'))

    def testEffort(self):
        self.assertEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2), 'description\nline 2'))
        
    def testActiveEffort(self): 
        self.assertEffort(effort.Effort(self.task, date.DateTime(2004,1,1)))
                
    def testNoEffort(self):
        xmlDocument = self.writeAndParse()
        efforts = xmlDocument.documentElement.getElementsByTagName('efforts')
        self.assertEqual([], efforts)
        
    def testBudget(self):
        self.task.setBudget(date.TimeDelta(hours=1))
        self.assertTaskAttribute(self.task.budget(), 'budget')
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.assertTaskAttribute('25:00:00', 'budget')
        
    def testOneCategory(self):
        self.assertCategories(['test'])
        
    def testMultipleCategories(self):
        self.assertCategories(['test', 'another', 'yetanother'])
        
    def testDefaultPriority(self):
        self.assertTaskAttribute('0', 'priority')
        
    def testPriority(self):
        self.task.setPriority(5)
        self.assertTaskAttribute('5', 'priority')
        
    def testId(self):
        self.assertTaskAttribute(self.task.id(), 'id')
        
    def testLastModificationTime(self):
        self.assertTaskAttribute(self.task.lastModificationTime(), 'lastModificationTime')

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
        
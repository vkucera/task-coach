import xml, test, task, date, effort
import cStringIO as StringIO

class XMLWriterTest(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.writer = task.writer.XMLWriter(self.fd)
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
    
    def assertTaskAttribute(self, expectedValue, attribute):
        xmlDocument = self.writeAndParse()
        self.assertEqual(str(expectedValue),
            xmlDocument.getElementsByTagName('task')[0].getAttribute(attribute))

    def assertEffort(self, effort):
        self.task.addEffort(effort)
        xmlDocument = self.writeAndParse()
        effortNode = xmlDocument.documentElement.getElementsByTagName('effort')[0]
        self.assertEqual(str(effort.getStart()), effortNode.getAttribute('start'))
        self.assertEqual(str(effort.getStop()), effortNode.getAttribute('stop'))
        self.assertEqual(effort.getDescription(), effortNode.getAttribute('description'))

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
        self.assertTaskAttribute(self.task.description(), 'description')
        
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
            date.DateTime(2004,1,2), 'description'))
        
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
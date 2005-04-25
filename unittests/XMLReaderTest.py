import test, task, date, xml.parsers.expat
import cStringIO as StringIO

class XMLReaderTest(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.reader = task.reader.XMLReader(self.fd)
    
    def writeAndRead(self, xml):
        self.fd.write(xml)
        self.fd.reset()
        return self.reader.read()
            
    def testReadEmptyStream(self):
        try:
            self.reader.read()
            self.fail('Expected ExpatError')
        except xml.parsers.expat.ExpatError:
            pass
        
    def testNoTasks(self):
        self.assertEqual([], self.writeAndRead('<tasks/>\n'))
        
    def testOneTask(self):
        tasks = self.writeAndRead('<tasks><task/></tasks>\n')
        self.assertEqual(1, len(tasks))
        self.assertEqual('', tasks[0].subject())
        
    def testOneTask_Subject(self):
        tasks = self.writeAndRead('<tasks><task subject="Yo"/></tasks>\n')
        self.assertEqual('Yo', tasks[0].subject())
        
    def testOneTask_UnicodeSubject(self):
        tasks = self.writeAndRead('<tasks><task subject="???"/></tasks>\n')
        self.assertEqual('???', tasks[0].subject())
        
    def testStartDate(self):
        tasks = self.writeAndRead('<tasks><task startdate="2005-04-17"/></tasks>\n')
        self.assertEqual(date.Date(2005,4,17), tasks[0].startDate())
        
    def testDueDate(self):
        tasks = self.writeAndRead('<tasks><task duedate="2005-04-17"/></tasks>\n')
        self.assertEqual(date.Date(2005,4,17), tasks[0].dueDate())
        
    def testCompletionDate(self):
        tasks = self.writeAndRead('<tasks><task completiondate="2005-01-01"/></tasks>\n')
        self.assertEqual(date.Date(2005,1,1), tasks[0].completionDate())
        self.failUnless(tasks[0].completed())
        
    def testBudget(self):
        tasks = self.writeAndRead('<tasks><task budget="4:10:10"/></tasks>\n')
        self.assertEqual(date.TimeDelta(hours=4, minutes=10, seconds=10), tasks[0].budget())

    def testBudget_NoBudget(self):
        tasks = self.writeAndRead('<tasks><task/></tasks>\n')
        self.assertEqual(date.TimeDelta(), tasks[0].budget())
        
    def testDescription(self):
        tasks = self.writeAndRead('<tasks><task description="%s"/></tasks>\n'%u'Description')
        self.assertEqual(u'Description', tasks[0].description())
        
    def testChild(self):
        tasks = self.writeAndRead('<tasks><task><task/></task></tasks>\n')
        self.assertEqual(1, len(tasks[0].children()))
        self.assertEqual(1, len(tasks))
        
    def testGrandchild(self):
        tasks = self.writeAndRead('<tasks><task><task><task/></task></task></tasks>\n')
        self.assertEqual(1, len(tasks))
        parent = tasks[0]
        self.assertEqual(1, len(parent.children()))
        self.assertEqual(1, len(parent.children()[0].children()))
        
    def testEffort(self):
        tasks = self.writeAndRead('<tasks><task><effort start="2004-01-01 10:00:00.123000" stop="2004-01-01 10:30:00.123000"/></task></tasks>')
        self.assertEqual(1, len(tasks[0].efforts()))
        self.assertEqual(date.TimeDelta(minutes=30), tasks[0].duration())
        self.assertEqual(tasks[0], tasks[0].efforts()[0].task())
        
    def testEffortDescription(self):
        tasks = self.writeAndRead('<tasks><task><effort start="2004-01-01 10:00:00.123000" stop="2004-01-01 10:30:00.123000" description="Yo"/></task></tasks>')
        self.assertEqual('Yo', tasks[0].efforts()[0].getDescription())
        
    def testActiveEffort(self):
        tasks = self.writeAndRead('<tasks><task><effort start="2004-01-01 10:00:00.123000" stop="None"/></task></tasks>')
        self.assertEqual(1, len(tasks[0].efforts()))
        self.failUnless(tasks[0].isBeingTracked())
        
        
import test, task, date, xml.parsers.expat, sets
import cStringIO as StringIO

class XMLReaderTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.reader = task.reader.XMLReader(self.fd)

    def writeAndRead(self, xml):
        xml = '<?taskcoach release="whatever" tskversion="%d"?>\n'%self.tskversion + xml
        self.fd.write(xml)
        self.fd.reset()
        return self.reader.read()

    
class XMLReaderVersion6Test(XMLReaderTestCase):
    tskversion = 6

    def testDescription(self):
        tasks = self.writeAndRead('<tasks><task description="%s"/></tasks>\n'%u'Description')
        self.assertEqual(u'Description', tasks[0].description())

    def testEffortDescription(self):
        tasks = self.writeAndRead('<tasks><task><effort start="2004-01-01 10:00:00.123000" stop="2004-01-01 10:30:00.123000" description="Yo"/></task></tasks>')
        self.assertEqual('Yo', tasks[0].efforts()[0].getDescription())


class XMLReaderVersion8Test(XMLReaderTestCase):   
    tskversion = 8

    def testReadTaskWithoutPriority(self):
        tasks = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual(0, tasks[0].priority())
        
        
class XMLReaderVersion9Test(XMLReaderTestCase):
    tskversion = 9
    
    def testReadTaskWithoutId(self):
        tasks = self.writeAndRead('<tasks><task/></tasks>')
        self.failUnless(tasks[0].id())
        
                
class XMLReaderTest(XMLReaderTestCase):   
    tskversion = 10
           
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
        description = u'Description\nline 2'
        tasks = self.writeAndRead('<tasks><task><description>%s</description></task></tasks>\n'%description)
        self.assertEqual(description, tasks[0].description())
        
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
        self.assertEqual(date.TimeDelta(minutes=30), tasks[0].timeSpent())
        self.assertEqual(tasks[0], tasks[0].efforts()[0].task())
        
    def testEffortDescription(self):
        description = u'Description\nLine 2'
        tasks = self.writeAndRead('<tasks><task><effort start="2004-01-01 10:00:00.123000" stop="None"><description>%s</description></effort></task></tasks>'%description)
        self.assertEqual(description, tasks[0].efforts()[0].getDescription())
        
    def testActiveEffort(self):
        tasks = self.writeAndRead('<tasks><task><effort start="2004-01-01 10:00:00.123000" stop="None"/></task></tasks>')
        self.assertEqual(1, len(tasks[0].efforts()))
        self.failUnless(tasks[0].isBeingTracked())
        
    def testOneCategory(self):
        tasks = self.writeAndRead('<tasks><task><category>test</category></task></tasks>')
        self.assertEqual(['test'], list(tasks[0].categories()))

    def testMultipleCategories(self):
        tasks = self.writeAndRead('<tasks><task><category>test</category><category>another</category><category>yetanother</category></task></tasks>')
        self.assertEqual(sets.Set(['test', 'another', 'yetanother']), tasks[0].categories())
        
    def testPriority(self):
        tasks = self.writeAndRead('<tasks><task priority="5"/></tasks>')        
        self.assertEqual(5, tasks[0].priority())
        
    def testId(self):
        tasks = self.writeAndRead('<tasks><task id="xyz"/></tasks>')
        self.assertEqual('xyz', tasks[0].id())
import test, task, date, effort
import cStringIO as StringIO


class TaskWriterAndReaderTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.taskWriter = task.TaskWriter(self.fd)
        self.taskReader = task.TaskReader(self.fd)

    def write(self):
        self.taskWriter.write(self.tasksToWrite)

    def writeAndRead(self):
        self.write()
        self.fd.reset()
        return self.taskReader.read()


class TaskWriterTest(TaskWriterAndReaderTestCase):
    def testVersionOnFirstLine(self):
        self.taskWriter.write([])
        self.fd.reset()
        self.assertEqual('%s'%self.taskWriter.version, 
            self.fd.readline().strip())


class WriteAndReadOneTaskTest(TaskWriterAndReaderTestCase):
    def setUp(self):
        super(WriteAndReadOneTaskTest, self).setUp()
        self.taskOrig = task.Task()
        self.tasksToWrite = [self.taskOrig]

    def testSubject(self):
        self.taskOrig.setSubject('ABC')
        tasks  = self.writeAndRead()
        self.assertEqual(self.taskOrig.subject(), tasks[0].subject())

    def testId(self):
        tasks = self.writeAndRead()
        self.assertEqual(self.taskOrig.id(), tasks[0].id())

    def testDueDate_Infinite(self):
        tasks = self.writeAndRead()
        self.assertEqual(self.taskOrig.dueDate(), tasks[0].dueDate())

    def testDueDate_Tomorrow(self):
        self.taskOrig.setDueDate(date.Tomorrow())
        tasks = self.writeAndRead()
        self.assertEqual(self.taskOrig.dueDate(), tasks[0].dueDate())

    def testStartDate(self):
        self.taskOrig.setStartDate(date.Yesterday())
        tasks = self.writeAndRead()
        self.assertEqual(self.taskOrig.startDate(), tasks[0].startDate())

    def testCompletionDate(self):
        self.taskOrig.setCompletionDate(date.Yesterday())
        tasks = self.writeAndRead()
        self.assertEqual(self.taskOrig.completionDate(),
            tasks[0].completionDate())

    def testChildren(self):
        tasks = self.writeAndRead()
        self.assertEqual([], tasks[0].children())

    def testParent(self):
        tasks = self.writeAndRead()
        self.assertEqual(None, tasks[0].parent())

    def testTemporaryAttribute(self):
        tasks = self.writeAndRead()
        try:
            tasks[0].childrenToAdd
            self.fail('Expected AttributeError for childrenToAdd')
        except AttributeError:
            pass


class WriteAndReadTwoTasksTest(TaskWriterAndReaderTestCase):
    def setUp(self):
        super(WriteAndReadTwoTasksTest, self).setUp()
        self.tasksToWrite = [task.Task(subject='Task1'), 
                             task.Task(subject='Task2')]

    def testOrder(self):
        tasks = self.writeAndRead()
        self.assertEqual(self.tasksToWrite, tasks)


class WriteAndReadTasksWithChildrenTest(TaskWriterAndReaderTestCase):
    def setUp(self):
        super(WriteAndReadTasksWithChildrenTest, self).setUp()
        parent = task.Task(subject='Parent')
        child = task.Task(subject='Child')
        parent.addChild(child)
        self.tasksToWrite = [parent, child]

    def testParentAndChild(self):
        tasks = self.writeAndRead()
        self.assertEqual(1, len(tasks))
        parent = tasks[0]
        self.assertEqual(1, len(parent.children()))
        child = parent.children()[0]
        self.assertEqual(parent, child.parent())
        self.assertEqual(None, parent.parent())

    def testGrandChild(self):
        grandChild = task.Task(subject='Grandchild')
        self.tasksToWrite[-1].addChild(grandChild)
        self.tasksToWrite.append(grandChild)
        tasks = self.writeAndRead()
        self.assertEqual(2, len(tasks[0].allChildren()))

class WriteEffortTest(TaskWriterAndReaderTestCase):
    def setUp(self):
        taskWithEffort = task.Task()
        self.effort = effort.Effort(taskWithEffort, description='Yo')
        taskWithEffort.addEffort(self.effort)
        self.tasksToWrite = [taskWithEffort]
        super(WriteEffortTest, self).setUp()
        
    def testEffort(self):
        tasks = self.writeAndRead()
        self.assertEqual(self.effort.task(), tasks[0])
        effortRead = tasks[0].efforts()[0]
        # microseconds get lost, so straight compare doesn't work:
        self.assertEqual(self.effort.getStart().date(), effortRead.getStart().date())
        self.assertEqual(self.effort.getStop(), effortRead.getStop())
        self.assertEqual(self.effort.getDescription(), effortRead.getDescription())

        
import xml
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
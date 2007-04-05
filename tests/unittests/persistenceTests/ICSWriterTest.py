import test, meta, persistence
import cStringIO as StringIO
from domain import task, effort, date


class ICSTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.writer = persistence.ICSWriter(self.fd)
        self.taskList = self.createTaskList()
        self.icsFile = self.writeAndParse()
        
    def createTaskList(self):
        self.task = task.Task()
        return task.TaskList([self.task])

    def writeAndParse(self):
        self.writer.write(self.taskList)
        self.fd.reset()
        return [line[:-1] for line in self.fd.readlines()]


class CommonICSTests(object):
    def testBeginCalendar(self):
        self.assertEqual('BEGIN:VCALENDAR', self.icsFile[0])

    def testEndCalendar(self):
        self.assertEqual('END:VCALENDAR', self.icsFile[-1])

    def testVersion(self):
        domain = meta.url[len('http://'):-1]
        self.assertEqual('PRODID:-//%s//NONSGML %s V%s//EN'%(domain,
            meta.name, meta.version), self.icsFile[2])


class WriteEmptyTaskFileAsICSTest(ICSTestCase, CommonICSTests):
    def testNoEffortRecords(self):
        self.assertEqual(4, len(self.icsFile))


class WriteOneEffortRecordAsICSTest(ICSTestCase, CommonICSTests):
    def createTaskList(self):
        taskList = super(WriteOneEffortRecordAsICSTest, self).createTaskList()
        self.effort = effort.Effort(self.task, date.DateTime(2005,1,1),
            date.DateTime(2005,1,2))
        self.task.addEffort(self.effort)
        return taskList
    
    def testBeginEvent(self):
        self.assertEqual('BEGIN:VEVENT', self.icsFile[3])

    def testEndEvent(self):
        self.assertEqual('END:VEVENT', self.icsFile[-2])

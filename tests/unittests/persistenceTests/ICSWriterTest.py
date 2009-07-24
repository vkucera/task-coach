'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import cStringIO as StringIO
import test
from taskcoachlib import meta, persistence
from taskcoachlib.domain import task, effort, date


class DummyViewer(object):
    def __init__(self, effortList):
        self.effortList = effortList
        
    def visibleItems(self):
        return self.effortList
        

class ICSTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.writer = persistence.ICSWriter(self.fd)
        self.taskList = self.createTaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.viewer = DummyViewer(self.effortList)
        self.settings = None
        self.icsFile = self.writeAndParse()
        
    def createTaskList(self):
        self.task = task.Task()
        return task.TaskList([self.task])

    def writeAndParse(self):
        self.writer.write(self.viewer, self.settings)
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


class WriteOneActiveEffortRecordAsICSTest(ICSTestCase, CommonICSTests):
    def createTaskList(self):
        taskList = super(WriteOneActiveEffortRecordAsICSTest, self).createTaskList()
        self.effort = effort.Effort(self.task, date.DateTime(2005,1,1))
        self.task.addEffort(self.effort)
        return taskList
    
    def testBeginEvent(self):
        self.assertEqual('BEGIN:VEVENT', self.icsFile[3])
        
    def testLastModified(self):
        stop = date.DateTime.now().strftime('%Y%m%dT%H%M')
        self.failUnless(self.icsFile[6].startswith('LAST-MODIFIED:%s'%stop))

    def testEndEvent(self):
        self.assertEqual('END:VEVENT', self.icsFile[-2])

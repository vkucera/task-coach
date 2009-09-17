'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

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

import StringIO
import test
from taskcoachlib import persistence, gui, config
from taskcoachlib.domain import task


class VCalWriterTestCase(test.wxTestCase):
    selectionOnly = treeMode = 'Subclass responsibility'
    
    def setUp(self):
        super(VCalWriterTestCase, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False) 
        self.fd = StringIO.StringIO()
        self.writer = persistence.VCalendarWriter(self.fd)
        self.task1 = task.Task('Task subject 1')
        self.task2 = task.Task('Task subject 2')
        self.taskFile = persistence.TaskFile()
        self.taskFile.tasks().extend([self.task1, self.task2])
        self.createViewer()

    def createViewer(self):
        self.settings.set('taskviewer', 'treemode', self.treeMode)
        # pylint: disable-msg=W0201
        self.viewer = gui.viewer.TaskViewer(self.frame, self.taskFile,
            self.settings)

    def writeAndRead(self):
        self.writer.write(self.viewer, self.settings, self.selectionOnly)
        return self.fd.getvalue().split('\r\n')[:-1]

    def selectItem(self, items):
        self.viewer.widget.select(items)


class VCalendarStartEndTestMixin(object):
    def testStart(self):
        self.assertEqual('BEGIN:VCALENDAR', self.vcalFile[0])

    def testEnd(self):
        self.assertEqual('END:VCALENDAR', self.vcalFile[-1])


class VCalendarSelectedTestMixin(object):
    def setUp(self):
        super(VCalendarSelectedTestMixin, self).setUp()
        self.selectItem([self.task2])
        self.vcalFile = self.writeAndRead()


class TestSelectionOnlyMixin(VCalendarStartEndTestMixin, 
                             VCalendarSelectedTestMixin):
    selectionOnly = True

    def testSelected(self):
        self.assertEqual(self.vcalFile.count('BEGIN:VTODO'), 1) # pylint: disable-msg=W0511
        self.failUnless('SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:Task=20subject=202' in self.vcalFile,
                    '\n'.join(self.vcalFile))


class TestSelectionList(TestSelectionOnlyMixin, VCalWriterTestCase):
    treeMode = 'False'

class TestSelectionTree(TestSelectionOnlyMixin, VCalWriterTestCase):
    treeMode = 'True'


class TestNotSelectionOnlyMixin(VCalendarStartEndTestMixin, 
                                VCalendarSelectedTestMixin):
    selectionOnly = False

    def testAll(self):
        self.assertEqual(self.vcalFile.count('BEGIN:VTODO'), 2) # pylint: disable-msg=W0511


class TestNotSelectionList(TestNotSelectionOnlyMixin, VCalWriterTestCase):
    treeMode = 'False'

class TestNotSelectionTree(TestNotSelectionOnlyMixin, VCalWriterTestCase):
    treeMode = 'True'

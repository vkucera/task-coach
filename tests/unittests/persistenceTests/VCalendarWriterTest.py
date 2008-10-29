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

import wx, StringIO
import test
from unittests import dummy
from taskcoachlib import persistence, gui, config, widgets
from taskcoachlib.domain import task, category, effort, date, note


class VCalWriterTestCase(test.wxTestCase):
    def setUp(self):
        super(VCalWriterTestCase, self).setUp()
        self.fd = StringIO.StringIO()
        self.writer = persistence.VCalendarWriter(self.fd)
        self.task1 = task.Task('Task subject 1')
        self.task2 = task.Task('Task subject 2')
        self.taskList = task.TaskList([self.task1, self.task2])
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.settings = config.Settings(load=False)
        self.viewerContainer = gui.viewercontainer.ViewerContainer(\
            widgets.Notebook(self.frame), self.settings, 'mainviewer')
        self.createViewer()

    def createViewer(self):
        self.settings.set('tasktreelistviewer', 'treemode', self.treeMode)
        self.viewer = gui.viewer.TaskViewer(self.frame, self.taskList, 
            self.settings, categories=self.categories, notes=self.notes,
            efforts=self.effortList)

    def writeAndRead(self):
        self.writer.write(self.viewer, self.selectionOnly)
        return self.fd.getvalue().split('\r\n')[:-1]

    def selectItem(self, index):
        self.viewer.widget.select((index,))


class VCalendarStartEndTest(object):
    def testStart(self):
        self.assertEqual('BEGIN:VCALENDAR', self.vcalFile[0])

    def testEnd(self):
        self.assertEqual('END:VCALENDAR', self.vcalFile[-1])


class VCalendarSelectedTest(object):
    def setUp(self):
        super(VCalendarSelectedTest, self).setUp()
        self.selectItem((1,))
        self.vcalFile = self.writeAndRead()


class TestSelectionOnly(VCalendarStartEndTest,
                        VCalendarSelectedTest):
    selectionOnly = True

    def testSelected(self):
        self.assertEqual(self.vcalFile.count('BEGIN:VTODO'), 1)
        self.failUnless('SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:Task=20subject=202' in self.vcalFile,
                    '\n'.join(self.vcalFile))


class TestSelectionList(TestSelectionOnly, VCalWriterTestCase):
    treeMode = 'False'

class TestSelectionTree(TestSelectionOnly, VCalWriterTestCase):
    treeMode = 'True'


class TestNotSelectionOnly(VCalendarStartEndTest,
                           VCalendarSelectedTest):
    selectionOnly = False

    def testAll(self):
        self.assertEqual(self.vcalFile.count('BEGIN:VTODO'), 2)


class TestNotSelectionList(TestNotSelectionOnly, VCalWriterTestCase):
    treeMode = 'False'

class TestNotSelectionTree(TestNotSelectionOnly, VCalWriterTestCase):
    treeMode = 'True'

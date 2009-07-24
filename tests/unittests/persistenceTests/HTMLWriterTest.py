'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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
from taskcoachlib import persistence, gui, config
from taskcoachlib.domain import task, category, effort, date, note


class HTMLWriterUnderTest(persistence.HTMLWriter):
    def _writeCSS(self):
        pass
    
    
class HTMLWriterTestCase(test.wxTestCase):
    def setUp(self):
        super(HTMLWriterTestCase, self).setUp()
        self.fd = StringIO.StringIO()
        self.filename = 'filename.html'
        self.writer = HTMLWriterUnderTest(self.fd, self.filename)
        self.taskFile = persistence.TaskFile()
        self.task = task.Task('Task subject')
        self.taskFile.tasks().append(self.task)
        self.settings = config.Settings(load=False)
        self.createViewer()
        
    def createViewer(self):
        self.settings.set('taskviewer', 'treemode', self.treeMode)
        self.viewer = gui.viewer.TaskViewer(self.frame, self.taskFile,
            self.settings)

    def __writeAndRead(self, selectionOnly):
        self.writer.write(self.viewer, self.settings, selectionOnly)
        return self.fd.getvalue()
    
    def expectInHTML(self, *htmlFragments, **kwargs):
        selectionOnly = kwargs.pop('selectionOnly', False)
        html = self.__writeAndRead(selectionOnly)
        for htmlFragment in htmlFragments:
            self.failUnless(htmlFragment in html, 
                            '%s not in %s'%(htmlFragment, html))
    
    def expectNotInHTML(self, *htmlFragments, **kwargs):
        selectionOnly = kwargs.pop('selectionOnly', False)
        html = self.__writeAndRead(selectionOnly)
        for htmlFragment in htmlFragments:
            self.failIf(htmlFragment in html, '%s in %s'%(htmlFragment, html))

    def selectItem(self, index):
        self.viewer.widget.select((index,))


class CommonTests(object):
    def testHTML(self):
        self.expectInHTML('<html>\n', '</html>\n')
        
    def testHeader(self):
        self.expectInHTML('  <head>\n', '  </head>\n')
        
    def testStyle(self):
        self.expectInHTML('    <style type="text/css">\n', '    </style>\n')
        
    def testBody(self):
        self.expectInHTML('  <body>\n', '  </body>\n')


class TaskTests(CommonTests):
    def testTaskSubject(self):
        self.expectInHTML('>Task subject<')
        
    def testCSSLink(self):
        self.expectInHTML('<link href="filename.css" rel="stylesheet" type="text/css" media="screen">')
        
    def testWriteSelectionOnly(self):
        self.expectNotInHTML('>Task subject<', selectionOnly=True)
        
    def testWriteSelectionOnly_SelectedChild(self):
        child = task.Task('Child')
        self.task.addChild(child)
        self.taskFile.tasks().append(child)
        self.selectItem(1)
        self.expectInHTML('>Task subject<')

    def testColumnStyle(self):
        self.expectInHTML('      .subject {text-align: left}\n')
        
    def testTaskStatusStyle(self):
        self.expectInHTML('      .completed {color: #00FF00}\n')
        
    def testTaskStatusStyleWhenColorChangedInSettings(self):
        self.settings.set('color', 'completedtasks', str(wx.RED))
        self.expectInHTML('      .completed {color: #FF0000}\n')
        
    def testOverdueTask(self):
        self.task.setDueDate(date.Yesterday())
        self.expectInHTML('<tr class="overdue">')

    def testCompletedTask(self):
        self.task.setCompletionDate()
        self.expectInHTML('<tr class="completed">')

    def testTaskDueToday(self):
        self.task.setDueDate(date.Today())
        self.expectInHTML('<tr class="duetoday">')
        
    def testInactiveTask(self):
        self.task.setStartDate(date.Tomorrow())
        self.expectInHTML('<tr class="inactive">')

    def testTaskColor(self):
        self.task.setColor(wx.RED)
        self.expectInHTML('<tr class="active" style="background: #FF0000">')
        
    def testCategoryColor(self):
        cat = category.Category('cat', color=wx.RED)
        self.task.addCategory(cat)
        self.expectInHTML('<tr class="active" style="background: #FF0000">')

    def testCategoryColorAsTuple(self):
        cat = category.Category('cat', color=(255, 0, 0, 0))
        self.task.addCategory(cat)
        self.expectInHTML('<tr class="active" style="background: #FF0000">')
        
        
class HTMLListWriterTest(TaskTests, HTMLWriterTestCase):
    treeMode = 'False'
        
    def testTaskDescription(self):
        self.task.setDescription('Task description')
        self.viewer.showColumnByName('description')
        self.expectInHTML('>Task description<')
    
    def testTaskDescriptionWithNewLine(self):
        self.task.setDescription('Line1\nLine2')
        self.viewer.showColumnByName('description')
        self.expectInHTML('>Line1<br>Line2<')
                      

class HTMLTreeWriterTest(TaskTests, HTMLWriterTestCase):
    treeMode = 'True'


class EffortWriterTest(HTMLWriterTestCase, CommonTests):
    def setUp(self):
        super(EffortWriterTest, self).setUp()
        now = date.DateTime.now()
        self.task.addEffort(effort.Effort(self.task, start=now,
                                          stop=now + date.TimeDelta(seconds=1)))

    def createViewer(self):
        self.viewer = gui.viewer.EffortViewer(self.frame, self.taskFile,
            self.settings)

    def testTaskSubject(self):
        self.expectInHTML('>Task subject<')
        
    def testEffortDuration(self):
        self.expectInHTML('>0:00:01<')
        
    def testColumnStyle(self):
        self.expectInHTML('      .task {text-align: left}\n')


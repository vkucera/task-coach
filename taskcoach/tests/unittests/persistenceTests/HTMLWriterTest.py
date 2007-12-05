import test, persistence, StringIO, gui, config, wx
from domain import task, category, effort, date, note
from unittests import dummy

class HTMLWriterTestCase(test.wxTestCase):
    def setUp(self):
        super(HTMLWriterTestCase, self).setUp()
        self.fd = StringIO.StringIO()
        self.writer = persistence.HTMLWriter(self.fd)
        self.task = task.Task('Task subject')
        self.taskList = task.TaskList([self.task])
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.settings = config.Settings(load=False)
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            self.settings, 'mainviewer')
        self.createViewer()

    def __writeAndRead(self, selectionOnly):
        self.writer.write(self.viewer, selectionOnly)
        return self.fd.getvalue()
    
    def expectInHTML(self, htmlFragment, selectionOnly=False):
        html = self.__writeAndRead(selectionOnly)
        self.failUnless(htmlFragment in html, 
                        '%s not in %s'%(htmlFragment, html))
    
    def expectNotInHTML(self, htmlFragment, selectionOnly=False):
        html = self.__writeAndRead(selectionOnly)
        self.failIf(htmlFragment in html, '%s in %s'%(htmlFragment, html))


class TaskTests(object):
    def testTaskSubject(self):
        self.expectInHTML('>Task subject<')
        
    def testWriteSelectionOnly(self):
        self.expectNotInHTML('>Task subject<', selectionOnly=True)
        
    def testWriteSelectionOnly_SelectedChild(self):
        child = task.Task('Child')
        self.task.addChild(child)
        self.taskList.append(child)
        self.selectItem(1)
        self.expectInHTML('>Task subject<')
        
    def testSubjectColumnAlignment(self):
        self.expectInHTML('<td align="left">Task subject</td>')
        
    def testOverdueTask(self):
        self.task.setDueDate(date.Yesterday())
        self.expectInHTML('<font color="#FF0000">Task subject</font>')

    def testCompletedTask(self):
        self.task.setCompletionDate()
        self.expectInHTML('<font color="#00FF00">Task subject</font>')

    def testTaskDueToday(self):
        self.task.setDueDate(date.Today())
        expectedColor = '%02X%02X%02X'%eval(self.settings.get('color', 'duetodaytasks'))[:3]
        self.expectInHTML('<font color="#%s">Task subject</font>'%expectedColor)
        
    def testInactiveTask(self):
        self.task.setStartDate(date.Tomorrow())
        expectedColor = '%02X%02X%02X'%eval(self.settings.get('color', 'inactivetasks'))[:3]
        self.expectInHTML('<font color="#%s">Task subject</font>'%expectedColor)

    def testCategoryColor(self):
        cat = category.Category('cat', color=wx.RED)
        self.task.addCategory(cat)
        self.expectInHTML('<tr bgcolor="#FF0000">')

    def testCategoryColorAsTuple(self):
        cat = category.Category('cat', color=(255, 0, 0, 0))
        self.task.addCategory(cat)
        self.expectInHTML('<tr bgcolor="#FF0000">')
        
        
class HTMLListWriterTest(TaskTests, HTMLWriterTestCase):
    def createViewer(self):
        self.viewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, self.effortList, self.categories, 
                self.notes), 
            self.settings, categories=self.categories)
        
    def selectItem(self, index):
        self.viewer.widget.SelectItem(index)
                    

class HTMLTreeWriterTest(TaskTests, HTMLWriterTestCase):
    def createViewer(self):
        self.viewer = gui.viewer.TaskTreeViewer(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, self.effortList, self.categories, 
                self.notes), 
            self.settings, categories=self.categories)

    def selectItem(self, index):
        item, cookie = self.viewer.widget.GetFirstChild(self.viewer.widget.GetRootItem())
        self.viewer.widget.SelectItem(item)
        

class EffortWriterTest(HTMLWriterTestCase):
    def setUp(self):
        super(EffortWriterTest, self).setUp()
        self.task.addEffort(effort.Effort(self.task))

    def createViewer(self):
        self.viewer = gui.viewer.EffortListViewer(self.frame, self.taskList,
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, self.effortList, self.categories, 
                self.notes), 
            self.settings)

    def testTaskSubject(self):
        self.expectInHTML('>Task subject<')
        
    def testEffortDuration(self):
        self.expectInHTML('>0:00:00<')
      
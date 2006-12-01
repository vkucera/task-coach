import test, persistence, StringIO, gui, config
from domain import task, category, effort
from unittests import dummy

class HTMLWriterTestCase(object):
    def setUp(self):
        super(HTMLWriterTestCase, self).setUp()
        self.fd = StringIO.StringIO()
        self.writer = persistence.HTMLWriter(self.fd)
        self.task = task.Task('Task subject')
        self.taskList = task.TaskList([self.task])
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.settings = config.Settings(load=False)
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


class HTMLListWriterTest(HTMLWriterTestCase, test.wxTestCase):
    def createViewer(self):
        self.viewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, None, self.settings, 
                self.taskList, self.effortList, self.categories), self.settings, 
                categories=self.categories)
        
    def selectItem(self, index):
        self.viewer.widget.SelectItem(index)
                    

class HTMLTreeWriterTest(HTMLWriterTestCase, test.wxTestCase):
    def createViewer(self):
        self.viewer = gui.viewer.TaskTreeViewer(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, None, self.settings, 
                self.taskList, self.effortList, self.categories), self.settings, 
                categories=self.categories)

    def selectItem(self, index):
        self.viewer.widget.SelectItem(self.viewer.widget[1])
                    
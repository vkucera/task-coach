import wx, test, gui, widgets, config
from domain import category, task, note, effort
    
       
class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.taskList = task.sorter.Sorter(task.TaskList())
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            self.settings, 'mainviewer')
        self.viewer = gui.viewer.TaskTreeViewer(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                self.viewerContainer, self.settings, self.taskList, 
                effort.EffortList(self.taskList), self.categories, self.notes), 
            self.settings, categories=self.categories)
        self.parent = task.Task('parent')
        self.child = task.Task('child')
        self.parent.addChild(self.child)
        self.child.setParent(self.parent)
        self.taskList.extend([self.parent, self.child])
        
    def testExpand(self):
        self.viewer.refresh()
        widget = self.viewer.widget
        widget.Expand(widget.GetFirstVisibleItem())
        self.failUnless(self.parent.isExpanded())
        
    def testCollapse(self):
        self.viewer.refresh()
        widget = self.viewer.widget
        widget.Expand(widget.GetFirstVisibleItem())
        widget.Collapse(widget.GetFirstVisibleItem())
        self.failIf(self.parent.isExpanded())

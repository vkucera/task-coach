import test, wx, gui, config
from domain import task, effort, category, note, date
from unittests import dummy

class UICommandTest(test.wxTestCase):
    def setUp(self):
        self.uicommand = dummy.DummyUICommand(menuText='undo', bitmap='undo')
        self.menu = wx.Menu()
        self.frame = wx.Frame(None)
        self.frame.Show(False)
        self.frame.SetMenuBar(wx.MenuBar())
        self.frame.CreateToolBar()

    def activate(self, window, id):
        window.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, id))

    def testAppendToMenu(self):
        id = self.uicommand.appendToMenu(self.menu, self.frame)
        self.assertEqual(id, self.menu.FindItem(self.uicommand.menuText))

    def testAppendToToolBar(self):
        id = self.uicommand.appendToToolBar(self.frame.GetToolBar())
        self.assertEqual(0, self.frame.GetToolBar().GetToolPos(id))

    def testActivationFromMenu(self):
        id = self.uicommand.appendToMenu(self.menu, self.frame)
        self.activate(self.frame, id)
        self.failUnless(self.uicommand.activated)

    def testActivationFromToolBar(self):
        id = self.uicommand.appendToToolBar(self.frame.GetToolBar())
        self.activate(self.frame.GetToolBar(), id)
        self.failUnless(self.uicommand.activated)


class UICommandsTest(test.wxTestCase):
    def testCreate(self):
        settings = config.Settings(load=False)
        taskList = task.TaskList()
        effortList = effort.EffortList(taskList)
        categories = category.CategoryList()
        viewerContainer = gui.viewercontainer.ViewerNotebook(self.frame, 
            settings, 'mainviewer')
        gui.uicommand.UICommands(self.frame, None, viewerContainer, None, 
            taskList, effortList, categories, note.NoteContainer())


class MailTaskTest(test.TestCase):
    def testCreate(self):
        mailTask = gui.uicommand.TaskMail()


class DummyViewer(object):
    def __init__(self, selection=None):
        self.selection = selection or []
        
    def curselection(self):
        return self.selection
    
    def isShowingTasks(self):
        return True
    
    
class MarkCompletedTest(test.TestCase):
    def assertMarkCompletedIsEnabled(self, selection, shouldBeEnabled=True):
        viewer = DummyViewer(selection)
        markCompleted = gui.uicommand.TaskToggleCompletion(viewer=viewer)
        isEnabled = markCompleted.enabled(None)
        if shouldBeEnabled:
            self.failUnless(isEnabled)
        else:
            self.failIf(isEnabled)
            
    def testNotEnabledWhenSelectionIsEmpty(self):
        self.assertMarkCompletedIsEnabled(selection=[], shouldBeEnabled=False)
        
    def testEnabledWhenSelectedTaskIsNotCompleted(self):
        self.assertMarkCompletedIsEnabled(selection=[task.Task()])
        
    def testEnabledWhenSelectedTaskIsCompleted(self):
        self.assertMarkCompletedIsEnabled(
            selection=[task.Task(completionDate=date.Today())])
        
    def testNotEnabledWhenSelectedTasksAreBothCompletedAndUncompleted(self):
        self.assertMarkCompletedIsEnabled(
            selection=[task.Task(completionDate=date.Today()), task.Task()], 
            shouldBeEnabled=False)
import test, wx, gui, config
import domain.category as category
import domain.task as task
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
        gui.uicommand.UICommands(None, None, None, None, None, None, None)


class ViewAllTasksTest(test.wxTestCase):
    def testTurnOfFilteredCategory(self):
        settings = config.Settings(load=False)
        uiCommands = dummy.DummyUICommands()
        categories = category.CategoryList()
        aCategory = category.Category('category')
        categories.append(aCategory)
        aCategory.setFiltered()
        viewAllTasks = gui.uicommand.ViewAllTasks(settings=settings, 
            uiCommands=uiCommands, categories=categories)
        viewAllTasks.doCommand(None)
        self.failIf(aCategory.isFiltered())
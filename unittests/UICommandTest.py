import test, wx, gui, dummy

class UICommandTest(test.wxTestCase):
    def setUp(self):
        self.uicommand = dummy.DummyUICommand()
        self.menu = wx.Menu()
        self.frame = wx.Frame(None)
        self.frame.Show(False)
        self.frame.SetMenuBar(wx.MenuBar())
        self.frame.CreateToolBar()

    def testAppendToMenu(self):
        self.uicommand.appendToMenu(self.menu, self.frame)
        self.assertEqual(self.uicommand.id(), 
            self.menu.FindItem(self.uicommand.menuText))

    def testAppendToToolBar(self):
        self.uicommand.appendToToolBar(self.frame.GetToolBar(), self.frame)
        self.assertEqual(0, 
            self.frame.GetToolBar().GetToolPos(self.uicommand.id()))

    def testActivationFromMenu(self):
        self.uicommand.appendToMenu(self.menu, self.frame)
        self.activate()
        self.failUnless(self.uicommand.activated)

    def testActivationFromToolBar(self):
        self.uicommand.appendToToolBar(self.frame.GetToolBar(), self.frame)
        self.activate()
        self.failUnless(self.uicommand.activated)

    def activate(self):
        wx.FutureCall(1, lambda: self.frame.Command(self.uicommand.id()))
        wx.FutureCall(2, lambda: self.app.ExitMainLoop())
        self.app.MainLoop()

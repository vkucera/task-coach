import test, gui, wx, dummy

class ToolBar(gui.toolbar.ToolBar):
    def commandNames(self):
        return []


class ToolBarTest(test.wxTestCase):
    def testAppendUICommand(self):
        gui.init()
        toolbar = ToolBar(self.frame, {})
        uiCommand = dummy.DummyUICommand()
        id = toolbar.appendUICommand(uiCommand)
        self.assertNotEqual(wx.NOT_FOUND, toolbar.GetToolPos(id))


class ToolBarSizeTest(test.wxTestCase):
    def testSizeDefault(self):
        self.createToolBarAndTestSize(None, (32, 32))

    def testSizeSmall(self):
        self.createToolBarAndTestSize((16, 16))

    def testSizeMedium(self):
        self.createToolBarAndTestSize((22, 22))

    def testSizeBig(self):
        self.createToolBarAndTestSize((32, 32))

    def createToolBarAndTestSize(self, size, expectedSize=None):
        toolbarArgs = [self.frame, {}]
        if size:
            toolbarArgs.append(size)
        toolbar = ToolBar(*toolbarArgs)
        if not expectedSize:
            expectedSize = size
        self.assertEqual(wx.Size(*expectedSize), toolbar.GetToolBitmapSize())

import test, wx

class TextCtrlTest(test.TestCase):
    def testClearDoesNotEmitEventOnMacOSX(self):
        self.clearTextCausesEvent = False
        app = wx.App()
        frame = wx.Frame(None)
        textCtrl = wx.TextCtrl(frame)
        textCtrl.Bind(wx.EVT_TEXT, self.onTextChanged)
        textCtrl.Clear()
        if '__WXMAC__' in wx.PlatformInfo:
            self.failIf(self.clearTextCausesEvent)
        else:
            self.failUnless(self.clearTextCausesEvent)

    def onTextChanged(self, event):
        self.clearTextCausesEvent = True

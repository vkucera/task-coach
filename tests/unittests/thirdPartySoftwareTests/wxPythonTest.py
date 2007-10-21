import test, wx

''' These are unittests of wxPython functionality. Of course, the goal is
    not to test all wxPython functions, but rather to document platform
    inconsistencies or surprising behaviour. '''


class TextCtrlTest(test.wxTestCase):
    def testClearEmitsNoEventOnMacOSX(self):
        self.clearTextCausesEvent = False
        textCtrl = wx.TextCtrl(self.frame)
        textCtrl.Bind(wx.EVT_TEXT, self.onTextChanged)
        textCtrl.Clear()
        if '__WXMAC__' in wx.PlatformInfo: 
            self.failIf(self.clearTextCausesEvent)
        else:
            self.failUnless(self.clearTextCausesEvent)

    def onTextChanged(self, event):
        self.clearTextCausesEvent = True


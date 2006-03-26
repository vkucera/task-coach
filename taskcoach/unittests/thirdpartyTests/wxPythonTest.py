import test, wx

class TextCtrlTest(test.wxTestCase):
    def testClearDoesNotEmitEventOnMacOSX(self):
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


class DatePickerCtrlTest(test.wxTestCase):
    def testStyleDP_ALLOWNONEOnlyWorksOnWindows(self):
        dpc = wx.DatePickerCtrl(self.frame, style=wx.DP_ALLOWNONE)
        value = dpc.GetValue()
        if '__WXMSW__' in wx.PlatformInfo:
            self.failIf(value.IsValid())
        else:
            self.failUnless(value.IsValid())

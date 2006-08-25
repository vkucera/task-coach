import test, wx

''' These are unittests of wxPython functionality. Of course, the goal is
    not to test all wxPython functions, but rather to document platform
    inconsistencies or surpiring behaviour. '''


class TextCtrlTest(test.wxTestCase):
    def testCleaEmitsEventOnMSWOnly(self):
        self.clearTextCausesEvent = False
        textCtrl = wx.TextCtrl(self.frame)
        textCtrl.Bind(wx.EVT_TEXT, self.onTextChanged)
        textCtrl.Clear()
        if '__WXMSW__' in wx.PlatformInfo:
            self.failUnless(self.clearTextCausesEvent)
        else:
            self.failIf(self.clearTextCausesEvent)

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

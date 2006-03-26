import test, widgets, wx

class DatePickerCtrlWithStyleDP_ALLOWNONETest(test.wxTestCase):
    def setUp(self):
        self.datePicker = widgets.DatePickerCtrl(self.frame, 
            style=wx.DP_ALLOWNONE)

    def testInitialValueIsNotValid(self):
        value = self.datePicker.GetValue()
        self.failIf(value.IsValid())

    def testValueWhenTurnedOnIsToday(self):
        class CheckedEvent:
            def IsChecked(self):
                return True

        self.datePicker.onCheck(CheckedEvent())
        value = self.datePicker.GetValue()
        today = wx.DateTime()
        today.SetToCurrent()
        self.failUnless(value.IsSameDate(today))

    def testSetValue(self):
        today = wx.DateTime()
        today.SetToCurrent()
        self.datePicker.SetValue(today)
        value = self.datePicker.GetValue()
        self.failUnless(value.IsSameDate(today))

    def testSetValueInvalid(self):
        invalid = wx.DateTime()
        self.datePicker.SetValue(invalid)
        value = self.datePicker.GetValue()
        self.failIf(value.IsValid())
        self.failIf(self.datePicker.IsEnabled())


class DatePickerCtrlFactoryTest(test.wxTestCase):
    def isWxDatePickerCtrl(self, instance):
        return isinstance(instance, wx.DatePickerCtrl)

    def testFactoryFunctionNoStyle(self):
        dpc = widgets.DatePickerCtrl(self.frame)
        self.failUnless(self.isWxDatePickerCtrl(dpc))

    def testFactoryFunctionStyleIncludesDP_ALLOWNONE(self):
        dpc = widgets.DatePickerCtrl(self.frame, style=wx.DP_ALLOWNONE)
        if '__WXMSW__' in wx.PlatformInfo:
            self.failUnless(self.isWxDatePickerCtrl(dpc))
        else:
            self.failIf(self.isWxDatePickerCtrl(dpc))
            
            
class StyleTest(test.TestCase):            
    def testGettingStyleFromOrredSetOfStyles(self):
        for style, allowNoneIncluded in [(wx.DP_DEFAULT, False), 
                (wx.DP_DEFAULT | wx.DP_SHOWCENTURY, False),
                (wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE, True),
                (wx.DP_ALLOWNONE, True),
                (wx.DP_DEFAULT | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE, True)]:
            self.assertEqual(allowNoneIncluded, 
                self.isOptionIncluded(style, wx.DP_ALLOWNONE))

    def isOptionIncluded(self, options, option):
        return (options & option) == option



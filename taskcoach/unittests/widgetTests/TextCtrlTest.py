import test, widgets

class MultiLineTextCtrlTest(test.wxTestCase):
        
    def testOpenWebbrowserOnURLClick(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame)
        textctrl.AppendText('test http://test.com/ test')
        # FIXME: simulate a mouseclick on the url
        
    def testSetInsertionPointAtStart(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame, text='Hiya')
        self.assertEqual(0, textctrl.GetInsertionPoint())
        
    def testRemoveAnyControlCharactersEnteredByUser(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame, text=u'Test\x01test') # ^A
        self.assertEqual('Testtest', textctrl.GetValue())
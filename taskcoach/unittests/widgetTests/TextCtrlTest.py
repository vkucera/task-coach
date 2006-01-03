import test, widgets


class BaseTextCtrlTest(test.wxTestCase):
    def testRemoveAnyControlCharactersEnteredByUser(self):
        textctrl = widgets.textctrl.BaseTextCtrl(self.frame, u'Test\x01test') # ^A
        self.assertEqual('Testtest', textctrl.GetValue())    
    
class MultiLineTextCtrlTest(test.wxTestCase):
        
    def testOpenWebbrowserOnURLClick(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame)
        textctrl.AppendText('test http://test.com/ test')
        # FIXME: simulate a mouseclick on the url
        
    def testSetInsertionPointAtStart(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame, text='Hiya')
        self.assertEqual(0, textctrl.GetInsertionPoint())
        

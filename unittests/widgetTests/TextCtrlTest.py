import test, widgets


class BaseTextCtrlTest(test.wxTestCase):
    def testRemoveAnyControlCharactersEnteredByUser(self):
        textctrl = widgets.textctrl.BaseTextCtrl(self.frame, u'T\x02\x01est\x09')
        self.assertEqual(u'Test\t', textctrl.GetValue())    
    
    
class MultiLineTextCtrlTest(test.wxTestCase):
    def testOpenWebbrowserOnURLClick(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame)
        textctrl.AppendText('test http://test.com/ test')
        # FIXME: simulate a mouseclick on the url
        
    def testSetInsertionPointAtStart(self):
        textctrl = widgets.MultiLineTextCtrl(self.frame, text='Hiya')
        self.assertEqual(0, textctrl.GetInsertionPoint())
        

class SingleLineTextCtrlWithEnterButtonTest(test.wxTestCase):
    def setUp(self):
        self.textCtrl = widgets.SingleLineTextCtrlWithEnterButton(self.frame, 
            label='Text', onEnter=self.onEnter)
            
    def onEnter(self, text):
        self.enteredText = text
        
    def testDontAllowEnterWhenTheTextCtrlIsEmpty(self):
        self.failIf(self.textCtrl.isButtonEnabled())
        
    def testAllowEnterWhenTheTextCtrlIsNotEmpty(self):
        self.textCtrl.SetValue('Some text')
        self.failUnless(self.textCtrl.isButtonEnabled())
        
    def testCallback(self): 
        self.textCtrl.SetValue('Some text')
        self.textCtrl.onEnter()
        self.assertEqual('Some text', self.enteredText)
    
    def testAfterCallbackTheTextCtrlIsCleared(self):
        self.textCtrl.SetValue('Some text')
        self.textCtrl.onEnter()
        self.failIf(self.textCtrl.isButtonEnabled())
        
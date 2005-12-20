import test, widgets

class TextCtrlTest(test.wxTestCase):
    def testOpenWebbrowserOnURLClick(self):
        textctrl = widgets.TextCtrl(self.frame)
        textctrl.AppendText('test http://test.com/ test')
        # FIXME: simulate a mouseclick on the url
        
    def testSetInsertionPointAtStart(self):
        textctrl = widgets.TextCtrl(self.frame, text='Hiya')
        self.assertEqual(0, textctrl.GetInsertionPoint())
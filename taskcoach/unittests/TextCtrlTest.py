import test, widgets

class TextCtrlTest(test.wxTestCase):
    def testOpenWebbrowserOnURLClick(self):
        textctrl = widgets.TextCtrl(self.frame)
        textctrl.AppendText('test http://test.com/ test')
        
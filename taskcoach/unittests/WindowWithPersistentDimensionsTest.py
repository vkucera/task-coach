import test, gui, config, wx

class WindowWithPersistentDimensions(gui.mainwindow.WindowWithPersistentDimensions):
    def __init__(self, settings, shown=True):
        self._shown = shown
        super(WindowWithPersistentDimensions, self).__init__(settings)
        
    def IsShown(self):
        return self._shown
        
        
class WindowTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.window = WindowWithPersistentDimensions(self.settings)
        self.section = self.window._section
        
    def testInitialPosition(self):
        self.assertEqual(eval(self.settings.get(self.section, 'position')), 
            self.window.GetPositionTuple())
         
    def testInitialSize(self):
        self.assertEqual(eval(self.settings.get(self.section, 'size')),
            self.window.GetSizeTuple())
     
    def testInitialIconizeState(self):
        self.assertEqual(self.settings.getboolean(self.section, 'iconized'),
            self.window.IsIconized())
            
    def testChangeSize(self):
        self.window.ProcessEvent(wx.SizeEvent((100, 100)))
        self.assertEqual((100, 100), eval(self.settings.get(self.section, 'size')))
        
    def testMove(self):
        self.window.ProcessEvent(wx.MoveEvent((100, 100)))
        #The move is not processed, dunno why:
        self.assertEqual((0, 0), eval(self.settings.get(self.section, 'position')))
import wx, icons

class SplashScreen(wx.SplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__( 
            icons.catalog['splash'].getBitmap(),
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 4000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
    def onClose(self, event):
        # We hide the splash screen instead of closing it, because closing it
        # (or destroying) also closes all open dialogs. This sucks, but I 
        # don't know a better solution unfortunately.
        self.Hide()
        event.Skip(False) 

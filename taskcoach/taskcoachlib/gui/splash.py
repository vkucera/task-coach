import wx, icons

class SplashScreen(wx.SplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__( 
            icons.catalog['splash'].getBitmap(),
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 4000, None, -1)

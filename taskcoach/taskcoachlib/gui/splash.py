import wx, icons, i18n

class SplashScreen(wx.SplashScreen):
    def __init__(self):
        splash = icons.catalog['splash']
        if i18n.Translator().currentLanguageIsRightToLeft():
            # RTL languages cause the bitmap to be mirrored too, but because
            # the splash image is not internationalized, we have to mirror it
            # (back). Unfortunately using SetLayoutDirection() on the 
            # SplashWindow doesn't work.
            bitmap = wx.BitmapFromImage(splash.getImage().Mirror())
        else:
            bitmap = splash.getBitmap()
        super(SplashScreen, self).__init__(bitmap,
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 4000, None, -1)

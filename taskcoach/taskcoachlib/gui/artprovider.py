import wx, icons

class ArtProvider(wx.ArtProvider):
    def CreateBitmap(self, artId, artClient, size):
        catalogKey = '%s%dx%d'%(artId, size[0], size[1])
        if catalogKey in icons.catalog.keys():
            bitmap = icons.catalog[catalogKey].getBitmap()
            if artClient == wx.ART_FRAME_ICON:
                bitmap = self.convertAlphaToMask(bitmap)
            return bitmap
        else:
            return wx.NullBitmap

    def convertAlphaToMask(self, bitmap):
        image = wx.ImageFromBitmap(bitmap)
        image.ConvertAlphaToMask()
        return wx.BitmapFromImage(image)


def init():
    if ('__WXMSW__' in wx.PlatformInfo) and (wx.GetApp().GetComCtl32Version() 
        >= 600) and (wx.DisplayDepth() >= 32):
        wx.SystemOptions_SetOption("msw.remap", "2")
    wx.ArtProvider_PushProvider(ArtProvider())

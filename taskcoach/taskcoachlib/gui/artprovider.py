'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx, icons
from taskcoachlib import patterns


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

    @staticmethod
    def convertAlphaToMask(bitmap):
        image = wx.ImageFromBitmap(bitmap)
        image.ConvertAlphaToMask()
        return wx.BitmapFromImage(image)    


class IconProvider(object):
    __metaclass__ = patterns.Singleton

    def __init__(self):
        self.__iconCache = dict()
        self.__iconSizeOnCurrentPlatform = 128 if '__WXMAC__' == wx.Platform else 16
        
    def getIcon(self, iconTitle): 
        ''' Return the icon. Use a cache to prevent leakage of GDI object 
            count. '''
        try:
            return self.__iconCache[iconTitle]
        except KeyError:
            icon = self.getIconFromArtProvider(iconTitle)
            self.__iconCache[iconTitle] = icon
            return icon
        
    def iconBundle(self, iconTitle):
        ''' Create an icon bundle with icons of different sizes. '''
        bundle = wx.IconBundle()
        for size in (16, 22, 32, 48, 64, 128):
            bundle.AddIcon(self.getIconFromArtProvider(iconTitle, size))
        return bundle
    
    def getIconFromArtProvider(self, iconTitle, iconSize=None):
        size = iconSize or self.__iconSizeOnCurrentPlatform
        # wx.ArtProvider_GetIcon doesn't convert alpha to mask, so we do it
        # ourselves:
        bitmap = wx.ArtProvider_GetBitmap(iconTitle, wx.ART_FRAME_ICON, 
                                          (size, size))    
        bitmap = ArtProvider.convertAlphaToMask(bitmap)
        return wx.IconFromBitmap(bitmap)


def iconBundle(iconTitle):
    return IconProvider().iconBundle(iconTitle)


def getIcon(iconTitle):
    return IconProvider().getIcon(iconTitle)


def init():
    if ('__WXMSW__' in wx.PlatformInfo) and (wx.DisplayDepth() >= 32):
        wx.SystemOptions_SetOption("msw.remap", "0") # pragma: no cover
    try:
        wx.ArtProvider_PushProvider(ArtProvider()) # pylint: disable-msg=E1101
    except AttributeError:
        wx.ArtProvider.Push(ArtProvider())


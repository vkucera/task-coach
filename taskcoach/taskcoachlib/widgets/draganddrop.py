'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

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

import wx, urlparse
from taskcoachlib.mailer import thunderbird, outlook


class FileDropTarget(wx.FileDropTarget):
    def __init__(self, onDropCallback=None, onDragOverCallback=None):
        wx.FileDropTarget.__init__(self)
        self.__onDropCallback = onDropCallback
        self.__onDragOverCallback = onDragOverCallback or self.__defaultDragOverCallback
        
    def OnDropFiles(self, x, y, filenames):
        if self.__onDropCallback:
            self.__onDropCallback(x, y, filenames)
            return True
        else:
            return False

    def OnDragOver(self, x, y, defaultResult):
        return self.__onDragOverCallback(x, y, defaultResult)
    
    def __defaultDragOverCallback(self, x, y, defaultResult):
        return defaultResult
    
    
class TextDropTarget(wx.TextDropTarget):
    def __init__(self, onDropCallback):
        wx.TextDropTarget.__init__(self)
        self.__onDropCallback = onDropCallback
        
    def OnDropText(self, x, y, text):
        self.__onDropCallback(text)


class DropTarget(wx.DropTarget):
    def __init__(self, onDropURLCallback, onDropFileCallback,
            onDropMailCallback, onDragOverCallback=None):
        super(DropTarget, self).__init__()
        self.__onDropURLCallback = onDropURLCallback
        self.__onDropFileCallback = onDropFileCallback
        self.__onDropMailCallback = onDropMailCallback
        self.__onDragOverCallback = onDragOverCallback
        self.reinit()

    def reinit(self):
        self.__compositeDataObject = wx.DataObjectComposite()
        self.__urlDataObject = wx.TextDataObject()
        self.__fileDataObject = wx.FileDataObject()
        self.__thunderbirdMailDataObject = wx.CustomDataObject('text/x-moz-message')
        self.__macThunderbirdMailDataObject = wx.CustomDataObject('MZ\x00\x00')
        self.__outlookDataObject = wx.CustomDataObject('Object Descriptor')
        for dataObject in self.__fileDataObject, \
                          self.__thunderbirdMailDataObject, self.__outlookDataObject, \
                          self.__macThunderbirdMailDataObject, \
                          self.__urlDataObject:
            # Note: The first data object added is the preferred data object.
            # We add urlData as last so that Outlook messages are not 
            # interpreted as text objects.
            self.__compositeDataObject.Add(dataObject)
        self.SetDataObject(self.__compositeDataObject)

    def OnDragOver(self, x, y, result):
        if self.__onDragOverCallback is None:
            return result
        self.__onDragOverCallback(x, y, result)
        return wx.DragCopy

    def OnDrop(self, x, y):
        return True
    
    def OnData(self, x, y, result):
        self.GetData()

        format = self.__compositeDataObject.GetReceivedFormat()

        if format.GetType() in [ wx.DF_TEXT, wx.DF_UNICODETEXT ]:
            if self.__onDropURLCallback:
                self.__onDropURLCallback(x, y, self.__urlDataObject.GetText())
        elif format.GetType() == wx.DF_FILENAME:
            if self.__onDropFileCallback:
                self.__onDropFileCallback(x, y, self.__fileDataObject.GetFilenames())
        elif format.GetId() == 'text/x-moz-message':
            if self.__onDropMailCallback:
                self.__onDropMailCallback(x, y,
                     thunderbird.getMail(self.__thunderbirdMailDataObject.GetData().decode('unicode_internal')))
        elif format.GetId() == 'MZ\x00\x00':
            if self.__onDropMailCallback:
                self.__onDropMailCallback(x, y,
                     thunderbird.getMail(self.__macThunderbirdMailDataObject.GetData().decode('unicode_internal')))
        elif format.GetId() == 'Object Descriptor':
            if self.__onDropMailCallback:
                for mail in outlook.getCurrentSelection():
                    self.__onDropMailCallback(x, y, mail)

        self.reinit()
        return wx.DragCopy

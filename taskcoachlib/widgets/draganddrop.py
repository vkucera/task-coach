import wx, urlparse
from mailer import thunderbird, outlook

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
        if self.__urlDataObject.GetText():
            if self.__onDropURLCallback:
                self.__onDropURLCallback(x, y, self.__urlDataObject.GetText())
        elif self.__thunderbirdMailDataObject.GetData():
            if self.__onDropMailCallback:
                self.__onDropMailCallback(x, y, thunderbird.getMail(self.__thunderbirdMailDataObject.GetData().decode('unicode_internal')))
        elif self.__macThunderbirdMailDataObject.GetData():
            if self.__onDropMailCallback:
                self.__onDropMailCallback(x, y, thunderbird.getMail(self.__macThunderbirdMailDataObject.GetData().decode('unicode_internal')))
        else:
            files = self.__fileDataObject.GetFilenames()
            if files:
                if self.__onDropFileCallback:
                    self.__onDropFileCallback(x, y, files)
            else:
                if self.__onDropMailCallback:
                    for mail in outlook.getCurrentSelection():
                        self.__onDropMailCallback(x, y, mail)
        self.reinit()
        return wx.DragCopy

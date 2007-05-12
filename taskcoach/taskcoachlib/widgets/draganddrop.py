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


class MailDropTarget(wx.DropTarget):
    def __init__(self, onDropCallback):
        wx.DropTarget.__init__(self)
        self.__onDropCallback = onDropCallback
        self.reinit()

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, result):
        self.GetData()
	if self.__macThunderbirdDataObject.GetData():
	    self.__onDropCallback(thunderbird.getMail(self.__macThunderbirdDataObject.GetData().decode('unicode_internal')))
        elif self.__thunderbirdDataObject.GetData():
            self.__onDropCallback(thunderbird.getMail(self.__thunderbirdDataObject.GetData().decode('unicode_internal')))
        else:
            for filename in outlook.getCurrentSelection():
                self.__onDropCallback(filename)

        self.reinit()
        return result

    def reinit(self):
        self.__compositeDataObject = wx.DataObjectComposite()
        self.__thunderbirdDataObject = wx.CustomDataObject('text/x-moz-message')
	self.__macThunderbirdDataObject = wx.CustomDataObject('MZ\x00\x00')
        self.__outlookDataObject = wx.CustomDataObject('Object Descriptor')
        for dataObject in (self.__thunderbirdDataObject, self.__outlookDataObject,
	           self.__macThunderbirdDataObject):
            self.__compositeDataObject.Add(dataObject)

        self.SetDataObject(self.__compositeDataObject)

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
        for dataObject in self.__fileDataObject, self.__urlDataObject, \
                          self.__thunderbirdMailDataObject, self.__outlookDataObject, \
                          self.__macThunderbirdMailDataObject:
            # NB: First data object added is the preferred data object
            self.__compositeDataObject.Add(dataObject)
        self.SetDataObject(self.__compositeDataObject)

    def OnDragOver(self, x, y, result):
        if self.__onDragOverCallback is None:
            return result
        return self.__onDragOverCallback(x, y, result)

    def OnDrop(self, x, y):
        return True
    
    def OnData(self, x, y, result):
        self.GetData()
        if self.__thunderbirdMailDataObject.GetData():
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
        return result

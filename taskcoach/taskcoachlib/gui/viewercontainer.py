import patterns, wx, widgets

class ViewerContainer(patterns.Observable):
    def __init__(self, parent, settings, setting, *args, **kwargs):
        self.__settings = settings
        self.__setting = setting
        self.__currentPageNumber = 0
        self.__desiredPageName = self.__settings.get('view', setting)
        super(ViewerContainer, self).__init__(parent, *args, **kwargs)

    def addViewer(self, viewer, pageName, bitmap=None):
        self.AddPage(viewer, pageName, bitmap)
        if pageName == self.__desiredPageName:
            self.SetSelection(self.GetPageCount() - 1)
        viewer.registerObserver(self.onNotify)
            
    def __getattr__(self, attr):
        ''' Find a viewer that has attr. Start by looking in the current viewer. '''
        for viewer in [self[self.__currentPageNumber]] + list(self):
            if hasattr(viewer, attr):
                return getattr(viewer, attr)
        else:
            raise AttributeError
        #return getattr(self[self.__currentPageNumber], attr)

    def onNotify(self, notification, *args, **kwargs):
        self.notifyObservers(notification)

    def onPageChanged(self, event):
        self.__currentPageNumber = event.GetSelection()
        self.__settings.set('view', self.__setting, self.currentPageName())
        self.notifyObservers(patterns.observer.Notification(self))
        event.Skip()
    
    def currentPageName(self):
        return self.GetPageText(self.__currentPageNumber)
        
        
class ViewerNotebook(ViewerContainer, widgets.Notebook):
    pass
        
        
class ViewerChoicebook(ViewerContainer, widgets.Choicebook):
    pass


class ViewerListbook(ViewerContainer, widgets.Listbook):
    pass
import patterns, wx, widgets

class ViewerContainer(patterns.Observable):
    def __init__(self, parent, settings, setting, *args, **kwargs):
        self.__settings = settings
        self.__setting = setting
        self.__currentPageNumber = 0
        # Prepare for an exception, because this setting used to be a string
        try:
            self.__desiredPageNumber = int(self.__settings.get('view', setting))
        except ValueError:
            self.__desiredPageNumber = 0
        super(ViewerContainer, self).__init__(parent, *args, **kwargs)

    def addViewer(self, viewer, pageName, bitmap=None):
        self.AddPage(viewer, pageName, bitmap)
        if self.GetPageCount() - 1 == self.__desiredPageNumber:
            self.SetSelection(self.__desiredPageNumber)
        viewer.registerObserver(self.onNotify)
            
    def __getattr__(self, attr):
        ''' Find a viewer that has attr. Start by looking in the current viewer. '''
        for viewer in [self[self.__currentPageNumber]] + list(self):
            if hasattr(viewer, attr):
                return getattr(viewer, attr)
        else:
            raise AttributeError

    def onNotify(self, notification, *args, **kwargs):
        self.notifyObservers(notification)

    def onPageChanged(self, event):
        self.__currentPageNumber = event.GetSelection()
        self.__settings.set('view', self.__setting, str(self.__currentPageNumber))
        self.notifyObservers(patterns.observer.Notification(self))
        event.Skip()
    
        
class ViewerNotebook(ViewerContainer, widgets.Notebook):
    pass
        
        
class ViewerChoicebook(ViewerContainer, widgets.Choicebook):
    pass


class ViewerListbook(ViewerContainer, widgets.Listbook):
    pass
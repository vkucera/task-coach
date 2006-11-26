import patterns, wx, widgets

class ViewerContainer(object):
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
        patterns.Publisher().registerObserver(self.onSelect, 
            eventType=viewer.selectEventType())
            
    def selectEventType(self):
        return '%s (%s).select'%(self.__class__, id(self))
    
    def viewerChangeEventType(self):
        return '%s (%s).viewerChange'%(self.__class__, id(self))
            
    def __getattr__(self, method):
        ''' Return a function that will call the method on the first viewer 
            that both has the requested method and does not raise an exception.
            Start looking in the current viewer. '''
        def findFirstViewer(*args, **kwargs):
            for viewer in [self[self.__currentPageNumber]] + list(self):
                if hasattr(viewer, method):
                    try:
                        return getattr(viewer, method)(*args, **kwargs)
                    except:
                        raise
            else:
                raise AttributeError
        return findFirstViewer
        
    def onSelect(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.selectEventType(), *event.values()))

    def onPageChanged(self, event):
        #self[self.__currentPageNumber].onDeactivateViewer()
        self.__currentPageNumber = event.GetSelection()
        self.__settings.set('view', self.__setting, str(self.__currentPageNumber))
        #self[self.__currentPageNumber].onActivateViewer()
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.viewerChangeEventType(), self.__currentPageNumber))
        event.Skip()
    
        
class ViewerNotebook(ViewerContainer, widgets.Notebook):
    pass
        
        
class ViewerChoicebook(ViewerContainer, widgets.Choicebook):
    pass


class ViewerListbook(ViewerContainer, widgets.Listbook):
    pass


class ViewerAUINotebook(ViewerContainer, widgets.AUINotebook):
    pass
import patterns, wx, widgets

class ViewerContainer(patterns.Observable):
    def __init__(self, *args, **kwargs):
        super(ViewerContainer, self).__init__(*args, **kwargs)
        self.currentPage = 0

    def addViewer(self, viewer, name, bitmap=None):
        self.AddPage(viewer, name, bitmap)
        viewer.registerObserver(self.onNotify)
            
    def __getattr__(self, attr):
        return getattr(self[self.currentPage], attr)

    def onNotify(self, notification, *args, **kwargs):
        self.notifyObservers(notification)

    def onPageChanged(self, event):
        self.currentPage = event.GetSelection()
        self.notifyObservers(patterns.observer.Notification(self))
        event.Skip()
    
        
class ViewerNotebook(ViewerContainer, widgets.Notebook):
    pass
        
        
class ViewerChoicebook(ViewerContainer, widgets.Choicebook):
    pass


class ViewerListbook(ViewerContainer, widgets.Listbook):
    pass
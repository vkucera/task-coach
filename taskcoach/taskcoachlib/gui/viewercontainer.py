'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import patterns, wx, widgets


class _ViewerContainer(object):
    def __init__(self, parent, settings, setting, *args, **kwargs):
        self._settings = settings
        self.__setting = setting
        self.__currentPageNumber = 0
        # Prepare for an exception, because this setting used to be a string
        try:
            self.__desiredPageNumber = int(self._settings.get('view', setting))
        except ValueError:
            self.__desiredPageNumber = 0
        super(_ViewerContainer, self).__init__(parent, *args, **kwargs)
        
    def addViewer(self, viewer, pageName, bitmap=''):
        self.AddPage(viewer, pageName, bitmap)
        if self.PageCount - 1 == self.__desiredPageNumber:
            # We need to use CallAfter because the AuiNotebook doesn't allow
            # PAGE_CHANGING events while the window is not active. See 
            # widgets/notebook.py
            wx.CallAfter(self.SetSelection, self.__desiredPageNumber)
        patterns.Publisher().registerObserver(self.onSelect, 
            eventType=viewer.selectEventType())
            
    def selectEventType(self):
        return '%s (%s).select'%(self.__class__, id(self))
    
    def viewerChangeEventType(self):
        return '%s (%s).viewerChange'%(self.__class__, id(self))
    
    def __getattr__(self, method):
        ''' Return a function that will call the method on the first viewer 
            that both has the requested method and does not raise an exception.
            Start looking in the current viewer. NB: this auto forwarding only 
            works for methods, not for properties. '''
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
    
    def __del__(self):
        pass # Don't forward del to one of the viewers.
    
    def __length_hint__(self):
        # Needed for python 2.5. Apparently, the call to list(self) above
        # silently calls self.__length_hint__(). If that method does not
        # exist a endless recursive loop starts, hanging the app as result.
        return self.GetPageCount()
    
    def onSelect(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.selectEventType(), *event.values()))

    def onPageChanged(self, event):
        self.__currentPageNumber = event.GetSelection()
        self._settings.set('view', self.__setting, str(self.__currentPageNumber))
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.viewerChangeEventType(), self.__currentPageNumber))
        event.Skip()
    
        
class ViewerNotebook(_ViewerContainer, widgets.Notebook):
    pass
        
        
class ViewerChoicebook(_ViewerContainer, widgets.Choicebook):
    pass


class ViewerListbook(_ViewerContainer, widgets.Listbook):
    pass


class ViewerAUINotebook(_ViewerContainer, widgets.AUINotebook):
    def onClosePage(self, event):
        viewer = self.GetPage(event.Selection)
        viewer.detach()
        setting = viewer.__class__.__name__.lower() + 'count'
        viewerCount = self._settings.getint('view', setting)
        self._settings.set('view', setting, str(viewerCount-1))
        super(ViewerAUINotebook, self).onClosePage(event)
        


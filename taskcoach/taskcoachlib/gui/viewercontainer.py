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

import patterns, wx


class ViewerContainer(object):
    def __init__(self, containerWidget, settings, setting, *args, **kwargs):
        self.containerWidget = containerWidget
        self.bindContainerWidgetEvents()
        self._settings = settings
        self.__setting = setting
        self.viewers = []
        self.__currentPageNumber = 0
        # Prepare for an exception, because this setting used to be a string
        try:
            self.__desiredPageNumber = int(self._settings.get('view', setting))
        except ValueError:
            self.__desiredPageNumber = 0
        super(ViewerContainer, self).__init__(*args, **kwargs)

    def bindContainerWidgetEvents(self):
        eventsAndHandlers = dict(pageClosedEvent=self.onPageClosed, 
                                pageChangedEvent=self.onPageChanged)
        for event, handler in eventsAndHandlers.items():
            if hasattr(self.containerWidget, event):
                self.containerWidget.Bind(getattr(self.containerWidget, event),
                    handler)
    
    def __getitem__(self, index):
        return self.viewers[index]

    def addViewer(self, viewer, pageName, bitmap=''):
        self.containerWidget.AddPage(viewer, pageName, bitmap)
        self.viewers.append(viewer)
        if len(self.viewers) - 1 == self.__desiredPageNumber:
            # We need to use CallAfter because the AuiNotebook doesn't allow
            # PAGE_CHANGING events while the window is not active. See 
            # widgets/notebook.py
            wx.CallAfter(self.containerWidget.SetSelection, self.__desiredPageNumber)
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
            for viewer in [self.activeViewer()] + self.viewers:
                if hasattr(viewer, method):
                    return getattr(viewer, method)(*args, **kwargs)
            else:
                raise AttributeError
        return findFirstViewer

    def activeViewer(self):
        windowWithFocus = wx.Window.FindFocus()
        while windowWithFocus:
            for viewer in self.viewers:
                if viewer == windowWithFocus:
                    return viewer
            windowWithFocus = windowWithFocus.Parent
        return self.viewers[self.__currentPageNumber]
    
    def __del__(self):
        pass # Don't forward del to one of the viewers.
    
    def onSelect(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.selectEventType(), *event.values()))

    def onPageChanged(self, event):
        self.__currentPageNumber = event.Selection
        self._settings.set('view', self.__setting, str(self.__currentPageNumber))
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.viewerChangeEventType(), self.__currentPageNumber))
        event.Skip()

    def onPageClosed(self, event):
        try: # Notebooks and similar widgets:
            viewer = self.viewers[event.Selection]
        except AttributeError: # Aui managed frame:
            viewer = event.GetPane().window
        # When closing a Aui managed frame, we get two close events, be prepared
        if viewer in self.viewers:
            self.viewers.remove(viewer)
            viewer.detach()
            setting = viewer.__class__.__name__.lower() + 'count'
            viewerCount = self._settings.getint('view', setting)
            self._settings.set('view', setting, str(viewerCount-1))
        event.Skip()

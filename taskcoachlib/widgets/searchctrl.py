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

import wx
from taskcoachlib.i18n import _


class SearchCtrl(wx.SearchCtrl):
    def __init__(self, *args, **kwargs):
        self.__callback = kwargs.pop('callback')
        self.__matchCase = kwargs.pop('matchCase', False)
        self.__includeSubItems = kwargs.pop('includeSubItems', False)
        size = kwargs.pop('size', (16, 16))
        super(SearchCtrl, self).__init__(*args, **kwargs)
        self.SetSearchMenuBitmap(wx.ArtProvider_GetBitmap('searchmenu', wx.ART_TOOLBAR, size))
        self.SetSearchBitmap(wx.ArtProvider_GetBitmap('search', wx.ART_TOOLBAR, size))
        self.SetCancelBitmap(wx.ArtProvider_GetBitmap('cancel', wx.ART_TOOLBAR, size))
        self.__timer = wx.Timer(self)
        self.__recentSearches = []
        self.__maxRecentSearches = 5
        self.bindEventHandlers()
        self.SetMenu(self.makeMenu())
        self.onFind(None)
        
    def bindEventHandlers(self):
        for eventType, eventHandler in \
            [(wx.EVT_TIMER, self.onFind),
             (wx.EVT_TEXT_ENTER, self.onFind),
             (wx.EVT_TEXT, self.onFindLater),
             (wx.EVT_SEARCHCTRL_CANCEL_BTN, self.onCancel)]:
            self.Bind(eventType, eventHandler)
        self.Bind(wx.EVT_MENU_RANGE, self.onRecentSearchMenuItem, id=1, 
            id2=self.__maxRecentSearches)
        self.__matchCaseMenuItemId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onMatchCaseMenuItem, 
            id=self.__matchCaseMenuItemId)
        self.__includeSubItemsMenuItemId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onIncludeSubItemsMenuItem,
            id=self.__includeSubItemsMenuItemId)
        
    def setMatchCase(self, matchCase):
        self.__matchCase = matchCase
        self.SetMenu(self.makeMenu())
        
    def setIncludeSubItems(self, includeSubItems):
        self.__includeSubItems = includeSubItems
        self.SetMenu(self.makeMenu())

    def onFindLater(self, event):
        # Start the timer so that the actual filtering will be done
        # only when the user pauses typing (at least 0.5 second)
        self.__timer.Start(500, oneShot=True)

    def onFind(self, event):
        if self.__timer.IsRunning():
            self.__timer.Stop()
        if not self.IsEnabled():
            return
        searchString = self.GetValue()
        if searchString:
            self.rememberSearchString(searchString)
        self.ShowCancelButton(bool(searchString))
        self.__callback(searchString, self.__matchCase, self.__includeSubItems)

    def onCancel(self, event):
        self.SetValue('')
        self.onFind(event)
    
    def onMatchCaseMenuItem(self, event):
        self.__matchCase = self._isMenuItemChecked(event)
        self.SetMenu(self.makeMenu())
        self.onFind(event)
        
    def onIncludeSubItemsMenuItem(self, event):
        self.__includeSubItems = self._isMenuItemChecked(event)
        self.SetMenu(self.makeMenu())
        self.onFind(event)
        
    def onRecentSearchMenuItem(self, event):
        self.SetValue(self.__recentSearches[event.GetId()-1])
        self.onFind(event)
                
    def rememberSearchString(self, searchString):
        if searchString in self.__recentSearches:
            self.__recentSearches.remove(searchString)
        self.__recentSearches.insert(0, searchString)
        if len(self.__recentSearches) > self.__maxRecentSearches:
            self.__recentSearches.pop()
        self.SetMenu(self.makeMenu())
                
    def makeMenu(self):
        menu = wx.Menu()
        menu.AppendCheckItem(self.__matchCaseMenuItemId, _('Match case'), 
            _('Match case when filtering'))
        menu.Check(self.__matchCaseMenuItemId, self.__matchCase)
        menu.AppendCheckItem(self.__includeSubItemsMenuItemId, 
            _('Include sub items'), 
            _('Include sub items of matching items in the search results'))
        menu.Check(self.__includeSubItemsMenuItemId, self.__includeSubItems)
        if self.__recentSearches:
            self.addRecentSearches(menu)
        return menu
    
    def addRecentSearches(self, menu):
        menu.AppendSeparator()
        item = menu.Append(-1, _('Recent searches'))
        item.Enable(False)
        for index, searchString in enumerate(self.__recentSearches):
            menu.Append(index+1, searchString)
            
    def Enable(self, enable=True):
        ''' When wx.SearchCtrl is disabled it doesn't grey out the buttons,
            so we remove those. '''
        if enable:
            self.SetMenu(self.makeMenu())
        else:
            self.SetValue(_('Viewer not searchable'))
            self.SetMenu(None)
        super(SearchCtrl, self).Enable(enable)
        self.ShowCancelButton(enable and bool(self.GetValue()))
        self.ShowSearchButton(enable)
        
    def _isMenuItemChecked(self, event):
        # There's a bug in wxPython 2.8.3 on Windows XP that causes 
        # event.IsChecked() to return the wrong value in the context menu.
        # The menu on the main window works fine. So we first try to access the
        # context menu to get the checked state from the menu item itself.
        # This will fail if the event is coming from the window, but in that
        # case we can event.IsChecked() expect to work so we use that.
        try:
            return event.GetEventObject().FindItemById(event.GetId()).IsChecked()
        except AttributeError:
            return event.IsChecked()
        

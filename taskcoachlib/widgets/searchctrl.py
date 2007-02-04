import wx
from i18n import _

class SearchCtrl(wx.SearchCtrl):
    def __init__(self, *args, **kwargs):
        self.__callback = kwargs.pop('callback')
        self.__matchCase = kwargs.pop('matchCase', False)
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

    def onFindLater(self, event):
        # Start the timer so that the actual filtering will be done
        # only when the user pauses typing (at least 0.5 second)
        self.__timer.Start(500, oneShot=True)

    def onFind(self, event):
        if self.__timer.IsRunning():
            self.__timer.Stop()
        searchString = self.GetValue()
        if searchString:
            self.rememberSearchString(searchString)
        self.ShowCancelButton(bool(searchString))
        self.__callback(searchString, self.__matchCase)

    def onCancel(self, event):
        self.SetValue('')
        self.onFind(event)
    
    def onMatchCaseMenuItem(self, event):
        self.__matchCase = event.IsChecked()
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
        if self.__recentSearches:
            self.addRecentSearches(menu)
        return menu
    
    def addRecentSearches(self, menu):
        menu.AppendSeparator()
        item = menu.Append(-1, _('Recent searches'))
        item.Enable(False)
        for index, searchString in enumerate(self.__recentSearches):
            menu.Append(index+1, searchString)


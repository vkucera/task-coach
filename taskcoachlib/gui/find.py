import wx 
import widgets
from i18n import _

class FindPanel(wx.Panel):
    def __init__(self, parent, viewer, settings):
        super(FindPanel, self).__init__(parent)
        self.__viewer = viewer
        self.__settings = settings
        self._createComponents()
        self._bindEventHandlers()
        self._layout()
        
    def _createComponents(self):
        self.__timer = wx.Timer(self)

        self._subjectEntry = widgets.SingleLineTextCtrl(self, 
            _('Type search string (a regular expression) here and press enter'),
            style=wx.TE_PROCESS_ENTER)
        self._caseCheckBox = wx.CheckBox(self, -1, _('Match case'))
        self._clearButton = wx.Button(self, -1, _('Clear'))

    def _bindEventHandlers(self):
        for eventSource, eventType, eventHandler in \
            [(self, wx.EVT_TIMER, self.onFind),
             (self._subjectEntry, wx.EVT_TEXT_ENTER, self.onFind),
             (self._subjectEntry, wx.EVT_TEXT, self.onFindLater),
             (self._caseCheckBox, wx.EVT_CHECKBOX, self.onFind),
             (self._clearButton, wx.EVT_BUTTON, self.clear)]:
            eventSource.Bind(eventType, eventHandler)
        
    def _layout(self):
        verticalSizer = wx.BoxSizer(wx.VERTICAL)
        verticalSizer.Add(self._subjectEntry, flag=wx.EXPAND, proportion=1)
        horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontalSizer.Add(self._caseCheckBox, flag=wx.ALIGN_CENTER_VERTICAL)
        horizontalSizer.Add(self._clearButton, flag=wx.ALIGN_CENTER_VERTICAL)
        verticalSizer.Add(horizontalSizer)
        '''

        space = (10, 0)
        align = {'flag' : wx.ALIGN_CENTER_VERTICAL}
        for component, options in [ \
                (self._subjectEntry, {'proportion' : 1, 'flag' : wx.EXPAND}),
                (space, {}), (self._caseCheckBox, align), (space, {}),
                (self._clearButton, align)]:
            sizer.Add(component, **options)
        '''
        self.SetSizerAndFit(verticalSizer)        

    def onFindLater(self, event):
        # Start the timer so that the actual filtering will be done
        # only when the user pauses typing (at least 0.5 second)
        self.__timer.Start(500, oneShot=True)

    def onFind(self, event):
        if self.__timer.IsRunning():
            self.__timer.Stop()
        searchString = self._subjectEntry.GetValue()
        self.__settings.set('view', 'tasksearchfilterstring', searchString)
        self.__settings.set('view', 'tasksearchfiltermatchcase', str(self._caseCheckBox.GetValue()))
        if searchString:
            self.__viewer.expandAll()
        
    def clear(self, event=None):
        self._subjectEntry.SetValue('')
        self.onFind(event)

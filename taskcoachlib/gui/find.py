import wx 

class FindPanel(wx.Panel):
    def __init__(self, parent, searchFilter, viewer):
        super(FindPanel, self).__init__(parent, -1)
        self.searchFilter = searchFilter
        self.viewer = viewer
        self.createComponents()
        self.layout()
        
    def createComponents(self):
        self._label = wx.StaticText(self, -1, 'Find: ')
        
        self._subjectEntry = wx.TextCtrl(self, -1, 
            'Type search string (a regular expression) here and press enter')
        self._subjectEntry.Bind(wx.EVT_TEXT_ENTER, self.find)
        
        self._caseCheckBox = wx.CheckBox(self, -1, 'Match case')
        self._caseCheckBox.Bind(wx.EVT_CHECKBOX, self.find)
        
        self._clearButton = wx.Button(self, -1, 'Clear')
        self._clearButton.Bind(wx.EVT_BUTTON, self.clear)
        
    def layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        space = (10, 0)
        align = {'flag' : wx.ALIGN_CENTER_VERTICAL}
        for component, options in [(self._label, align),
                (self._subjectEntry, {'proportion' : 1, 'flag' : wx.EXPAND}),
                (space, {}), (self._caseCheckBox, align), (space, {}),
                (self._clearButton, align)]:
            sizer.Add(component, **options)
        self.SetSizerAndFit(sizer)        

    def find(self, event):
        self.searchFilter.setSubject(self._subjectEntry.GetValue())
        self.searchFilter.setMatchCase(self._caseCheckBox.GetValue())
        self.viewer.expandAll()
        
    def clear(self, event=None):
        self._subjectEntry.SetValue('')
        self.find(event)

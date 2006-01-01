import wx 
import widgets
from i18n import _

class FindPanel(wx.Panel):
    def __init__(self, parent, viewer, settings):
        super(FindPanel, self).__init__(parent, -1)
        self.__viewer = viewer
        self.__settings = settings
        self.createComponents()
        self.layout()
        
    def createComponents(self):
        self._label = wx.StaticText(self, -1, _('Find: '))
        
        self._subjectEntry = widgets.SingleLineTextCtrl(self, 
            _('Type search string (a regular expression) here and press enter'),
            style=wx.TE_PROCESS_ENTER)
        self._subjectEntry.Bind(wx.EVT_TEXT_ENTER, self.find)
        
        self._caseCheckBox = wx.CheckBox(self, -1, _('Match case'))
        self._caseCheckBox.Bind(wx.EVT_CHECKBOX, self.find)
        
        self._clearButton = wx.Button(self, -1, _('Clear'))
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
        searchString = self._subjectEntry.GetValue()
        self.__settings.set('view', 'tasksearchfilterstring', searchString)
        self.__settings.set('view', 'tasksearchfiltermatchcase', str(self._caseCheckBox.GetValue()))
        if searchString:
            self.__viewer.expandAll()
        
    def clear(self, event=None):
        self._subjectEntry.SetValue('')
        self.find(event)

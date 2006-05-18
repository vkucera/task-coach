import widgets, wx
from i18n import _ 

class CategoriesFilterPanel(wx.Panel):
    def __init__(self, taskList, settings, *args, **kwargs):
        super(CategoriesFilterPanel, self).__init__(*args, **kwargs)
        self.__taskList = taskList
        self.__settings = settings
        self.createInterior()
        self.layoutInterior()

    def createInterior(self):
        taskList = self.__taskList
        self._about = wx.StaticText(self,
            label='Show tasks that belong to the categories selected below.\n'
                'Unselect all categories to reset the filter.')
        self._checkListBox = wx.CheckListBox(self, style=wx.LB_SORT)
        self._checkListBox.InsertItems(list(taskList.categories()), 0)
        for category in taskList.categories():
            if category in taskList.filteredCategories():
                self._checkListBox.Check( \
                    self._checkListBox.FindString(category))
        self._radioBox = wx.RadioBox(self, majorDimension=1, 
            label=_('Show tasks that match'),
            choices=[_('any of the above selected categories'),
                     _('all of the above selected categories')])
        if settings.getboolean('view', 'taskcategoryfiltermatchall'):
            index = 1
        else:
            index = 0
        self._radioBox.SetSelection(index)

    def layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self._about, flag=wx.EXPAND|wx.ALL, border=5)
        panelSizer.Add(wx.StaticLine(self._interior), flag=wx.EXPAND)
        panelSizer.Add(self._checkListBox, proportion=1, flag=wx.EXPAND|wx.ALL, 
            border=5)
        panelSizer.Add(self._radioBox, flag=wx.ALL, border=5)
        self.SetSizer(panelSizer)

    def bindEventHandlers(self):
        self._checkListBox.Bind(wx.EVT_CHECKLISTBOX, self.onCheckCategory)
        self._radioBox.Bind(wx.EVT_RADIOBOX, self.onCheckMatchAll)

    def onCheckCategory(self, event):
        category = event.GetString()
        if event.IsChecked():
            self._taskList.addCategory(category)                
        else:
            self._taskList.removeCategory(category)

    def onCheckMatchAll(self, event):
        index = event.GetInt()
        setting = ['False', 'True'][index]
        self.__settings.set('view', 'taskcategoryfiltermatchall', setting)



class CategoriesFilterDialog(widgets.Dialog):
    def __init__(self, taskList, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self._taskList = taskList
        super(CategoriesFilterDialog, self).__init__(bitmap='category', 
            *args, **kwargs)
        
    def createInterior(self):
        return wx.Panel(self._panel)
        
    def fillInterior(self):
        self._about = wx.StaticText(self._interior, 
            label='Show tasks that belong to the categories selected below.\n'
                'Unselect all categories to reset the filter.')
        self._checkListBox = wx.CheckListBox(self._interior, style=wx.LB_SORT)
        self._checkListBox.InsertItems(list(self._taskList.categories()), 0)
        for category in self._taskList.categories():
            if category in self._taskList.filteredCategories():
                self._checkListBox.Check(self._checkListBox.FindString(category))
        self._radioBox = wx.RadioBox(self._interior, majorDimension=1, 
            label=_('Show tasks that match'),
            choices=[_('any of the above selected categories'),
                     _('all of the above selected categories')])
        if self.__settings.getboolean('view', 'taskcategoryfiltermatchall'):
            index = 1
        else:
            index = 0
        self._radioBox.SetSelection(index)
        self.layoutInterior()
        
    def layoutInterior(self):
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self._about, flag=wx.EXPAND|wx.ALL, border=5)
        panelSizer.Add(wx.StaticLine(self._interior), flag=wx.EXPAND)
        panelSizer.Add(self._checkListBox, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        panelSizer.Add(self._radioBox, flag=wx.ALL, border=5)
        self._interior.SetSizer(panelSizer)
        
    def ok(self, *args, **kwargs):
        for category in self._taskList.categories():
            if self._checkListBox.IsChecked(self._checkListBox.FindString(category)):
                self._taskList.addCategory(category)                
            else:
                self._taskList.removeCategory(category)
        matchAll = self._radioBox.GetSelection() == 1
        self.__settings.set('view', 'taskcategoryfiltermatchall', str(matchAll))
        super(CategoriesFilterDialog, self).ok(*args, **kwargs)

import widgets, wx
from i18n import _ 


class CategoriesFilterDialog(widgets.Dialog):
    def __init__(self, taskList, *args, **kwargs):
        self._settings = kwargs.pop('settings')
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
            if category in self.filteredCategories():
                self._checkListBox.Check(self._checkListBox.FindString(category))
        self._radioBox = wx.RadioBox(self._interior, majorDimension=1, 
            label=_('Show tasks that match'),
            choices=[_('any of the above selected categories'),
                     _('all of the above selected categories')])
        if self._settings.getboolean('view', 'taskcategoryfiltermatchall'):
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
        filteredCategories = self.filteredCategories()
        for category in self._taskList.categories():
            if self._checkListBox.IsChecked(self._checkListBox.FindString(category)):
                if category not in filteredCategories:
                    filteredCategories.append(category)   
            else:
                if category in filteredCategories:
                    filteredCategories.remove(category)
        self._settings.setlist('view', 'taskcategoryfilterlist', 
                               filteredCategories)
        matchAll = self._radioBox.GetSelection() == 1
        self._settings.set('view', 'taskcategoryfiltermatchall', str(matchAll))
        super(CategoriesFilterDialog, self).ok(*args, **kwargs)

    def filteredCategories(self):
        return self._settings.getlist('view', 'taskcategoryfilterlist')
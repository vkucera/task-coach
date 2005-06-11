import widgets, wx

class CategoriesFilterDialog(widgets.Dialog):
    def __init__(self, taskList, *args, **kwargs):
        self._taskList = taskList
        super(CategoriesFilterDialog, self).__init__(bitmap='category', *args, **kwargs)
        
    def createInterior(self):
        self._checkListBox = wx.CheckListBox(self._panel, -1)
        self._checkListBox.InsertItems(list(self._taskList.categories()), 0)
        for category in self._taskList.categories():
            if category not in self._taskList.filteredCategories():
                self._checkListBox.Check(self._checkListBox.FindString(category))
        return self._checkListBox
        
    def ok(self, *args, **kwargs):
        for category in self._taskList.categories():
            if self._checkListBox.IsChecked(self._checkListBox.FindString(category)):
                self._taskList.removeCategory(category)
            else:
                self._taskList.addCategory(category)
        super(CategoriesFilterDialog, self).ok(*args, **kwargs)
import test, gui, config, widgets
import domain.task as task

class CategoriesFilterPanelTest(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        self.filterSideBarFoldPanel = widgets.FoldPanelBar(self.frame)
        parent = self.filterSideBarFoldPanel.AddFoldPanel('Title', 
                                                          collapsed=False)
        self.panel = gui.filter.CategoriesFilterPanel(parent, self.taskList, 
                                                      self.settings)
        self.task = task.Task()

    def testCheckListBoxIsEmptyWhenNoCategories(self):
        self.assertEqual(0, self.panel._checkListBox.GetCount())
        
    def testCheckListBoxContainsCategoryAfterAddingTaskWithCategory(self):
        self.task.addCategory('Category')
        self.taskList.append(self.task)
        self.assertEqual('Category', self.panel._checkListBox.GetString(0))
        
    def testCategoryIsRemovedFromCheckListBoxWhenTaskWithCategoryIsRemoved(self):
        self.task.addCategory('Category')
        self.taskList.append(self.task)
        self.taskList.remove(self.task)
        self.assertEqual(0, self.panel._checkListBox.GetCount())
        
    def testCategoryIsAddedToCheckListBoxWhenCategoryIsAddedToTask(self):
        self.taskList.append(self.task)
        self.task.addCategory('Category')
        self.assertEqual('Category', self.panel._checkListBox.GetString(0))
        
    def testCategoryIsRemovedFromCheckListBoxWhenCategoryIsRemovedFromTask(self):
        self.taskList.append(self.task)
        self.task.addCategory('Category')
        self.task.removeCategory('Category')
        self.assertEqual(0, self.panel._checkListBox.GetCount())
        
    def testFilterOnCategory(self):
        self.taskList.append(self.task)
        self.task.addCategory('Category')
        self.settings.setlist('view', 'taskcategoryfilterlist', ['Category'])
        self.failUnless(self.panel._checkListBox.IsChecked(0))
        
    def testSetFilterThroughCheckListBox(self):
        self.taskList.append(self.task)
        self.task.addCategory('Category')
        self.panel._checkListBox.Check(0)
        import wx
        event = wx.CommandEvent(wx.wxEVT_COMMAND_CHECKLISTBOX_TOGGLED)
        event.SetInt(0)
        self.panel._checkListBox.ProcessEvent(event)
        self.assertEqual(['Category'], self.settings.getlist('view', 'taskcategoryfilterlist'))
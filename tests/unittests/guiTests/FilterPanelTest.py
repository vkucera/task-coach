import test, gui, config, widgets
import domain.category as category
try:
    import wx.lib.customtreectrl as customtree # for wxPython >= 2.7.1
except ImportError:
    import thirdparty.CustomTreeCtrl as customtree # for wxPython < 2.7.1


class CategoriesFilterPanelTest(test.wxTestCase):
    def setUp(self):
        self.categories = category.CategoryList()
        self.settings = config.Settings(load=False)
        self.filterSideBarFoldPanel = widgets.FoldPanelBar(self.frame)
        parent = self.filterSideBarFoldPanel.AddFoldPanel('Title', 
                                                          collapsed=False)
        self.panel = gui.filter.CategoriesFilterPanel(parent, self.categories, 
                                                      self.settings)
        self.category = category.Category('category')

    def testCheckTreeIsEmptyWhenNoCategories(self):
        self.assertEqual(0, self.panel._treeCtrl.GetCount())
        
    def testCategoryDisplayedAfterAddingCategory(self):
        self.categories.append(self.category)
        self.assertEqual(self.category.subject(), 
                         self.panel._treeCtrl[0].GetText())
      
    def testCategoryIsNotDisplayedWhenCategoryIsRemoved(self):
        self.categories.append(self.category)
        self.categories.remove(self.category)
        self.assertEqual(0, self.panel._treeCtrl.GetCount())
         
    def testFilterOnCategory(self):
        self.categories.append(self.category)
        self.category.setFiltered()
        self.failUnless(self.panel._treeCtrl[0].IsChecked())
        
    def testSetFilterThroughCheckTreeCtrl(self):
        self.categories.append(self.category)
        self.panel._treeCtrl[0].Check()
        event = customtree.CommandTreeEvent(customtree.wxEVT_TREE_ITEM_CHECKED, 0)
        event.SetItem(self.panel._treeCtrl[0])
        self.panel._treeCtrl.ProcessEvent(event)
        self.failUnless(self.category.isFiltered())
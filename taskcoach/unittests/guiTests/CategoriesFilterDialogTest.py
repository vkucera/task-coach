import test, gui, config
from domain import task

class CategoriesFilterDialogTest(test.wxTestCase):
    def setUp(self):
        aTask = task.Task()
        aTask.addCategory('test')
        taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        self.filter = task.filter.CategoryFilter(taskList, settings=self.settings)
        taskList.append(aTask)
        self.dialog = gui.CategoriesFilterDialog(parent=self.frame,
            title='View categories', taskList=self.filter, settings=self.settings)
            
    def testFilterOnCategory(self):
        self.dialog._checkListBox.Check(0)
        self.dialog.ok()
        self.failUnless('test' in self.filter.filteredCategories())
        
    def testFilteredCategoriesAreDisplayedCorrectly(self):
        self.failIf(self.dialog._checkListBox.IsChecked(0))
        
    def testFilterOnAllCategoriesIsDisplayedCorrectly(self):
        self.assertEqual(1, self.dialog._radioBox.GetSelection())
        
    def testFilterOnAnyCategoryIsProcessedCorrectly(self):
        self.dialog._radioBox.SetSelection(0)
        self.dialog.ok()
        self.failIf(self.settings.getboolean('view', 'taskcategoryfiltermatchall'))
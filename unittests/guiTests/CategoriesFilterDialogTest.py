import test, gui
from domain import task

class CategoriesFilterDialogTest(test.wxTestCase):
    def setUp(self):
        aTask = task.Task()
        aTask.addCategory('test')
        taskList = task.TaskList()
        self.filter = task.filter.CategoryFilter(taskList)
        taskList.append(aTask)
        self.dialog = gui.CategoriesFilterDialog(parent=self.frame,
            title='View categories', taskList=self.filter)
            
    def testFilterOnCategory(self):
        self.dialog._checkListBox.Check(0)
        self.dialog.ok()
        self.failUnless('test' in self.filter.filteredCategories())
        
    def testFilteredCategoriesAreDisplayedCorrectly(self):
        self.failIf(self.dialog._checkListBox.IsChecked(0))
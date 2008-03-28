'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import test, wx, gui, config
from domain import task, effort, category, note, date
from unittests import dummy

class UICommandTest(test.wxTestCase):
    def setUp(self):
        self.uicommand = dummy.DummyUICommand(menuText='undo', bitmap='undo')
        self.menu = wx.Menu()
        self.frame = wx.Frame(None)
        self.frame.Show(False)
        self.frame.SetMenuBar(wx.MenuBar())
        self.frame.CreateToolBar()

    def activate(self, window, id):
        window.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, id))

    def testAppendToMenu(self):
        id = self.uicommand.appendToMenu(self.menu, self.frame)
        self.assertEqual(id, self.menu.FindItem(self.uicommand.menuText))

    def testAppendToToolBar(self):
        id = self.uicommand.appendToToolBar(self.frame.GetToolBar())
        self.assertEqual(0, self.frame.GetToolBar().GetToolPos(id))

    def testActivationFromMenu(self):
        id = self.uicommand.appendToMenu(self.menu, self.frame)
        self.activate(self.frame, id)
        self.failUnless(self.uicommand.activated)

    def testActivationFromToolBar(self):
        id = self.uicommand.appendToToolBar(self.frame.GetToolBar())
        self.activate(self.frame.GetToolBar(), id)
        self.failUnless(self.uicommand.activated)


class NewTaskWithSelectedCategoryTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.viewerContainer = gui.viewercontainer.ViewerContainer(self.frame, 
            self.settings, 'mainviewer')         
        self.uiCommands = gui.uicommand.UICommands(self.frame, None, 
            self.viewerContainer, self.settings, self.taskList, 
            self.effortList, self.categories, note.NoteContainer())
        self.categories.append(category.Category('cat'))
        self.viewer = gui.viewer.CategoryViewer(self.frame, self.categories, 
            self.uiCommands, self.settings)
        
    def createNewTask(self):
        taskNew = gui.uicommand.NewTaskWithSelectedCategories(taskList=self.taskList,
                                                viewer=self.viewer,
                                                categories=self.categories)
        dialog = taskNew.doCommand(None, show=False)
        tree = dialog[0][2]._treeCtrl
        return tree.GetFirstChild(tree.GetRootItem())[0]

    def selectFirstCategory(self):
        tree = self.viewer.widget
        tree.SelectItem(tree.GetFirstChild(tree.GetRootItem())[0])

    def testNewTaskWithSelectedCategory(self):
        self.selectFirstCategory()
        firstCategoryInTaskDialog = self.createNewTask()
        self.failUnless(firstCategoryInTaskDialog.IsChecked())
        
    def testNewTaskWithoutSelectedCategory(self):
        firstCategoryInTaskDialog = self.createNewTask()
        self.failIf(firstCategoryInTaskDialog.IsChecked())


class MailTaskTest(test.TestCase):
    def testCreate(self):
        mailTask = gui.uicommand.TaskMail()


class DummyViewer(object):
    def __init__(self, selection=None):
        self.selection = selection or []
        
    def curselection(self):
        return self.selection
    
    def isShowingTasks(self):
        return True
    
    
class MarkCompletedTest(test.TestCase):
    def assertMarkCompletedIsEnabled(self, selection, shouldBeEnabled=True):
        viewer = DummyViewer(selection)
        markCompleted = gui.uicommand.TaskToggleCompletion(viewer=viewer)
        isEnabled = markCompleted.enabled(None)
        if shouldBeEnabled:
            self.failUnless(isEnabled)
        else:
            self.failIf(isEnabled)
            
    def testNotEnabledWhenSelectionIsEmpty(self):
        self.assertMarkCompletedIsEnabled(selection=[], shouldBeEnabled=False)
        
    def testEnabledWhenSelectedTaskIsNotCompleted(self):
        self.assertMarkCompletedIsEnabled(selection=[task.Task()])
        
    def testEnabledWhenSelectedTaskIsCompleted(self):
        self.assertMarkCompletedIsEnabled(
            selection=[task.Task(completionDate=date.Today())])
        
    def testNotEnabledWhenSelectedTasksAreBothCompletedAndUncompleted(self):
        self.assertMarkCompletedIsEnabled(
            selection=[task.Task(completionDate=date.Today()), task.Task()], 
            shouldBeEnabled=False)
        
        
class TaskNewTest(test.TestCase):
    def testNewTaskWithCategories(self):
        cat = category.Category('cat', filtered=True)
        categories = category.CategoryList([cat])
        taskNew = gui.uicommand.TaskNew(taskList=task.TaskList(), 
                                        categories=categories)
        dialog = taskNew.doCommand(None, show=False)
        tree = dialog[0][2]._treeCtrl
        firstChild, cookie = tree.GetFirstChild(tree.GetRootItem())
        self.failUnless(firstChild.IsChecked())
        

class NoteNewTest(test.TestCase):
    def testNewNoteWithCategories(self):
        cat = category.Category('cat', filtered=True)
        categories = category.CategoryList([cat])
        noteNew = gui.uicommand.NoteNew(notes=note.NoteContainer(), 
                                        categories=categories)
        dialog = noteNew.doCommand(None, show=False)
        tree = dialog[0][1]._treeCtrl
        firstChild, cookie = tree.GetFirstChild(tree.GetRootItem())
        self.failUnless(firstChild.IsChecked())

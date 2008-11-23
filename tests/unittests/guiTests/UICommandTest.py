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

import wx
import test
from unittests import dummy
from taskcoachlib import gui, config, persistence
from taskcoachlib.domain import task, effort, category, note, date


class UICommandTest(test.wxTestCase):
    def setUp(self):
        super(UICommandTest, self).setUp()
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


class wxTestCaseWithFrameAsTopLevelWindow(test.wxTestCase):
    def setUp(self):
        wx.GetApp().SetTopWindow(self.frame)
        self.frame.taskFile = persistence.TaskFile()
        

class NewTaskWithSelectedCategoryTest(wxTestCaseWithFrameAsTopLevelWindow):
    def setUp(self):
        super(NewTaskWithSelectedCategoryTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = self.frame.taskFile = persistence.TaskFile()
        self.categories = self.taskFile.categories()
        self.categories.append(category.Category('cat'))
        self.viewer = gui.viewer.CategoryViewer(self.frame, self.taskFile, 
                                                self.settings)
        
    def createNewTask(self):
        taskNew = gui.uicommand.NewTaskWithSelectedCategories(taskList=self.taskFile.tasks(),
                                                viewer=self.viewer,
                                                categories=self.categories,
                                                settings=self.settings)
        dialog = taskNew.doCommand(None, show=False)
        tree = dialog[0][2]._categoryViewer.widget
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
    def testException(self):
        class DummyTask(object):
            def subject(self, *args, **kwargs):
                return 'subject'
            def description(self):
                return 'description'
        class DummyViewer(object):
            def curselection(self):
                return [DummyTask()]
        def mail(*args):
            raise RuntimeError, 'message'
        def showerror(*args, **kwargs):
            self.showerror = args
        mailTask = gui.uicommand.TaskMail(viewer=DummyViewer())
        mailTask.doCommand(None, mail=mail, showerror=showerror)
        self.assertEqual('Cannot send email:\nmessage', self.showerror[0])


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



class TaskNewTest(wxTestCaseWithFrameAsTopLevelWindow):
    def testNewTaskWithCategories(self):
        settings = config.Settings(load=False)
        cat = category.Category('cat', filtered=True)
        self.frame.taskFile.categories().append(cat)
        taskNew = gui.uicommand.TaskNew(taskList=self.frame.taskFile.tasks(), 
                                        settings=settings)
        dialog = taskNew.doCommand(None, show=False)
        tree = dialog[0][2]._categoryViewer.widget
        firstChild, cookie = tree.GetFirstChild(tree.GetRootItem())
        self.failUnless(firstChild.IsChecked())
        

class NoteNewTest(wxTestCaseWithFrameAsTopLevelWindow):
    def testNewNoteWithCategories(self):        
        cat = category.Category('cat', filtered=True)
        self.frame.taskFile.categories().append(cat)
        noteNew = gui.uicommand.NoteNew(notes=self.frame.taskFile.notes(), 
                                        settings=config.Settings(load=False))
        dialog = noteNew.doCommand(None, show=False)
        tree = dialog[0][1]._categoryViewer.widget
        firstChild, cookie = tree.GetFirstChild(tree.GetRootItem())
        self.failUnless(firstChild.IsChecked())


class MailNoteTest(test.TestCase):
    def testCreate(self):
        mailNote = gui.uicommand.NoteMail()


class EditPreferencesTest(test.TestCase):
    def testEditPreferences(self):
        self.settings = config.Settings(load=False)
        editPreferences = gui.uicommand.EditPreferences(settings=self.settings)
        editPreferences.doCommand(None, show=False)
        # No assert, just checking whether it works without exceptions
        
        
class EffortViewerAggregationChoiceTest(test.TestCase):
    def setUp(self):
        self.selectedAggregation = 'details'
        self.showAggregationCalled = False
        self.choice = gui.uicommand.EffortViewerAggregationChoice(viewer=self)
        self.choice.currentChoice = 0
        class DummyEvent(object):
            def __init__(self, selection):
                self.selection = selection
            def GetInt(self):
                return self.selection
        self.DummyEvent = DummyEvent
        
    def showEffortAggregation(self, aggregation):
        self.selectedAggregation = aggregation
        self.showAggregationCalled = True
    
    def testUserPicksCurrentChoice(self):
        self.choice.onChoice(self.DummyEvent(0))
        self.failIf(self.showAggregationCalled)

    def testUserPicksSameChoiceTwice(self):
        self.choice.onChoice(self.DummyEvent(1))
        self.showAggregationCalled = False
        self.choice.onChoice(self.DummyEvent(1))
        self.failIf(self.showAggregationCalled)
    
    def testUserPicksEffortPerDay(self):
        self.choice.onChoice(self.DummyEvent(1))
        self.assertEqual('day', self.selectedAggregation)

    def testUserPicksEffortPerWeek(self):
        self.choice.onChoice(self.DummyEvent(2))
        self.assertEqual('week', self.selectedAggregation)

    def testUserPicksEffortPerMonth(self):
        self.choice.onChoice(self.DummyEvent(3))
        self.assertEqual('month', self.selectedAggregation)

    def testSetChoice(self):
        class DummyToolBar(wx.Frame):
            def AddControl(self, *args, **kwargs):
                pass
        self.choice.appendToToolBar(DummyToolBar(None))
        self.choice.setChoice('week')
        self.assertEqual('Effort per week',
                         self.choice.choiceCtrl.GetStringSelection())
        self.assertEqual(2, self.choice.currentChoice)


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

import test, gui, widgets, TaskTreeViewerTest, TaskListViewerTest
from unittests import dummy
from gui import render
from domain import task, date, effort, category, note

class TaskTreeListViewerUnderTest(gui.viewer.TaskTreeListViewer):
    def createWidgetWithColumns(self):
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemImage, self.getItemAttr, self.getItemId,
            self.getRootIndices, self.getChildIndices,
            self.onSelect, dummy.DummyUICommand())
        widget.AssignImageList(self.createImageList())
        return widget

class TaskTreeListViewerTest(TaskTreeViewerTest.CommonTests,
                             TaskListViewerTest.CommonTests,
                             TaskTreeViewerTest.TaskTreeViewerTestCase):
    def setUp(self):
        super(TaskTreeListViewerTest, self).setUp()
        effortList = effort.EffortList(self.taskList)
        viewerContainer = gui.viewercontainer.ViewerContainer(\
            widgets.Notebook(self.frame), self.settings, 'mainviewer')
        self.viewer = TaskTreeListViewerUnderTest(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                viewerContainer, self.settings, self.taskList, effortList, 
                self.categories, note.NoteContainer()), 
            self.settings, categories=self.categories)
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending()
          
    def testOneDayLeft(self):
        self.showColumn('timeLeft')
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        firstItem, cookie = self.viewer.widget.GetFirstChild(self.viewer.widget.GetRootItem())
        self.assertEqual(render.daysLeft(self.task.timeLeft(), False), 
            self.viewer.widget.GetItemText(firstItem, 3))
        
    def testReverseSortOrderWithGrandchildren(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        grandchild = task.Task(subject='grandchild')
        child.addChild(grandchild)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.setSortOrderAscending(False)
        self.assertItems(task2, (self.task, 1), (child, 1), grandchild)
                
    def testReverseSortOrder(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task(subject='zzz')
        self.taskList.extend([self.task, task2])
        self.viewer.setSortOrderAscending(False)
        self.assertItems(task2, (self.task, 1), child)

    def testSortByDueDate(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task('zzz')
        child2 = task.Task('child 2')
        task2.addChild(child2)
        self.taskList.extend([self.task, task2])
        self.assertItems((self.task, 1), child, (task2, 1), child2)
        child2.setDueDate(date.Today())
        self.viewer.sortBy('dueDate')
        self.assertItems((task2, 1), child2, (self.task, 1), child)
        


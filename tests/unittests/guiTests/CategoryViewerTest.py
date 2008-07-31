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

import test
from unittests import dummy
from taskcoachlib import gui, config, widgets
from taskcoachlib.domain import task, effort, category, note


class CategoryViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.viewer = gui.viewer.CategoryViewer(self.frame, self.categories, 
            gui.uicommand.UICommands(None, 
                gui.viewercontainer.ViewerContainer(widgets.Notebook(self.frame), 
                    self.settings, 'mainviewer'), 
                None, self.taskList,
                self.effortList, self.categories, note.NoteContainer()), 
            self.settings)
        
    def addTwoCategories(self):
        cat1 = category.Category('1')
        cat2 = category.Category('2')
        self.categories.extend([cat2, cat1])
        return cat1, cat2
        
    def testInitialSize(self):
        self.assertEqual(0, self.viewer.size())

    def testCopyCategoryWithChildren(self):
        parent, child = self.addTwoCategories()
        parent.addChild(child)
        copy = parent.copy()
        self.categories.append(copy)
        self.viewer.expandAll()
        self.assertEqual(4, self.viewer.size())

    def testSortInWidget(self):
        self.addTwoCategories()
        widget = self.viewer.widget
        for item, cat in zip(widget.GetItemChildren(), self.viewer.model()):
            self.assertEqual(cat.subject(), widget.GetItemText(item))
            
    def testSelectAll(self):
        self.addTwoCategories()
        self.viewer.widget.SelectItem(self.viewer.widget.GetFirstVisibleItem())
        self.viewer.selectall()
        self.assertEqual(2, len(self.viewer.curselection()))
        
    def testInvertSelection(self):
        self.addTwoCategories()
        self.viewer.invertselection()
        self.assertEqual(2, len(self.viewer.curselection()))

        

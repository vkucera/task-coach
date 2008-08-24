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
from taskcoachlib import gui, widgets, config
from taskcoachlib.domain import category, task, effort
    
       
class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        super(TreeViewerTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.taskList = task.sorter.Sorter(task.TaskList())
        self.effortList = effort.EffortList(self.taskList)
        self.viewer = gui.viewer.TaskTreeListViewer(self.frame, self.taskList,
            self.settings, categories=self.categories, efforts=self.effortList)
        self.expansionContext = self.viewer.settingsSection()
        self.parent = task.Task('parent')
        self.child = task.Task('child')
        self.parent.addChild(self.child)
        self.child.setParent(self.parent)
        self.taskList.extend([self.parent, self.child])
        self.viewer.refresh()
        self.widget = self.viewer.widget
                
    def testWidgetDisplayAllItems(self):
        self.assertEqual(2, self.viewer.widget.GetCount())
        
    def testExpand(self):
        self.widget.Expand(self.widget.GetFirstVisibleItem())
        self.failUnless(self.parent.isExpanded(context=self.expansionContext))
        
    def testCollapse(self):
        firstVisibleItem = self.widget.GetFirstVisibleItem()
        self.widget.Expand(firstVisibleItem)
        self.widget.Collapse(firstVisibleItem)
        self.failIf(self.parent.isExpanded(context=self.expansionContext))
        

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
from taskcoachlib.domain import category, task, note, effort
    
       
class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.taskList = task.sorter.Sorter(task.TaskList())
        notebook = widgets.Notebook(self.frame)
        self.viewerContainer = gui.viewercontainer.ViewerContainer(notebook, 
            self.settings, 'mainviewer')
        self.viewer = gui.viewer.TaskTreeViewer(notebook,
            self.taskList, gui.uicommand.UICommands(None, 
                self.viewerContainer, self.settings, self.taskList, 
                effort.EffortList(self.taskList), self.categories, self.notes), 
            self.settings, categories=self.categories)
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
        self.failUnless(self.parent.isExpanded())
        
    def testCollapse(self):
        firstVisibleItem = self.widget.GetFirstVisibleItem()
        self.widget.Expand(firstVisibleItem)
        self.widget.Collapse(firstVisibleItem)
        self.failIf(self.parent.isExpanded())
        

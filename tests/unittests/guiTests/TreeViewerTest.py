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

import wx, test, gui, widgets, config
from domain import category, task, note, effort
    
       
class TreeViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.taskList = task.sorter.Sorter(task.TaskList())
        self.viewerContainer = gui.viewercontainer.ViewerNotebook(self.frame, 
            self.settings, 'mainviewer')
        self.viewer = gui.viewer.TaskTreeViewer(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                self.viewerContainer, self.settings, self.taskList, 
                effort.EffortList(self.taskList), self.categories, self.notes), 
            self.settings, categories=self.categories)
        self.parent = task.Task('parent')
        self.child = task.Task('child')
        self.parent.addChild(self.child)
        self.child.setParent(self.parent)
        self.taskList.extend([self.parent, self.child])
        
    def testExpand(self):
        self.viewer.refresh()
        widget = self.viewer.widget
        widget.Expand(widget.GetFirstVisibleItem())
        self.failUnless(self.parent.isExpanded())
        
    def testCollapse(self):
        self.viewer.refresh()
        widget = self.viewer.widget
        widget.Expand(widget.GetFirstVisibleItem())
        widget.Collapse(widget.GetFirstVisibleItem())
        self.failIf(self.parent.isExpanded())

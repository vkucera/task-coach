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
from taskcoachlib import gui, config, widgets
from taskcoachlib.domain import task, effort, category, note


class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        
    def testCreate(self):
        effortViewer = gui.viewer.EffortListViewer(self.frame, self.effortList, 
            gui.uicommand.UICommands(None, 
                gui.viewercontainer.ViewerContainer(widgets.Notebook(self.frame), 
                    self.settings, 'mainviewer'), 
                self.settings, self.taskList, self.effortList, 
                category.CategoryList(), note.NoteContainer()), 
                self.settings, taskList=self.taskList)
        self.assertEqual(0, effortViewer.size())

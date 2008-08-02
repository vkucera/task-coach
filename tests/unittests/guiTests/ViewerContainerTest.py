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
from taskcoachlib import gui, config, widgets
from taskcoachlib.domain import task, effort, category, note


class ViewerContainerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList())
        notebook = widgets.Notebook(self.frame)
        self.container = gui.viewercontainer.ViewerContainer(notebook, 
            self.settings, 'mainviewer')
        self.container.addViewer(dummy.ViewerWithDummyWidget(notebook,
            self.taskList, None, 
            self.settings, settingsSection='bla'), 'Dummy')

    def testCreate(self):
        self.assertEqual(0, self.container.size())

    def testAddTask(self):
        self.taskList.append(task.Task())
        self.assertEqual(1, self.container.size())

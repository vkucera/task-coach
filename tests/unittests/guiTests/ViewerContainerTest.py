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
from taskcoachlib import gui, config, widgets, patterns
from taskcoachlib.domain import task, effort, category, note


class DummyEvent(object):
    def __init__(self, selection=0):
        self.__selection = selection
    
    def GetSelection(self):
        return self.__selection
        
    Selection = property(GetSelection)

    def Skip(self):
        pass


class ViewerContainerTest(test.wxTestCase):
    def setUp(self):
        self.events = []
        self.settings = config.Settings(load=False)
        self.settings.set('view', 'viewerwithdummywidgetcount', '2', new=True)
        self.taskList = task.sorter.Sorter(task.TaskList())
        self.notebook = widgets.Notebook(self.frame)
        self.container = gui.viewercontainer.ViewerContainer(self.notebook, 
            self.settings, 'mainviewer')
        self.viewer1 = self.createViewer()
        self.container.addViewer(self.viewer1, 'Dummy 1')
        self.viewer2 = self.createViewer()
        self.container.addViewer(self.viewer2, 'Dummy 2')

    def createViewer(self):
        return dummy.ViewerWithDummyWidget(self.notebook,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                self.container, self.settings, self.taskList, 
                effort.EffortList(self.taskList), category.CategoryList(), 
                note.NoteContainer()), 
            self.settings, settingsSection='bla')
            
    def onEvent(self, event):
        self.events.append(event)
    
    def testCreate(self):
        self.assertEqual(0, self.container.size())

    def testAddTask(self):
        self.taskList.append(task.Task())
        self.assertEqual(1, self.container.size())
        
    def testChangePage_ChangesActiveViewer(self):
        self.container.onPageChanged(DummyEvent(1))
        self.assertEqual(self.viewer2, self.container.activeViewer())

    def testChangePage_SavesActiveViewerInSettings(self):
        self.container.onPageChanged(DummyEvent(1))
        self.assertEqual(1, self.settings.getint('view', 'mainviewer'))

    def testChangePage_NotifiesObserversAboutNewActiveViewer(self):
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType=self.container.viewerChangeEventType())
        self.container.onPageChanged(DummyEvent(1))
        self.failUnless(self.events)
        
    def testCloseViewer_RemovesViewerFromContainer(self):
        self.container.onPageClosed(DummyEvent())
        self.assertEqual([self.viewer2], self.container.viewers)
        
    def testCloseViewer_RemovesViewerFromSettings(self):
        self.container.onPageClosed(DummyEvent())
        self.assertEqual(1, self.settings.getint('view', 
            'viewerwithdummywidgetcount'))
        
    def testCloseViewer_ChangesActiveViewer(self):
        self.container.onPageChanged(DummyEvent(1))
        self.container.onPageClosed(DummyEvent())
        self.assertEqual(self.viewer2, self.container.activeViewer())
        
    def testCloseViewer_SavesActiveViewerInSettings(self):
        self.container.onPageChanged(DummyEvent(1))
        self.container.onPageClosed(DummyEvent())
        self.assertEqual(0, self.settings.getint('view', 'mainviewer'))

    def testCloseViewer_NotifiesObserversAboutNewActiveViewer(self):
        self.container.onPageChanged(DummyEvent(1))
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType=self.container.viewerChangeEventType())
        self.container.onPageClosed(DummyEvent())
        self.failUnless(self.events)


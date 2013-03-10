'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import persistence, config
from taskcoachlib.domain import task, category
from unittests import dummy
import test, os
from taskcoachlib.changes import ChangeMonitor
    
    
class DummyTaskStore(persistence.TaskStore):
    def __init__(self, *args, **kwargs):
        self.saveCalled = 0
        self.throw = False
        super(DummyTaskStore, self).__init__(*args, **kwargs)

    def exists(self, *args, **kwargs):  # pylint: disable=W0613
        return True

    def saveSession(self, *args, **kwargs):
        if kwargs.get('doNotify', True):
            self.saveCalled += 1
        super(DummyTaskStore, self).saveSession(*args, **kwargs)

    def loadSession(self, guid):
        if self.throw:
            raise IOError('error')
        return super(DummyTaskStore, self).loadSession(guid)


class AutoSaverTestCase(test.TestCase):
    def setUp(self):
        super(AutoSaverTestCase, self).setUp()
        self.taskStore = DummyTaskStore(self.settings)
        self.autoSaver = persistence.AutoSaver(self.settings)

        file('filetomerge.tsk', 'wb').write('<?xml version="1.0" encoding="UTF-8" ?><tasks><task subject="foo" /></tasks>')

    def tearDown(self):
        super(AutoSaverTestCase, self).tearDown()
        self.taskStore.close()
        self.taskStore.stop()
        del self.autoSaver # Make sure AutoSaver is not observing task files
        os.remove('filetomerge.tsk')
        if os.path.exists('newfilename.tsk'):
            os.remove('newfilename.tsk')
            os.remove('newfilename.tsk.delta')
        
    def testCreate(self):
        self.failIf(self.taskStore.saveCalled)
        
    def testFileChanged_ButAutoSaveOff(self):
        self.settings.set('file', 'autosave', 'False')
        self.taskStore.loadSession('whatever')
        self.taskStore.tasks().append(task.Task())
        self.autoSaver.on_idle(dummy.Event())
        self.failIf(self.taskStore.saveCalled)
     
    def testFileChanged(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskStore.loadSession('whatever')
        self.taskStore.tasks().append(task.Task())
        self.autoSaver.on_idle(dummy.Event())
        self.assertEqual(1, self.taskStore.saveCalled)

    def testSaveAsDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskStore.loadSession('whatever')
        self.taskStore.saveas('newfilename.tsk')
        self.autoSaver.on_idle(dummy.Event())
        self.assertEqual(1, self.taskStore.saveCalled)
           
    def testCloseDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskStore.loadSession('whatever')
        self.taskStore.tasks().append(task.Task())
        self.autoSaver.on_idle(dummy.Event())
        self.taskStore.clear()
        self.assertEqual(1, self.taskStore.saveCalled)
     
    def testLoadDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskStore.loadSession('whatever')
        self.autoSaver.on_idle(dummy.Event())
        self.failIf(self.taskStore.saveCalled)

    def testLoadWithExceptionDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskStore.throw = True
        try:
            self.taskStore.loadSession('whatever')
        except IOError:
            pass
        self.autoSaver.on_idle(dummy.Event())
        self.failIf(self.taskStore.saveCalled)
     
    def testMergeDoesTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskStore.loadSession('whatever')
        self.taskStore.merge('filetomerge.tsk')
        self.autoSaver.on_idle(dummy.Event())
        self.assertEqual(1, self.taskStore.saveCalled)

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

import test
from taskcoachlib import persistence, config
from taskcoachlib.domain import date, task


class DummyFile(object):
    encoding = 'utf-8'
    name = 'whatever.tsk'
    
    def close(self, *args, **kwargs): # pylint: disable=W0613
        pass

    def write(self, *args, **kwargs): # pylint: disable=W0613
        pass
    
    
class DummyTaskStore(persistence.TaskStore):
    def _openForRead(self, *args, **kwargs): # pylint: disable=W0613
        return DummyFile()
        
    def _openForWrite(self, *args, **kwargs): # pylint: disable=W0613
        return None, DummyFile()
    
    def _read(self, *args, **kwargs): # pylint: disable=W0613
        return [task.Task()], [], [], dict(), None
    
    def exists(self):
        return True
    
    def filename(self):
        return super(DummyTaskStore, self).filename() or 'whatever.tsk'


class AutoBackupTest(test.TestCase):
    # pylint: disable=E1101,E1002,W0232
    def setUp(self):
        super(AutoBackupTest, self).setUp()
        self.taskStore = DummyTaskStore()
        self.backup = persistence.AutoBackup(self.settings, copyfile=self.onCopyFile)
        self.copyCalled = False

    def tearDown(self):
        super(AutoBackupTest, self).tearDown()
        self.taskStore.close()
        self.taskStore.stop()

    def onCopyFile(self, *args): # pylint: disable=W0613
        self.copyCalled = True

    def oneBackupFile(self):
        return [self.backup.backupFilename(self.taskStore)]

    def fourBackupFiles(self):
        files = [self.backup.backupFilename(self.taskStore),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2001,1,1,1,1,1)),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2002,1,1,1,1,1)),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2000,1,1,1,1,1))]
        files.sort()
        return files

    def fiveBackupFiles(self):
        files = [self.backup.backupFilename(self.taskStore),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2001,1,1,1,1,1)),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2002,1,1,1,1,1)),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2002,1,1,1,1,2)),
                 self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2000,1,1,1,1,1))]
        files.sort()
        return files

    def globMany(self, pattern): # pylint: disable=W0613
        return self.manyBackupFiles()
    
    def manyBackupFiles(self):
        files = [self.backup.backupFilename(self.taskStore)]*100 + \
            [self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2000,1,1,1,1,1))]
        files.sort()
        return files
        
    def testNoBackupFiles(self):
        self.assertEqual([], self.backup.backupFiles(self.taskStore, glob=lambda pattern: []))

    def testOneBackupFile(self):
        self.assertEqual(['1'], self.backup.backupFiles(self.taskStore, glob=lambda pattern: ['1']))
        
    def testNotTooManyBackupFiles(self):
        self.assertEqual(0, self.backup.numberOfExtraneousBackupFiles(self.oneBackupFile()))

    def testTooManyBackupFiles_(self):    
        self.assertEqual(86, self.backup.numberOfExtraneousBackupFiles(self.manyBackupFiles()))

    def testRemoveExtraneousBackFiles(self):
        self.backup.maxNrOfBackupFilesToRemoveAtOnce = 100
        removedFiles = []
        def remove(filename):
            removedFiles.append(filename)
        self.backup.removeExtraneousBackupFiles(self.taskStore, remove=remove, glob=self.globMany)
        self.assertEqual(86, len(removedFiles))
                
    def testRemoveExtraneousBackFiles_OSError(self):
        def remove(filename): # pylint: disable=W0613
            raise OSError
        self.backup.removeExtraneousBackupFiles(self.taskStore, remove=remove, glob=self.globMany)

    def testBackupFilename(self):
        now = date.DateTime(2004,1,1)
        self.assertEqual('whatever.20040101-000000.tsk.bak', 
            self.backup.backupFilename(self.taskStore, lambda: now)) # pylint: disable=W0212
        
    def testBackupFilenameOfBackupFilename(self):
        self.taskStore.setFilename('whatever.20040101-000000.tsk.bak')
        now = date.DateTime(2004,1,2)
        self.assertEqual('whatever.20040101-000000.20040102-000000.tsk.bak', 
            self.backup.backupFilename(self.taskStore, lambda: now)) # pylint: disable=W0212

    def testCreateBackupOnSave(self):
        self.settings.set('file', 'backup', 'True')
        self.taskStore.tasks().append(task.Task())
        self.taskStore.save()
        self.failUnless(self.copyCalled)

    def testCreateBackupOnSave_ButBackupOff(self):
        self.settings.set('file', 'backup', 'False')
        self.taskStore.tasks().append(task.Task())
        self.taskStore.save()
        self.failIf(self.copyCalled)

    def testDontCreateBackupOnOpen(self):
        self.settings.set('file', 'backup', 'True')
        self.taskStore.load()
        self.failIf(self.copyCalled)
        
    def testDontCreateBackupWhenSettingFilename(self):
        self.settings.set('file', 'backup', 'True')
        self.taskStore.setFilename('newname.tsk')
        self.failIf(self.copyCalled)
                        
    def testLeastUniqueBackupFile_FourBackupFiles(self):  
        self.assertEqual(self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2001,1,1,1,1,1)), 
                         self.backup.leastUniqueBackupFile(self.fourBackupFiles()))
        
    def testLeastUniqueBackupFile_FiveBackupFiles(self):  
        self.assertEqual(self.backup.backupFilename(self.taskStore, now=lambda: date.DateTime(2002,1,1,1,1,1)), 
                         self.backup.leastUniqueBackupFile(self.fiveBackupFiles()))

import test, persistence
from domain import task, category, date


class DummySettings(dict):        
    def set(self, section, setting, value):
        self[setting] = value
        
    def getboolean(self, section, setting):
        return self.get(setting, 'False') == 'True'


class DummyFile:
    name = 'testfile.tsk'

    def close(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass
    
    
class DummyTaskFile(persistence.TaskFile):
    def __init__(self, *args, **kwargs):
        self.saveCalled = 0
        super(DummyTaskFile, self).__init__(*args, **kwargs)
        
    def _read(self, *args, **kwargs):
        if self._throw:
            raise IOError
        else:
            return [task.Task()], [category.Category('category')], []
        
    def exists(self, *args, **kwargs):
        return True
        
    def _openForRead(self, *args, **kwargs):
        return DummyFile()
        
    def _openForWrite(self, *args, **kwargs):
        return DummyFile()
    
    def save(self, *args, **kwargs):
        self.saveCalled += 1
        super(DummyTaskFile, self).save(*args, **kwargs)

    def load(self, throw=False, *args, **kwargs):
        self._throw = throw
        return super(DummyTaskFile, self).load(*args, **kwargs)


class AutoSaverTestCase(test.TestCase):
    def setUp(self):
        self.settings = DummySettings()
        self.taskFile = DummyTaskFile()
        self.autoSaver = persistence.AutoSaver(self.settings)
        
    def tearDown(self):
        super(AutoSaverTestCase, self).tearDown()
        del self.autoSaver # Make sure AutoSaver is not observing task files
        
    def testCreate(self):
        self.failIf(self.taskFile.saveCalled)
        
    def testFileChanged_ButNoFilenameAndAutoSaveOff(self):
        self.taskFile.tasks().append(task.Task())
        self.failIf(self.taskFile.saveCalled)
        
    def testFileChanged_ButAutoSaveOff(self):
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.tasks().append(task.Task())
        self.failIf(self.taskFile.saveCalled)
                
    def testFileChanged_ButNoFilename(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.tasks().append(task.Task())
        self.failIf(self.taskFile.saveCalled)
        
    def testFileChanged(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.tasks().append(task.Task())
        self.assertEqual(1, self.taskFile.saveCalled)
        
    def testSaveAsDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.saveas('newfilename.tsk')
        self.assertEqual(1, self.taskFile.saveCalled)
              
    def testCloseDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.tasks().append(task.Task())
        self.taskFile.close()
        self.assertEqual(1, self.taskFile.saveCalled)
        
    def testLoadDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.load()
        self.failIf(self.taskFile.saveCalled)
        
    def testMergeDoesTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.merge('another-non-existing-file.tsk')
        self.assertEqual(1, self.taskFile.saveCalled)


class TestableAutoSaver(persistence.AutoSaver):
    def __init__(self, *args, **kwargs):
        self.copyCalled = False
        super(TestableAutoSaver, self).__init__(*args, **kwargs)
        
    def _createBackup(self, *args, **kwargs):
        self.copyCalled = True    


class AutoSaverBackupTestCase(test.TestCase):
    def setUp(self):
        self.settings = DummySettings()
        self.taskFile = DummyTaskFile()
        self.autoSaver = TestableAutoSaver(self.settings)

    def tearDown(self):
        super(AutoSaverBackupTestCase, self).tearDown()
        del self.autoSaver
        
    def testBackupFilename(self):
        now = date.DateTime(2004,1,1)
        self.taskFile.setFilename('whatever.tsk')
        self.assertEqual('whatever.20040101-000000.tsk.bak', 
            self.autoSaver._backupFilename(self.taskFile, lambda: now))
        
    def testBackupFilenameOfBackupFilename(self):
        self.taskFile.setFilename('whatever.20040101-000000.tsk.bak')
        now = date.DateTime(2004,1,2)
        self.assertEqual('whatever.20040101-000000.20040102-000000.tsk.bak', 
            self.autoSaver._backupFilename(self.taskFile, lambda: now))

    def testDontCreateBackupWhenSettingFilename(self):
        self.settings.set('file', 'backup', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.failIf(self.autoSaver.copyCalled)

    def testDontCreateBackupOnOpen(self):
        self.settings.set('file', 'backup', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.load()
        self.failIf(self.autoSaver.copyCalled)
        
    def testCreateBackupOnSave_ButBackupOff(self):
        self.settings.set('file', 'backup', 'False')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.tasks().append(task.Task())
        self.taskFile.save()
        self.failIf(self.autoSaver.copyCalled)
        
    def testCreateBackupOnSave(self):
        self.settings.set('file', 'backup', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.tasks().append(task.Task())
        self.taskFile.save()
        self.failUnless(self.autoSaver.copyCalled)
                

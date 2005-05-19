import test, task

class DummySettings(dict):        
    def set(self, section, setting, value):
        self[setting] = value
        
    def getboolean(self, section, setting):
        return self.get(setting, 'False') == 'True'

class DummyFile:
    def close(self, *args, **kwargs):
        pass

class DummyTaskFile(task.TaskFile):
    def __init__(self, *args, **kwargs):
        self.saveCalled = 0
        super(DummyTaskFile, self).__init__(*args, **kwargs)
        
    def _read(self, *args, **kwargs):
        return [task.Task()]
        
    def _exists(self, *args, **kwargs):
        return True
        
    def _open(self, *args, **kwargs):
        return DummyFile()
        
    def save(self, *args, **kwargs):
        self.saveCalled += 1

  
class AutoSaverTestCase(test.TestCase):
    def setUp(self):
        self.settings = DummySettings()
        self.taskFile = DummyTaskFile()
        self.autoSaver = task.AutoSaver(self.settings, self.taskFile)
        
    def testCreate(self):
        self.failIf(self.taskFile.saveCalled)
        
    def testFileChanged_ButNoFilenameAndAutoSaveOff(self):
        self.taskFile.append(task.Task())
        self.failIf(self.taskFile.saveCalled)
        
    def testFileChanged_ButAutoSaveOff(self):
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.append(task.Task())
        self.failIf(self.taskFile.saveCalled)
                
    def testFileChanged_ButNoFilename(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.append(task.Task())
        self.failIf(self.taskFile.saveCalled)
        
    def testFileChanged(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.append(task.Task())
        self.assertEqual(1, self.taskFile.saveCalled)
        
    def testSaveAsDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.saveas('newfilename.tsk')
        self.assertEqual(1, self.taskFile.saveCalled)
              
    def testCloseDoesNotTriggerAutoSave(self):
        self.settings.set('file', 'autosave', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.append(task.Task())
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


class TestableAutoSaver(task.AutoSaver):
    def __init__(self, *args, **kwargs):
        self.copyCalled = False
        super(TestableAutoSaver, self).__init__(*args, **kwargs)
        
    def _createBackup(self, *args, **kwargs):
        self.copyCalled = True    


class AutoSaverBackupTestCase(test.TestCase):
    def setUp(self):
        self.settings = DummySettings()
        self.taskFile = DummyTaskFile()
        self.autoSaver = TestableAutoSaver(self.settings, self.taskFile)

    def testCreateBackupOnOpen(self):
        self.settings.set('file', 'backup', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.load()
        self.failUnless(self.autoSaver.copyCalled)
        
    def testCreateBackupOnOpen_ButBackupOff(self):
        self.settings.set('file', 'backup', 'False')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.load()
        self.failIf(self.autoSaver.copyCalled)
        
    def testDontCreateBackupOnSave(self):
        self.settings.set('file', 'backup', 'True')
        self.taskFile.setFilename('whatever.tsk')
        self.taskFile.append(task.Task())
        self.taskFile.save()
        self.failIf(self.autoSaver.copyCalled)
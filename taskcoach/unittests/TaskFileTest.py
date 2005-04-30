import test, task, os, date, effort, date

class TaskFileTestCase(test.TestCase):
    def setUp(self):
        self.taskFile = task.TaskFile()
        self.emptyTaskFile = task.TaskFile()
        self.task = task.Task()
        self.taskFile.append(self.task)
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2)))
        self.filename = 'test.tsk'
        
    def tearDown(self):
        self.remove(self.filename)

    def remove(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)

class TaskFileTest(TaskFileTestCase):
    def testFileNameAfterCreate(self):
        self.assertEqual('', self.taskFile.filename())

    def testFileName(self):
        self.taskFile.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskFile.filename())

    def testLoadWithoutFilename(self):
        self.taskFile.load()
        self.assertEqual(0, len(self.taskFile))

    def testLoadFromNotExistingFile(self):
        self.taskFile.setFilename(self.filename)
        self.failIf(os.path.isfile(self.taskFile.filename()))
        self.taskFile.load()
        self.assertEqual(0, len(self.taskFile))

    def testClose(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.close()
        self.assertEqual('', self.taskFile.filename())
        self.assertEqual(0, len(self.taskFile))

    def testNeedSave_Initial(self):
        self.failIf(self.emptyTaskFile.needSave())

    def testNeedSave_AfterSetFileName(self):
        self.emptyTaskFile.setFilename(self.filename)
        self.failIf(self.emptyTaskFile.needSave())

    def testNeedSave_AfterNewTaskAdded(self):
        newTask = task.Task(subject='Task')
        self.emptyTaskFile.append(newTask)
        self.failUnless(self.emptyTaskFile.needSave())
        
    def testNeedSave_AfterSave(self):
        self.emptyTaskFile.append(task.Task())
        self.emptyTaskFile.setFilename(self.filename)
        self.emptyTaskFile.save()
        self.failIf(self.emptyTaskFile.needSave())

    def testNeedSave_AfterClose(self):
        self.taskFile.close()
        self.failIf(self.taskFile.needSave())
        
    def testNeedSave_AfterMerge(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.emptyTaskFile.merge(self.filename)
        self.failUnless(self.emptyTaskFile.needSave())
        
    def testNeedSave_AfterLoad(self):
        self.taskFile.append(task.Task())
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.taskFile.close()
        self.taskFile.load()
        self.failIf(self.taskFile.needSave())

    def testNeedSave_AfterEffortAdded(self):
        self.task.addEffort(effort.Effort(self.task, None, None))
        self.failUnless(self.taskFile.needSave())
        
        
class TaskFileSaveAndLoadTest(TaskFileTestCase):
    def setUp(self):
        super(TaskFileSaveAndLoadTest, self).setUp()
        self.emptyTaskFile.setFilename(self.filename)

    def saveAndLoad(self, tasks):
        self.emptyTaskFile.extend(tasks)
        self.emptyTaskFile.save()
        self.emptyTaskFile.load()
        self.assertEqual([task.subject() for task in tasks], 
            [task.subject() for task in self.emptyTaskFile])

    def testSaveAndLoad(self):
        self.saveAndLoad([task.Task(subject='ABC'), 
            task.Task(duedate=date.Tomorrow())])

    def testSaveAndLoadedTaskWithChild(self):
        parentTask = task.Task()
        childTask = task.Task(parent=parentTask)
        self.saveAndLoad([parentTask])

    def testSaveAs(self):
        self.taskFile.saveas('new.tsk')
        self.taskFile.load()
        self.assertEqual(1, len(self.taskFile))
        self.remove('new.tsk')

    def testMerge(self):
        mergeFile = task.TaskFile('merge.tsk')
        mergeFile.append(task.Task())
        mergeFile.save()
        self.taskFile.merge('merge.tsk')
        self.assertEqual(2, len(self.taskFile))
        self.remove('merge.tsk')

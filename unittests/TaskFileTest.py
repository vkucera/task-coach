import test, task, os, date, effort, date

class TaskFileTestCase(test.TestCase):
    def setUp(self):
        self.effortList = effort.EffortList()
        self.taskFile = task.TaskFile(self.effortList)
        self.emptyTaskFile = task.TaskFile(effort.EffortList())
        self.task = task.Task()
        self.taskFile.append(self.task)
        self.effortList.append(effort.Effort(self.task, date.DateTime(2004,1,1),
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

    def testNonZero(self):
        self.failIf(self.taskFile)
        self.taskFile.setFilename(self.filename)
        self.failUnless(self.taskFile)

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
        self.assertEqual(0, len(self.taskFile.effortList()))

    def testNeedSave_Initial(self):
        self.failIf(self.emptyTaskFile.needSave())

    def testNeedSave_AfterSetFileName(self):
        self.emptyTaskFile.setFilename(self.filename)
        self.failIf(self.emptyTaskFile.needSave())

    def testNeedSave_AfterNewTaskAdded(self):
        self.taskFile.append(task.Task())
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterSave(self):
        self.taskFile.append(task.Task())
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())

    def testNeedSave_AfterClose(self):
        self.taskFile.close()
        self.failIf(self.taskFile.needSave())

    def testNeedSave_AfterMerge(self):
        self.taskFile.merge(self.filename)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterLoad(self):
        self.taskFile.append(task.Task())
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.taskFile.close()
        self.taskFile.load()
        self.failIf(self.taskFile.needSave())

    def testNeedSave_AfterEffortAdded(self):
        self.emptyTaskFile.effortList().append(effort.Effort(None, None, None))
        self.failUnless(self.emptyTaskFile.needSave())
        
        
class TaskFileSaveAndLoadTest(TaskFileTestCase):
    def setUp(self):
        super(TaskFileSaveAndLoadTest, self).setUp()
        self.emptyTaskFile.setFilename(self.filename)

    def saveAndLoad(self, tasks):
        self.emptyTaskFile.extend(tasks)
        self.emptyTaskFile.save()
        self.emptyTaskFile.load()
        self.assertEqual(tasks, list(self.emptyTaskFile))

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
        mergeFile = task.TaskFile(effort.EffortList(), 'merge.tsk')
        mergeFile.append(task.Task())
        mergeFile.save()
        self.taskFile.merge('merge.tsk')
        self.assertEqual(2, len(self.taskFile))
        self.remove('merge.tsk')

    def testEffort(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.taskFile.load()
        self.assertEqual(1, len(self.effortList))
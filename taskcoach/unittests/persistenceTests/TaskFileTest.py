import test, os, persistence
import domain.task as task
import domain.effort as effort
import domain.date as date

class TaskFileTestCase(test.TestCase):
    def setUp(self):
        self.taskFile = persistence.TaskFile()
        self.emptyTaskFile = persistence.TaskFile()
        self.task = task.Task()
        self.taskFile.append(self.task)
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2)))
        self.filename = 'test.tsk'
        self.filename2 = 'test.tsk'
        
    def tearDown(self):
        self.remove(self.filename, self.filename2)

    def remove(self, *filenames):
        for filename in filenames:
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
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.failIf(self.taskFile.needSave())
        self.task.addEffort(effort.Effort(self.task, None, None))
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditTaskDescription(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setDescription('new description')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterEditEffortDescription(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setDescription('new description')
        self.failUnless(self.taskFile.needSave())
        
    def testDontNeedSave_AfterEverySecond(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        clock = date.Clock()
        clock.notify()
        self.failIf(self.taskFile.needSave())
        del clock
    
    def testNeedSave_AfterAddCategory(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.addCategory('category')
        self.failUnless(self.taskFile.needSave())
    
    def testNeedSave_AfterRemoveCategory(self):
        self.task.addCategory('category')
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.removeCategory('category')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterChangePriority(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setPriority(10)
        self.failUnless(self.taskFile.needSave())        
        
    def testLastFilename_Initially(self):
        self.assertEqual('', self.taskFile.lastFilename())
        
    def testLastFilename_AfterSetFilename(self):
        self.taskFile.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskFile.lastFilename())
        
    def testLastFilename_AfterClose(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.close()
        self.assertEqual(self.filename, self.taskFile.lastFilename())
        
    def testLastFilename_AfterSaveAs(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.saveas(self.filename2)
        self.assertEqual(self.filename2, self.taskFile.lastFilename())


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
        mergeFile = persistence.TaskFile('merge.tsk')
        mergeFile.append(task.Task())
        mergeFile.save()
        self.taskFile.merge('merge.tsk')
        self.assertEqual(2, len(self.taskFile))
        self.remove('merge.tsk')

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

    def testNeedSave_AfterEffortRemoved(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.failIf(self.taskFile.needSave())
        self.task.removeEffort(newEffort)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditTaskSubject(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setSubject('new subject')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditTaskDescription(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setDescription('new description')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterEditTaskStartDate(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setStartDate(date.Tomorrow())
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditTaskDueDate(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setDueDate(date.Tomorrow())
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterEditTaskCompletionDate(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setCompletionDate(date.Tomorrow())
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortDescription(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setDescription('new description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortStart(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setStart(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterEditEffortStop(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setStop(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortTask(self):
        task2 = task.Task()
        self.taskFile.append(task2)
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setTask(task2)
        self.failUnless(self.taskFile.needSave())

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

    def testNeedSave_AfterChangeBudget(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setBudget(date.TimeDelta(10))
        self.failUnless(self.taskFile.needSave())        
        
    def testNeedSave_AfterChangeHourlyFee(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setHourlyFee(100)
        self.failUnless(self.taskFile.needSave())        
        
    def testNeedSave_AfterChangeFixedFee(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.setFixedFee(500)
        self.failUnless(self.taskFile.needSave())        
        
    def testNeedSave_AfterAttachmentAdded(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.task.addAttachments('attachment')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAttachmentRemoved(self):
        self.taskFile.setFilename(self.filename)
        self.task.addAttachments('attachment')
        self.taskFile.save()
        self.task.removeAttachments('attachment')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAllAttachmentsRemoved(self):
        self.taskFile.setFilename(self.filename)
        self.task.addAttachments('attachment')
        self.taskFile.save()
        self.task.removeAllAttachments()
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterAddChild(self):
        self.taskFile.setFilename(self.filename)
        child = task.Task()
        self.taskFile.append(child)
        self.taskFile.save()
        self.task.addChild(child)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterRemoveChild(self):
        self.taskFile.setFilename(self.filename)
        child = task.Task()
        self.taskFile.append(child)
        self.task.addChild(child)
        self.taskFile.save()
        self.task.removeChild(child)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterSetReminder(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.task.setReminder(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterChangeSetting(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = True
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

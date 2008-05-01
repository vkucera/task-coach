'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

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

import os, wx
import test
from taskcoachlib import persistence
from taskcoachlib.domain import task, effort, date, category, note


class FakeAttachment(object):
    def __init__(self, type_, filename):
        self.type_ = type_
        self.filename = filename

    def data(self):
        return self.filename

    def setTask(self, task):
        pass

    def __unicode__(self):
        return self.filename


class TaskFileTestCase(test.TestCase):
    def setUp(self):
        self.taskFile = persistence.TaskFile()
        self.emptyTaskFile = persistence.TaskFile()
        self.task = task.Task()
        self.category = category.Category('category')
        self.taskFile.tasks().append(self.task)
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2)))
        self.note = note.Note()
        self.taskFile.notes().append(self.note)
        self.filename = 'test.tsk'
        self.filename2 = 'test.tsk'
        
    def tearDown(self):
        super(TaskFileTestCase, self).tearDown()
        self.remove(self.filename, self.filename2)

    def remove(self, *filenames):
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)


class TaskFileTest(TaskFileTestCase):
    def testIsEmptyInitially(self):
        self.failUnless(self.emptyTaskFile.isEmpty())
    
    def testHasNoTasksInitially(self):
        self.failIf(self.emptyTaskFile.tasks())
        
    def testHasNoCategoriesInitially(self):
        self.failIf(self.emptyTaskFile.categories())
        
    def testHasNoNotesInitially(self):
        self.failIf(self.emptyTaskFile.notes())
        
    def testHasNoEffortsInitially(self):
        self.failIf(self.emptyTaskFile.efforts())
            
    def testFileNameAfterCreate(self):
        self.assertEqual('', self.taskFile.filename())

    def testFileName(self):
        self.taskFile.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskFile.filename())

    def testLoadWithoutFilename(self):
        self.taskFile.load()
        self.failUnless(self.taskFile.isEmpty())
        
    def testLoadFromNotExistingFile(self):
        self.taskFile.setFilename(self.filename)
        self.failIf(os.path.isfile(self.taskFile.filename()))
        self.taskFile.load()
        self.failUnless(self.taskFile.isEmpty())

    def testClose_EmptyTaskFileWithoutFilename(self):
        self.taskFile.close()
        self.assertEqual('', self.taskFile.filename())
        self.failUnless(self.taskFile.isEmpty())
    
    def testClose_EmptyTaskFileWithFilename(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.close()
        self.assertEqual('', self.taskFile.filename())
        self.failUnless(self.taskFile.isEmpty())

    def testClose_TaskFileWithTasksDeletesTasks(self):
        self.taskFile.close()
        self.failUnless(self.taskFile.isEmpty())
        
    def testClose_TaskFileWithCategoriesDeletesCategories(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.close()
        self.failUnless(self.taskFile.isEmpty())

    def testClose_TaskFileWithNotesDeletesNotes(self):
        self.taskFile.notes().append(note.Note())
        self.taskFile.close()
        self.failUnless(self.taskFile.isEmpty())
        
    def testDoesNotNeedSave_Initial(self):
        self.failIf(self.emptyTaskFile.needSave())

    def testDoesNotNeedSave_AfterSetFileName(self):
        self.emptyTaskFile.setFilename(self.filename)
        self.failIf(self.emptyTaskFile.needSave())

    def testNeedSave_AfterNewTaskAdded(self):
        newTask = task.Task(subject='Task')
        self.emptyTaskFile.tasks().append(newTask)
        self.failUnless(self.emptyTaskFile.needSave())

    def testNeedSave_AfterNewNoteAdded(self):
        newNote = note.Note('Note')
        self.emptyTaskFile.notes().append(newNote)
        self.failUnless(self.emptyTaskFile.needSave())
    
    def testNeedSave_AfterNoteRemoved(self):
        self.taskFile.notes().remove(self.note)
        self.failUnless(self.taskFile.needSave())
        
    def testDoesNotNeedSave_AfterSave(self):
        self.emptyTaskFile.tasks().append(task.Task())
        self.emptyTaskFile.setFilename(self.filename)
        self.emptyTaskFile.save()
        self.failIf(self.emptyTaskFile.needSave())

    def testDoesNotNeedSave_AfterClose(self):
        self.taskFile.close()
        self.failIf(self.taskFile.needSave())
        
    def testNeedSave_AfterMerge(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.emptyTaskFile.merge(self.filename)
        self.failUnless(self.emptyTaskFile.needSave())
        
    def testDoesNotNeedSave_AfterLoad(self):
        self.taskFile.tasks().append(task.Task())
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
        newEffort = effort.Effort(self.task)
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setDescription('new description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortStart(self):
        newEffort = effort.Effort(self.task, date.DateTime(2000,1,1),
            date.DateTime(2000,1,2))
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setStart(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterEditEffortStop(self):
        newEffort = effort.Effort(self.task, date.DateTime(2000,1,1),
            date.DateTime(2000,1,2))
        self.task.addEffort(newEffort)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        newEffort.setStop(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortTask(self):
        task2 = task.Task()
        self.taskFile.tasks().append(task2)
        newEffort = effort.Effort(self.task)
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
        self.task.addCategory(self.category)
        self.failUnless(self.taskFile.needSave())
    
    def testNeedSave_AfterRemoveCategory(self):
        self.task.addCategory(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.removeCategory(self.category)
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
        self.task.addAttachments(FakeAttachment('file', 'attachment'))
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAttachmentRemoved(self):
        self.taskFile.setFilename(self.filename)
        att = FakeAttachment('file', 'attachment')
        self.task.addAttachments(att)
        self.taskFile.save()
        self.task.removeAttachments(att)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAllAttachmentsRemoved(self):
        self.taskFile.setFilename(self.filename)
        self.task.addAttachments(FakeAttachment('file', 'attachment'))
        self.taskFile.save()
        self.task.removeAllAttachments()
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterAddChild(self):
        self.taskFile.setFilename(self.filename)
        child = task.Task()
        self.taskFile.tasks().append(child)
        self.taskFile.save()
        self.task.addChild(child)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterRemoveChild(self):
        self.taskFile.setFilename(self.filename)
        child = task.Task()
        self.taskFile.tasks().append(child)
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

    def testNeedSave_AfterAddingCategory(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.taskFile.categories().append(self.category)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterRemovingCategory(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.taskFile.categories().remove(self.category)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterFilteringCategory(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.category.setFiltered()
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterCategorySubjectChanged(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.category.setSubject('new subject')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterCategoryDescriptionChanged(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.category.setDescription('new description')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterChangingCategoryColor(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.category.setColor(wx.RED)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterNoteSubjectChanged(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        list(self.taskFile.notes())[0].setSubject('new subject')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterNoteDescriptionChanged(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        list(self.taskFile.notes())[0].setDescription('new description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterAddNoteChild(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        list(self.taskFile.notes())[0].addChild(note.Note())
        self.failUnless(self.taskFile.needSave())
    
    def testNeedSave_AfterRemoveNoteChild(self):
        child = note.Note()
        list(self.taskFile.notes())[0].addChild(child)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        list(self.taskFile.notes())[0].removeChild(child)
        self.failUnless(self.taskFile.needSave())
        
    def testLastFilename_IsEmptyInitially(self):
        self.assertEqual('', self.taskFile.lastFilename())
        
    def testLastFilename_EqualsCurrentFilenameAfterSetFilename(self):
        self.taskFile.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskFile.lastFilename())
        
    def testLastFilename_EqualsPreviousFilenameAfterClose(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.close()
        self.assertEqual(self.filename, self.taskFile.lastFilename())
        
    def testLastFilename_IsEmptyAfterClosingTwice(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.close()
        self.taskFile.close()
        self.assertEqual('', self.taskFile.lastFilename())
        
    def testLastFilename_EqualsCurrentFilenameAfterSaveAs(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.saveas(self.filename2)
        self.assertEqual(self.filename2, self.taskFile.lastFilename())


class TaskFileSaveAndLoadTest(TaskFileTestCase):
    def setUp(self):
        super(TaskFileSaveAndLoadTest, self).setUp()
        self.emptyTaskFile.setFilename(self.filename)
        
    def saveAndLoad(self, tasks, categories=None, notes=None):
        categories = categories or []
        notes = notes or []
        self.emptyTaskFile.tasks().extend(tasks)
        self.emptyTaskFile.categories().extend(categories)
        self.emptyTaskFile.notes().extend(notes)
        self.emptyTaskFile.save()
        self.emptyTaskFile.load()
        self.assertEqual([task.subject() for task in tasks], 
            [task.subject() for task in self.emptyTaskFile.tasks()])
        self.assertEqual([category.subject() for category in categories],
            [category.subject() for category in self.emptyTaskFile.categories()])
        self.assertEqual([note.subject() for note in notes],
            [note.subject() for note in self.emptyTaskFile.notes()])
        
    def testSaveAndLoad(self):
        self.saveAndLoad([task.Task(subject='ABC'), 
            task.Task(duedate=date.Tomorrow())])

    def testSaveAndLoadTaskWithChild(self):
        parentTask = task.Task()
        childTask = task.Task(parent=parentTask)
        self.saveAndLoad([parentTask])

    def testSaveAndLoadCategory(self):
        self.saveAndLoad([], [self.category])
    
    def testSaveAndLoadNotes(self):
        self.saveAndLoad([], [], [self.note])
        
    def testSaveAs(self):
        self.taskFile.saveas('new.tsk')
        self.taskFile.load()
        self.assertEqual(1, len(self.taskFile.tasks()))
        self.remove('new.tsk')


class TaskFileMergeTest(TaskFileTestCase):
    def setUp(self):
        super(TaskFileMergeTest, self).setUp()
        self.mergeFile = persistence.TaskFile('merge.tsk')
    
    def tearDown(self):
        self.remove('merge.tsk')
        super(TaskFileMergeTest, self).tearDown()
        
    def merge(self):
        self.mergeFile.save()
        self.taskFile.merge('merge.tsk')
        
    def testMerge_Tasks(self):
        self.mergeFile.tasks().append(task.Task())
        self.merge()
        self.assertEqual(2, len(self.taskFile.tasks()))

    def testMerge_OneCategoryInMergeFile(self):
        self.mergeFile.categories().append(self.category)
        self.merge()
        self.assertEqual([self.category.subject()], 
                         [cat.subject() for cat in self.taskFile.categories()])
        
    def testMerge_DifferentCategories(self):
        self.mergeFile.categories().append(self.category)
        self.taskFile.categories().append(category.Category('another category'))
        self.merge()
        self.assertEqual(2, len(self.taskFile.categories()))
        
    def testMerge_SameCategory(self):
        self.mergeFile.categories().append(self.category)
        self.taskFile.categories().append(category.Category(self.category.subject()))
        self.merge()
        self.assertEqual([self.category.subject()]*2, 
                         [cat.subject() for cat in self.taskFile.categories()])
        
    def testMerge_CategoryWithTask(self):
        self.mergeFile.categories().append(self.category)
        aTask = task.Task(subject='merged task')
        self.mergeFile.tasks().append(aTask)
        self.category.addCategorizable(aTask)
        self.merge()
        self.assertEqual(aTask.id(), 
                         list(self.taskFile.categories())[0].categorizables()[0].id())
                         
    def testMerge_Notes(self):
        self.mergeFile.notes().append(self.note)
        self.merge()
        self.assertEqual(self.note.subject(), list(self.taskFile.notes())[0].subject())

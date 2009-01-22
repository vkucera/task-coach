'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
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
from taskcoachlib.domain import base, task, effort, date, category, note, attachment


class FakeAttachment(base.Object):
    def __init__(self, type_, location, notes=None, data=None):
        super(FakeAttachment, self).__init__()
        self.type_ = type_
        self.__location = location
        self.__data = data
        if notes is None:
            self.__notes = []
        else:
            self.__notes = notes

    def data(self):
        return self.__data

    def location(self):
        return self.__location

    def notes(self):
        return self.__notes


class TaskFileTestCase(test.TestCase):
    def setUp(self):
        self.taskFile = persistence.TaskFile()
        self.emptyTaskFile = persistence.TaskFile()
        self.task = task.Task()
        self.taskFile.tasks().append(self.task)
        self.category = category.Category('category')
        self.taskFile.categories().append(self.category)
        self.note = note.Note()
        self.taskFile.notes().append(self.note)
        self.effort = effort.Effort(self.task, date.DateTime(2004,1,1),
                                               date.DateTime(2004,1,2))
        self.task.addEffort(self.effort)
        self.filename = 'test.tsk'
        self.filename2 = 'test2.tsk'
        
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

    def testNeedSave_AfterTaskMarkedDeleted(self):
        self.task.markDeleted()
        self.failUnless(self.taskFile.needSave())

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
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.effort.setDescription('new description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortStart(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.effort.setStart(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterEditEffortStop(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.effort.setStop(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortTask(self):
        task2 = task.Task()
        self.taskFile.tasks().append(task2)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.effort.setTask(task2)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterEditEffortColor(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.effort.setColor(wx.RED)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterTaskAddedToCategory(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.addCategory(self.category)
        self.failUnless(self.taskFile.needSave())
    
    def testNeedSave_AfterTaskRemovedFromCategory(self):
        self.task.addCategory(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.task.removeCategory(self.category)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterNoteAddedToCategory(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.note.addCategory(self.category)
        self.failUnless(self.taskFile.needSave())
    
    def testNeedSave_AfterNoteRemovedFromCategory(self):
        self.note.addCategory(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.failIf(self.taskFile.needSave())
        self.note.removeCategory(self.category)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAddingNoteToTask(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.task.addNote(note.Note(subject='Note'))
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
        
    def testNeedSave_AfterChangeRecurrence(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.task.setRecurrence(date.Recurrence('daily'))
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

    def testNeedSave_AfterChangingTaskExpansionState(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.task.expand()
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterChangingCategoryExpansionState(self):
        self.taskFile.categories().append(self.category)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.category.expand()
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterChangingNoteExpansionState(self):
        self.taskFile.notes().append(self.note)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.note.expand()
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterMarkDeleted(self):
        self.taskFile.notes().append(self.note)
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.note.markDeleted()
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterMarkNotDeleted(self):
        self.taskFile.notes().append(self.note)
        self.note.markDeleted()
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()        
        self.note.cleanDirty()
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


class ChangingAttachmentsTests(object):        
    def testNeedSave_AfterAttachmentAdded(self):
        self.taskFile.setFilename(self.filename)
        self.taskFile.save()
        self.item.addAttachments(self.attachment)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAttachmentRemoved(self):
        self.taskFile.setFilename(self.filename)
        self.item.addAttachments(self.attachment)
        self.taskFile.save()
        self.item.removeAttachments(self.attachment)
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterAttachmentsReplaced(self):
        self.taskFile.setFilename(self.filename)
        self.item.addAttachments(self.attachment)
        self.taskFile.save()
        self.item.setAttachments([FakeAttachment('file', 'attachment2')])
        self.failUnless(self.taskFile.needSave())

    def addAttachment(self, attachment):
        self.taskFile.setFilename(self.filename)
        self.item.addAttachments(attachment)
        self.taskFile.save()
               
    def addFileAttachment(self):
        self.fileAttachment = attachment.FileAttachment('Old location')
        self.addAttachment(self.fileAttachment)

    def testNeedSave_AfterFileAttachmentLocationChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setLocation('New location')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterFileAttachmentSubjectChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setSubject('New subject')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterFileAttachmentDescriptionChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setDescription('New description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterFileAttachmentColorChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setColor(wx.RED)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterFileAttachmentNoteAdded(self):
        self.addFileAttachment()
        self.fileAttachment.addNote(note.Note(subject='Note'))
        self.failUnless(self.taskFile.needSave())

    def addURIAttachment(self):
        self.uriAttachment = attachment.URIAttachment('Old location')
        self.addAttachment(self.uriAttachment)

    def testNeedSave_AfterURIAttachmentLocationChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setLocation('New location')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterURIAttachmentSubjectChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setSubject('New subject')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterURIAttachmentDescriptionChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setDescription('New description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterURIAttachmentColorChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setColor(wx.RED)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterURIAttachmentNoteAdded(self):
        self.addURIAttachment()
        self.uriAttachment.addNote(note.Note(subject='Note'))
        self.failUnless(self.taskFile.needSave())

    def addMailAttachment(self):
        self.mailAttachment = attachment.MailAttachment(self.filename, 
                                  readMail=lambda location: ('', ''))
        self.addAttachment(self.mailAttachment)
        
    def testNeedSave_AfterMailAttachmentLocationChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setLocation('New location')
        self.failUnless(self.taskFile.needSave())
        
    def testNeedSave_AfterURIAttachmentSubjectChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setSubject('New subject')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterURIAttachmentDescriptionChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setDescription('New description')
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterURIAttachmentColorChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setColor(wx.RED)
        self.failUnless(self.taskFile.needSave())

    def testNeedSave_AfterURIAttachmentNoteAdded(self):
        self.addMailAttachment()
        self.mailAttachment.addNote(note.Note(subject='Note'))
        self.failUnless(self.taskFile.needSave())


class TaskFileDirtyWhenChangingAttachmentsTestCase(TaskFileTestCase):
    def setUp(self):
        super(TaskFileDirtyWhenChangingAttachmentsTestCase, self).setUp()
        self.attachment = FakeAttachment('file', 'attachment')
    

class TaskFileDirtyWhenChangingTaskAttachmentsTestCase(\
        TaskFileDirtyWhenChangingAttachmentsTestCase, ChangingAttachmentsTests):
    def setUp(self):
        super(TaskFileDirtyWhenChangingTaskAttachmentsTestCase, self).setUp()
        self.item = self.task

        
class TaskFileDirtyWhenChangingNoteAttachmentsTestCase(\
        TaskFileDirtyWhenChangingAttachmentsTestCase, ChangingAttachmentsTests):
    def setUp(self):
        super(TaskFileDirtyWhenChangingNoteAttachmentsTestCase, self).setUp()
        self.item = self.note


class TaskFileDirtyWhenChangingCategoryAttachmentsTestCase(\
        TaskFileDirtyWhenChangingAttachmentsTestCase, ChangingAttachmentsTests):
    def setUp(self):
        super(TaskFileDirtyWhenChangingCategoryAttachmentsTestCase, self).setUp()
        self.item = self.category


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
        
    def testMerge_TasksWithSubtask(self):
        parent = task.Task(subject='parent')
        child = task.Task(subject='child')
        parent.addChild(child)
        child.setParent(parent)
        self.mergeFile.tasks().extend([parent, child])
        self.merge()
        self.assertEqual(3, len(self.taskFile.tasks()))
        self.assertEqual(2, len(self.taskFile.tasks().rootItems()))

    def testMerge_OneCategoryInMergeFile(self):
        self.taskFile.categories().remove(self.category)
        self.mergeFile.categories().append(self.category)
        self.merge()
        self.assertEqual([self.category.subject()], 
                         [cat.subject() for cat in self.taskFile.categories()])
        
    def testMerge_DifferentCategories(self):
        self.mergeFile.categories().append(category.Category('another category'))
        self.merge()
        self.assertEqual(2, len(self.taskFile.categories()))
        
    def testMerge_SameCategory(self):
        self.mergeFile.categories().append(category.Category(self.category.subject()))
        self.merge()
        self.assertEqual([self.category.subject()]*2, 
                         [cat.subject() for cat in self.taskFile.categories()])
        
    def testMerge_CategoryWithTask(self):
        self.taskFile.categories().remove(self.category)
        self.mergeFile.categories().append(self.category)
        aTask = task.Task(subject='merged task')
        self.mergeFile.tasks().append(aTask)
        self.category.addCategorizable(aTask)
        self.merge()
        self.assertEqual(aTask.id(), 
                         list(self.taskFile.categories())[0].categorizables()[0].id())
                         
    def testMerge_Notes(self):
        newNote = note.Note('new note')
        self.mergeFile.notes().append(newNote)
        self.merge()
        self.assertEqual(2, len(self.taskFile.notes()))

    def testMerge_SameTask(self):
        mergedTask = task.Task(subject='merged task', id=self.task.id())
        self.mergeFile.tasks().append(mergedTask)
        self.merge()
        self.assertEqual(1, len(self.taskFile.tasks()))
        self.assertEqual('merged task', list(self.taskFile.tasks())[0].subject())
        
    def testMerge_SameNote(self):
        mergedNote = note.Note(subject='merged note', id=self.note.id())
        self.mergeFile.notes().append(mergedNote)
        self.merge()
        self.assertEqual(1, len(self.taskFile.notes()))
        self.assertEqual('merged note', list(self.taskFile.notes())[0].subject())

    def testMerge_SameCategory(self):
        mergedCategory = category.Category(subject='merged category', id=self.category.id())
        self.mergeFile.categories().append(mergedCategory)
        self.merge()
        self.assertEqual(1, len(self.taskFile.categories()))
        self.assertEqual('merged category', list(self.taskFile.categories())[0].subject())
        
        
class LockTest(test.TestCase):
    @test.onlyOnPlatform('__WXGTK__')
    def testLock(self):
        import fcntl
        file1 = open('file', 'w')
        fcntl.flock(file1.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
        file2 = open('file', 'w')
        try:
            fcntl.flock(file2.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.fail()
        except IOError:
            pass
        finally:
            file1.close()
        os.remove('file')

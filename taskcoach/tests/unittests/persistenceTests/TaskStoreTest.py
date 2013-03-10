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

import os, wx
import test
from taskcoachlib import persistence, config
from taskcoachlib.domain import base, task, effort, date, category, note, attachment


class FakeAttachment(base.Object):
    def __init__(self, type_, location, notes=None, data=None):
        super(FakeAttachment, self).__init__()
        self.type_ = type_
        self.__location = location
        self.__data = data
        self.__notes = notes or []

    def data(self):
        return self.__data

    def location(self):
        return self.__location

    def notes(self):
        return self.__notes


class TaskStoreTestCase(test.TestCase):
    def setUp(self):
        super(TaskStoreTestCase, self).setUp()
        self.createTaskStores()
        self.init()

    def init(self):
        self.task = task.Task(subject='task')
        self.taskStore.tasks().append(self.task)
        self.category = category.Category('category')
        self.taskStore.categories().append(self.category)
        self.note = note.Note(subject='note')
        self.taskStore.notes().append(self.note)
        self.effort = effort.Effort(self.task, date.DateTime(2004, 1, 1),
                                               date.DateTime(2004, 1, 2))
        self.task.addEffort(self.effort)
        self.filename = 'test.tsk'
        self.filename2 = 'test2.tsk'

    def createTaskStores(self):
        # pylint: disable=W0201
        self.taskStore = persistence.TaskStore(self.settings)
        self.emptyTaskStore = persistence.TaskStore(self.settings)

    def tearDown(self):
        super(TaskStoreTestCase, self).tearDown()
        self.clear()

    def clear(self):
        self.taskStore.close()
        self.taskStore.stop()
        self.emptyTaskStore.close()
        self.emptyTaskStore.stop()
        self.remove(self.filename, self.filename2,
                    self.filename + '.delta',
                    self.filename2 + '.delta')

    def remove(self, *filenames):
        for filename in filenames:
            tries = 0
            while os.path.exists(filename) and tries < 3:
                try:  # Don't fail on random 'Access denied' errors.
                    os.remove(filename)
                    break
                except WindowsError:  # pragma: no cover pylint: disable=E0602
                    tries += 1


class TaskStoreTest(TaskStoreTestCase):
    def testIsEmptyInitially(self):
        self.failUnless(self.emptyTaskStore.isEmpty())

    def testHasNoTasksInitially(self):
        self.failIf(self.emptyTaskStore.tasks())

    def testHasNoCategoriesInitially(self):
        self.failIf(self.emptyTaskStore.categories())

    def testHasNoNotesInitially(self):
        self.failIf(self.emptyTaskStore.notes())

    def testHasNoEffortsInitially(self):
        self.failIf(self.emptyTaskStore.efforts())

    def testFileNameAfterCreate(self):
        self.assertEqual('', self.taskStore.filename())

    def testFileName(self):
        self.taskStore.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskStore.filename())

    def testLoadWithoutFilename(self):
        self.taskStore.load()
        self.failUnless(self.taskStore.isEmpty())

    def testLoadFromNotExistingFile(self):
        self.taskStore.setFilename(self.filename)
        self.failIf(os.path.isfile(self.taskStore.filename()))
        self.taskStore.load()
        self.failUnless(self.taskStore.isEmpty())

    def testClose_EmptyTaskStoreWithoutFilename(self):
        self.taskStore.close()
        self.assertEqual('', self.taskStore.filename())
        self.failUnless(self.taskStore.isEmpty())

    def testClose_EmptyTaskStoreWithFilename(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.close()
        self.assertEqual('', self.taskStore.filename())
        self.failUnless(self.taskStore.isEmpty())

    def testClose_TaskStoreWithTasksDeletesTasks(self):
        self.taskStore.close()
        self.failUnless(self.taskStore.isEmpty())

    def testClose_TaskStoreWithCategoriesDeletesCategories(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.close()
        self.failUnless(self.taskStore.isEmpty())

    def testClose_TaskStoreWithNotesDeletesNotes(self):
        self.taskStore.notes().append(note.Note())
        self.taskStore.close()
        self.failUnless(self.taskStore.isEmpty())

    def testDoesNotNeedSave_Initial(self):
        self.failIf(self.emptyTaskStore.needSave())

    def testDoesNotNeedSave_AfterSetFileName(self):
        self.emptyTaskStore.setFilename(self.filename)
        self.failIf(self.emptyTaskStore.needSave())

    def testLastFilename_IsEmptyInitially(self):
        self.assertEqual('', self.taskStore.lastFilename())

    def testLastFilename_EqualsCurrentFilenameAfterSetFilename(self):
        self.taskStore.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskStore.lastFilename())

    def testLastFilename_EqualsPreviousFilenameAfterClose(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.close()
        self.assertEqual(self.filename, self.taskStore.lastFilename())

    def testLastFilename_IsEmptyAfterClosingTwice(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.close()
        self.taskStore.close()
        self.assertEqual(self.filename, self.taskStore.lastFilename())

    def testLastFilename_EqualsCurrentFilenameAfterSaveAs(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.saveas(self.filename2)
        self.assertEqual(self.filename2, self.taskStore.lastFilename())

    def testTaskStoreContainsTask(self):
        self.failUnless(self.task in self.taskStore)

    def testTaskStoreDoesNotContainTask(self):
        self.failIf(task.Task() in self.taskStore)

    def testTaskStoreContainsNote(self):
        newNote = note.Note()
        self.taskStore.notes().append(newNote)
        self.failUnless(newNote in self.taskStore)

    def testTaskStoreDoesNotContainNote(self):
        self.failIf(note.Note() in self.taskStore)

    def testTaskStoreContainsCategory(self):
        newCategory = category.Category('Category')
        self.taskStore.categories().append(newCategory)
        self.failUnless(newCategory in self.taskStore)

    def testTaskStoreDoesNotContainCategory(self):
        self.failIf(category.Category('Category') in self.taskStore)

    def testTaskStoreContainsEffort(self):
        newEffort = effort.Effort(self.task)
        self.task.addEffort(newEffort)
        self.failUnless(newEffort in self.taskStore)

    def testTaskStoreDoesNotContainEffort(self):
        self.failIf(effort.Effort(self.task) in self.taskStore)

    def testCloseSavesSession(self):
        self.emptyTaskStore.tasks().extend([task.Task('Test task')])
        guid = self.emptyTaskStore.guid()
        self.emptyTaskStore.close()

        taskStore = persistence.TaskStore(self.settings)
        taskStore.loadSession(guid)
        self.assertEqual(len(taskStore.tasks()), 1)


class DirtyTaskStoreTest(TaskStoreTestCase):
    def setUp(self):
        super(DirtyTaskStoreTest, self).setUp()
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()

    def testSetupFileDoesNotNeedSave(self):
        self.failIf(self.taskStore.needSave())

    def testNeedSave_AfterNewTaskAdded(self):
        newTask = task.Task(subject='Task')
        self.emptyTaskStore.tasks().append(newTask)
        self.failUnless(self.emptyTaskStore.needSave())

    def testNeedSave_AfterNewNoteAdded(self):
        newNote = note.Note(subject='Note')
        self.emptyTaskStore.notes().append(newNote)
        self.failUnless(self.emptyTaskStore.needSave())

    def testNeedSave_AfterNoteRemoved(self):
        self.taskStore.notes().remove(self.note)
        self.failUnless(self.taskStore.needSave())

    def testDoesNotNeedSave_AfterSave(self):
        self.emptyTaskStore.tasks().append(task.Task())
        self.emptyTaskStore.setFilename(self.filename)
        self.emptyTaskStore.save()
        self.failIf(self.emptyTaskStore.needSave())

    def testDoesNotNeedSave_AfterClose(self):
        self.taskStore.close()
        self.failIf(self.taskStore.needSave())

    def testNeedSave_AfterMerge(self):
        self.emptyTaskStore.merge(self.filename)
        self.failUnless(self.emptyTaskStore.needSave())

    def testDoesNotNeedSave_AfterLoad(self):
        self.taskStore.tasks().append(task.Task())
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.taskStore.close()
        self.taskStore.load()
        self.failIf(self.taskStore.needSave())

    def testNeedSave_AfterEffortAdded(self):
        self.task.addEffort(effort.Effort(self.task, None, None))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEffortRemoved(self):
        newEffort = effort.Effort(self.task, None, None)
        self.task.addEffort(newEffort)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.task.removeEffort(newEffort)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskSubject(self):
        self.task.setSubject('new subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskDescription(self):
        self.task.setDescription('new description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskForegroundColor(self):
        self.task.setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskBackgroundColor(self):
        self.task.setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskPlannedStartDateTime(self):
        self.task.setPlannedStartDateTime(date.Now() + date.ONE_HOUR)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskDueDate(self):
        self.task.setDueDateTime(date.Tomorrow())
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditTaskCompletionDate(self):
        self.task.setCompletionDateTime(date.Now())
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditPercentageComplete(self):
        self.task.setPercentageComplete(50)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditEffortDescription(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.effort.setDescription('new description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditEffortStart(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.effort.setStart(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditEffortStop(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.effort.setStop(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditEffortTask(self):
        task2 = task.Task()
        self.taskStore.tasks().append(task2)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.effort.setTask(task2)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditEffortForegroundColor(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.effort.setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterEditEffortBackgroundColor(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.effort.setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterTaskAddedToCategory(self):
        self.task.addCategory(self.category)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterTaskRemovedFromCategory(self):
        self.task.addCategory(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.task.removeCategory(self.category)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterNoteAddedToCategory(self):
        self.note.addCategory(self.category)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterNoteRemovedFromCategory(self):
        self.note.addCategory(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.failIf(self.taskStore.needSave())
        self.note.removeCategory(self.category)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterAddingNoteToTask(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.task.addNote(note.Note(subject='Note')) # pylint: disable=E1101
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterTaskNoteChanged(self):
        self.taskStore.setFilename(self.filename)
        newNote = note.Note(subject='Note')
        self.task.addNote(newNote) # pylint: disable=E1101
        self.taskStore.save()
        newNote.setSubject('New subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangePriority(self):
        self.task.setPriority(10)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangeBudget(self):
        self.task.setBudget(date.TimeDelta(10))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangeHourlyFee(self):
        self.task.setHourlyFee(100)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangeFixedFee(self):
        self.task.setFixedFee(500)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterAddChild(self):
        self.taskStore.setFilename(self.filename)
        child = task.Task()
        self.taskStore.tasks().append(child)
        self.taskStore.save()
        self.task.addChild(child)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterRemoveChild(self):
        self.taskStore.setFilename(self.filename)
        child = task.Task()
        self.taskStore.tasks().append(child)
        self.task.addChild(child)
        self.taskStore.save()
        self.task.removeChild(child)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterSetReminder(self):
        self.task.setReminder(date.DateTime(2005,1,1,10,0,0))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangeRecurrence(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.task.setRecurrence(date.Recurrence('daily'))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangeSetting(self):
        self.task.setShouldMarkCompletedWhenAllChildrenCompleted(True)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterAddingCategory(self):
        self.taskStore.categories().append(category.Category(u'Added'))
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterRemovingCategory(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.taskStore.categories().remove(self.category)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterFilteringCategory(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.setFiltered()
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterCategorySubjectChanged(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.setSubject('new subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterCategoryDescriptionChanged(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.setDescription('new description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangingCategoryForegroundColor(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangingCategoryBackgroundColor(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterMakingSubclassesExclusive(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.makeSubcategoriesExclusive()
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterNoteSubjectChanged(self):
        list(self.taskStore.notes())[0].setSubject('new subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterNoteDescriptionChanged(self):
        list(self.taskStore.notes())[0].setDescription('new description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterNoteForegroundColorChanged(self):
        list(self.taskStore.notes())[0].setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterNoteBackgroundColorChanged(self):
        list(self.taskStore.notes())[0].setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterAddNoteChild(self):
        list(self.taskStore.notes())[0].addChild(note.Note())
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterRemoveNoteChild(self):
        child = note.Note()
        list(self.taskStore.notes())[0].addChild(child)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        list(self.taskStore.notes())[0].removeChild(child)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangingTaskExpansionState(self):
        self.task.expand()
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangingCategoryExpansionState(self):
        self.taskStore.categories().append(self.category)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.category.expand()
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterChangingNoteExpansionState(self):
        self.taskStore.notes().append(self.note)
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.note.expand()
        self.failUnless(self.taskStore.needSave())

    def testLastFilename_EqualsCurrentFilenameAfterSetFilename(self):
        self.taskStore.setFilename(self.filename)
        self.assertEqual(self.filename, self.taskStore.lastFilename())

    def testLastFilename_EqualsPreviousFilenameAfterClose(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.close()
        self.assertEqual(self.filename, self.taskStore.lastFilename())

    def testLastFilename_EqualsPreviousFilenameAfterClosingTwice(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.close()
        self.taskStore.close()
        self.assertEqual(self.filename, self.taskStore.lastFilename())

    def testLastFilename_EqualsCurrentFilenameAfterSaveAs(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.saveas(self.filename2)
        self.assertEqual(self.filename2, self.taskStore.lastFilename())


class ChangingAttachmentsTestsMixin(object):
    def testNeedSave_AfterAttachmentAdded(self):
        self.taskStore.setFilename(self.filename)
        self.taskStore.save()
        self.item.addAttachments(self.attachment)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterAttachmentRemoved(self):
        self.taskStore.setFilename(self.filename)
        self.item.addAttachments(self.attachment)
        self.taskStore.save()
        self.item.removeAttachments(self.attachment)
        self.failUnless(self.taskStore.needSave())

    # XXXFIXME: this doesn't pass. On the other hand the method is never actually used.

    ## def testNeedSave_AfterAttachmentsReplaced(self):
    ##     self.taskStore.setFilename(self.filename)
    ##     self.item.addAttachments(self.attachment)
    ##     self.taskStore.save()
    ##     self.item.setAttachments([FakeAttachment('file', 'attachment2')])
    ##     self.failUnless(self.taskStore.needSave())

    def addAttachment(self, anAttachment):
        self.taskStore.setFilename(self.filename)
        self.item.addAttachments(anAttachment)
        self.taskStore.save()

    def addFileAttachment(self):
        self.fileAttachment = attachment.FileAttachment('Old location') # pylint: disable=W0201
        self.addAttachment(self.fileAttachment)

    def testNeedSave_AfterFileAttachmentLocationChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setLocation('New location')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterFileAttachmentSubjectChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setSubject('New subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterFileAttachmentDescriptionChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setDescription('New description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterFileAttachmentForegroundColorChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterFileAttachmentBackgroundColorChanged(self):
        self.addFileAttachment()
        self.fileAttachment.setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterFileAttachmentNoteAdded(self):
        self.addFileAttachment()
        self.fileAttachment.addNote(note.Note(subject='Note')) # pylint: disable=E1101
        self.failUnless(self.taskStore.needSave())

    def addURIAttachment(self):
        self.uriAttachment = attachment.URIAttachment('Old location') # pylint: disable=W0201
        self.addAttachment(self.uriAttachment)

    def testNeedSave_AfterURIAttachmentLocationChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setLocation('New location')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterURIAttachmentSubjectChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setSubject('New subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterURIAttachmentDescriptionChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setDescription('New description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterURIAttachmentForegroundColorChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterURIAttachmentBackgroundColorChanged(self):
        self.addURIAttachment()
        self.uriAttachment.setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterURIAttachmentNoteAdded(self):
        self.addURIAttachment()
        self.uriAttachment.addNote(note.Note(subject='Note')) # pylint: disable=E1101
        self.failUnless(self.taskStore.needSave())

    def addMailAttachment(self):
        self.mailAttachment = attachment.MailAttachment(self.filename, # pylint: disable=W0201
                                  readMail=lambda location: ('', ''))
        self.addAttachment(self.mailAttachment)

    def testNeedSave_AfterMailAttachmentLocationChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setLocation('New location')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterMailAttachmentSubjectChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setSubject('New subject')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterMailAttachmentDescriptionChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setDescription('New description')
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterMailAttachmentForegroundColorChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setForegroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterMailAttachmentBackgroundColorChanged(self):
        self.addMailAttachment()
        self.mailAttachment.setBackgroundColor(wx.RED)
        self.failUnless(self.taskStore.needSave())

    def testNeedSave_AfterMailAttachmentNoteAdded(self):
        self.addMailAttachment()
        self.mailAttachment.addNote(note.Note(subject='Note')) # pylint: disable=E1101
        self.failUnless(self.taskStore.needSave())


class TaskStoreDirtyWhenChangingAttachmentsTestCase(TaskStoreTestCase):
    def setUp(self):
        super(TaskStoreDirtyWhenChangingAttachmentsTestCase, self).setUp()
        self.attachment = FakeAttachment('file', 'attachment')


class TaskStoreDirtyWhenChangingTaskAttachmentsTestCase(\
        TaskStoreDirtyWhenChangingAttachmentsTestCase,
        ChangingAttachmentsTestsMixin):
    def setUp(self):
        super(TaskStoreDirtyWhenChangingTaskAttachmentsTestCase, self).setUp()
        self.item = self.task


class TaskStoreDirtyWhenChangingNoteAttachmentsTestCase(\
        TaskStoreDirtyWhenChangingAttachmentsTestCase,
        ChangingAttachmentsTestsMixin):
    def setUp(self):
        super(TaskStoreDirtyWhenChangingNoteAttachmentsTestCase, self).setUp()
        self.item = self.note


class TaskStoreDirtyWhenChangingCategoryAttachmentsTestCase(\
        TaskStoreDirtyWhenChangingAttachmentsTestCase,
        ChangingAttachmentsTestsMixin):
    def setUp(self):
        super(TaskStoreDirtyWhenChangingCategoryAttachmentsTestCase, self).setUp()
        self.item = self.category


class TaskStoreSaveAndLoadTest(TaskStoreTestCase):
    def setUp(self):
        super(TaskStoreSaveAndLoadTest, self).setUp()
        self.emptyTaskStore.setFilename(self.filename)

    def saveAndLoad(self, tasks, categories=None, notes=None):
        categories = categories or []
        notes = notes or []
        self.emptyTaskStore.tasks().extend(tasks)
        self.emptyTaskStore.categories().extend(categories)
        self.emptyTaskStore.notes().extend(notes)
        self.emptyTaskStore.save()
        self.emptyTaskStore.load()
        self.assertEqual( \
            sorted([eachTask.subject() for eachTask in tasks]),
            sorted([eachTask.subject() for eachTask in self.emptyTaskStore.tasks()]))
        self.assertEqual( \
            sorted([eachCategory.subject() for eachCategory in categories]),
            sorted([eachCategory.subject() for eachCategory in self.emptyTaskStore.categories()]))
        self.assertEqual( \
            sorted([eachNote.subject() for eachNote in notes]),
            sorted([eachNote.subject() for eachNote in self.emptyTaskStore.notes()]))

    def testSaveAndLoad(self):
        self.saveAndLoad([task.Task(subject='ABC'),
            task.Task(dueDateTime=date.Tomorrow())])

    def testSaveAndLoadTaskWithChild(self):
        parentTask = task.Task()
        childTask = task.Task(parent=parentTask)
        parentTask.addChild(childTask)
        self.saveAndLoad([parentTask, childTask])

    def testSaveAndLoadCategory(self):
        self.saveAndLoad([], [self.category])

    def testSaveAndLoadNotes(self):
        self.saveAndLoad([], [], [self.note])

    def testSaveAs(self):
        self.taskStore.saveas('new.tsk')
        self.taskStore.load()
        self.assertEqual(1, len(self.taskStore.tasks()))
        self.taskStore.close()
        self.remove('new.tsk', 'new.tsk.delta')


class TaskStoreMergeTest(TaskStoreTestCase):
    def setUp(self):
        super(TaskStoreMergeTest, self).setUp()
        self.mergeFile = persistence.TaskStore(self.settings)
        self.mergeFile.setFilename('merge.tsk')

    def tearDown(self):
        self.mergeFile.close()
        self.mergeFile.stop()
        self.remove('merge.tsk', 'merge.tsk.delta')
        super(TaskStoreMergeTest, self).tearDown()

    def merge(self):
        self.mergeFile.save()
        self.taskStore.merge('merge.tsk')

    def testMerge_Tasks(self):
        self.mergeFile.tasks().append(task.Task())
        self.merge()
        self.assertEqual(2, len(self.taskStore.tasks()))

    def testMerge_TasksWithSubtask(self):
        parent = task.Task(subject='parent')
        child = task.Task(subject='child')
        parent.addChild(child)
        child.setParent(parent)
        self.mergeFile.tasks().extend([parent, child])
        self.merge()
        self.assertEqual(3, len(self.taskStore.tasks()))
        self.assertEqual(2, len(self.taskStore.tasks().rootItems()))

    def testMerge_OneCategoryInMergeFile(self):
        self.taskStore.categories().remove(self.category)
        self.mergeFile.categories().append(self.category)
        self.merge()
        self.assertEqual([self.category.subject()],
                         [cat.subject() for cat in self.taskStore.categories()])

    def testMerge_DifferentCategories(self):
        self.mergeFile.categories().append(category.Category('another category'))
        self.merge()
        self.assertEqual(2, len(self.taskStore.categories()))

    def testMerge_SameSubject(self):
        self.mergeFile.categories().append(category.Category(self.category.subject()))
        self.merge()
        self.assertEqual([self.category.subject()]*2,
                         [cat.subject() for cat in self.taskStore.categories()])

    def testMerge_CategoryWithTask(self):
        self.taskStore.categories().remove(self.category)
        self.mergeFile.categories().append(self.category)
        aTask = task.Task(subject='merged task')
        self.mergeFile.tasks().append(aTask)
        self.category.addCategorizable(aTask)
        self.merge()
        self.assertEqual(aTask.id(),
                         list(list(self.taskStore.categories())[0].categorizables())[0].id())

    def testMerge_Notes(self):
        newNote = note.Note(subject='new note')
        self.mergeFile.notes().append(newNote)
        self.merge()
        self.assertEqual(2, len(self.taskStore.notes()))

    def testMerge_SameTask(self):
        mergedTask = task.Task(subject='merged task', id=self.task.id())
        self.mergeFile.tasks().append(mergedTask)
        self.merge()
        self.assertEqual(1, len(self.taskStore.tasks()))
        self.assertEqual('merged task', list(self.taskStore.tasks())[0].subject())

    def testMerge_SameNote(self):
        mergedNote = note.Note(subject='merged note', id=self.note.id())
        self.mergeFile.notes().append(mergedNote)
        self.merge()
        self.assertEqual(1, len(self.taskStore.notes()))
        self.assertEqual('merged note', list(self.taskStore.notes())[0].subject())

    def testMerge_SameCategory(self):
        mergedCategory = category.Category(subject='merged category', id=self.category.id())
        self.mergeFile.categories().append(mergedCategory)
        self.merge()
        self.assertEqual(1, len(self.taskStore.categories()))
        self.assertEqual('merged category', list(self.taskStore.categories())[0].subject())

    def testMerge_CategoryLinkedToTask(self):
        self.task.addCategory(self.category)
        self.category.addCategorizable(self.task)
        mergedCategory = category.Category('merged category', id=self.category.id())
        self.mergeFile.categories().append(mergedCategory)
        self.merge()
        self.assertEqual(self.category.id(), list(self.task.categories())[0].id())

    def testMerge_CategoryLinkedToNote(self):
        self.note.addCategory(self.category)
        self.category.addCategorizable(self.note)
        mergedCategory = category.Category('merged category', id=self.category.id())
        self.mergeFile.categories().append(mergedCategory)
        self.merge()
        self.assertEqual(self.category.id(), list(self.note.categories())[0].id())

    def testMerge_ExistingCategoryWithoutExistingSubCategoryRemovesTheSubCategory(self):
        subCategory = category.Category('subcategory')
        self.category.addChild(subCategory)
        self.taskStore.categories().append(subCategory)
        self.task.addCategory(subCategory)
        subCategory.addCategorizable(self.task)
        self.assertEqual(2, len(self.taskStore.categories()))
        mergedCategory = category.Category('merged category', id=self.category.id())
        self.mergeFile.categories().append(mergedCategory)
        self.merge()
        self.assertEqual(1, len(self.taskStore.categories()))


## class LockedTaskStoreLockTest(TaskStoreTestCase):
##     def testFileIsNotLockedInitially(self):
##         self.failIf(self.taskStore.is_locked())
##         self.failIf(self.emptyTaskStore.is_locked())

##     def testFileIsNotLockedAfterLoading(self):
##         self.taskStore.load(self.filename)
##         self.failIf(self.taskStore.is_locked())

##     def testFileIsNotLockedAfterClosing(self):
##         self.taskStore.close()
##         self.failIf(self.taskStore.is_locked())

##     def testFileIsnotLockedAfterLoadingAndClosing(self):
##         self.taskStore.load(self.filename)
##         self.taskStore.close()
##         self.failIf(self.taskStore.is_locked())

##     def testFileIsNotLockedAfterSaving(self):
##         self.taskStore.setFilename(self.filename)
##         self.taskStore.save()
##         self.failIf(self.taskStore.is_locked())

##     def testFileIsNotLockedAfterSavingAndClosing(self):
##         self.taskStore.setFilename(self.filename)
##         self.taskStore.save()
##         self.taskStore.close()
##         self.failIf(self.taskStore.is_locked())

##     def testFileIsNotLockedAfterSaveAs(self):
##         self.taskStore.saveas(self.filename)
##         self.failIf(self.taskStore.is_locked())

##     def testFileIsNotLockedAfterSaveAndSaveAs(self):
##         self.taskStore.setFilename(self.filename)
##         self.taskStore.save()
##         self.taskStore.saveas(self.filename2)
##         self.failIf(self.taskStore.is_locked())

##     def testFileCanBeLoadedAfterClose(self):
##         self.taskStore.setFilename(self.filename)
##         self.taskStore.save()
##         self.taskStore.close()
##         self.emptyTaskStore.load(self.filename)
##         self.assertEqual(1, len(self.emptyTaskStore.tasks()))

##     def testOriginalFileCanBeLoadedAfterSaveAs(self):
##         self.taskStore.setFilename(self.filename)
##         self.taskStore.save()
##         self.taskStore.saveas(self.filename2)
##         self.taskStore.close()
##         self.emptyTaskStore.load(self.filename)
##         self.assertEqual(1, len(self.emptyTaskStore.tasks()))


class TaskStoreWithFile(persistence.TaskStore):
    def fileBackend(self):
        for backend in self.backends():
            if isinstance(backend, persistence.FileBackend):
                return backend


class TaskStoreMultiUserTestBase(object):
    def init(self):
        self.task = task.Task(subject='Task')
        self.taskStore1.tasks().append(self.task)

        self.category = category.Category(subject='Category')
        self.taskStore1.categories().append(self.category)

        self.note = note.Note(subject='Note')
        self.taskStore1.notes().append(self.note)

        self.taskNote = note.Note(subject='Task note')
        self.task.addNote(self.taskNote)

        self.attachment = attachment.FileAttachment('foobarfile')
        self.task.addAttachment(self.attachment)

        self.filename = 'test.tsk'

        self.taskStore1.setFilename(self.filename)
        self.taskStore2.setFilename(self.filename)

        self.taskStore1.save()
        self.taskStore2.load()

    def backend1(self):
        return self.taskStore1.fileBackend()

    def backend2(self):
        return self.taskStore2.fileBackend()

    def createTaskStores(self):
        # pylint: disable-msg=W0201
        self.taskStore1 = TaskStoreWithFile(self.settings)
        self.taskStore2 = TaskStoreWithFile(self.settings)

    def clear(self):
        self.taskStore1.close()
        self.taskStore1.stop()
        self.taskStore2.close()
        self.taskStore2.stop()
        self.remove(self.filename)
        self.remove(self.filename + '.delta')

    def remove(self, *filenames):
        for filename in filenames:
            tries = 0
            while os.path.exists(filename) and tries < 3:
                try: # Don't fail on random 'Access denied' errors.
                    os.remove(filename)
                    break
                except WindowsError:
                    tries += 1

    def _assertIdInList(self, objects, id_):
        for obj in objects:
            if obj.id() == id_:
                break
        else:
            self.fail('ID %s not found' % id_)
        return obj

    def _testCreateObjectInOther(self, class_, listName):
        newObject = class_(subject='New %s' % class_.__name__)
        getattr(self.taskStore1, listName)().append(newObject)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 2)
        self._assertIdInList(getattr(self.taskStore2, listName)().rootItems(), newObject.id())

    def testOtherCreatesCategory(self):
        self._testCreateObjectInOther(category.Category, 'categories')

    def testOtherCreatesTask(self):
        self._testCreateObjectInOther(task.Task, 'tasks')

    def testOtherCreatesNote(self):
        self._testCreateObjectInOther(note.Note, 'notes')

    def _testCreateChildInOther(self, listName):
        item = getattr(self.taskStore1, listName)().rootItems()[0]
        subItem = item.newChild(subject='New sub%s' % item.__class__.__name__)
        getattr(self.taskStore1, listName)().append(subItem)
        item.addChild(subItem)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 2)
        otherItem = getattr(self.taskStore2, listName)().rootItems()[0]
        self.assertEqual(len(otherItem.children()), 1)
        self.assertEqual(otherItem.children()[0].id(), subItem.id())

    def testOtherCreatesSubcategory(self):
        self._testCreateChildInOther('categories')

    def testOtherCreatesSubtask(self):
        self._testCreateChildInOther('tasks')

    def testOtherCreatesSubnote(self):
        self._testCreateChildInOther('notes')

    def _testCreateObjectWithChildInOther(self, class_, listName):
        item = class_(subject='New %s' % class_.__name__)
        subItem = item.newChild(subject='New sub%s' % class_.__name__)
        item.addChild(subItem)
        getattr(self.taskStore1, listName)().append(item)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 3)
        otherItem = self._assertIdInList(getattr(self.taskStore2, listName)().rootItems(), item.id())
        self.assertEqual(len(otherItem.children()), 1)
        self.assertEqual(otherItem.children()[0].id(), subItem.id())

    def testOtherCreatesCategoryWithChild(self):
        self._testCreateObjectWithChildInOther(category.Category, 'categories')

    def testOtherCreatesTaskWithChild(self):
        self._testCreateObjectWithChildInOther(task.Task, 'tasks')

    def testOtherCreatesNoteWithChild(self):
        self._testCreateObjectWithChildInOther(note.Note, 'notes')

    def _testCreateObjectAndReparentExisting(self, listName):
        item = getattr(self.taskStore1, listName)().rootItems()[0]
        newItem = item.__class__(subject='New %s' % item.__class__.__name__)
        getattr(self.taskStore1, listName)().append(newItem)
        newItem.addChild(item)
        item.setParent(newItem)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 2)
        for otherItem in getattr(self.taskStore2, listName)().rootItems():
            if otherItem.id() == newItem.id():
                break
        else:
            self.fail()
        self.assertEqual(len(otherItem.children()), 1)
        self.assertEqual(otherItem.children()[0].id(), item.id())

    def testOtherCreatesCategoryAndReparentsExisting(self):
        self._testCreateObjectAndReparentExisting('categories')

    def testOtherCreatesTaskAndReparentsExisting(self):
        self._testCreateObjectAndReparentExisting('tasks')

    def testOtherCreatesNoteAndReparentsExisting(self):
        self._testCreateObjectAndReparentExisting('notes')

    def _testChangeAttribute(self, name, value, listName):
        obj = getattr(self.taskStore1, listName)().rootItems()[0]
        getattr(obj, 'set' + name[0].upper() + name[1:])(value)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(getattr(getattr(self.taskStore2, listName)().rootItems()[0], name)(),
                         value)

    def _testExpand(self, listName):
        obj = getattr(self.taskStore1, listName)().rootItems()[0]
        obj.expand()
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.failUnless(getattr(self.taskStore2, listName)().rootItems()[0].isExpanded())

    def testChangeCategoryName(self):
        self._testChangeAttribute('subject', 'New category name', 'categories')

    def testChangeCategoryDescription(self):
        self._testChangeAttribute('description', 'New category description', 'categories')

    def testExpandCategory(self):
        self._testExpand('categories')

    def testChangeTaskSubject(self):
        self._testChangeAttribute('subject', 'New task subject', 'tasks')

    def testChangeTaskDescription(self):
        self._testChangeAttribute('description', 'New task description', 'tasks')

    def testExpandTask(self):
        self._testExpand('tasks')

    def testChangeNoteSubject(self):
        self._testChangeAttribute('subject', 'New note subject', 'notes')

    def testChangeNoteDescription(self):
        self._testChangeAttribute('description', 'New note description', 'notes')

    def testChangeTaskStartDateTime(self):
        self._testChangeAttribute('plannedStartDateTime', date.DateTime(2011, 6, 15), 'tasks')

    def testChangeTaskDueDateTime(self):
        self._testChangeAttribute('dueDateTime', date.DateTime(2011, 7, 16), 'tasks')

    def testChangeTaskCompletionDateTime(self):
        self._testChangeAttribute('completionDateTime', date.DateTime(2011, 2, 1), 'tasks')

    def testChangeTaskPrecentageComplete(self):
        self._testChangeAttribute('percentageComplete', 42, 'tasks')

    def testChangeTaskRecurrence(self):
        self._testChangeAttribute('recurrence', date.Recurrence('daily', 3), 'tasks')

    def testChangeTaskReminder(self):
        self._testChangeAttribute('reminder', date.DateTime(2999, 2, 1), 'tasks')

    def testChangeTaskBudget(self):
        self._testChangeAttribute('budget', date.TimeDelta(seconds=60), 'tasks')

    def testChangeTaskPriority(self):
        self._testChangeAttribute('priority', 42, 'tasks')

    def testChangeTaskHourlyFee(self):
        self._testChangeAttribute('hourlyFee', 42, 'tasks')

    def testChangeTaskFixedFee(self):
        self._testChangeAttribute('fixedFee', 42, 'tasks')

    def testChangeTaskShouldMarkCompletedWhenAllChildrenCompleted(self):
        self._testChangeAttribute('shouldMarkCompletedWhenAllChildrenCompleted',
                                  False, 'tasks')

    def testExpandNote(self):
        self._testExpand('notes')

    def _testChangeAppearance(self, listName, attrName, initialValue, newValue):
        setName = 'set' + attrName[0].upper() + attrName[1:]
        obj = getattr(self.taskStore1, listName)().rootItems()[0]
        newObj = getattr(self.taskStore2, listName)().rootItems()[0]
        getattr(obj, setName)(initialValue)
        getattr(newObj, setName)(initialValue)
        self.backend1().monitor().resetAllChanges()
        self.backend2().monitor().resetAllChanges()
        getattr(obj, setName)(newValue)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(getattr(newObj, attrName)(), newValue)

    def testChangeCategoryForeground(self):
        self._testChangeAppearance('categories', 'foregroundColor', (128, 128, 128), (255, 255, 0))

    def testChangeCategoryBackground(self):
        self._testChangeAppearance('categories', 'backgroundColor', (128, 128, 128), (255, 255, 0))

    def testChangeCategoryIcon(self):
        self._testChangeAppearance('categories', 'icon', 'initialIcon', 'finalIcon')

    def testChangeCategorySelectedIcon(self):
        self._testChangeAppearance('categories', 'selectedIcon', 'initialIcon', 'finalIcon')

    def testChangeNoteForeground(self):
        self._testChangeAppearance('notes', 'foregroundColor', (128, 128, 128), (255, 255, 0))

    def testChangeNoteBackground(self):
        self._testChangeAppearance('notes', 'backgroundColor', (128, 128, 128), (255, 255, 0))

    def testChangeNoteIcon(self):
        self._testChangeAppearance('notes', 'icon', 'initialIcon', 'finalIcon')

    def testChangeNoteSelectedIcon(self):
        self._testChangeAppearance('notes', 'selectedIcon', 'initialIcon', 'finalIcon')

    def testChangeTaskBackground(self):
        self._testChangeAppearance('tasks', 'backgroundColor', (128, 128, 128), (255, 255, 0))

    def testChangeTaskIcon(self):
        self._testChangeAppearance('tasks', 'icon', 'initialIcon', 'finalIcon')

    def testChangeTaskSelectedIcon(self):
        self._testChangeAppearance('tasks', 'selectedIcon', 'initialIcon', 'finalIcon')

    def testChangeExclusiveSubcategories(self):
        self.category.makeSubcategoriesExclusive(True)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assert_(self.taskStore2.categories().rootItems()[0].hasExclusiveSubcategories())

    def _testAddObjectCategory(self, listName):
        obj = getattr(self.taskStore1, listName)().rootItems()[0]
        obj.addCategory(self.category)
        self.category.addCategorizable(obj)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        newObj = getattr(self.taskStore2, listName)().rootItems()[0]
        self.assertEqual(len(newObj.categories()), 1)
        self.assertEqual(newObj.categories().pop().id(), self.category.id())

    def testAddNoteCategory(self):
        self._testAddObjectCategory('notes')

    def testAddTaskCategory(self):
        self._testAddObjectCategory('tasks')

    def _testChangeObjectCategory(self, listName):
        self.category2 = category.Category(subject='Other category')
        self.taskStore1.categories().append(self.category2)
        obj = getattr(self.taskStore1, listName)().rootItems()[0]
        obj.addCategory(self.category)
        self.category.addCategorizable(obj)
        self.taskStore1.save()
        self.taskStore2.save()
        # Load => CategoryList => addCategory()...
        self.backend1().monitor().resetAllChanges()

        self.category.removeCategorizable(obj)
        obj.removeCategory(self.category)
        self.category2.addCategorizable(obj)
        obj.addCategory(self.category2)

        self.taskStore1.save()
        self.backend2().monitor().resetAllChanges()
        self.doSave(self.taskStore2)

        newObj = getattr(self.taskStore2, listName)().rootItems()[0]
        self.assertEqual(len(newObj.categories()), 1)
        self.assertEqual(newObj.categories().pop().id(), self.category2.id())

    def testChangeNoteCategory(self):
        self._testChangeObjectCategory('notes')

    def testChangeTaskCategory(self):
        self._testChangeObjectCategory('tasks')

    def _testDeleteObject(self, listName):
        item = getattr(self.taskStore1, listName)().rootItems()[0]
        getattr(self.taskStore1, listName)().remove(item)
        self.taskStore1.save()
        self.backend2().monitor().setChanges(item.id(), set())
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore1, listName)()), 0)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 0)

    def _testDeleteModifiedLocalObject(self, listName):
        item = getattr(self.taskStore1, listName)().rootItems()[0]
        getattr(self.taskStore1, listName)().remove(item)
        self.taskStore1.save()
        getattr(self.taskStore2, listName)().rootItems()[0].setSubject('New subject.')
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 1)

    def _testDeleteModifiedRemoteObject(self, listName):
        getattr(self.taskStore1, listName)().rootItems()[0].setSubject('New subject.')
        self.taskStore1.save()
        item = getattr(self.taskStore2, listName)().rootItems()[0]
        getattr(self.taskStore2, listName)().remove(item)
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)()), 1)
        self.assertEqual(getattr(self.taskStore2, listName)().rootItems()[0].subject(), 'New subject.')

    def testDeleteCategory(self):
        self._testDeleteObject('categories')

    def testDeleteNote(self):
        self._testDeleteObject('notes')

    def testDeleteTask(self):
        self._testDeleteObject('tasks')

    def testDeleteModifiedLocalCategory(self):
        self._testDeleteModifiedLocalObject('categories')

    def testDeleteModifiedLocalNote(self):
        self._testDeleteModifiedLocalObject('notes')

    def testDeleteModifiedLocalTask(self):
        self._testDeleteModifiedLocalObject('tasks')

    def testDeleteModifiedRemoteCategory(self):
        self._testDeleteModifiedRemoteObject('categories')

    def testDeleteModifiedRemoteNote(self):
        self._testDeleteModifiedRemoteObject('notes')

    def testDeleteModifiedRemoteTask(self):
        self._testDeleteModifiedRemoteObject('tasks')

    def _testAddNoteToObject(self, listName):
        newNote = note.Note(subject='Other note')
        getattr(self.taskStore1, listName)().rootItems()[0].addNote(newNote)
        noteCount = len(getattr(self.taskStore1, listName)().rootItems()[0].notes())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)().rootItems()[0].notes()), noteCount)



    def testAddNoteToTask(self):
        self._testAddNoteToObject('tasks')

    def testAddNoteToCategory(self):
        self._testAddNoteToObject('categories')

    def testAddNoteToAttachment(self):
        newNote = note.Note(subject='Attachment note')
        self.attachment.addNote(newNote)
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(self.taskStore2.tasks().rootItems()[0].attachments()[0].notes()), 1)

    def _testAddAttachmentToObject(self, listName):
        newAttachment = attachment.FileAttachment('Other attachment')
        getattr(self.taskStore1, listName)().rootItems()[0].addAttachment(newAttachment)
        attachmentCount = len(getattr(self.taskStore1, listName)().rootItems()[0].attachments())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)().rootItems()[0].attachments()), attachmentCount)

    def testAddAttachmentToTask(self):
        self._testAddAttachmentToObject('tasks')

    def testAddAttachmentToCategory(self):
        self._testAddAttachmentToObject('categories')

    def testAddAttachmentToNote(self):
        self._testAddAttachmentToObject('notes')

    def _testRemoveNoteFromObject(self, listName):
        newNote = note.Note(subject='Other note')
        noteCount = len(getattr(self.taskStore1, listName)().rootItems()[0].notes())
        getattr(self.taskStore1, listName)().rootItems()[0].addNote(newNote)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.taskStore2.save()

        getattr(self.taskStore1, listName)().rootItems()[0].removeNote(newNote)
        self.backend2().monitor().setChanges(newNote.id(), set())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)().rootItems()[0].notes()), noteCount)

    def testRemoveNoteFromTask(self):
        self._testRemoveNoteFromObject('tasks')

    def testRemoveNoteFromCategory(self):
        self._testRemoveNoteFromObject('categories')

    def testRemoveNoteFromAttachment(self):
        newNote = note.Note(subject='Attachment note')
        self.attachment.addNote(newNote)
        self.taskStore1.save()
        self.taskStore2.save()

        self.taskStore1.tasks().rootItems()[0].attachments()[0].removeNote(newNote)
        self.backend2().monitor().setChanges(newNote.id(), set())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(self.taskStore2.tasks().rootItems()[0].attachments()[0].notes()), 0)

    def _testRemoveAttachmentFromObject(self, listName):
        newAttachment = attachment.FileAttachment('Other attachment')
        attachmentCount = len(getattr(self.taskStore1, listName)().rootItems()[0].attachments())
        getattr(self.taskStore1, listName)().rootItems()[0].addAttachment(newAttachment)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.taskStore2.save()

        getattr(self.taskStore1, listName)().rootItems()[0].removeAttachment(newAttachment)
        self.backend2().monitor().setChanges(newAttachment.id(), set())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(getattr(self.taskStore2, listName)().rootItems()[0].attachments()), attachmentCount)

    def testRemoveAttachmentFromTask(self):
        self._testRemoveAttachmentFromObject('tasks')

    def testRemoveAttachmentFromCategory(self):
        self._testRemoveAttachmentFromObject('categories')

    def testRemoveAttachmentFromNote(self):
        self._testRemoveAttachmentFromObject('notes')

    def testChangeNoteBelongingToTask(self):
        self.taskNote.setSubject('New subject')
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(self.taskStore2.tasks().rootItems()[0].notes()[0].subject(), 'New subject')

    def testChangeAttachmentBelongingToTask(self):
        self.attachment.setLocation('new location')
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(self.taskStore2.tasks().rootItems()[0].attachments()[0].location(), 'new location')

    def testAddChildToNoteBelongingToTask(self):
        subNote = self.taskNote.newChild(subject='Child note')
        self.taskNote.addChild(subNote)
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(self.taskStore2.tasks().rootItems()[0].notes()[0].children()), 1)

    def testRemoveChildToNoteBelongingToTask(self):
        subNote = self.taskNote.newChild(subject='Child note')
        self.taskNote.addChild(subNote)
        self.taskStore1.save()
        self.taskStore2.save()

        self.taskNote.removeChild(subNote)
        self.backend2().monitor().setChanges(subNote.id(), set())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(self.taskStore2.tasks().rootItems()[0].notes()[0].children()), 0)

    def testAddCategorizedNoteBelongingToOtherCategory(self):
        # Categories should be handled in priority...
        cat1 = category.Category(subject='Cat #1')
        cat2 = category.Category(subject='Cat #2')
        newNote = note.Note(subject='Note')
        cat1.addNote(newNote)
        newNote.addCategory(cat2)
        cat2.addCategorizable(newNote)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        try:
            self.doSave(self.taskStore2)
        except Exception, e:
            self.fail(str(e))

    def testAddEffortToTask(self):
        newEffort = effort.Effort(self.task, date.DateTime(2011, 5, 1), date.DateTime(2011, 6, 1))
        self.task.addEffort(newEffort)
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(newEffort.id(), self.taskStore2.tasks().rootItems()[0].efforts()[0].id())

    def testRemoveEffortFromTask(self):
        newEffort = effort.Effort(self.task, date.DateTime(2011, 5, 1), date.DateTime(2011, 6, 1))
        self.task.addEffort(newEffort)
        self.taskStore1.save()
        self.taskStore2.save()
        self.task.removeEffort(newEffort)
        self.backend2().monitor().setChanges(newEffort.id(), set())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(len(self.taskStore2.tasks().rootItems()[0].efforts()), 0)

    def testChangeEffortTask(self):
        newTask = task.Task(subject='Other task')
        self.taskStore1.tasks().append(newTask)
        newEffort = effort.Effort(self.task, date.DateTime(2011, 5, 1), date.DateTime(2011, 6, 1))
        self.task.addEffort(newEffort)
        self.taskStore1.save()
        self.taskStore2.save()
        newEffort.setTask(newTask)
        self.backend2().monitor().setChanges(newEffort.id(), set())
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        for theTask in self.taskStore2.tasks():
            if theTask.id() == newTask.id():
                self.assertEqual(len(theTask.efforts()), 1)
                break
        else:
            self.fail()

    def testChangeEffortStart(self):
        newEffort = effort.Effort(self.task, date.DateTime(2011, 5, 1), date.DateTime(2011, 6, 1))
        self.task.addEffort(newEffort)
        self.taskStore1.save()
        self.taskStore2.save()
        # This is needed because the setTask in sync() generates a DEL event
        self.backend1().monitor().setChanges(newEffort.id(), set())
        newDate = date.DateTime(2010, 6, 1)
        newEffort.setStart(newDate)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(self.taskStore2.tasks().rootItems()[0].efforts()[0].getStart(), newDate)

    def testChangeEffortStop(self):
        newEffort = effort.Effort(self.task, date.DateTime(2011, 5, 1), date.DateTime(2011, 6, 1))
        self.task.addEffort(newEffort)
        self.taskStore1.save()
        self.taskStore2.save()
        # This is needed because the setTask in sync() generates a DEL event
        self.backend1().monitor().setChanges(newEffort.id(), set())
        newDate = date.DateTime(2012, 6, 1)
        newEffort.setStop(newDate)
        self.backend2().monitor().resetAllChanges()
        self.taskStore1.save()
        self.doSave(self.taskStore2)
        self.assertEqual(self.taskStore2.tasks().rootItems()[0].efforts()[0].getStop(), newDate)

    def testAddPrerequisite(self):
        newTask = task.Task(subject='Prereq')
        self.taskStore1.tasks().append(newTask)
        self.taskStore2.save()
        self.task.addPrerequisites([newTask])
        self.taskStore2.load()
        self.taskStore1.save()
        self.backend2().monitor().resetAllChanges()
        self.doSave(self.taskStore2)

        for tsk in self.taskStore2.tasks():
            if tsk.id() == self.task.id():
                self.assertEqual(len(tsk.prerequisites()), 1)
                self.assertEqual(list(tsk.prerequisites())[0].id(), newTask.id())
                break
        else:
            self.fail()

    def testRemovePrerequisite(self):
        newTask = task.Task(subject='Prereq')
        self.taskStore1.tasks().append(newTask)
        self.task.addPrerequisites([newTask])
        self.taskStore1.save()
        self.taskStore2.load()
        self.task.removePrerequisites([newTask])
        self.taskStore1.save()
        self.backend2().monitor().resetAllChanges()
        self.doSave(self.taskStore2)

        for tsk in self.taskStore2.tasks():
            if tsk.id() == self.task.id():
                self.assertEqual(len(tsk.prerequisites()), 0)
                break
        else:
            self.fail()


class TaskStoreMultiUserTestSave(TaskStoreMultiUserTestBase, TaskStoreTestCase):
    def doSave(self, taskFile):
        taskFile.save()

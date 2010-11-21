# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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

import wx, sys
import test
from taskcoachlib import gui, config, persistence
from taskcoachlib.domain import task, effort, date, note, attachment
from taskcoachlib.gui import uicommand


class DummyEvent(object):
    def Skip(self):
        pass


class TaskEditorSetterBase(object):
    def setSubject(self, newSubject):
        page = self.editor._interior[0]
        page._subjectEntry.SetFocus()
        page._subjectEntry.SetValue(newSubject)

    def setDescription(self, newDescription):
        page = self.editor._interior[0]
        page._descriptionEntry.SetFocus()
        page._descriptionEntry.SetValue(newDescription)

    def setReminder(self, newReminderDateTime):
        self.editor._interior[1].setReminder(newReminderDateTime)
        
    def setRecurrence(self, newRecurrence):
        page = self.editor._interior[1]
        page.setRecurrence(newRecurrence)
        page.onRecurrenceEdited(DummyEvent())


class TaskEditorBySettingFocusMixin(TaskEditorSetterBase):
    def setSubject(self, newSubject):
        super(TaskEditorBySettingFocusMixin, self).setSubject(newSubject)
        if '__WXGTK__' == wx.Platform: 
            page._subjectSync.onAttributeEdited(DummyEvent()) # pragma: no cover
        else:
            page._descriptionEntry.SetFocus() # pragma: no cover
        
    def setDescription(self, newDescription):
        super(TaskEditorBySettingFocusMixin, self).setDescription(newDescription)
        if '__WXGTK__' == wx.Platform:
            page._descriptionSync.onAttributeEdited(DummyEvent()) # pragma: no cover
        else:
            page._subjectEntry.SetFocus() # pragma: no cover


class TaskEditorByClosingMixin(TaskEditorSetterBase):
    def setSubject(self, newSubject):
        super(TaskEditorBySettingFocusMixin, self).setSubject(newSubject)
        self.editor.Close()

    def setDescription(self, newDescription):
        super(TaskEditorBySettingFocusMixin, self).setDescription(newDescription)
        self.editor.Close()


class TaskEditorTestCase(test.wxTestCase):
    def setUp(self):
        super(TaskEditorTestCase, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False)
        self.tomorrow = date.Now() + date.oneDay
        self.yesterday = date.Now() - date.oneDay
        self.taskFile = persistence.TaskFile()
        self.taskList = self.taskFile.tasks()
        self.effortList = self.taskFile.efforts()
        self.taskList.extend(self.createTasks())
        self.editor = self.createEditor()
        
    def createEditor(self):
        return gui.dialog.editor.TaskEditor(self.frame, self.getItems(),
            self.settings, self.taskList, self.taskFile, raiseDialog=False)

    def tearDown(self):
        # TaskEditor uses CallAfter for setting the focus, make sure those 
        # calls are dealt with, otherwise they'll turn up in other tests
        if '__WXMAC__' not in wx.PlatformInfo and ('__WXMSW__' not in wx.PlatformInfo or sys.version_info < (2, 5)):
            wx.Yield() # pragma: no cover 
        super(TaskEditorTestCase, self).tearDown()
        
    def createTasks(self):
        raise NotImplementedError # pragma: no cover
    
    def getItems(self):
        raise NotImplementedError # pragma: no cover


class EditorDisplayTest(TaskEditorTestCase):
    ''' Does the editor display the task data correctly when opened? '''
    
    def getItems(self):
        return [self.task]
    
    def createTasks(self):
        # pylint: disable-msg=W0201
        self.task = task.Task('Task to edit')
        self.task.setRecurrence(date.Recurrence('daily', amount=1))
        return [self.task]
    
    def testSubject(self):
        self.assertEqual('Task to edit',
			 self.editor._interior[0]._subjectEntry.GetValue())

    def testDueDateTime(self):
        self.assertEqual(date.DateTime(),
                         self.editor._interior[1]._dueDateTimeEntry.get())
        
    def testRecurrenceUnit(self):
        choice = self.editor._interior[1]._recurrenceEntry
        self.assertEqual('Daily', choice.GetString(choice.GetSelection()))

    def testRecurrenceFrequency(self):
        freq = self.editor._interior[1]._recurrenceFrequencyEntry
        self.assertEqual(1, freq.GetValue())    
        

class EditTaskTestBase(object):
    def getItems(self):
        return [self.task]

    def createTasks(self):
        # pylint: disable-msg=W0201
        self.task = task.Task('Task to edit')
        self.attachment = attachment.FileAttachment('some attachment')
        self.task.addAttachments(self.attachment) # pylint: disable-msg=E1101
        return [self.task]

    def testEditSubject(self):
        self.setSubject('Done')        
        self.assertEqual('Done', self.task.subject())

    def testEditDescription(self):
        self.setDescription('Description')
        self.assertEqual('Description', self.task.description())

    # pylint: disable-msg=W0212
    
    def testSetDueDateTime(self):
        self.editor._interior[1]._dueDateTimeEntry.set(self.tomorrow)
        self.assertAlmostEqual(self.tomorrow.toordinal(), 
                               self.task.dueDateTime().toordinal(),
                               places=2)

    def testSetStartDateTime(self):
        self.editor._interior[1]._startDateTimeEntry.set(self.tomorrow)
        self.assertAlmostEqual(self.tomorrow.toordinal(), 
                               self.task.startDateTime().toordinal(),
                               places=2)

    def testSetCompletionDateTime(self):
        self.editor._interior[1]._completionDateTimeEntry.set(self.tomorrow)
        self.assertAlmostEqual(self.tomorrow.toordinal(), 
                               self.task.completionDateTime().toordinal(),
                               places=2)

    def testSetUncompleted(self):
        self.editor._interior[1]._completionDateTimeEntry.set(date.Now())
        self.editor._interior[1]._completionDateTimeEntry.set(date.DateTime())
        self.assertEqual(date.DateTime(), self.task.completionDateTime())

    def testSetReminder(self):
        reminderDateTime = date.DateTime(2005,1,1)
        self.setReminder(reminderDateTime)
        self.assertEqual(reminderDateTime, self.task.reminder())

    def testSetRecurrence(self):
        self.setRecurrence(date.Recurrence('weekly'))
        self.assertEqual('weekly', self.task.recurrence().unit)
        
    def testSetDailyRecurrence(self):
        self.setRecurrence(date.Recurrence('daily', amount=1))
        self.assertEqual('daily', self.task.recurrence().unit)
        self.assertEqual(1, self.task.recurrence().amount)
        
    def testSetYearlyRecurrence(self):
        self.setRecurrence(date.Recurrence('yearly'))
        self.assertEqual('yearly', self.task.recurrence().unit)
        
    def testSetMaxRecurrence(self):
        self.setRecurrence(date.Recurrence('weekly', max=10))
        self.assertEqual(10, self.task.recurrence().max)
        
    def testSetRecurrenceFrequency(self):
        self.setRecurrence(date.Recurrence('weekly', amount=3))
        self.assertEqual(3, self.task.recurrence().amount)
        
    def testSetRecurrenceSameWeekday(self):
        self.setRecurrence(date.Recurrence('monthly', sameWeekday=True))
        self.failUnless(self.task.recurrence().sameWeekday)
        
    def testPriority(self):
        self.editor._interior[0]._priorityEntry.SetValue(45)
        self.assertEqual(45, self.editor._interior[0]._priorityEntry.GetValue())
        
    def testSetNegativePriority(self):
        self.editor._interior[0]._priorityEntry.SetValue(-1)
        self.editor._interior[0]._prioritySync.onAttributeEdited(DummyEvent())
        self.assertEqual(-1, self.task.priority())
        
    def testSetHourlyFee(self):
        self.editor._interior[5]._hourlyFeeEntry.set(100)
        self.editor._interior[5].onHourlyFeeEdited(DummyEvent())
        self.assertEqual(100, self.task.hourlyFee())

    def testSetFixedFee(self):
        self.editor._interior[5]._fixedFeeEntry.set(100.5)
        self.editor._interior[5].onFixedFeeEdited(DummyEvent())
        self.assertEqual(100.5, self.task.fixedFee())

    def testBehaviorMarkCompleted(self):
        page = self.editor._interior[3]
        page._markTaskCompletedEntry.SetStringSelection('Yes')
        page.onShouldMarkCompletedEdited(DummyEvent())
        self.assertEqual(True, 
                         self.task.shouldMarkCompletedWhenAllChildrenCompleted())

    def testAddAttachment(self):
        self.editor._interior[8].viewer.onDropFiles(self.task, ['filename'])
        # pylint: disable-msg=E1101
        self.failUnless('filename' in [att.location() for att in self.task.attachments()])
        self.failUnless('filename' in [att.subject() for att in self.task.attachments()])
        
    def testRemoveAttachment(self):
        self.editor._interior[8].viewer.select(self.task.attachments())
        self.editor._interior[8].viewer.deleteItemCommand().do()
        self.assertEqual([], self.task.attachments()) # pylint: disable-msg=E1101

    def testOpenAttachmentWithNonAsciiFileNameThrowsException(self): # pragma: no cover
        ''' os.startfile() does not accept unicode filenames. This will be 
            fixed in Python 2.5. This test will fail if the bug is fixed. '''
        self.errorMessage = ''  # pylint: disable-msg=W0201
        def onError(*args, **kwargs): # pylint: disable-msg=W0613
            self.errorMessage = args[0]
        att = attachment.FileAttachment(u'tÃƒÂ©st.ÃƒÂ©')
        openAttachment = uicommand.AttachmentOpen(\
            viewer=self.editor._interior[6].viewer,
            attachments=attachment.AttachmentList([att]),
            settings=self.settings)
        openAttachment.doCommand(None, showerror=onError)
        if '__WXMSW__' in wx.PlatformInfo: # pragma: no cover
            if sys.version_info < (2,5):
                errorMessageStart = "'ascii' codec can't encode character"
            else:
                errorMessageStart = ''
        elif '__WXMAC__' in wx.PlatformInfo and sys.version_info >= (2,5):
            errorMessageStart = '' # pragma: no cover
        elif '__WXGTK__' in wx.PlatformInfo: # pragma: no cover
            errorMessageStart = ''
        else:
            errorMessageStart = '[Error 2] '
        self.failUnless(self.errorMessage.startswith(errorMessageStart))

    def testAddNote(self):
        viewer = self.editor._interior[7].viewer
        viewer.newItemCommand(viewer.presentation()).do()
        self.assertEqual(1, len(self.task.notes()))
        
    def testAddNoteWithSubnote(self):
        parent = note.Note(subject='New note')
        child = note.Note(subject='Child')
        parent.addChild(child)
        child.setParent(parent)
        viewer = self.editor._interior[7].viewer
        viewer.newItemCommand(viewer.presentation()).do()
        viewer.newSubItemCommandClass()(list=viewer.presentation(), 
                                        items=viewer.presentation()).do()
        # Only the parent note should be added to the notes list:
        self.assertEqual(1, len(self.task.notes())) 


class EditTaskTestBySettingFocus(TaskEditorBySettingFocusMixin, EditTaskTestBase, TaskEditorTestCase):
    pass


class EditTaskTestByClosing(TaskEditorByClosingMixin, EditTaskTestBase, TaskEditorTestCase):
    pass


class EditTaskWithChildrenTestBase(object):
    def getItems(self):
        return [self.parent]

    def createTasks(self):
        # pylint: disable-msg=W0201
        self.parent = task.Task('Parent', startDateTime=date.Now())
        self.child = task.Task('Child', startDateTime=date.Now())
        self.parent.addChild(self.child)
        return [self.parent] # self.child is added to tasklist automatically

    def testEditSubject(self):
        self.setSubject('New Parent Subject')
        self.assertEqual('New Parent Subject', self.parent.subject())

    # pylint: disable-msg=W0212
    
    def testChangeDueDateTimeOfParentAffectsChildToo(self):
        self.editor._interior[1]._dueDateTimeEntry.set(self.yesterday)
        self.assertAlmostEqual(self.yesterday.toordinal(), 
                               self.child.dueDateTime().toordinal(), places=2)

    def testChangeStartDateTimeOfParentHasNoEffectOnChild(self):
        self.editor._interior[1]._startDateTimeEntry.set(self.tomorrow)
        self.assertAlmostEqual(self.tomorrow.toordinal(), 
                               self.child.startDateTime().toordinal(),
                               places=2)


class EditTaskWithChildrenTestBySettingFocus(TaskEditorBySettingFocusMixin, EditTaskWithChildrenTestBase, TaskEditorTestCase):
    pass


class EditTaskWithChildrenTestByClosing(TaskEditorByClosingMixin, EditTaskWithChildrenTestBase, TaskEditorTestCase):
    pass


class EditTaskWithEffortTest(TaskEditorTestCase):    
    def getItems(self):
        return [self.task]

    def createTasks(self):
        self.task = task.Task('task') # pylint: disable-msg=W0201
        self.task.addEffort(effort.Effort(self.task))
        return [self.task]
    
    def testEffortIsShown(self):
        self.assertEqual(1, self.editor._interior[6].viewer.widget.GetItemCount())
                                  
        
class FocusTest(TaskEditorTestCase):
    def createTasks(self):
        self.task = task.Task('Task to edit')
        return [self.task]
    
    def getItems(self):
        return [self.task]

    def testFocus(self):
        if '__WXMAC__' not in wx.PlatformInfo and ('__WXMSW__' not in wx.PlatformInfo or sys.version_info < (2, 5)):
            wx.Yield() # pragma: no cover
        # pylint: disable-msg=W0212
        self.assertEqual(self.editor._interior[0]._subjectEntry, wx.Window_FindFocus())

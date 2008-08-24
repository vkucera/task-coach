# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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
from unittests import dummy
from taskcoachlib import gui, command, config, widgets
from taskcoachlib.domain import task, effort, date, category, note, attachment


class DummyViewer:
    def __init__(self):
        self.taskList = task.TaskList()

    def extend(self, *args):
        self.taskList.extend(*args)

    def select(self, *args):
        pass

    def curselection(self, *args, **kwargs):
        return self.taskList

    def __getitem__(self, index):
        return self.taskList[index]


class DummyEvent:
    def __init__(self, checked):
        self._checked = checked

    def IsChecked(self):
        return self._checked


class TaskEditorTestCase(test.wxTestCase):
    def setUp(self):
        super(TaskEditorTestCase, self).setUp()
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.taskList.extend(self.createTasks())
        self.settings = config.Settings(load=False)
        self.editor = self.createEditor()
        
    def createEditor(self):
        categories = category.CategoryList()
        return gui.dialog.editor.TaskEditor(self.frame, self.createCommand(),
            self.taskList, self.settings, categories, raiseDialog=False)

    def tearDown(self):
        # TaskEditor uses CallAfter for setting the focus, make sure those 
        # calls are dealt with, otherwise they'll turn up in other tests
        if '__WXMAC__' not in wx.PlatformInfo and ('__WXMSW__' not in wx.PlatformInfo or sys.version_info < (2, 5)):
            wx.Yield() 
        super(TaskEditorTestCase, self).tearDown()
        
    def createTasks(self):
        return []

    def setSubject(self, newSubject, index=0):
        self.editor[index][0].setSubject(newSubject)

    def setDescription(self, newDescription, index=0):
        self.editor[index][0].setDescription(newDescription)

    def setReminder(self, newReminderDateTime, index=0):
        self.editor[index][1].setReminder(newReminderDateTime)
        
    def setRecurrence(self, newRecurrence, index=0):
        self.editor[index][1].setRecurrence(newRecurrence)

    def setMaxRecurrenceCount(self, maxRecurrence, index=0):
        self.editor[index][1].setMaxRecurrenceCount(maxRecurrence)
        
    def setRecurrenceFrequency(self, recurrenceFrequency, index=0):
        self.editor[index][1].setRecurrenceFrequency(recurrenceFrequency)
                

class NewTaskTest(TaskEditorTestCase):
    def createCommand(self):
        newTaskCommand = command.NewTaskCommand(self.taskList)
        self.task = newTaskCommand.items[0]
        return newTaskCommand

    def testCreate(self):
        self.assertEqual('New task', self.editor[0][0]._subjectEntry.GetValue())
        self.assertEqual(date.Date(), self.editor[0][1]._dueDateEntry.get())

    def testOk(self):
        self.setSubject('Done')
        self.editor.ok()
        self.assertEqual('Done', self.task.subject())

    def testCancel(self):
        self.setSubject('Done')
        self.editor.cancel()
        self.assertEqual('New task', self.task.subject())

    def testDueDate(self):
        self.editor[0][1]._dueDateEntry.set(date.Today())
        self.editor.ok()
        self.assertEqual(date.Today(), self.task.dueDate())

    def testSetCompleted(self):
        self.editor[0][1]._completionDateEntry.set(date.Today())
        self.editor.ok()
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetUncompleted(self):
        self.editor[0][1]._completionDateEntry.set(date.Today())
        self.editor[0][1]._completionDateEntry.set(date.Date())
        self.editor.ok()
        self.assertEqual(date.Date(), self.task.completionDate())

    def testSetDescription(self):
        self.setDescription('Description')
        self.editor.ok()
        self.assertEqual('Description', self.task.description())

    def testSetReminder(self):
        reminderDateTime = date.DateTime(2005,1,1)
        self.setReminder(reminderDateTime)
        self.editor.ok()
        self.assertEqual(reminderDateTime, self.task.reminder())
        
    def testSetRecurrence(self):
        self.setRecurrence(date.Recurrence('weekly'))
        self.editor.ok()
        self.assertEqual('weekly', self.task.recurrence().unit)
        
    def testSetYearlyRecurrence(self):
        self.setRecurrence(date.Recurrence('yearly'))
        self.editor.ok()
        self.assertEqual('yearly', self.task.recurrence().unit)
        
    def testSetMaxRecurrence(self):
        self.setRecurrence(date.Recurrence('weekly', max=10))
        self.editor.ok()
        self.assertEqual(10, self.task.recurrence().max)
        
    def testSetRecurrenceFrequency(self):
        self.setRecurrence(date.Recurrence('weekly', amount=3))
        self.editor.ok()
        self.assertEqual(3, self.task.recurrence().amount)
        
    def testSetRecurrenceSameWeekday(self):
        self.setRecurrence(date.Recurrence('monthly', sameWeekday=True))
        self.editor.ok()
        self.failUnless(self.task.recurrence().sameWeekday)
    
    def testOpenAttachmentWithNonAsciiFileNameThrowsException(self):
        ''' os.startfile() does not accept unicode filenames. This will be 
            fixed in Python 2.5. This test will fail if the bug is fixed. '''
        self.errorMessage = ''
        def onError(*args, **kwargs):
            self.errorMessage = args[0]
        att = attachment.FileAttachment(u'tÃƒÂ©st.ÃƒÂ©')
        id_ = wx.NewId()
        item = wx.ListItem()
        item.SetId(0)
        item.SetText(unicode(att))
        item.SetData(id_)
        item.SetState(wx.LIST_STATE_SELECTED)
        self.editor[0][5]._listCtrl.InsertItem(item)
        self.editor[0][5]._listData[id_] = att
        self.editor[0][5].onOpen(None, showerror=onError)
        if '__WXMSW__' in wx.PlatformInfo and sys.version_info < (2,5):
            errorMessageStart = "'ascii' codec can't encode character"
        elif '__WXMAC__' in wx.PlatformInfo and sys.version_info >= (2,5):
            errorMessageStart = ""    
        elif '__WXGTK__' in wx.PlatformInfo:
            errorMessageStart = ""
        else:
            errorMessageStart = "[Error 2] "
        self.failUnless(self.errorMessage.startswith(errorMessageStart))

    def testAddNote(self):
        self.editor[0][4].noteContainer.append(note.Note('New note'))
        self.editor.ok()
        self.assertEqual(1, len(self.task.notes()))
        
    def testAddNoteWithSubnote(self):
        parent = note.Note('New note')
        child = note.Note('Child')
        parent.addChild(child)
        child.setParent(parent)
        self.editor[0][4].noteContainer.extend([parent, child])
        self.editor.ok()
        # Only the parent note should be added to the notes list:
        self.assertEqual(1, len(self.task.notes())) 
        

class NewSubTaskTest(TaskEditorTestCase):
    def createCommand(self):
        newSubTaskCommand = command.NewSubTaskCommand(self.taskList, [self.task])
        self.subtask = newSubTaskCommand.items[0]
        return newSubTaskCommand

    def createTasks(self):
        self.task = task.Task()
        return [self.task]

    def testOk(self):
        self.editor.ok()
        self.assertEqual([self.subtask], self.task.children())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual([], self.task.children())


class EditTaskTest(TaskEditorTestCase):
    def setUp(self):
        super(EditTaskTest, self).setUp()
        self.setSubject('Done')

    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task])

    def createTasks(self):
        self.task = task.Task('Task to edit')
        self.task.addAttachments(attachment.FileAttachment('some attachment'))
        return [self.task]

    def testOk(self):
        self.editor.ok()
        self.assertEqual('Done', self.task.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Task to edit', self.task.subject())

    def testSetDueDate(self):
        self.editor[0][1]._dueDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Tomorrow(), self.task.dueDate())

    def testSetStartDate(self):
        self.editor[0][1]._startDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Tomorrow(), self.task.startDate())
        
    def testSetNegativePriority(self):
        self.editor[0][0]._prioritySpinner.SetValue(-1)
        self.editor.ok()
        self.assertEqual(-1, self.task.priority())
        
    def testSetHourlyFee(self):
        self.editor[0][3]._hourlyFeeEntry.set(100)
        self.editor.ok()
        self.assertEqual(100, self.task.hourlyFee())

    def testSetFixedFee(self):
        self.editor[0][3]._fixedFeeEntry.set(100.5)
        self.editor.ok()
        self.assertEqual(100.5, self.task.fixedFee())

    def XXXtestAddCategory(self): # FIXME
        self.editor[0][2]._textEntry.SetValue('New category')
        self.editor[0][2]._textEntry.onEnter()
        self.assertEqual('New category', self.editor[0][2]._checkListBox.GetString(0))
        
    def testBehaviorMarkCompleted(self):
        self.editor[0][6]._markTaskCompletedEntry.SetStringSelection('Yes')
        self.editor.ok()
        self.assertEqual(True, self.task.shouldMarkCompletedWhenAllChildrenCompleted)

    def testAddAttachment(self):
        self.editor[0][5].onFileDrop(0, 0, ['filename'])
        self.editor.ok()
        self.failUnless('filename' in map(unicode, self.task.attachments()))
        
    def testRemoveAttachment(self):
        self.editor[0][5]._listCtrl.DeleteItem(0)
        self.editor.ok()
        self.assertEqual([], self.task.attachments())


class EditMultipleTasksTest(TaskEditorTestCase):
    def setUp(self):
        super(EditMultipleTasksTest, self).setUp()
        self.setSubject('TaskA', 0)
        self.setSubject('TaskB', 1)

    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task1, self.task2])

    def createTasks(self):
        self.task1 = task.Task('Task1')
        self.task2 = task.Task('Task2')
        return [self.task1, self.task2]

    def testOk(self):
        self.editor.ok()
        self.assertEqual('TaskA', self.task1.subject())
        self.assertEqual('TaskB', self.task2.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Task1', self.task1.subject())
        self.assertEqual('Task2', self.task2.subject())


class EditTaskWithChildrenTest(TaskEditorTestCase):
    def setUp(self):
        super(EditTaskWithChildrenTest, self).setUp()
        self.setSubject('TaskA', 0)
        self.setSubject('TaskB', 1)

    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.parent, self.child])

    def createTasks(self):
        self.parent = task.Task('Parent')
        self.child = task.Task('Child')
        self.parent.addChild(self.child)
        return [self.parent] # self.child is added to tasklist automatically

    def testOk(self):
        self.editor.ok()
        self.assertEqual('TaskA', self.parent.subject())
        self.assertEqual('TaskB', self.child.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Parent', self.parent.subject())
        self.assertEqual('Child', self.child.subject())

    def testChangeDueDateOfParentHasNoEffectOnChild(self):
        self.editor[0][1]._dueDateEntry.set(date.Yesterday())
        self.editor.ok()
        self.assertEqual(date.Date(), self.child.dueDate())

    def testChangeStartDateOfParentHasNoEffectOnChild(self):
        self.editor[0][1]._startDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Today(), self.child.startDate())


class EditTaskWithEffortTest(TaskEditorTestCase):    
    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task])

    def createTasks(self):
        self.task = task.Task('task')
        self.task.addEffort(effort.Effort(self.task))
        return [self.task]
    
    def testEffortIsShown(self):
        self.assertEqual(1, self.editor[0][4].effortViewer.widget.GetItemCount())
                          
    def testCancel(self):
        self.editor.cancel()
        self.assertEqual(1, len(self.task.efforts()))
        
        
class FocusTest(TaskEditorTestCase):
    def createCommand(self):
        return command.NewTaskCommand(self.taskList)

    def testFocus(self):
        if '__WXMAC__' not in wx.PlatformInfo and ('__WXMSW__' not in wx.PlatformInfo or sys.version_info < (2, 5)):
            wx.Yield()
        self.assertEqual(self.editor[0][0]._subjectEntry, wx.Window_FindFocus())


class EffortEditorTest(TaskEditorTestCase):      
    def createCommand(self):
        return command.EditEffortCommand(self.effortList, self.effortList)
        
    def createTasks(self):
        self.task1 = task.Task('task1')
        self.effort = effort.Effort(self.task1)
        self.task1.addEffort(self.effort)
        self.task2 = task.Task('task2')
        return [self.task1, self.task2]
    
    def createEditor(self):
        return gui.dialog.editor.EffortEditor(self.frame, self.createCommand(), 
            self.effortList, self.taskList, self.settings, raiseDialog=False)
    
    def testCreate(self):
        self.assertEqual(self.effort.getStart().date(), 
            self.editor[0]._startEntry.GetValue().date())
        self.assertEqual(self.effort.task().subject(), 
            self.editor[0]._taskEntry.GetValue())

    def testOK(self):
        stop = self.effort.getStop()
        self.editor.ok()
        self.assertEqual(stop, self.effort.getStop())
        
    def testInvalidEffort(self):
        self.effort.setStop(date.DateTime(1900, 1, 1))
        self.editor = self.createEditor()
        self.editor._interior[0].preventNegativeEffortDuration()
        self.failIf(self.editor._buttonBox['OK'].IsEnabled())
        
    def testChangeTask(self):
        self.editor[0]._taskEntry.SetStringSelection('task2')
        self.editor.ok()
        self.assertEqual(self.task2, self.effort.task())
        self.failIf(self.effort in self.task1.efforts())

import test, asserts, command, gui, dummy, patterns
import domain.task as task
import domain.effort as effort
import domain.date as date

class EffortCommandTestCase(test.wxTestCase, asserts.CommandAsserts):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.originalTask = task.Task()
        self.taskList.append(self.originalTask)
        self.originalStop = date.DateTime.now() 
        self.originalStart = self.originalStop - date.TimeDelta(hours=1) 
        self.effort = effort.Effort(self.originalTask, self.originalStart, 
                                    self.originalStop)
        self.originalTask.addEffort(self.effort)

    def undo(self):
        patterns.CommandHistory().undo()
        
    def redo(self):
        patterns.CommandHistory().redo()


class NewEffortCommandTest(EffortCommandTestCase):        
    def testNewEffort(self):
        newEffortCommand = command.NewEffortCommand(self.effortList, 
                                                    [self.originalTask])
        newEffortCommand.do()
        newEffort = newEffortCommand.efforts[0]
        self.assertDoUndoRedo(
            lambda: self.failUnless(newEffort in self.originalTask.efforts()),
            lambda: self.assertEqual([self.effort], self.originalTask.efforts()))

        
class EditEffortCommandTest(EffortCommandTestCase):
    def testEditStartDateTime(self):
        edit = command.EditEffortCommand(self.effortList, [self.effort])
        expected = date.DateTime(2000,1,1)
        edit.items[0].setStart(expected)
        edit.do()
        self.assertDoUndoRedo(
            lambda: self.assertEqual(expected, self.effort.getStart()),
            lambda: self.assertEqual(self.originalStart, self.effort.getStart()))

    def testEditTask(self):
        edit = command.EditEffortCommand(self.effortList, [self.effort])
        expected = task.Task()
        edit.items[0].setTask(expected)
        edit.do()
        self.assertDoUndoRedo(
            lambda: self.assertEqual(expected, self.effort.task()),
            lambda: self.assertEqual(self.originalTask, self.effort.task()))


class EditEffortCommandNotificationTest(EffortCommandTestCase):
    def setUp(self):
        super(EditEffortCommandNotificationTest, self).setUp()
        self.originalTask.registerObserver(self.onNotify)
        self.edit = command.EditEffortCommand(self.effortList, [self.effort])
        newTask = task.Task()
        newTask.registerObserver(self.onNotify)
        self.edit.items[0].setTask(newTask)
        self.edit.do()        
    
    def clearNotifications(self):           
        self.notifiedOfEffortRemoved = False
        self.notifiedOfEffortAdded = False
        
    def onNotify(self, notification, *args, **kwargs):
        if notification.effortsRemoved:
            self.notifiedOfEffortRemoved = True
        elif notification.effortsAdded:
            self.notifiedOfEffortAdded = True
            
    def assertNotifiedOfEffortsAddedAndRemoved(self):
        self.failUnless(self.notifiedOfEffortRemoved and \
                        self.notifiedOfEffortAdded)
            
    def testEditTaskNotifiesOldAndNewTaskAfterDo(self):
        self.assertNotifiedOfEffortsAddedAndRemoved()
        
    def testEditTaskNotifiesOldAndNewTaskAfterUndo(self):
        self.clearNotifications()
        self.edit.undo()
        self.assertNotifiedOfEffortsAddedAndRemoved()

    def testEditTaskNotifiesOldAndNewTaskAfterRedo(self):
        self.edit.undo()
        self.clearNotifications()
        self.edit.redo()
        self.assertNotifiedOfEffortsAddedAndRemoved()
        

class StartAndStopEffortCommandTest(EffortCommandTestCase):
    def setUp(self):
        super(StartAndStopEffortCommandTest, self).setUp()
        self.start = command.StartEffortCommand(self.taskList, [self.originalTask])
        self.start.do()
        
    def testStart(self):
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.originalTask.isBeingTracked()),
            lambda: self.failIf(self.originalTask.isBeingTracked()))
                        
    def testStop(self):
        stop = command.StopEffortCommand(self.taskList)
        stop.do()
        self.assertDoUndoRedo(
            lambda: self.failIf(self.originalTask.isBeingTracked()),
            lambda: self.failUnless(self.originalTask.isBeingTracked()))
                
    def testStartStopsPreviousStart(self):
        task2 = task.Task()
        start = command.StartEffortCommand(self.taskList, [task2])
        start.do()
        self.assertDoUndoRedo(
            lambda: self.failIf(self.originalTask.isBeingTracked()),
            lambda: self.failUnless(self.originalTask.isBeingTracked()))

import test, asserts, command, effort, gui, task, dummy, patterns, date

class EffortCommandTestCase(test.wxTestCase, asserts.CommandAsserts):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.task = task.Task()
        self.taskList.append(self.task)
        self.originalStop = date.DateTime.now() 
        self.originalStart = self.originalStop - date.TimeDelta(hours=1) 
        self.effort = effort.Effort(self.task, self.originalStart, self.originalStop)
        self.task.addEffort(self.effort)

    def undo(self):
        patterns.CommandHistory().undo()
        
    def redo(self):
        patterns.CommandHistory().redo()
           
class NewEffortCommandTest(EffortCommandTestCase):        
    def testNewEffort(self):
        newEffortCommand = command.NewEffortCommand(self.effortList, [self.task])
        newEffortCommand.do()
        newEffort = newEffortCommand.efforts[0]
        self.assertDoUndoRedo(
            lambda: self.failUnless(newEffort in self.task.efforts()),
            lambda: self.assertEqual([self.effort], self.task.efforts()))
            
        
class EditEffortCommandTest(EffortCommandTestCase):
    def testEditEffort(self):
        edit = command.EditEffortCommand(self.effortList, [self.effort])
        expected = date.DateTime(2000,1,1)
        edit.items[0].setStart(expected)
        edit.do()
        self.assertDoUndoRedo(
            lambda: self.assertEqual(expected, self.effort.getStart()),
            lambda: self.assertEqual(self.originalStart, self.effort.getStart()))


class DeleteEffortCommandTest(EffortCommandTestCase):
    def testDeleteEffort(self):
        delete = command.DeleteEffortCommand(self.effortList, [self.effort])
        delete.do()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([], self.task.efforts()),
            lambda: self.assertEqual([self.effort], self.task.efforts()))

class StartAndStopEffortCommandTest(EffortCommandTestCase):
    def setUp(self):
        super(StartAndStopEffortCommandTest, self).setUp()
        self.start = command.StartEffortCommand(self.taskList, [self.task])
        self.start.do()
        
    def testStart(self):
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task.isBeingTracked()),
            lambda: self.failIf(self.task.isBeingTracked()))
                        
    def testStop(self):
        stop = command.StopEffortCommand(self.taskList)
        stop.do()
        self.assertDoUndoRedo(
            lambda: self.failIf(self.task.isBeingTracked()),
            lambda: self.failUnless(self.task.isBeingTracked()))
                
    def testStartStopsPreviousStart(self):
        task2 = task.Task()
        start = command.StartEffortCommand(self.taskList, [task2])
        start.do()
        self.assertDoUndoRedo(
            lambda: self.failIf(self.task.isBeingTracked()),
            lambda: self.failUnless(self.task.isBeingTracked()))
            
 
class StartFromEndOfLastEffortCommandTest(EffortCommandTestCase):
    def setUp(self):
        super(StartFromEndOfLastEffortCommandTest, self).setUp()
        self.start = command.StartEffortCommand(self.taskList, [self.task],
            adjacent=True)
        self.start.do()
 
    def testStartFromEndOfLastEffort(self):
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task.isBeingTracked()),
            lambda: self.failIf(self.task.isBeingTracked()))
                   
    def testStartFromEndOfLastEffortAndStop(self):
        stop = command.StopEffortCommand(self.taskList)
        stop.do()
        self.assertEqual(self.task.efforts()[0].getStop(), self.task.efforts()[-1].getStart())
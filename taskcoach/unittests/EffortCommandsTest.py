import test, asserts, command, effort, gui, task, dummy, patterns, date

class EffortCommandTestCase(test.wxTestCase, asserts.CommandAsserts):
    def setUp(self):
        self.effortList = effort.EffortList()
        self.task = task.Task()
        self.originalStop = date.DateTime.now() 
        self.originalStart = self.originalStop - date.TimeDelta(hours=1) 
        self.effort = effort.Effort(self.task, self.originalStart, self.originalStop)
        self.effortList.append(self.effort)

    def undo(self):
        patterns.CommandHistory().undo()
        
    def redo(self):
        patterns.CommandHistory().redo()
           
class NewEffortCommandTest(EffortCommandTestCase):
    def testNewEffort(self):
        command.NewEffortCommand(self.effortList, [self.task]).do()
        newEffort = self.effortList[0]
        self.assertDoUndoRedo(
            lambda: self.failUnless(newEffort in self.effortList),
            lambda: self.assertEqual([self.effort], self.effortList))
        
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
            lambda: self.assertEqual([], self.effortList),
            lambda: self.assertEqual([self.effort], self.effortList))

class StartAndStopEffortCommandTest(EffortCommandTestCase):
    def setUp(self):
        super(StartAndStopEffortCommandTest, self).setUp()
        self.start = command.StartEffortCommand(self.effortList, [self.task])
        self.start.do()
        
    def testStart(self):
        self.assertDoUndoRedo(
            lambda: self.assertEqual([self.task], self.effortList.getActiveTasks()),
            lambda: self.assertEqual([], self.effortList.getActiveTasks()))

    def testStop(self):
        stop = command.StopEffortCommand(self.effortList)
        stop.do()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([], self.effortList.getActiveTasks()),
            lambda: self.assertEqual([self.task], self.effortList.getActiveTasks()))
                        
    def testStartStopsPreviousStart(self):
        task2 = task.Task()
        start = command.StartEffortCommand(self.effortList, [task2])
        start.do()
        self.assertDoUndoRedo(
            lambda: self.assertEqual(3, len(self.effortList)),
            lambda: self.assertEqual(2, len(self.effortList)))           
    
 
class StartFromEndOfLastEffortCommandTest(EffortCommandTestCase):
    def setUp(self):
        super(StartFromEndOfLastEffortCommandTest, self).setUp()
        self.start = command.StartEffortCommand(self.effortList, [self.task],
            adjacent=True)
        self.start.do()
 
    def testStartFromEndOfLastEffort(self):
        self.assertDoUndoRedo(
            lambda: self.assertEqual([self.task], self.effortList.getActiveTasks()),
            lambda: self.assertEqual([], self.effortList.getActiveTasks()))
                   
    def testStartFromEndOfLastEffortAndStop(self):
        stop = command.StopEffortCommand(self.effortList)
        stop.do()
        self.assertEqual(self.effortList[0].getStop(), self.effortList[-1].getStart())
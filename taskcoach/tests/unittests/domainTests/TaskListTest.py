import test, sets, patterns
import unittests.asserts as asserts
import domain.task as task
import domain.effort as effort
import domain.date as date

class TaskListTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task1 = task.Task(dueDate=date.Date(2010,1,1))
        self.task2 = task.Task(dueDate=date.Date(2011,1,1))
        self.task3 = task.Task()
    
    def testNrCompleted(self):
        self.assertEqual(0, self.taskList.nrCompleted())
        self.taskList.append(self.task1)
        self.assertEqual(0, self.taskList.nrCompleted())
        self.task1.setCompletionDate()
        self.assertEqual(1, self.taskList.nrCompleted())
    
    def testNrOverdue(self):
        self.assertEqual(0, self.taskList.nrOverdue())
        self.taskList.append(self.task1)
        self.assertEqual(0, self.taskList.nrOverdue())
        self.task1.setDueDate(date.Date(1990, 1, 1))
        self.assertEqual(1, self.taskList.nrOverdue())

    def testAllCompleted(self):
        self.failIf(self.taskList.allCompleted())
        self.task1.setCompletionDate()
        self.taskList.append(self.task1)
        self.failUnless(self.taskList.allCompleted())

    def testNrDueToday(self):
        self.assertEqual(0, self.taskList.nrDueToday())
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertEqual(1, self.taskList.nrDueToday())
        
    def testNrBeingTracked(self):
        self.assertEqual(0, self.taskList.nrBeingTracked())
        activeTask = task.Task()
        activeTask.addEffort(effort.Effort(activeTask))
        self.taskList.append(activeTask)
        self.assertEqual(1, self.taskList.nrBeingTracked())

    def testMinDate_EmptyTaskList(self):
        self.assertEqual(date.Date(), self.taskList.minDate())
        
    def testMinDate_TaskWithoutDates(self):
        self.taskList.append(task.Task(startDate=date.Date()))
        self.assertEqual(date.Date(), self.taskList.minDate())
        
    def testMinDate_TaskWithStartDate(self):
        self.taskList.append(task.Task())
        self.assertEqual(date.Today(), self.taskList.minDate())
        
    def testMinDate_TaskWithDueDate(self):
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.assertEqual(date.Yesterday(), self.taskList.minDate())

    def testMinDate_TaskWithCompletionDate(self):
        self.taskList.append(task.Task(completionDate=date.Yesterday()))
        self.assertEqual(date.Yesterday(), self.taskList.minDate())

    def testMaxDate_EmptyTaskList(self):
        self.assertEqual(date.Date(), self.taskList.maxDate())
        
    def testMaxDate_TaskWithoutDates(self):
        self.taskList.append(task.Task(startDate=date.Date()))
        self.assertEqual(date.Date(), self.taskList.maxDate())
        
    def testMaxDate_TaskWithStartDate(self):
        self.taskList.append(task.Task())
        self.assertEqual(date.Today(), self.taskList.maxDate())

    def testMaxDate_TaskWithDueDate(self):
        self.taskList.append(task.Task(dueDate=date.Tomorrow()))
        self.assertEqual(date.Tomorrow(), self.taskList.maxDate())
    
    def testMaxDate_TaskWithCompletionDate(self):
        self.taskList.append(task.Task(completionDate=date.Tomorrow()))
        self.assertEqual(date.Tomorrow(), self.taskList.maxDate())
        
    def testOriginalLength(self):
        self.assertEqual(0, self.taskList.originalLength())

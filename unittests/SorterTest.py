import test, patterns, date, dummy, config
import domain.task as task
import domain.effort as effort

class TaskSorterTest(test.TestCase):
    def setUp(self):
        a = self.a = task.Task('a')
        b = self.b = task.Task('b')
        c = self.c = task.Task('c')
        d = self.d = task.Task('d')
        self.list = dummy.TaskList([d, b, c, a])
        self.settings = config.Settings(load=False)
        self.settings.set('view', 'sortby', 'subject')
        self.sorter = task.sorter.Sorter(self.list, settings=self.settings)

    def testInitiallyEmpty(self):
        sorter = task.sorter.Sorter(dummy.TaskList(), settings=self.settings)
        self.assertEqual(0, len(sorter))

    def testLength(self):
        self.assertEqual(4, len(self.sorter))

    def testGetItem(self):
        self.assertEqual(self.a, self.sorter[0])

    def testOrder(self):
        self.assertEqual([self.a, self.b, self.c, self.d], list(self.sorter))

    def testRemoveItem(self):
        self.sorter.remove(self.c)
        self.assertEqual(3, len(self.sorter))
        self.assertEqual([self.a, self.b, self.d], list(self.sorter))
        self.assertEqual([self.d, self.b, self.a], self.list)

    def testAppend(self):
        e = task.Task('e')
        self.list.append(e)
        self.assertEqual(5, len(self.sorter))
        self.assertEqual(e, self.sorter[-1])

    def testChange(self):
        self.a.setSubject('z')
        self.assertEqual([self.b, self.c, self.d, self.a], list(self.sorter))


class TaskSorterSettingsTest(test.TestCase):        
    def setUp(self):
        self.taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        self.sorter = task.sorter.Sorter(self.taskList, settings=self.settings)        
        self.task1 = task.Task(subject='A', duedate=date.Tomorrow())
        self.task2 = task.Task(subject='B', duedate=date.Today())
        self.taskList.extend([self.task1, self.task2])

    def tearDown(self):
        task.sorter.SortOrderReverser.deleteInstance()
        
    def testSortDueDate(self):
        self.assertEqual([self.task2, self.task1], list(self.sorter))
        
    def testSortBySubject(self):
        self.settings.set('view', 'sortby', 'subject')
        self.assertEqual([self.task1, self.task2], list(self.sorter))
        
    def testSortBySubject_TurnOff(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortby', 'dueDate')
        self.assertEqual([self.task2, self.task1], list(self.sorter))
        
    def testSortByCompletionStatus(self):
        self.task2.setCompletionDate(date.Today())
        self.assertEqual([self.task1, self.task2], list(self.sorter))
        
    def testSortByInactiveStatus(self):
        self.task2.setStartDate(date.Tomorrow())
        self.assertEqual([self.task1, self.task2], list(self.sorter))
    
    def testSortBySubjectDescending(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'False')
        self.assertEqual([self.task2, self.task1], list(self.sorter))
        
    def testSortByStartDate(self):
        self.settings.set('view', 'sortby', 'startDate')
        self.task1.setDueDate(date.Yesterday())
        self.task2.setStartDate(date.Yesterday())
        self.assertEqual([self.task2, self.task1], list(self.sorter))
        
    def testDescending(self):
        self.settings.set('view', 'sortascending', 'False')
        self.assertEqual([self.task1, self.task2], list(self.sorter))
        
    def testByDueDateWithoutFirstSortingByStatus(self):
        self.settings.set('view', 'sortbystatusfirst', 'False')
        self.task2.setCompletionDate(date.Today())
        self.assertEqual([self.task2, self.task1], list(self.sorter))

    def testSortBySubjectWithFirstSortingByStatus(self):
        self.settings.set('view', 'sortbystatusfirst', 'True')
        self.settings.set('view', 'sortby', 'subject')
        self.task1.setCompletionDate(date.Today())
        self.assertEqual([self.task2, self.task1], list(self.sorter))
        
    def testSortBySubjectWithoutFirstSortingByStatus(self):
        self.settings.set('view', 'sortbystatusfirst', 'False')
        self.settings.set('view', 'sortby', 'subject')
        self.task1.setCompletionDate(date.Today())
        self.assertEqual([self.task1, self.task2], list(self.sorter))
                
    def testSortCaseSensitive(self):
        self.settings.set('view', 'sortcasesensitive', 'True')
        self.settings.set('view', 'sortby', 'subject')
        task3 = task.Task('a')
        self.taskList.append(task3)
        self.assertEqual([self.task1, self.task2, task3], list(self.sorter))

    def testSortCaseInsensitive(self):
        self.settings.set('view', 'sortcasesensitive', 'False')
        self.settings.set('view', 'sortby', 'subject')
        task3 = task.Task('a')
        self.taskList.append(task3)
        self.assertEqual([self.task1, task3, self.task2], list(self.sorter))
    
    def testFlipSortOrder(self):
        self.settings.set('view', 'sortascending', 'True')
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortby', 'subject')
        self.assertEqual('False', self.settings.get('view', 'sortascending'))

    def testSortByTotalTimeLeft(self):
        self.settings.set('view', 'sortascending', 'True')
        self.settings.set('view', 'sortby', 'totaltimeLeft')
        self.assertEqual([self.task2, self.task1], list(self.sorter))


class TaskSorterTreeModeTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        self.sorter = task.sorter.Sorter(self.taskList, settings=self.settings, treeMode=True)        
        self.parent1 = task.Task(subject='parent 1')
        self.child1 = task.Task(subject='child 1')
        self.parent1.addChild(self.child1)
        self.parent2 = task.Task(subject='parent 2')
        self.child2 = task.Task(subject='child 2')
        self.parent2.addChild(self.child2)
        self.taskList.extend([self.parent1, self.parent2])
        
    def testSortByDueDate(self):
        self.settings.set('view', 'sortby', 'dueDate')
        self.child2.setDueDate(date.Today())
        self.failUnless(list(self.sorter).index(self.parent2)< list(self.sorter).index(self.parent1))

    def testSortByPriority(self):
        self.settings.set('view', 'sortby', 'priority')
        self.settings.set('view', 'sortascending', 'False')
        self.child2.setPriority(10)
        self.failUnless(list(self.sorter).index(self.parent2)< list(self.sorter).index(self.parent1))
        
        
class EffortSorterTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.sorter = effort.EffortSorter(self.effortList)
        self.task = task.Task()
        self.task.addEffort(effort.Effort(self.task,
            date.DateTime(2004,1,1), date.DateTime(2004,1,2)))
        self.task.addEffort(effort.Effort(self.task,
            date.DateTime(2004,2,1), date.DateTime(2004,2,2)))
        self.taskList.append(self.task)

    def testDescending(self):
        self.assertEqual(2, len(self.sorter))
        self.assertEqual(self.effortList[0], self.sorter[1])
        self.assertEqual(self.effortList[1], self.sorter[0])

    def testResort(self):
        self.effortList[0].setStart(date.DateTime(2004,3,1))
        self.assertEqual(self.effortList[0], self.sorter[0])
        self.assertEqual(self.effortList[1], self.sorter[1])

    def testCreateWhenEffortListIsFilled(self):
        sorter = effort.EffortSorter(self.effortList)
        self.assertEqual(2, len(sorter))

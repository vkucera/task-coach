import test, gui, config, TaskViewerTest, wx
from gui import render
from i18n import _
from domain import task, effort, date, category


class CommonTests:
    ''' Tests common to all TaskListViewers, i.e. TaskListViewer and
        TaskTreeListViewer. '''
    
    def testSubjectColumnIsVisible(self):
        self.assertEqual(_('Subject'), self.viewer.GetColumn(0).GetText())
    
    def testStartDateColumnIsVisibleByDefault(self):
        self.assertEqual(_('Start date'), self.viewer.GetColumn(1).GetText())
        
    def testDueDateColumnIsVisibleByDefault(self):
        self.assertEqual(_('Due date'), self.viewer.GetColumn(2).GetText())

    def testThreeColumnsByDefault(self):
        self.assertEqual(3, self.viewer.GetColumnCount())
    
    def testTurnOffStartDateColumn(self):
        self.settings.set('view', 'startdate', 'False')
        self.assertEqual(_('Due date'), self.viewer.GetColumn(1).GetText())
        self.assertEqual(2, self.viewer.GetColumnCount())
        
    def DONTRUNtestShowSort_Subject(self):
        # This tests only fails for the TaskList (i.e. the ListCtrl),
        # but succeeds for the TaskTreeList (i.e. the TreeListCtrl . Weird.
        self.settings.set('view', 'sortby', 'subject')
        self.assertNotEqual(-1, self.viewer.GetColumn(0).GetImage())
        self.assertEqual(-1, self.viewer.GetColumn(1).GetImage())
    
    def testColorWhenTaskIsCompleted(self):
        self.taskList.append(self.task)
        self.task.setCompletionDate()
        newColor = gui.color.taskColor(self.task, self.settings)
        self.newColor = newColor.Red(), newColor.Green(), newColor.Blue()
        self.assertColor()

    def testTurnOnHourlyFeeColumn(self):
        self.settings.set('view', 'hourlyfee', 'True')
        self.assertEqual(_('Hourly fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnFixedFeeColumn(self):
        self.settings.set('view', 'fixedfee', 'True')
        self.assertEqual(_('Fixed fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnTotalFixedFeeColumn(self):
        self.settings.set('view', 'totalfixedfee', 'True')
        self.assertEqual(_('Total fixed fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnFixedFeeColumnWithItemsInTheList(self):
        taskWithFixedFee = task.Task(fixedFee=100)
        self.taskList.append(taskWithFixedFee)
        self.settings.set('view', 'fixedfee', 'True')
        self.assertEqual(_('Fixed fee'), self.viewer.GetColumn(3).GetText())


class TaskListViewerTest(CommonTests, TaskViewerTest.CommonTests, 
        test.wxTestCase):
    def setUp(self):
        super(TaskListViewerTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.taskList = task.sorter.Sorter(task.TaskList(), 
            settings=self.settings)
        self.settings.set('view', 'sortby', 'subject')
        self.task = task.Task('task')
        self.viewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, None, self.settings, 
                self.taskList, effort.EffortList(self.taskList), 
                self.categories), self.settings, categories=self.categories)
        
    def assertItems(self, *tasks):
        self.assertEqual(len(tasks), self.viewer.size())
        for index, task in enumerate(tasks):
            self.assertEqual(render.subject(task, recursively=True), 
                             self.viewer.widget.GetItemText(index))
                             
    def getFirstItemTextColor(self):
        return self.viewer.widget.GetItemTextColour(0)

    def assertColor(self):
        # There seems to be a bug in the ListCtrl causing GetItemTextColour() to
        # always return the 'unknown' colour on Windows. We keep this test like
        # this so it will fail when the bug is fixed.
        if '__WXMSW__' in wx.PlatformInfo:
            self.assertEqual(wx.NullColour, self.getFirstItemTextColor())
        else:
            super(TaskListViewerTest, self).assertColor()
        
    def testEmptyTaskList(self):
        self.assertItems()

    def testAddTask(self):
        self.taskList.append(self.task)
        self.assertItems(self.task)

    def testRemoveTask(self):
        self.taskList.append(self.task)
        self.taskList.remove(self.task)
        self.assertItems()

    def testCurrent(self):
        self.taskList.append(self.task)
        self.viewer.widget.select([0])
        self.assertEqual([self.task], self.viewer.curselection())

    def testOneDayLeft(self):
        self.settings.set('view', 'timeleft', 'True')
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        self.assertEqual(render.daysLeft(self.task.timeLeft()), 
            self.viewer.widget.GetItem(0, 3).GetText())

    def testChildSubjectRendering(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems(child, self.task)
           
    def testMarkCompleted(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        task2 = task.Task(subject='task2')
        self.taskList.extend([self.task, task2])
        self.assertItems(self.task, task2)
        self.task.setCompletionDate()
        self.assertItems(task2, self.task)
            
    def testSortByDueDate(self):
        self.settings.set('view', 'sortby', 'subject')
        self.settings.set('view', 'sortascending', 'True')
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task('zzz')
        child2 = task.Task('child 2')
        task2.addChild(child2)
        self.taskList.extend([self.task, task2])
        self.assertItems(child, child2, self.task, task2) 
        child2.setDueDate(date.Today())
        self.settings.set('view', 'sortby', 'dueDate')
        self.assertItems(child2, child, self.task, task2)


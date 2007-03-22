import wx, test
import domain.task as task
import domain.date as date

class CommonTests(object):
    ''' Common test cases for all task viewers. This class is mixed in with
        TaskListViewerTest, TaskTreeListViewerTest, etc. '''
    
    def setUp(self):
        super(CommonTests, self).setUp()
        self.newColor = (100, 200, 100)
        
    def getItemTextColor(self, index):
        raise NotImplementedError
    
    def assertColor(self):    
        self.assertEqual(wx.Colour(*self.newColor), self.getItemTextColor(0))
                         
    def setColor(self, setting):
        self.settings.set('color', setting, str(self.newColor))
        
    def testChangeActiveTaskColor(self):
        self.taskList.append(task.Task(subject='test'))
        self.setColor('activetasks')
        self.assertColor()
    
    def testChangeInactiveTaskColor(self):
        self.setColor('inactivetasks')
        self.taskList.append(task.Task(startDate=date.Tomorrow()))
        self.assertColor()
    
    def testChangeCompletedTaskColor(self):
        self.setColor('completedtasks')
        self.taskList.append(task.Task(completionDate=date.Today()))
        self.assertColor()

    def testChangeDueTodayTaskColor(self):
        self.setColor('duetodaytasks')
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertColor()

    def testChangeOverDueTaskColor(self):
        self.setColor('overduetasks')
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.assertColor()
            
    def testStatusMessage_EmptyTaskList(self):
        self.assertEqual(('Tasks: 0 selected, 0 visible, 0 total', 
            'Status: 0 over due, 0 inactive, 0 completed'),
            self.viewer.statusMessages())
    
    def testOnDropFiles(self):
        self.taskList.append(task.Task())
        self.viewer.onDropFiles((0,), ['filename'])
        self.assertEqual(['filename'], self.taskList[0].attachments())

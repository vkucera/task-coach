import wx, test, os
from domain import task, date, attachment

class CommonTests(object):
    ''' Common test cases for all task viewers. This class is mixed in with
        TaskListViewerTest, TaskTreeListViewerTest, etc. '''
    
    def setUp(self):
        super(CommonTests, self).setUp()
        self.newColor = (100, 200, 100)
        file('test.mail', 'wb').write('Subject: foo\r\n\r\nBody\r\n')
        attachment.MailAttachment.attdir = os.getcwd()

    def tearDown(self):
        super(CommonTests, self).tearDown()
        attachment.MailAttachment.attdir = None

        for name in os.listdir('.'):
            if os.path.isdir(name) and name.endswith('_attachments'):
                os.rmdir(name)

        try:
            os.remove('test.mail')
        except OSError:
            pass

    def getFirstItemTextColor(self):
        raise NotImplementedError
    
    def assertColor(self):    
        self.assertEqual(wx.Colour(*self.newColor), self.getFirstItemTextColor())
                         
    def setColor(self, setting):
        self.settings.set('color', setting, str(self.newColor))

    def showColumn(self, columnName, show=True):
        self.viewer.showColumnByName(columnName, show)
        
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
        aTask = task.Task()
        self.taskList.append(aTask)
        self.viewer.onDropFiles(self.viewer.getIndexOfItem(aTask), ['filename'])
        self.assertEqual([attachment.FileAttachment('filename')], self.taskList[0].attachments())

    def testOnDropURL(self):
        aTask = task.Task()
        self.taskList.append(aTask)
        self.viewer.onDropURL(self.viewer.getIndexOfItem(aTask), 'http://www.example.com/')
        self.assertEqual([attachment.URIAttachment('http://www.example.com/')], self.taskList[0].attachments())

    def testOnDropMail(self):
        aTask = task.Task()
        self.taskList.append(aTask)
        self.viewer.onDropMail(self.viewer.getIndexOfItem(aTask), 'test.mail')
        self.assertEqual([attachment.MailAttachment('test.mail')], self.taskList[0].attachments())

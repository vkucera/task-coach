import test, gui, config
from unittests import dummy
from domain import task, effort, date


class EffortViewerUnderTest(gui.viewer.EffortListViewer):
    def createWidget(self):
        return dummy.DummyWidget(self)
    
    def columns(self):
        return []


class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.task = task.Task()
        self.taskList.append(self.task)
        self.effort1 = effort.Effort(self.task, date.DateTime(2006,1,1),
            date.DateTime(2006,1,2))
        self.effort2 = effort.Effort(self.task, date.DateTime(2006,1,2),
            date.DateTime(2006,1,3))
        self.viewer = EffortViewerUnderTest(self.frame, self.taskList, {}, 
            self.settings)
            
    def assertStatusMessages(self, message1, message2):
        self.assertEqual((message1, message2), self.viewer.statusMessages())
        
    def testStatusMessage_EmptyTaskList(self):
        self.taskList.clear()
        self.assertStatusMessages('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking')
            
    def testStatusMessage_OneTaskNoEffort(self):
        self.assertStatusMessages('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking')
        
    def testStatusMessage_OneTaskOneEffort(self):
        self.task.addEffort(self.effort1)
        self.assertStatusMessages('Effort: 0 selected, 1 visible, 1 total', 
            'Status: 0 tracking')
            
    def testStatusMessage_OneTaskTwoEfforts(self):
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.assertStatusMessages('Effort: 0 selected, 2 visible, 2 total', 
            'Status: 0 tracking')
            
    def testStatusMessage_OneTaskOneActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertStatusMessages('Effort: 0 selected, 1 visible, 1 total',
            'Status: 1 tracking')

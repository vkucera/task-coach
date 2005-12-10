import test, gui, dummy, config
import domain.task as task
import domain.date as date

class GanttChartViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), settings=self.settings)
        self.settings.set('view', 'sortby', 'subject')
        self.ganttChartViewer = gui.viewer.GanttChartViewer(self.frame, self.taskList, 
            dummy.DummyUICommands(), self.settings)

    def testAddTask(self):
        self.taskList.append(task.Task(subject='Test'))
        self.ganttChartViewer.refresh()
        self.assertEqual('Test', self.ganttChartViewer.widget.GetRowLabelValue(0))
        
    def testDatesShown(self):
        self.taskList.append(task.Task(startdate=date.Today(), duedate=date.Tomorrow()))
        self.ganttChartViewer.refresh()
        self.assertEqual(gui.render.date(date.Yesterday()), self.ganttChartViewer.widget.GetColLabelValue(0))
        self.assertEqual(4, self.ganttChartViewer.widget.GetNumberCols())
        
    def testDatesShown_MaxDateInfinite(self):
        self.taskList.append(task.Task())
        self.assertEqual(3, self.ganttChartViewer.widget.GetNumberCols())
        
    def testDatesShown_MaxDateNotInfinite(self):
        self.taskList.append(task.Task())
        self.taskList.append(task.Task(duedate=date.Tomorrow()))
        self.assertEqual(4, self.ganttChartViewer.widget.GetNumberCols())
    
    def testIsEmptyFirstColumn(self):
        self.taskList.append(task.Task())
        self.assertEqual('', self.ganttChartViewer.widget.GetCellValue(0,0))
        
    def testIsEmptyLastColumn(self):
        self.taskList.append(task.Task(duedate=date.Today()))    
        self.assertEqual('', self.ganttChartViewer.widget.GetCellValue(0,2))
        
    def testDateOverflowError(self):
        self.taskList.append(task.Task(duedate=date.Date(9999,12,30)))
        
    def testDateUnderflowError(self):
        self.taskList.append(task.Task(startdate=date.Date(1,1,1), duedate=date.Date(9999,12,30)))
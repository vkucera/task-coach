import test, persistence
import StringIO
from domain import task, category, effort, date, note, attachment


class IntegrationTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.fd.name = 'testfile.tsk'
        self.reader = persistence.XMLReader(self.fd)
        self.writer = persistence.XMLWriter(self.fd)
        self.taskList = task.TaskList()
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.fillContainers()
        tasks, categories, notes = self.readAndWrite()
        self.tasksWrittenAndRead = task.TaskList(tasks)
        self.categoriesWrittenAndRead = category.CategoryList(categories)
        self.notesWrittenAndRead = note.NoteContainer(notes)

    def fillContainers(self):
        pass

    def readAndWrite(self):
        self.fd.seek(0)
        self.writer.write(self.taskList, self.categories, self.notes)
        self.fd.seek(0)
        return self.reader.read()


class IntegrationTest_EmptyList(IntegrationTestCase):
    def testEmptyTaskList(self):
        self.assertEqual([], self.tasksWrittenAndRead)
        
    def testNoCategories(self):
        self.assertEqual([], self.categoriesWrittenAndRead)
        
        
class IntegrationTest(IntegrationTestCase):
    def fillContainers(self):
        self.description = 'Description\nLine 2'
        self.task = task.Task('Subject', self.description, 
            startdate=date.Yesterday(), duedate=date.Tomorrow(), 
            completiondate=date.Yesterday(), budget=date.TimeDelta(hours=1), 
            priority=4, hourlyFee=100.5, fixedFee=1000, recurrence='weekly',
            reminder=date.DateTime(2004,1,1),
            shouldMarkCompletedWhenAllChildrenCompleted=True)
        self.child = task.Task()
        self.task.addChild(self.child)
        self.grandChild = task.Task()
        self.child.addChild(self.grandChild)
        self.task.addEffort(effort.Effort(self.task, start=date.DateTime(2004,1,1), 
            stop=date.DateTime(2004,1,2), description=self.description))
        self.category = category.Category('test', [self.task], filtered=True,
                                          description='Description')
        self.categories.append(self.category)
        self.task.addAttachments(attachment.FileAttachment('/home/frank/whatever.txt'))
        self.task2 = task.Task('Task 2', priority=-1954)
        self.taskList.extend([self.task, self.task2])
        self.note = note.Note('Note', 'Description', children=[note.Note('Child')])
        self.notes.append(self.note)
        self.category.addCategorizable(self.note)

    def getTaskWrittenAndRead(self, id):
        return [task for task in self.tasksWrittenAndRead if task.id() == id][0]

    def assertAttributeWrittenAndRead(self, task, attribute):
        taskWrittenAndRead = self.getTaskWrittenAndRead(task.id())
        self.assertEqual(getattr(task, attribute)(), 
                         getattr(taskWrittenAndRead, attribute)())
                         
    def assertPropertyWrittenAndRead(self, task, property):
        taskWrittenAndRead = self.getTaskWrittenAndRead(task.id())
        self.assertEqual(getattr(task, property), 
                         getattr(taskWrittenAndRead, property))

    def testSubject(self):
        self.assertAttributeWrittenAndRead(self.task, 'subject')

    def testDescription(self):
        self.assertAttributeWrittenAndRead(self.task, 'description')
         
    def testStartDate(self):
        self.assertAttributeWrittenAndRead(self.task, 'startDate')
                
    def testDueDate(self):
        self.assertAttributeWrittenAndRead(self.task, 'dueDate')
 
    def testCompletionDate(self):
        self.assertAttributeWrittenAndRead(self.task, 'completionDate')
 
    def testBudget(self):
        self.assertAttributeWrittenAndRead(self.task, 'budget')
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.tasksWrittenAndRead = task.TaskList(self.readAndWrite()[0])
        self.assertAttributeWrittenAndRead(self.task, 'budget')
        
    def testEffort(self):
        self.assertAttributeWrittenAndRead(self.task, 'timeSpent')
        
    def testEffortDescription(self):
        self.assertEqual(self.task.efforts()[0].getDescription(), 
            self.getTaskWrittenAndRead(self.task.id()).efforts()[0].getDescription())
        
    def testChildren(self):
        self.assertEqual(len(self.task.children()), 
            len(self.getTaskWrittenAndRead(self.task.id()).children()))
        
    def testGrandChildren(self):
        self.assertEqual(len(self.task.children(recursive=True)),  
            len(self.getTaskWrittenAndRead(self.task.id()).children(recursive=True)))
       
    def testCategory(self):
        self.assertEqual(self.task.id(), 
                         self.categoriesWrittenAndRead[0].categorizables()[0].id())

    def testFilteredCategory(self):
        self.failUnless(self.categoriesWrittenAndRead[0].isFiltered())
        
    def testPriority(self):
        self.assertAttributeWrittenAndRead(self.task, 'priority')
        
    def testNegativePriority(self):
        self.assertAttributeWrittenAndRead(self.task2, 'priority')
        
    def testHourlyFee(self):
        self.assertAttributeWrittenAndRead(self.task, 'hourlyFee')

    def testFixedFee(self):
        self.assertAttributeWrittenAndRead(self.task, 'fixedFee')

    def testReminder(self):
        self.assertAttributeWrittenAndRead(self.task, 'reminder')
        
    def testNoReminder(self):
        self.assertAttributeWrittenAndRead(self.task2, 'reminder')
        
    def testMarkCompletedWhenAllChildrenCompletedSetting_True(self):
        self.assertPropertyWrittenAndRead(self.task, 
            'shouldMarkCompletedWhenAllChildrenCompleted')
 
    def testMarkCompletedWhenAllChildrenCompletedSetting_None(self):
        self.assertPropertyWrittenAndRead(self.task2, 
            'shouldMarkCompletedWhenAllChildrenCompleted')
 
    def testAttachment(self):
        self.assertAttributeWrittenAndRead(self.task, 'attachments')

    def testRecurrence(self):
        self.assertAttributeWrittenAndRead(self.task, 'recurrence')
                
    def testNote(self):
        self.assertEqual(len(self.notes), len(self.notesWrittenAndRead))

    def testRootNote(self):
        self.assertEqual(self.notes.rootItems()[0].subject(), 
            self.notesWrittenAndRead.rootItems()[0].subject())
        
    def testChildNote(self):
        self.assertEqual(self.notes.rootItems()[0].children()[0].subject(), 
            self.notesWrittenAndRead.rootItems()[0].children()[0].subject())
        
    def testCategoryDescription(self):
        self.assertEqual(self.categories[0].description(), 
                         self.categoriesWrittenAndRead[0].description())

    def testNoteId(self):
        self.assertEqual(self.notes.rootItems()[0].id(),
                         self.notesWrittenAndRead.rootItems()[0].id())
        
    def testCategoryId(self):
        self.assertEqual(self.category.id(),
                         self.categoriesWrittenAndRead[0].id())
        
    def testNoteWithCategory(self):
        self.failUnless(self.notesWrittenAndRead.rootItems()[0] in \
                        self.categoriesWrittenAndRead[0].categorizables())
        

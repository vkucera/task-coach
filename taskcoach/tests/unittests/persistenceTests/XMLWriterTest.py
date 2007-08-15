# -*- coding: utf-8 -*-

import test, persistence
import StringIO # We cannot use CStringIO since unicode strings are used below.
from domain import task, effort, date, category, note, attachment

class XMLWriterTest(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.fd.name = 'testfile.tsk'
        self.writer = persistence.XMLWriter(self.fd)
        self.task = task.Task()
        self.taskList = task.TaskList([self.task])
        self.categoryContainer = category.CategoryList()
        self.noteContainer = note.NoteContainer()
            
    def __writeAndRead(self):
        self.writer.write(self.taskList, self.categoryContainer, 
            self.noteContainer)
        return self.fd.getvalue()
    
    def expectInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.failUnless(xmlFragment in xml, '%s not in %s'%(xmlFragment, xml))
    
    def expectNotInXML(self, xmlFragment):
        xml = self.__writeAndRead()
        self.failIf(xmlFragment in xml, '%s in %s'%(xmlFragment, xml))
    
    # tests
        
    def testVersion(self):
        import meta
        self.expectInXML('<?taskcoach release="%s"'%meta.data.version)
        
    def testTaskSubject(self):
        self.task.setSubject('Subject')
        self.expectInXML('subject="Subject"')
        
    def testTaskSubjectWithUnicode(self):
        self.task.setSubject(u'ï¬Ÿï­Žï­–')
        self.expectInXML(u'subject="ï¬Ÿï­Žï­–"')
            
    def testTaskDescription(self):
        self.task.setDescription('Description')
        self.expectInXML('<description>Description</description>')
        
    def testEmptyTaskDescriptionIsNotWritten(self):
        self.expectNotInXML('<description>')
        
    def testTaskStartDate(self):
        self.task.setStartDate(date.Date(2004,1,1))
        self.expectInXML('startdate="%s"'%str(self.task.startDate()))
        
    def testNoStartDate(self):
        self.task.setStartDate(date.Date())
        self.expectNotInXML('startdate')
        
    def testTaskDueDate(self):
        self.task.setDueDate(date.Date(2004,1,1))
        self.expectInXML('duedate="%s"'%str(self.task.dueDate()))

    def testNoDueDate(self):
        self.expectNotInXML('duedate')
                
    def testTaskCompletionDate(self):
        self.task.setCompletionDate(date.Date(2004, 1, 1))
        self.expectInXML('completiondate="%s"'%str(self.task.completionDate()))

    def testNoCompletionDate(self):
        self.expectNotInXML('completiondate')
        
    def testChildTask(self):
        self.task.addChild(task.Task(subject='child'))
        self.expectInXML('subject="child"/></task></tasks>')

    def testEffort(self):
        taskEffort = effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2), 'description\nline 2')
        self.task.addEffort(taskEffort)
        self.expectInXML('<effort start="%s" stop="%s"><description>description\nline 2</description></effort>'% \
            (taskEffort.getStart(), taskEffort.getStop()))
        
    def testThatEffortTimesDoNotContainMilliseconds(self):
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2004,1,1,10,0,0,123456), 
            date.DateTime(2004,1,1,10,0,10,654310)))
        self.expectInXML('start="2004-01-01 10:00:00"')
        self.expectInXML('stop="2004-01-01 10:00:10"')
        
    def testThatEffortStartAndStopAreNotEqual(self):
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2004,1,1,10,0,0,123456), 
            date.DateTime(2004,1,1,10,0,0,654310)))
        self.expectInXML('start="2004-01-01 10:00:00"')
        self.expectInXML('stop="2004-01-01 10:00:01"')
            
    def testEmptyEffortDescriptionIsNotWritten(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1),
            date.DateTime(2004,1,2)))
        self.expectNotInXML('<description>')
        
    def testActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2004,1,1)))
        self.expectInXML('<effort start="%s"/>'%self.task.efforts()[0].getStart()) 
                
    def testNoEffortByDefault(self):
        self.expectNotInXML('<efforts>')
        
    def testBudget(self):
        self.task.setBudget(date.TimeDelta(hours=1))
        self.expectInXML('budget="%s"'%str(self.task.budget()))
        
    def testNoBudget(self):
        self.expectNotInXML('budget')
        
    def testBudget_MoreThan24Hour(self):
        self.task.setBudget(date.TimeDelta(hours=25))
        self.expectInXML('budget="25:00:00"')
        
    def testOneCategoryWithoutTask(self):
        self.categoryContainer.append(category.Category('test'))
        self.expectInXML('<category subject="test"/>')
    
    def testOneCategoryWithOneTask(self):
        self.categoryContainer.append(category.Category('test', [self.task]))
        self.expectInXML('<category subject="test" tasks="%s"/>'%self.task.id())
        
    def testTwoCategoriesWithOneTask(self):
        subjects = ['test', 'another']
        expectedResult = ''
        for subject in subjects:
            self.categoryContainer.append(category.Category(subject, [self.task]))
            expectedResult += '<category subject="%s" tasks="%s"/>'%(subject, self.task.id())
        self.expectInXML(expectedResult)
        
    def testOneCategoryWithSubTask(self):
        child = task.Task()
        self.taskList.append(child)
        self.task.addChild(child)
        self.categoryContainer.append(category.Category('test', [child]))
        self.expectInXML('<category subject="test" tasks="%s"/>'%child.id())
        
    def testSubCategoryWithoutTasks(self):
        parentCategory = category.Category('parent')
        childCategory = category.Category('child')
        parentCategory.addChild(childCategory)
        self.categoryContainer.extend([parentCategory, childCategory])
        self.expectInXML('<category subject="parent">'
                         '<category subject="child"/></category>')

    def testSubCategoryWithOneTask(self):
        parentCategory = category.Category('parent')
        childCategory = category.Category('child', tasks=[self.task])
        parentCategory.addChild(childCategory)
        self.categoryContainer.extend([parentCategory, childCategory])
        self.expectInXML('<category subject="parent">'
                         '<category subject="child" tasks="%s"/>'
                         '</category>'%self.task.id())
    
    def testFilteredCategory(self):
        filteredCategory = category.Category('test', filtered=True)
        self.categoryContainer.extend([filteredCategory])
        self.expectInXML('<category filtered="True" subject="test"/>')

    def testCategoryWithDescription(self):
        aCategory = category.Category('subject', description='Description')
        self.categoryContainer.append(aCategory)
        self.expectInXML('<category subject="subject"><description>Description</description></category>')
        
    def testCategoryWithUnicodeSubject(self):
        unicodeCategory = category.Category(u'ï¬Ÿï­Žï­–')
        self.categoryContainer.extend([unicodeCategory])
        self.expectInXML(u'<category subject="ï¬Ÿï­Žï­–"/>')

    def testCategoryWithDeletedTask(self):
        aCategory = category.Category('category', tasks=[self.task])
        self.categoryContainer.append(aCategory)
        self.taskList.remove(self.task)
        self.expectInXML('<category subject="category"/>')
 
    def testDefaultPriority(self):
        self.expectNotInXML('priority')
        
    def testPriority(self):
        self.task.setPriority(5)
        self.expectInXML('priority="5"')
        
    def testId(self):
        self.expectInXML('id="%s"'%self.task.id())
        
    def testLastModificationTime(self):
        formattedModificationTime = self.task.lastModificationTime().strftime("%Y-%m-%d %H:%M:%S")
        self.expectInXML('lastModificationTime="%s"'%formattedModificationTime)

    def testTwoTasks(self):
        self.task.setSubject('task 1')
        task2 = task.Task('task 2')
        self.taskList.append(task2)
        self.expectInXML('subject="task 2"')

    def testDefaultHourlyFee(self):
        self.expectNotInXML('hourlyFee')
        
    def testHourlyFee(self):
        self.task.setHourlyFee(100)
        self.expectInXML('hourlyFee="100"')
        
    def testDefaultFixedFee(self):
        self.expectNotInXML('fixedFee')
        
    def testFixedFee(self):
        self.task.setFixedFee(1000)
        self.expectInXML('fixedFee="1000"')

    def testNoReminder(self):
        self.expectNotInXML('reminder')
        
    def testReminder(self):
        self.task.setReminder(date.DateTime(2005, 5, 7, 13, 15, 10))
        self.expectInXML('reminder="%s"'%str(self.task.reminder()))
        
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_None(self):
        self.expectNotInXML('shouldMarkCompletedWhenAllChildrenCompleted')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_True(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = True
        self.expectInXML('shouldMarkCompletedWhenAllChildrenCompleted="True"')
            
    def testMarkCompletedWhenAllChildrenAreCompletedSetting_False(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = False
        self.expectInXML('shouldMarkCompletedWhenAllChildrenCompleted="False"')
              
    def testNoAttachments(self):
        self.expectNotInXML('attachment')
        
    def testOneAttachment(self):
        self.task.addAttachments(attachment.FileAttachment('whatever.txt'))
        self.expectInXML('<attachment>FILE:whatever.txt</attachment>')
        
    def testTwoAttachments(self):
        attachments = ['whatever.txt',
                       '/home/frank/attachment.doc']
        for a in attachments:
            self.task.addAttachments(attachment.FileAttachment(a))
        self.expectInXML('<attachment>FILE:%s</attachment>'*2%tuple(attachments))

    def testNote(self):
        self.noteContainer.append(note.Note())
        self.expectInXML('<note/>')
        
    def testNoteWithSubject(self):
        self.noteContainer.append(note.Note(subject='Note'))
        self.expectInXML('<note subject="Note"/>')
        
    def testNoteWithDescription(self):
        self.noteContainer.append(note.Note(description='Description'))
        self.expectInXML('<note><description>Description</description></note>')
        
    def testNoteWithChild(self):
        aNote = note.Note()
        child = note.Note()
        aNote.addChild(child)
        self.noteContainer.append(aNote)
        self.expectInXML('<note><note/></note>')

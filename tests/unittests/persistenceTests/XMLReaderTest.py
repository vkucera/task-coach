'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import test, xml.parsers.expat, sets, persistence, wx
import StringIO
from domain import task, date


class XMLReaderTestCase(test.TestCase):
    def setUp(self):
        self.fd = StringIO.StringIO()
        self.fd.name = 'testfile.tsk'
        self.reader = persistence.XMLReader(self.fd)

    def writeAndRead(self, xml):
        xml = '<?taskcoach release="whatever" tskversion="%d"?>\n'%self.tskversion + xml
        self.fd.write(xml)
        self.fd.seek(0)
        return self.reader.read()

    
class XMLReaderVersion6Test(XMLReaderTestCase):
    tskversion = 6

    def testDescription(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task description="%s"/>
        </tasks>\n'''%u'Description')
        self.assertEqual(u'Description', tasks[0].description())

    def testEffortDescription(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <effort start="2004-01-01 10:00:00.123000" 
                        stop="2004-01-01 10:30:00.123000" 
                        description="Yo"/>
            </task>
        </tasks>''')
        self.assertEqual('Yo', tasks[0].efforts()[0].getDescription())


class XMLReaderVersion8Test(XMLReaderTestCase):   
    tskversion = 8

    def testReadTaskWithoutPriority(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual(0, tasks[0].priority())
        
        
class XMLReaderVersion9Test(XMLReaderTestCase):
    tskversion = 9
    
    def testReadTaskWithoutId(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.failUnless(tasks[0].id())
        

class XMLReaderVersion10Test(XMLReaderTestCase):
    tskversion = 10
    
    def testReadTaskWithoutFee(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual(0, tasks[0].hourlyFee())
        self.assertEqual(0, tasks[0].fixedFee())


class XMLReaderVersion11Test(XMLReaderTestCase):
    tskversion = 11
    
    def testReadTaskWithoutReminder(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual(None, tasks[0].reminder())
        
        
class XMLReaderVersion12Test(XMLReaderTestCase):
    tskversion = 12
    
    def testReadTaskWithoutMarkCompletedWhenAllChildrenCompletedSetting(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual(None, 
                         tasks[0].shouldMarkCompletedWhenAllChildrenCompleted)
        

class XMLReaderVersion13Test(XMLReaderTestCase):
    tskversion = 13

    def testOneCategory(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task id="1">
                <category>test</category>
            </task>
        </tasks>''')
        self.assertEqual('test', categories[0].subject())
        self.assertEqual([tasks[0]], categories[0].categorizables())

    def testMultipleCategories(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task id="1">
                <category>test</category>
                <category>another</category>
                <category>yetanother</category>
            </task>
        </tasks>''')
        for category in categories:
            self.assertEqual([tasks[0]], category.categorizables())
            
    def testSubTaskWithCategories(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task id="1">
                <category>test</category>
                <task id="1.1">
                    <category>another</category>
                </task>
            </task>
        </tasks>''')
        testCategory = categories[0]
        anotherCategory = categories[1]
        self.assertEqual("1", testCategory.categorizables()[0].id())
        self.assertEqual("1.1", anotherCategory.categorizables()[0].id())         


class XMLReaderVersion14Test(XMLReaderTestCase):
    tskversion = 14
    
    def testEffortWithMilliseconds(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <effort start="2004-01-01 10:00:00.123000" 
                        stop="2004-01-01 10:30:00.123000"/>
            </task>
        </tasks>''')
        self.assertEqual(1, len(tasks[0].efforts()))
        self.assertEqual(date.TimeDelta(minutes=30), tasks[0].timeSpent())
        self.assertEqual(tasks[0], tasks[0].efforts()[0].task())


class XMLReaderVersion16Text(XMLReaderTestCase):
    tskversion = 16

    def testOneAttachmentCompat(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <attachment>whatever.tsk</attachment>
            </task>
        </tasks>''')
        self.assertEqual(['whatever.tsk'], map(unicode, tasks[0].attachments()))
        
    def testTwoAttachmentsCompat(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <attachment>whatever.tsk</attachment>
                <attachment>another.txt</attachment>
            </task>
        </tasks>''')
        self.assertEqual(['whatever.tsk', 'another.txt'], 
                         map(unicode, tasks[0].attachments()))
        
    def testOneAttachment(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <attachment>FILE:whatever.tsk</attachment>
            </task>
        </tasks>''')
        self.assertEqual(['whatever.tsk'], map(unicode, tasks[0].attachments()))
        
    def testTwoAttachments(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <attachment>FILE:whatever.tsk</attachment>
                <attachment>FILE:another.txt</attachment>
            </task>
        </tasks>''')
        self.assertEqual(['whatever.tsk', 'another.txt'], 
                         map(unicode, tasks[0].attachments()))


# There's no XMLReaderVersion17Test because the only difference between version
# 17 and 18 is the addition of an optional color attribute to categories in
# version 18. So the tests for version 18 test version 17 as well.


class XMLReaderVersion18Test(XMLReaderTestCase):
    tskversion = 18

    def testLastModificationTime(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task lastModificationTime="2004-01-01 10:00:00"/>
        </tasks>''')
        self.assertEqual(1, len(tasks)) # Ignore lastModificationTime
        

class XMLReaderVersion18Test(XMLReaderTestCase):
    tskversion = 19 # For release 0.69.0
           
    def testReadEmptyStream(self):
        try:
            self.reader.read()
            self.fail('Expected ExpatError')
        except xml.parsers.expat.ExpatError:
            pass
        
    def testNoTasksAndNoCategories(self):
        self.assertEqual(([], [], []), self.writeAndRead('<tasks/>\n'))
        
    def testOneTask(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>\n')
        self.assertEqual(1, len(tasks))
        self.assertEqual('', tasks[0].subject())

    def testTwoTasks(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task subject="1"/>
            <task subject="2"/>
        </tasks>\n''')
        self.assertEqual(2, len(tasks))
        self.assertEqual('1', tasks[0].subject())
        self.assertEqual('2', tasks[1].subject())
        
    def testOneTask_Subject(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task subject="Yo"/>
        </tasks>\n''')
        self.assertEqual('Yo', tasks[0].subject())
        
    def testOneTask_UnicodeSubject(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task subject="???"/>
        </tasks>\n''')
        self.assertEqual('???', tasks[0].subject())
        
    def testStartDate(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task startdate="2005-04-17"/>
        </tasks>\n''')
        self.assertEqual(date.Date(2005,4,17), tasks[0].startDate())
        
    def testDueDate(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task duedate="2005-04-17"/>
        </tasks>\n''')
        self.assertEqual(date.Date(2005,4,17), tasks[0].dueDate())
        
    def testCompletionDate(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task completiondate="2005-01-01"/>
        </tasks>\n''')
        self.assertEqual(date.Date(2005,1,1), tasks[0].completionDate())
        self.failUnless(tasks[0].completed())
        
    def testBudget(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task budget="4:10:10"/>
        </tasks>\n''')
        self.assertEqual(date.TimeDelta(hours=4, minutes=10, seconds=10), tasks[0].budget())

    def testBudget_NoBudget(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>\n')
        self.assertEqual(date.TimeDelta(), tasks[0].budget())
        
    def testDescription(self):
        description = u'Description\nline 2'
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <description>%s</description>
            </task>
        </tasks>\n'''%description)
        self.assertEqual(description, tasks[0].description())
    
    def testNoChildren(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>\n')
        self.failIf((tasks[0].children()))
        
    def testChild(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <task/>
            </task>
        </tasks>\n''')
        self.assertEqual(1, len(tasks[0].children()))
        self.assertEqual(1, len(tasks))
        
    def testChildren(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <task/>
                <task/>
            </task>
        </tasks>\n''')
        self.assertEqual(2, len(tasks[0].children()))
        self.assertEqual(1, len(tasks))
        
    def testGrandchild(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <task>
                    <task/>
                </task>
            </task>
        </tasks>\n''')
        self.assertEqual(1, len(tasks))
        parent = tasks[0]
        self.assertEqual(1, len(parent.children()))
        self.assertEqual(1, len(parent.children()[0].children()))
        
    def testEffort(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <effort start="2004-01-01 10:00:00" 
                        stop="2004-01-01 10:30:00"/>
            </task>
        </tasks>''')
        self.assertEqual(1, len(tasks[0].efforts()))
        self.assertEqual(date.TimeDelta(minutes=30), tasks[0].timeSpent())
        self.assertEqual(tasks[0], tasks[0].efforts()[0].task())
    
    def testChildEffort(self):    
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <task>
                    <effort start="2004-01-01 10:00:00" 
                            stop="2004-01-01 10:30:00"/>
                </task>
            </task>
        </tasks>''')
        child = tasks[0].children()[0]
        self.assertEqual(1, len(child.efforts()))
        self.assertEqual(date.TimeDelta(minutes=30), child.timeSpent())
        self.assertEqual(child, child.efforts()[0].task())

    def testEffortDescription(self):
        description = u'Description\nLine 2'
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <effort start="2004-01-01 10:00:00">
                    <description>%s</description>
                </effort>
            </task>
        </tasks>'''%description)
        self.assertEqual(description, tasks[0].efforts()[0].getDescription())
        
    def testActiveEffort(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <effort start="2004-01-01 10:00:00"/>
            </task>
        </tasks>''')
        self.assertEqual(1, len(tasks[0].efforts()))
        self.failUnless(tasks[0].isBeingTracked())
                
    def testPriority(self):
        tasks, categories, notes = \
            self.writeAndRead('<tasks><task priority="5"/></tasks>')        
        self.assertEqual(5, tasks[0].priority())
        
    def testTaskId(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task id="xyz"/></tasks>')
        self.assertEqual('xyz', tasks[0].id())
                
    def testHourlyFee(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task hourlyFee="100"/>
            <task hourlyFee="5.5"/>
        </tasks>''')
        self.assertEqual(100, tasks[0].hourlyFee())
        self.assertEqual(5.5, tasks[1].hourlyFee())
        
    def testFixedFee(self):
        tasks, categories, notes = \
            self.writeAndRead('<tasks><task fixedFee="240.50"/></tasks>')
        self.assertEqual(240.5, tasks[0].fixedFee())

    def testNoReminder(self):
        tasks, categories, notes = \
            self.writeAndRead('<tasks><task reminder="None"/></tasks>')
        self.assertEqual(None, tasks[0].reminder())
        
    def testReminder(self):
        tasks, categories,notes = self.writeAndRead('''
        <tasks>
            <task reminder="2004-01-01 10:00:00"/>
        </tasks>''')
        self.assertEqual(date.DateTime(2004,1,1,10,0,0,0), 
                         tasks[0].reminder())
        
    def testMarkCompletedWhenAllChildrenCompletedSetting_True(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task shouldMarkCompletedWhenAllChildrenCompleted="True"/>
        </tasks>''')
        self.assertEqual(True, 
                         tasks[0].shouldMarkCompletedWhenAllChildrenCompleted)

    def testMarkCompletedWhenAllChildrenCompletedSetting_False(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task shouldMarkCompletedWhenAllChildrenCompleted="False"/>
        </tasks>''')
        self.assertEqual(False,
                         tasks[0].shouldMarkCompletedWhenAllChildrenCompleted)
 
    def testMarkCompletedWhenAllChildrenCompletedSetting_None(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual(None,
                         tasks[0].shouldMarkCompletedWhenAllChildrenCompleted)

    def testNoAttachments(self):
        tasks, categories, notes = self.writeAndRead('<tasks><task/></tasks>')
        self.assertEqual([], tasks[0].attachments())
        
    def testOneAttachment(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <attachment type="file"><description>whatever.tsk</description><data>whatever.tsk</data></attachment>
            </task>
        </tasks>''')
        self.assertEqual(['whatever.tsk'], map(unicode, tasks[0].attachments()))
        
    def testTwoAttachments(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task>
                <attachment type="file"><description>whatever.tsk</description><data>whatever.tsk</data></attachment>
                <attachment type="file"><description>another.txt</description><data>another.txt</data></attachment>
            </task>
        </tasks>''')
        self.assertEqual(['whatever.tsk', 'another.txt'], 
                         map(unicode, tasks[0].attachments()))
        
    def testOneCategory(self):
        tasks, categories, notes = \
            self.writeAndRead('<tasks><category subject="cat"/></tasks>')
        self.assertEqual('cat', categories[0].subject())

    def testTwoCategories(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat1"/>
            <category subject="cat2"/>
        </tasks>''')
        self.assertEqual(['cat1', 'cat2'], 
            [category.subject() for category in categories])

    def testCategoryId(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category id="catId"/>
        </tasks>''')
        self.assertEqual('catId', categories[0].id())
            
    def testCategoryWithDescription(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat">
                <description>Description</description>
            </category>
        </tasks>''')
        self.assertEqual('Description', categories[0].description())
    
    def testCategoryWithColor(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat" color="(255, 0, 0, 255)"/>
        </tasks>''')
        self.assertEqual(wx.RED, categories[0].color())
        
    def testOneTaskWithCategory(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat" categorizables="1"/>
            <task id="1"/>
        </tasks>''')
        self.assertEqual(tasks, categories[0].categorizables())
        
    def testTwoRecursiveCategories(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat1">
                <category subject="cat1.1"/>
            </category>
        </tasks>''')
        self.assertEqual('cat1.1', categories[0].children()[0].subject())
        
    def testRecursiveCategoriesNotInResultList(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat1">
                <category subject="cat1.1"/>
            </category>
        </tasks>''')
        self.assertEqual(1, len(categories))

    def testRecursiveCategoriesWithTwoTasks(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat1" categorizables="1">
                <category subject="cat1.1" categorizables="2"/>
            </category>
            <task subject="task1" id="1"/>
            <task subject="task2" id="2"/>
        </tasks>''')
        self.assertEqual(tasks[0], categories[0].categorizables()[0])
        self.assertEqual(tasks[1], categories[0].children()[0].categorizables()[0])
        
    def testSubtaskCategory(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat1" categorizables="1.1"/>
            <task subject="task1" id="1">
                <task subject="task2" id="1.1"/>
            </task>
        </tasks>''')
        self.assertEqual(tasks[0].children()[0], categories[0].categorizables()[0])
        
    def testFilteredCategory(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <category filtered="True" subject="category"/>
        </tasks>''')
        self.failUnless(categories[0].isFiltered())
    
    def testCategoryWithDeletedTasks(self):
        ''' There's a bug in release 0.61.5 that causes the task file to contain
            references to deleted tasks. Ignore these when loading the task file.'''
        task, categories, notes = self.writeAndRead('''
        <tasks>
            <category subject="cat" tasks="some_task_id"/>
        </tasks>''')
        self.failIf(categories[0].categorizables())
        
    def testNote(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <note/>
        </tasks>''')
        self.failUnless(notes)

    def testNoteSubject(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <note subject="Note"/>
        </tasks>''')
        self.assertEqual('Note', notes[0].subject())

    def testNoteDescription(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <note>
                <description>Description</description>
            </note>
        </tasks>''')
        self.assertEqual('Description', notes[0].description())

    def testNoteChild(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <note>
                <note/>
            </note>
        </tasks>''')
        self.assertEqual(1, len(notes[0].children()))
        
    def testNoteCategory(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <note id="noteId" subject="Note"/>
            <category categorizables="noteId" subject="Category"/>
        </tasks>''')
        self.assertEqual(notes[0], categories[0].categorizables()[0])
        
    def testNoteId(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <note id="noteId"/>
        </tasks>''')
        self.assertEqual('noteId', notes[0].id())
        
    def testNoRecurrence(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task/>
        </tasks>''')
        self.failIf(tasks[0].recurrence())

    def testDailyRecurrence(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task recurrence="daily"/>
        </tasks>''')
        self.assertEqual('daily', tasks[0].recurrence())    

    def testWeeklyRecurrence(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task recurrence="weekly"/>
        </tasks>''')
        self.assertEqual('weekly', tasks[0].recurrence())

    def testMonthlyRecurrence(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task recurrence="monthly"/>
        </tasks>''')
        self.assertEqual('monthly', tasks[0].recurrence())
        
    def testRecurrenceCount(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task recurrenceCount="10"/>
        </tasks>''')
        self.assertEqual(10, tasks[0].recurrenceCount())
        
    def testMaxRecurrenceCount(self):
        tasks, categories, notes = self.writeAndRead('''
        <tasks>
            <task maxRecurrenceCount="10"/>
        </tasks>''')
        self.assertEqual(10, tasks[0].maxRecurrenceCount())


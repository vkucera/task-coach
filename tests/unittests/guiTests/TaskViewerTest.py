'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import wx, test, os
from domain import task, date, attachment, category


class CommonTests(object):
    ''' Common test cases for all task viewers. This class is mixed in with
        TaskListViewerTest, TaskTreeListViewerTest, etc. '''
    
    def setUp(self):
        super(CommonTests, self).setUp()
        self.newColor = (100, 200, 100, 255)
        attachment.MailAttachment.attdir = os.getcwd()

    def tearDown(self):
        super(CommonTests, self).tearDown()
        attachment.MailAttachment.attdir = None

        for name in os.listdir('.'):
            if os.path.isdir(name) and name.endswith('_attachments'):
                os.rmdir(name)


    def getFirstItemTextColor(self):
        raise NotImplementedError
    
    def getFirstItemBackgroundColor(self):
        raise NotImplementedError
    
    def assertColor(self):    
        self.assertEqual(wx.Colour(*self.newColor), 
                         self.getFirstItemTextColor())
        
    def assertBackgroundColor(self):
        self.assertEqual(wx.Colour(*self.newColor), 
                         self.getFirstItemBackgroundColor())
                         
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
        self.assertEqual([attachment.FileAttachment('filename')],
                         self.viewer.model()[0].attachments())

    def testOnDropURL(self):
        aTask = task.Task()
        self.taskList.append(aTask)
        self.viewer.onDropURL(self.viewer.getIndexOfItem(aTask), 
                              'http://www.example.com/')
        self.assertEqual([attachment.URIAttachment('http://www.example.com/')],
                         self.viewer.model()[0].attachments())

    def testOnDropMail(self):
        file('test.mail', 'wb').write('Subject: foo\r\n\r\nBody\r\n')
        aTask = task.Task()
        self.taskList.append(aTask)
        self.viewer.onDropMail(self.viewer.getIndexOfItem(aTask), 'test.mail')
        self.assertEqual([attachment.MailAttachment('test.mail')],
                         self.viewer.model()[0].attachments())
        os.remove('test.mail')
        
    def testCategoryColor(self):
        cat = category.Category('category with color', color=self.newColor)
        aTask = task.Task()
        cat.addCategorizable(aTask)
        aTask.addCategory(cat)
        self.taskList.append(aTask)
        self.assertBackgroundColor()
        
    def testNewItem(self):
        self.categories.append(category.Category('cat', filtered=True))
        dialog = self.viewer.newItemDialog(bitmap='new')
        tree = dialog[0][2]._treeCtrl
        firstChild, cookie = tree.GetFirstChild(tree.GetRootItem())
        self.failUnless(firstChild.IsChecked())


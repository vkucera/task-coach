'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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

import wx, sys
import test
from taskcoachlib import gui, command, config, persistence
from taskcoachlib.domain import category, attachment


class DummyEvent(object):
    def Skip(self):
        pass
    

class CategoryEditorTest(test.wxTestCase):
    def setUp(self):
        super(CategoryEditorTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.categories = self.taskFile.categories()
        self.categories.extend(self.createCategories())
        self.editor = gui.dialog.editor.CategoryEditor(self.frame, 
            list(self.categories), self.settings, self.categories, 
            self.taskFile, raiseDialog=False)

    def tearDown(self):
        # CategoryEditor uses CallAfter for setting the focus, make sure those 
        # calls are dealt with, otherwise they'll turn up in other tests
        if '__WXMAC__' not in wx.PlatformInfo and ('__WXMSW__' not in wx.PlatformInfo or sys.version_info < (2, 5)):
            wx.Yield() # pragma: no cover 
        super(CategoryEditorTest, self).tearDown()
        
    def createCommand(self):
        newCategoryCommand = command.NewCategoryCommand(self.categories)
        self.category = newCategoryCommand.items[0] # pylint: disable-msg=W0201
        return newCategoryCommand

    # pylint: disable-msg=E1101,E1103,W0212
    
    def createCategories(self):
        # pylint: disable-msg=W0201
        self.category = category.Category('Category to edit')
        self.attachment = attachment.FileAttachment('some attachment')
        self.category.addAttachments(self.attachment)
        return [self.category]

    def setSubject(self, newSubject):
        page = self.editor._interior[0]
        page._subjectEntry.SetFocus()
        page._subjectEntry.SetValue(newSubject)
        if '__WXGTK__' == wx.Platform:
            page._subjectSync.onSubjectEdited(DummyEvent())
        else:
            page._descriptionEntry.SetFocus()

    def setDescription(self, newDescription):
        page = self.editor._interior[0]
        page._descriptionEntry.SetFocus()
        page._descriptionEntry.SetValue(newDescription)
        if '__WXGTK__' == wx.Platform:
            page._descriptionSync.onDescriptionEdited(DummyEvent())
        else: 
            page._subjectEntry.SetFocus()
        
    def testCreate(self):
        self.assertEqual('Category to edit', self.editor._interior[0]._subjectEntry.GetValue())
    
    def testEditSubject(self):
        self.setSubject('Done')
        self.assertEqual('Done', self.category.subject())

    def testEditDescription(self):
        self.setDescription('Description')
        self.assertEqual('Description', self.category.description())        

    def testAddAttachment(self):
        self.editor._interior[2].viewer.onDropFiles(self.category, ['filename'])
        self.failUnless('filename' in [att.location() for att in self.category.attachments()])
        self.failUnless('filename' in [att.subject() for att in self.category.attachments()])
        
    def testRemoveAttachment(self):
        self.editor._interior[2].viewer.selectall()
        self.editor._interior[2].viewer.deleteItemCommand().do()
        self.assertEqual([], self.category.attachments())

    def testEditMutualExclusiveSubcategories(self):
        self.editor._interior[0]._exclusiveSubcategoriesCheckBox.SetValue(True)
        self.editor._interior[0]._exclusiveSubcategoriesSync.onAttributeEdited(DummyEvent())
        self.failUnless(self.category.hasExclusiveSubcategories())
        
    def testAddNote(self):
        viewer = self.editor._interior[1].viewer
        viewer.newItemCommand(viewer.presentation()).do() 
        self.assertEqual(1, len(self.category.notes()))

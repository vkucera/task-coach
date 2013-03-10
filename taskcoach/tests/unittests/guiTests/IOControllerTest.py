'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import gui, config, persistence
from taskcoachlib.domain import task, note, category
from taskcoachlib.thirdparty import lockfile
from unittests import dummy
import os
import shutil
import wx
import test


class IOControllerTest(test.TestCase):
    def setUp(self):
        super(IOControllerTest, self).setUp()
        self.taskStore = dummy.TaskStore()
        self.iocontroller = gui.IOController(self.taskStore, 
            lambda *args: None, self.settings)
        self.filename1 = 'whatever.tsk'
        self.filename2 = 'another.tsk' 

    def tearDown(self):
        self.taskStore.close()
        self.taskStore.stop()
        for filename in self.filename1, self.filename2:
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(filename + '.lock'):
                shutil.rmtree(filename + '.lock')  # pragma: no cover
            if os.path.exists(filename + '.delta'):
                os.remove(filename + '.delta')
        super(IOControllerTest, self).tearDown()
        
    def doIOAndCheckRecentFiles(self, open=None, saveas=None,  # pylint: disable=W0622
            saveselection=None, merge=None, expectedFilenames=None):
        open = open or []
        saveas = saveas or []
        saveselection = saveselection or []
        merge = merge or []
        self.doIO(open, saveas, saveselection, merge)
        self.checkRecentFiles(expectedFilenames or \
            open + saveas + saveselection + merge)
    
    def doIO(self, open, saveas, saveselection, merge):  # pylint: disable=W0622
        for filename in open:
            self.iocontroller.open(filename, fileExists=lambda filename: True)
        for filename in saveas:
            self.iocontroller.saveas(filename)
        for filename in saveselection:
            self.iocontroller.saveselection([], filename)
        for filename in merge:
            self.iocontroller.merge(filename)
        
    def checkRecentFiles(self, expectedFilenames):
        expectedFilenames.reverse()
        expectedFilenames = str(expectedFilenames)
        self.assertEqual(expectedFilenames, 
                         self.settings.get('file', 'recentfiles'))
        
    def testOpenFileAddsItToRecentFiles(self):
        self.doIOAndCheckRecentFiles(open=[self.filename1])
        
    def testOpenTwoFilesAddBothToRecentFiles(self):
        self.doIOAndCheckRecentFiles(open=[self.filename1, self.filename2])

    def testOpenTheSameFileTwiceAddsItToRecentFilesOnce(self):
        self.doIOAndCheckRecentFiles(open=[self.filename1] * 2,
                                     expectedFilenames=[self.filename1])
        
    def testSaveFileAsAddsItToRecentFiles(self):
        self.doIOAndCheckRecentFiles(saveas=[self.filename1])
        
    def testMergeFileAddsItToRecentFiles(self):    
        self.doIOAndCheckRecentFiles(open=[self.filename1], 
                                     merge=[self.filename2])
    
    def testSaveSelectionAddsItToRecentFiles(self):
        self.doIOAndCheckRecentFiles(saveselection=[self.filename1])
        
    def testMaximumNumberOfRecentFiles(self):
        maximumNumberOfRecentFiles = self.settings.getint('file', 
                                                          'maxrecentfiles')
        filenames = ['filename %d' % index for index in \
                     range(maximumNumberOfRecentFiles + 1)]
        self.doIOAndCheckRecentFiles(filenames, 
                                     expectedFilenames=filenames[1:])
        
    def testSaveTaskStoreWithoutTasksButWithNotes(self):
        self.taskStore.notes().append(note.Note(subject='Note'))
        
        def saveasReplacement(*args, **kwargs):  # pylint: disable=W0613
            self.saveAsCalled = True  # pylint: disable=W0201
            
        originalSaveAs = self.iocontroller.__class__.saveas
        self.iocontroller.__class__.saveas = saveasReplacement
        self.iocontroller.save()
        self.failUnless(self.saveAsCalled)
        self.iocontroller.__class__.saveas = originalSaveAs
    
    def testIOErrorOnSave(self):
        self.taskStore.setFilename(self.filename1)
        
        def saveasReplacement(*args, **kwargs):  # pylint: disable=W0613
            self.saveAsCalled = True
            
        originalSaveAs = self.iocontroller.__class__.saveas
        self.iocontroller.__class__.saveas = saveasReplacement
        self.taskStore.raiseError = IOError
        
        def showerror(*args, **kwargs):  # pylint: disable=W0613
            self.showerrorCalled = True  # pylint: disable=W0201
            
        self.iocontroller.save(showerror=showerror)
        self.failUnless(self.showerrorCalled and self.saveAsCalled)
        self.iocontroller.__class__.saveas = originalSaveAs

    def testIOErrorOnSaveAs(self):
        self.taskStore.raiseError = IOError
        
        def saveasReplacement(*args, **kwargs):  # pylint: disable=W0613
            self.saveAsCalled = True
            
        originalSaveAs = self.iocontroller.__class__.saveas
        
        def showerror(*args, **kwargs):  # pylint: disable=W0613
            self.showerrorCalled = True 
            # Prevent the recursive call of saveas:
            self.iocontroller.__class__.saveas = saveasReplacement
            
        self.iocontroller.saveas(filename=self.filename1, showerror=showerror)
        self.failUnless(self.showerrorCalled and self.saveAsCalled)
        self.iocontroller.__class__.saveas = originalSaveAs
    
    def testSaveSelectionAddsCategories(self):
        task1 = task.Task()
        task2 = task.Task()
        self.taskStore.tasks().extend([task1, task2])
        aCategory = category.Category('A Category')
        self.taskStore.categories().append(aCategory)
        for eachTask in self.taskStore.tasks():
            eachTask.addCategory(aCategory)
            aCategory.addCategorizable(eachTask)
        self.iocontroller.saveselection(tasks=self.taskStore.tasks(), 
                                        filename=self.filename1)
        taskStore = persistence.TaskStore()
        taskStore.setFilename(self.filename1)
        taskStore.load()
        try:
            self.assertEqual(1, len(taskStore.categories()))
        finally:
            taskStore.close()
            taskStore.stop()
     
    def testSaveSelectionAddsParentCategoriesWhenSubcategoriesAreUsed(self):
        task1 = task.Task()
        self.taskStore.tasks().extend([task1])
        aCategory = category.Category('A category')
        aSubCategory = category.Category('A subcategory')
        aCategory.addChild(aSubCategory)
        self.taskStore.categories().append(aCategory)
        task1.addCategory(aSubCategory)
        aSubCategory.addCategorizable(task1)
        self.iocontroller.saveselection(tasks=self.taskStore.tasks(), 
                                        filename=self.filename1)
        taskStore = persistence.TaskStore()
        taskStore.setFilename(self.filename1)
        taskStore.load()
        self.assertEqual(2, len(taskStore.categories()))
        
    def testIOErrorOnSaveSave(self):
        self.taskStore.raiseError = IOError
        self.taskStore.setFilename(self.filename1)
        
        def showerror(*args, **kwargs):  # pylint: disable=W0613
            self.showerrorCalled = True
            
        self.taskStore.tasks().append(task.Task())
        self.iocontroller._saveSave(self.taskStore, showerror)  # pylint: disable=W0212
        self.failUnless(self.showerrorCalled)

    def testIOErrorOnExport(self):
        self.taskStore.setFilename(self.filename1)
        self.taskStore.tasks().append(task.Task())
        
        def showerror(*args, **kwargs):  # pylint: disable=W0613
            self.showerrorCalled = True
            
        def openfile(*args, **kwargs):  # pylint: disable=W0613
            raise IOError
        
        self.iocontroller.exportAsHTML(None, filename="Don't ask", 
                                       openfile=openfile, showerror=showerror)
        self.failUnless(self.showerrorCalled)

    def testMerge(self):
        mergeFile = persistence.TaskStore()
        mergeFile.setFilename(self.filename2)
        mergeFile.tasks().append(task.Task(subject='Task to merge'))
        mergeFile.save()
        mergeFile.close()
        targetFile = persistence.TaskStore()
        iocontroller = gui.IOController(targetFile, lambda *args: None, 
                                        self.settings)
        iocontroller.merge(self.filename2)
        try:
            self.assertEqual('Task to merge', list(targetFile.tasks())[0].subject())
        finally:
            mergeFile.close()
            mergeFile.stop()
            targetFile.close()
            targetFile.stop()
        
    def testOpenWhenLockFailed(self):
        self.taskStore.raiseError = lockfile.LockFailed
        
        def askOpenUnlocked(*args, **kwargs):  # pylint: disable=W0613
            self.askOpenUnlockedCalled = True 
            
        self.iocontroller._IOController__askOpenUnlocked = askOpenUnlocked
        self.iocontroller.open(self.filename1, fileExists=lambda filename: True)
        self.failUnless(self.askOpenUnlockedCalled)

    def testOpenWhenAlreadyLocked(self):
        self.taskStore.raiseError = lockfile.LockTimeout
        
        def askBreakLock(*args, **kwargs):  # pylint: disable=W0613
            self.askBreakLockCalled = True
            
        self.iocontroller._IOController__askBreakLock = askBreakLock
        self.iocontroller.open(self.filename1, fileExists=lambda filename: True)
        self.failUnless(self.askBreakLockCalled)


class IOControllerOverwriteExistingFileTest(test.TestCase):
    def setUp(self):
        super(IOControllerOverwriteExistingFileTest, self).setUp()
        self.originalFileSelector = wx.FileSelector
        wx.FileSelector = lambda *args, **kwargs: 'filename without extension to trigger our own overwrite warning'
        self.originalMessageBox = wx.MessageBox
        
        def messageBox(*args, **kwargs):  # pylint: disable=W0613
            self.userWarned = True
            return wx.CANCEL
        
        wx.MessageBox = messageBox
        self.taskStore = dummy.TaskStore()
        self.iocontroller = gui.IOController(self.taskStore, 
            lambda *args: None, self.settings)

    def tearDown(self):
        self.taskStore.close()
        self.taskStore.stop()
        wx.FileSelector = self.originalFileSelector
        wx.MessageBox = self.originalMessageBox
        super(IOControllerOverwriteExistingFileTest, self).tearDown()
        
    def testCancelSaveAsExistingFile(self):
        self.iocontroller.saveas(fileExists=lambda filename: True)
        self.failUnless(self.userWarned)
        
    def testCancelSaveSelectionToExistingFile(self):
        self.iocontroller.saveselection([], fileExists=lambda filename: True)
        self.failUnless(self.userWarned)
        
    def testCancelExportAsHTMLToExistingFile(self):
        self.iocontroller.exportAsHTML(None, fileExists=lambda filename: True)
        self.failUnless(self.userWarned)
        
    def testCancelExportAsCSVToExistingFile(self):
        self.iocontroller.exportAsCSV(None, fileExists=lambda filename: True)
        self.failUnless(self.userWarned)
        
    def testCancelExportAsICalendarToExistingFile(self):
        self.iocontroller.exportAsICalendar(None, 
                                            fileExists=lambda filename: True)
        self.failUnless(self.userWarned)

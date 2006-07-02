import test, gui, config
from unittests import dummy
import domain.task as task

class IOControllerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.iocontroller = gui.IOController(dummy.TaskFile(), lambda *args: None, self.settings)
        self.filename1 = 'whatever.tsk'
        self.filename2 = 'another.tsk' 
        
    def doIOAndCheckRecentFiles(self, open=None, saveas=None, saveselection=None, merge=None, expectedFilenames=None):
        open = open or []
        saveas = saveas or []
        saveselection = saveselection or []
        merge = merge or []
        self.doIO(open, saveas, saveselection, merge)
        self.checkRecentFiles(expectedFilenames or open+saveas+saveselection+merge)
    
    def doIO(self, open, saveas, saveselection, merge):
        for filename in open:
            self.iocontroller.open(filename)
        for filename in saveas:
            self.iocontroller.saveas(filename)
        for filename in saveselection:
            self.iocontroller.saveselection([], filename)
        for filename in merge:
            self.iocontroller.merge(filename)
        
    def checkRecentFiles(self, expectedFilenames):
        expectedFilenames.reverse()
        expectedFilenames = str(expectedFilenames)
        self.assertEqual(expectedFilenames, self.settings.get('file', 'recentfiles'))
        
    def testOpenFileAddsItToRecentFiles(self):
        self.doIOAndCheckRecentFiles(open=[self.filename1])
        
    def testOpenTwoFilesAddBothToRecentFiles(self):
        self.doIOAndCheckRecentFiles(open=[self.filename1, self.filename2])

    def testOpenTheSameFileTwiceAddsItToRecentFilesOnce(self):
        self.doIOAndCheckRecentFiles(open=[self.filename1]*2,
                                     expectedFilenames=[self.filename1])
        
    def testSaveFileAsAddsItToRecentFiles(self):
        self.doIOAndCheckRecentFiles(saveas=[self.filename1])
        
    def testMergeFileAddsItToRecentFiles(self):    
        self.doIOAndCheckRecentFiles(open=[self.filename1], merge=[self.filename2])
    
    def testSaveSelectionAddsItToRecentFiles(self):
        self.doIOAndCheckRecentFiles(saveselection=[self.filename1])
        
    def testMaximumNumberOfRecentFiles(self):
        maximumNumberOfRecentFiles = self.settings.getint('file', 'maxrecentfiles')
        filenames = ['filename %d'%index for index in range(maximumNumberOfRecentFiles+1)]
        self.doIOAndCheckRecentFiles(filenames, expectedFilenames=filenames[1:])
        
    

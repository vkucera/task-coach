# -*- coding: utf-8 -*-

import test, sys, os, meta, config, patterns

class SettingsUnderTest(config.Settings):
    def __init__(self, *args, **kwargs):
        kwargs['load'] = False
        super(SettingsUnderTest, self).__init__(*args, **kwargs)

    def read(self, *args):
        pass


class SettingsTestCase(test.TestCase):
    def setUp(self):
        self.settings = SettingsUnderTest()

    def tearDown(self):
        super(SettingsTestCase, self).tearDown()
        del self.settings


class SettingsTest(SettingsTestCase):
    def testDefaults(self):
        self.failUnless(self.settings.has_section('view'))
        self.assertEqual('False', self.settings.get('view', 'filtersidebar'))

    def testSet(self):
        self.settings.set('view', 'toolbarsize', '16')
        self.assertEqual('16', self.settings.get('view', 'toolbarsize'))

    def testPathWithAppData(self):
        environ = {'APPDATA' : 'test' }
        expected = os.path.join(environ['APPDATA'], meta.filename)
        self.assertEqual(expected, self.settings.path(environ=environ))

    def testPathWithoutAppData(self):
        expected = os.path.join(os.path.expanduser("~"), '.%s'%meta.filename)
        self.assertEqual(expected, self.settings.path(environ={}))

    def testGetList_EmptyByDefault(self):
        self.assertEqual([], self.settings.getlist('file', 'recentfiles'))

    def testSetList_Empty(self):
        self.settings.setlist('file', 'recentfiles', [])
        self.assertEqual([], self.settings.getlist('file', 'recentfiles'))
    
    def testSetList_SimpleStrings(self):
        recentfiles = ['abc', 'C:\Documents And Settings\Whatever']
        self.settings.setlist('file', 'recentfiles', recentfiles)
        self.assertEqual(recentfiles, 
                         self.settings.getlist('file', 'recentfiles'))
        
    def testSetList_UnicodeStrings(self):
        recentfiles = ['Ã¼mlaut', 'Î£Î¿Î¼Î· Ï‡Ï�ÎµÎµÎº']
        self.settings.setlist('file', 'recentfiles', recentfiles)
        self.assertEqual(recentfiles, 
                         self.settings.getlist('file', 'recentfiles'))
        
        
class SettingsIOTest(SettingsTestCase):
    def setUp(self):
        super(SettingsIOTest, self).setUp()
        import StringIO
        self.fakeFile = StringIO.StringIO()

    def testSave(self):
        self.settings.write(self.fakeFile)
        self.fakeFile.seek(0)
        self.assertEqual('[%s]\n'%self.settings.sections()[0], 
            self.fakeFile.readline())

    def testRead(self):
        self.fakeFile.write('[testing]\n')
        self.fakeFile.seek(0)
        self.settings.readfp(self.fakeFile)
        self.failUnless(self.settings.has_section('testing'))


class SettingsObservableTest(SettingsTestCase):
    def setUp(self):
        super(SettingsObservableTest, self).setUp()
        self.events = []
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType='view.toolbarsize')
        
    def onEvent(self, event):
        self.events.append(event)
        
    def testChangingTheSettingCausesNotification(self):
        self.settings.set('view', 'toolbarsize', '16')
        self.assertEqual('16', self.events[0].value())
        
    def testChangingAnotherSettingDoesNotCauseANotification(self):
        self.settings.set('view', 'statusbar', 'True')
        self.failIf(self.events)


class UnicodeAwareConfigParserTest(test.TestCase):
    ''' The default Python ConfigParser does not deal with unicode. So we
        build a wrapper around ConfigParser that does. These are the unitttests
        for UnicodeAwareConfigParser. '''
        
    def setUp(self):
        import config.settings, StringIO
        self.parser = config.settings.UnicodeAwareConfigParser()
        self.parser.add_section('section')
        self.iniFile = StringIO.StringIO()
        self.asciiValue = 'ascii'
        self.unicodeValue = u'Ã�â€¦ÃŽÂ½ÃŽÂ¹ÃŽÂ³ÃŽÂ¿ÃŽÂ´ÃŽÂ·'
        
    def testWriteAsciiValue(self):
        self.parser.set('section', 'setting', self.asciiValue)
        self.parser.write(self.iniFile)
        fileContents = self.iniFile.getvalue()
        self.assertEqual('[section]\nsetting = %s\n\n'%self.asciiValue, 
                         fileContents)
                
    def testWriteUnicodeValue(self):
        self.parser.set('section', 'setting', self.unicodeValue)
        self.parser.write(self.iniFile)
        fileContents = self.iniFile.getvalue()
        self.assertEqual('[section]\nsetting = %s\n\n' \
                         %self.unicodeValue.encode('utf-8'), fileContents)
    
    def testReadAsciiValue(self):
        iniFileContents = '[section]\nsetting = %s\n\n'%self.asciiValue
        self.iniFile.write(iniFileContents)
        self.iniFile.seek(0)
        self.parser.readfp(self.iniFile)
        self.assertEqual(self.asciiValue, self.parser.get('section', 'setting'))
        
    def testReadUnicodeValue(self):
        iniFileContents = '[section]\nsetting = %s\n\n' \
            %self.unicodeValue.encode('utf-8')
        self.iniFile.write(iniFileContents)
        self.iniFile.seek(0)
        self.parser.readfp(self.iniFile)
        self.assertEqual(self.unicodeValue, 
                         self.parser.get('section', 'setting'))
        

class SpecificSettingsTest(SettingsTestCase):
    def testDefaultWindowPosition(self):
        self.assertEqual('(-1, -1)', self.settings.get('window', 'position'))

    def testDefaultTaskCategoryFilterList(self):
        self.assertEqual([], self.settings.getlist('view', 
            'taskcategoryfilterlist'))
            

class SettingsFileLocationTest(SettingsTestCase):
    def testDefaultSetting(self):
        self.assertEqual(False, self.settings.getboolean('file', 
                         'saveinifileinprogramdir'))

    def testPathWhenNotSavingIniFileInProgramDir(self):
        self.assertNotEqual(sys.argv[0], self.settings.path())
        
    def testPathWhenSavingIniFileInProgramDir(self):
        self.settings.setboolean('file', 'saveinifileinprogramdir', True)
        self.assertEqual(os.path.dirname(sys.argv[0]), self.settings.path())
        
    def testPathWhenSavingIniFileInProgramDirAndRunFromZipFile(self):
        self.settings.setboolean('file', 'saveinifileinprogramdir', True)
        sys.argv.insert(0, r'd:\TaskCoach\library.zip')
        self.assertEqual(r'd:\TaskCoach', self.settings.path())
        del sys.argv[0]
        
    def testSettingSaveIniFileInProgramDirToFalseRemovesIniFile(self):
        self.settings.setboolean('file', 'saveinifileinprogramdir', True)
        self.settings.setboolean('file', 'saveinifileinprogramdir', False)
        
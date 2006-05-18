# -*- coding: utf-8 -*-

import test, sys, os, meta, config

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
        self.notifications = 0
        self.settings.registerObserver(self.onNotify, ('view', 'toolbarsize'))
        
    def onNotify(self, *args, **kwargs):
        self.notifications += 1
        
    def testChangingTheSettingCausesNotification(self):
        self.settings.set('view', 'toolbarsize', '16')
        self.assertEqual(1, self.notifications)
        
    def testChangingAnotherSettingDoesNotCauseANotification(self):
        self.settings.set('view', 'statusbar', 'True')
        self.assertEqual(0, self.notifications)


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
        self.unicodeValue = u'υνιγοδη'
        
    def testWriteAsciiValue(self):
        self.parser.set('section', 'setting', self.asciiValue)
        self.parser.write(self.iniFile)
        fileContents = self.iniFile.getvalue()
        self.assertEqual('[section]\nsetting = %s\n\n'%self.asciiValue, fileContents)
                
    def testWriteUnicodeValue(self):
        self.parser.set('section', 'setting', self.unicodeValue)
        self.parser.write(self.iniFile)
        fileContents = self.iniFile.getvalue()
        self.assertEqual('[section]\nsetting = %s\n\n'%self.unicodeValue.encode('utf-8'), fileContents)
    
    def testReadAsciiValue(self):
        iniFileContents = '[section]\nsetting = %s\n\n'%self.asciiValue
        self.iniFile.write(iniFileContents)
        self.iniFile.seek(0)
        self.parser.readfp(self.iniFile)
        self.assertEqual(self.asciiValue, self.parser.get('section', 'setting'))
        
    def testReadUnicodeValue(self):
        iniFileContents = '[section]\nsetting = %s\n\n'%self.unicodeValue.encode('utf-8')
        self.iniFile.write(iniFileContents)
        self.iniFile.seek(0)
        self.parser.readfp(self.iniFile)
        self.assertEqual(self.unicodeValue, self.parser.get('section', 'setting'))
        

class SpecificSettingsTest(SettingsTestCase):
    def testDefaultWindowPosition(self):
        self.assertEqual('(-1, -1)', self.settings.get('window', 'position'))

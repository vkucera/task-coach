import test, sys, os, meta, config

class Settings(config.Settings):
    def read(self, *args):
        pass


class SettingsTestCase(test.TestCase):
    def setUp(self):
        self.settings = Settings()

    def tearDown(self):
        del self.settings


class SettingsTest(SettingsTestCase):
    def testDefaults(self):
        self.failUnless(self.settings.has_section('view'))
        self.assertEqual('False', self.settings.get('view', 'finddialog'))

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
        
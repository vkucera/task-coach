import test, sys, os, meta, config


class Settings(config.Settings):
    def read(self, *args):
        pass

class SettingsTest(test.TestCase):
    def setUp(self):
        self.settings = Settings()

    def tearDown(self):
        del self.settings

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


class SettingsIOTest(test.TestCase):
    def setUp(self):
        import StringIO
        self.fakeFile = StringIO.StringIO()
        self.settings = Settings()

    def tearDown(self):
        del self.settings

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



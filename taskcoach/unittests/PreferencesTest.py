import test, gui

class DummySettings:
    def __init__(self, assertEqual):
        ''' DummySettings is not a TestCase, so we pass it the
        assertEqual method of the TestCase '''
        self.assertEqual = assertEqual
        
    def getboolean(self, section, setting):
        return False
        
    def get(self, section, setting):
        return 'bla'
        
    def getint(self, section, setting):
        return 0
        
    def set(self, section, setting, value):
        self.assertEqual(type(''), type(value))


class PreferencesTest(test.wxTestCase):
    def setUp(self):
        self.settings = DummySettings(self.assertEqual)
        self.preferences = gui.Preferences(parent=self.frame, title='Test',
            settings=self.settings)
        
    def testCancel(self):
        self.preferences.cancel()
        
    def testOk(self):
        self.preferences.ok()
import test, gui, config, wx


class PreferencesTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.preferences = gui.Preferences(parent=self.frame, title='Test',
            settings=self.settings)
        self.originalColor = self.settings.get('color', 'activetasks')
        self.newColor = (1, 2, 29)
        
    def testCancel(self):
        self.preferences[3]._colorSettings[0][2].SetColour(self.newColor)
        self.preferences.cancel()
        self.assertEqual(self.originalColor, self.settings.get('color', 'activetasks'))
        
    def testOk(self):
        self.preferences[3]._colorSettings[0][2].SetColour(self.newColor)
        self.preferences.ok()
        self.assertEqual(self.newColor, eval(self.settings.get('color', 'activetasks')))
        
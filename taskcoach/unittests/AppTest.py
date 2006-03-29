import test, meta, taskcoach, wx

class AppTests(test.TestCase):
    def testAppProperties(self):
        # Normally I prefer one assert per test, but creating the app is
        # expensive, so we do all the queries in one test method.
        app = taskcoach.App(loadSettings=False, loadTaskFile=False)
        wxApp = wx.GetApp()
        self.assertEqual(meta.name, wxApp.GetAppName())
        self.assertEqual(meta.author, wxApp.GetVendorName())

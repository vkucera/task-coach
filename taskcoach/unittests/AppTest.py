import test, meta, taskcoach, wx

class AppTests(test.TestCase):
    def setUp(self):
        self.app = taskcoach.App(loadSettings=False, loadTaskFile=False)

    def testAppName(self):
        self.assertEqual(meta.name, wx.GetApp().GetAppName())

    def testVendorName(self):
        self.assertEqual(meta.author, wx.GetApp().GetVendorName())


import base

class TestLaunch(base.Win32TestCase):
    def test_launch(self):
        self.expectWindow('^Tip of the Day$')

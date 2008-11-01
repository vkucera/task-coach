
import os, base
from taskcoachlib import meta

class TestLaunch(base.Win32TestCase):
    def test_launch(self):
        self.expectWindow('^Tip of the Day$')

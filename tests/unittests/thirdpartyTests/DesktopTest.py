import test, thirdparty.desktop

class DesktopTest(test.TestCase):
    def testOpenByForcingAnException(self):
        ''' desktop.open will open a browser or other program and we
        don't want that during unittesting. So we provide a non-existing
        desktop, which will cause desktop.open to raise an exception. '''

        try:
            thirdparty.desktop.open('http://taskcoach.niessink.com',
                desktop='Force exception')
            self.fail('desktop.open ignored our non-existing desktop?!')
        except OSError:
            pass

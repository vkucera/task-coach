import test, gui, wx, config
from gui import uicommand

class DummyCommand(uicommand.UICommand):
    def onActivateCommand(self, event):
        self.event = event

class DummyCheckCommand(uicommand.UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(DummyCheckCommand, self).__init__(section='test',
            setting='test', *args, **kwargs)

    def onCommandActivate(self, event):
        self.event = event

class DummyRadioCommand(uicommand.UIRadioCommand):
    def __init__(self, *args, **kwargs):
        super(DummyRadioCommand, self).__init__(section='test',
            setting='test', value='on', *args, **kwargs)

    def onCommandActivate(self, event):
        self.event = event

class DummySettings(config.Settings):
    def __init__(self, value, *args, **kwargs):
        super(DummySettings, self).__init__(*args, **kwargs)
        self.add_section('test')
        self.set('test', 'test', str(value))

    def read(self, *args):
        pass

class MenuTest(test.wxTestCase):
    def setUp(self):
        self.menu = gui.menu.Menu(self.frame)
        self.command = DummyCommand()

    def testLenEmptyMenu(self):
        self.assertEqual(0, len(self.menu))

    def testLenNonEmptyMenu(self):
        self.menu.appendUICommand(self.command)
        self.menu.AppendSeparator()
        self.assertEqual(2, len(self.menu))

    def testAppendUICommandDoesNotInvokeTheCommand(self):
        self.menu.appendUICommand(self.command)
        self.failIf(hasattr(self.command, 'event'))

    def testCheckedCheckCommandIsNotInvoked(self):
        settings = DummySettings(True)
        command = DummyCheckCommand(settings=settings)
        self.menu.appendUICommand(command)
        self.failIf(hasattr(self.command, 'event'))

    def testUncheckedUICheckCommandIsInvoked(self):
        settings = DummySettings(False)
        command = DummyCheckCommand(settings=settings)
        self.menu.appendUICommand(command)
        self.assertEqual(command._id, command.event.GetId())

    def testUncheckedUIRadioCommandIsNotInvoked(self):
        settings = DummySettings('off')
        command = DummyRadioCommand(settings=settings)
        self.menu.appendUICommand(command)
        self.failIf(hasattr(self.command, 'event'))

    def testCheckedUIRadioCommandIsInvoked(self):
        settings = DummySettings('on')
        command = DummyRadioCommand(settings=settings)
        self.menu.appendUICommand(command)
        self.assertEqual(command._id, command.event.GetId())

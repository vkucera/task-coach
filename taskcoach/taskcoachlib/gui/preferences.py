import widgets, wx
from i18n import _

class SettingsPage(widgets.BookPage):
    def __init__(self, settings=None, *args, **kwargs):
        super(SettingsPage, self).__init__(*args, **kwargs)
        self.settings = settings
        self._booleanSettings = []

    def addBooleanSetting(self, section, setting, text):
        checkBox = wx.CheckBox(self, -1)
        checkBox.SetValue(self.settings.getboolean(section, setting))
        self.addEntry(text, checkBox)
        self._booleanSettings.append((section, setting, checkBox))
        
    def ok(self):
        for section, setting, checkBox in self._booleanSettings:
            self.settings.set(section, setting, str(checkBox.IsChecked()))


class SavePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(SavePage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('file', 'autosave', 
            _('Auto save after every change'))
            
               
class StartupPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(StartupPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('window', 'splash', _('Splash screen'))


class Preferences(widgets.ListbookDialog):
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(Preferences, self).__init__(bitmap='configure', *args, **kwargs) 
                   
    def addPages(self):
        self.SetMinSize((300, 200))
        self._book.AddPage(StartupPage(parent=self._book, columns=2, settings=self.settings), _('Startup'))
        self._book.AddPage(SavePage(parent=self._book, columns=2, settings=self.settings), _('Save'), bitmap='save')
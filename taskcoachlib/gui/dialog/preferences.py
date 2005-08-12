import widgets, wx, meta
from i18n import _

class SettingsPage(widgets.BookPage):
    def __init__(self, settings=None, *args, **kwargs):
        super(SettingsPage, self).__init__(*args, **kwargs)
        self.settings = settings
        self._booleanSettings = []
        self._choiceSettings = []
        
    def addBooleanSetting(self, section, setting, text, helpText=''):
        checkBox = wx.CheckBox(self, -1)
        checkBox.SetValue(self.settings.getboolean(section, setting))
        self.addEntry(text, checkBox, helpText)
        self._booleanSettings.append((section, setting, checkBox))

    def addChoiceSetting(self, section, setting, text, choices, helpText=''):
        choice = wx.Choice(self, -1)
        for choiceValue, choiceText in choices:
            choice.Append(choiceText, choiceValue)
            if choiceValue == self.settings.get(section, setting):
                choice.SetSelection(choice.GetCount()-1)
        if choice.GetSelection() == wx.NOT_FOUND: # force a selection if necessary
            choice.SetSelection(0)
        self.addEntry(text, choice, helpText)
        self._choiceSettings.append((section, setting, choice))
        
    def ok(self):
        for section, setting, checkBox in self._booleanSettings:
            self.settings.set(section, setting, str(checkBox.IsChecked()))
        for section, setting, choice in self._choiceSettings:
            self.settings.set(section, setting, choice.GetClientData(choice.GetSelection()))
            

class SavePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(SavePage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('file', 'autosave', 
            _('Auto save after every change'))
        self.addBooleanSetting('file', 'backup', 
            _('Create backup copy when opening a %s file')%meta.name)
            
               
class StartupPage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(StartupPage, self).__init__(*args, **kwargs)
        self.addBooleanSetting('window', 'splash', _('Splash screen'),
            _('This setting will take effect after you restart %s')%meta.name)


class LanguagePage(SettingsPage):
    def __init__(self, *args, **kwargs):
        super(LanguagePage, self).__init__(*args, **kwargs)
        self.addChoiceSetting('view', 'language', _('Language'), 
            [('en_US', _('English (US)')), 
             ('en_GB', _('English (UK)')),
             ('de_DE', _('German')),
             ('nl_NL', _('Dutch')),
             ('fr_FR', _('French')),
             ('zh_CN', _('Simplified Chinese')),
             ('ru_RU', _('Russian')),
             ('es_ES', _('Spanish'))],
             _('This setting will take effect after you restart %s')%meta.name)


class Preferences(widgets.ListbookDialog):
    def __init__(self, settings=None, *args, **kwargs):
        self.settings = settings
        super(Preferences, self).__init__(bitmap='configure', *args, **kwargs) 
                   
    def addPages(self):
        self.SetMinSize((300, 300))
        self._interior.AddPage(StartupPage(parent=self._interior, columns=3, settings=self.settings), _('Startup'), bitmap='taskcoach')
        self._interior.AddPage(SavePage(parent=self._interior, columns=3, settings=self.settings), _('Save'), bitmap='save')
        self._interior.AddPage(LanguagePage(parent=self._interior, columns=3, settings=self.settings), _('Language'), bitmap='language')